from __future__ import annotations

from datetime import datetime

import pandas as pd

from .archetype import Archetype
from .card import Card
from .enums import *
from .yugidb import YugiDB


class CustomDB(YugiDB):
    def __init__(self, name, dbpath):
        self.name = name
        self.dbpath = dbpath
        super().__init__()

    def _build_card_db(self, con):
        def make_datetime(timestamp: int):
            try:
                dt = datetime.fromtimestamp(timestamp)
            except:
                dt = None
            return dt

        def apply_enum(value: int, enum_class):
            return [enum_member for enum_member in enum_class if value & enum_member]

        def parse_pendulum(value: int):
            lscale = (value & 0xFF000000) >> 24
            rscale = (value & 0x00FF0000) >> 16
            level = value & 0x0000FFFF
            return lscale, rscale, level

        cards: list[dict] = pd.read_sql_query(
            """
            SELECT *
            FROM datas
            INNER JOIN texts
            USING(id)
            """,
            con,
        ).to_dict(orient="records")
        self.card_data: dict[int, Card] = {}

        for card in cards:
            card_type = apply_enum(card["type"], Type)
            card_race = Race(card["race"])
            card_attribute = Attribute(card["attribute"])
            card_category = apply_enum(card["category"], Category)
            card_genre = apply_enum(card["genre"], Genre)

            if card["type"] & Type.Pendulum:
                card_lscale, card_rscale, card_level = parse_pendulum(card["level"])
            else:
                card_lscale, card_rscale, card_level = 0, 0, card["level"]

            if card["type"] & Type.Link:
                card_def = 0
                card_markers = apply_enum(card["def"], LinkMarker)
            else:
                card_def = card["def"]
                card_markers = []

            card_data = Card(
                id=card["id"],
                name=card["name"],
                type=card_type,
                race=card_race,
                attribute=card_attribute,
                category=card_category,
                genre=card_genre,
                level=card_level,
                lscale=card_lscale,
                rscale=card_rscale,
                atk=card["atk"],
                def_=card_def,
                linkmarkers=card_markers,
                text=card["desc"],
                tcgdate=make_datetime(card["tcgdate"]),
                ocgdate=make_datetime(card["ocgdate"]),
                ot=card["ot"],
                archcode=card["setcode"],
                supportcode=card["support"],
                alias=card["alias"],
                scripted=card["script"] is not None,
                script=card["script"],
            )
            self.card_data[card["id"]] = card_data

    def _build_archetype_db(self, con):
        archetypes = pd.read_sql_query(
            """
            SELECT name,
                CASE
                    WHEN officialcode > 0 THEN officialcode
                    ELSE betacode
                END AS archcode 
            FROM setcodes
            WHERE (officialcode > 0 AND betacode = officialcode) OR (officialcode = 0 AND betacode > 0);
            """,
            con,
        ).to_dict(orient="records")

        self.arch_data: dict[int, Archetype] = {
            arch["archcode"]: Archetype(
                id=arch["archcode"],
                name=arch["name"],
            )
            for arch in archetypes
        }

        def split_chunks(n: int, nchunks: int):
            return [(n >> (16 * i)) & 0xFFFF for i in range(nchunks)]

        for card in self.card_data.values():
            card.archetypes = [
                arch["archcode"]
                for chunk in split_chunks(card.archcode, 4)
                for arch in archetypes
                if arch["archcode"] == chunk
            ]
            card.support = [
                arch["archcode"]
                for chunk in split_chunks(card.supportcode, 2)
                for arch in archetypes
                if arch["archcode"] == chunk
            ]
            card.related = [
                arch["archcode"]
                for chunk in split_chunks(card.supportcode >> 32, 2)
                for arch in archetypes
                if arch["archcode"] == chunk
            ]

            for arch in card.archetypes:
                self.arch_data[arch].cards.append(card.id)
            for arch in card.support:
                self.arch_data[arch].support.append(card.id)
            for arch in card.related:
                self.arch_data[arch].related.append(card.id)

    def _build_set_db(self, _):
        self.set_data = {}
