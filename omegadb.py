from __future__ import annotations

import math
import os
from datetime import datetime

import pandas as pd
import requests

from .archetype import Archetype
from .card import Card
from .enums import Attribute, Category, Genre, LinkMarker, Race, Type
from .set import Set
from .yugidb import YugiDB

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"


class OmegaDB(YugiDB):
    initialised = False

    def __init__(self):
        self.name = "OmegaDB"
        self.dbpath = "db/omega/omega.db"
        if not OmegaDB.initialised:
            self._download_omegadb()
            OmegaDB.initialised = True
        super().__init__()

    def _download_omegadb(self, force_update: bool = False):
        def download(url: str, path: str):
            r = requests.get(url, allow_redirects=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)

        db_url = os.path.join(OMEGA_BASE_URL, "OmegaDB.cdb")
        hash_url = os.path.join(OMEGA_BASE_URL, "Database.hash")
        dbdir = os.path.dirname(self.dbpath)
        hashpath = os.path.join(dbdir, "omega.hash")

        if not os.path.exists(dbdir):
            os.makedirs(dbdir)

        if os.path.exists(self.dbpath) and not force_update:
            if os.path.exists(hashpath):
                with open(hashpath) as f:
                    old_hash = f.read()
            else:
                old_hash = None

            try:
                download(hash_url, hashpath)
            except requests.ConnectionError:
                print("Failed to get current Hash, skipping update.")
                return

            with open(hashpath) as f:
                new_hash = f.read()

            if old_hash == new_hash:
                return
            else:
                print("A new version of the Omega database is available.")
                user_response = input(
                    "Do you want to update the database? (y/n): "
                ).lower()
                if user_response != "y":
                    print("Skipping database update.")
                    return

        print("Downloading up-to-date db...")
        download(db_url, self.dbpath)
        download(hash_url, hashpath)

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
            LEFT JOIN koids
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
                card["id"],
                card["name"],
                card_type,
                card_race,
                card_attribute,
                card_category,
                card_genre,
                card_level,
                card_lscale,
                card_rscale,
                card["atk"],
                card_def,
                card_markers,
                card["desc"],
                [],
                [],
                [],
                [],
                make_datetime(card["tcgdate"]),
                make_datetime(card["ocgdate"]),
                card["ot"],
                card["setcode"],
                card["support"],
                card["alias"],
                not math.isnan(card["script"]),
                card["script"],
                int(card["koid"]) if not math.isnan(card["koid"]) else 0,
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
                arch["archcode"],
                arch["name"],
                [],
                [],
                [],
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

    def _build_set_db(self, con):
        sets = pd.read_sql_query(
            """
            SELECT
                packs.id,
                packs.abbr,
                packs.name,
                packs.ocgdate,
                packs.tcgdate,
                GROUP_CONCAT(relations.cardid) AS cardids
            FROM
                packs
            JOIN
                relations ON packs.id = relations.packid
            GROUP BY
                packs.name;
            """,
            con,
        ).to_dict(orient="records")

        self.set_data: dict[int, Set] = {
            set["id"]: Set(
                set["id"],
                set["name"],
                set["abbr"],
                set["tcgdate"],
                set["ocgdate"],
                [
                    int(id)
                    for id in set["cardids"].split(",")
                    if int(id) in self.card_data
                ],
            )
            for set in sets
        }

        for set in self.set_data.values():
            for cardid in set.contents:
                self.card_data[cardid].sets.append(set.id)
