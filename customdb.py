from __future__ import annotations

import pandas as pd

from .archetype import Archetype
from .card import Card
from .yugidb import YugiDB


class CustomDB(YugiDB):
    def __init__(self, name, dbpath, rebuild_pkl=False):
        self.name = name
        self.dbpath = dbpath
        super().__init__(rebuild_pkl=rebuild_pkl)

    def _build_card_db(self, con):
        values = ",".join(
            [
                "datas.id",
                "datas.ot",
                "datas.alias",
                "datas.setcode as _archcode",
                "datas.type as _type",
                "datas.atk",
                "datas.def as _def",
                "datas.level as _level",
                "datas.race as _race",
                "datas.attribute as _attribute",
                "datas.category as _category",
                "datas.genre as _genre",
                "datas.script",
                "datas.support as _supportcode",
                "datas.ocgdate as _ocgdate",
                "datas.tcgdate as _tcgdate",
                "texts.name",
                "texts.desc as text",
            ]
        )

        cards: list[dict] = pd.read_sql_query(
            f"""
            SELECT {values}
            FROM datas
            INNER JOIN texts
            USING(id)
            """,
            con,
        ).to_dict(orient="records")

        self.card_data = {card["id"]: Card(**card) for card in cards}

    def _build_archetype_db(self, con):
        archetypes: list[dict] = pd.read_sql_query(
            """
            SELECT name,
                CASE
                    WHEN officialcode > 0 THEN officialcode
                    ELSE betacode
                END AS id 
            FROM setcodes
            WHERE (officialcode > 0 AND betacode = officialcode) OR (officialcode = 0 AND betacode > 0);
            """,
            con,
        ).to_dict(orient="records")

        self.arch_data: dict[int, Archetype] = {
            arch["id"]: Archetype(**arch) for arch in archetypes
        }

        def split_chunks(n: int, nchunks: int):
            return [(n >> (16 * i)) & 0xFFFF for i in range(nchunks)]

        for card in self.card_data.values():
            card.archetypes = [
                arch["id"]
                for chunk in split_chunks(card._archcode, 4)
                for arch in archetypes
                if arch["id"] == chunk
            ]
            card.support = [
                arch["id"]
                for chunk in split_chunks(card._supportcode, 2)
                for arch in archetypes
                if arch["id"] == chunk
            ]
            card.related = [
                arch["id"]
                for chunk in split_chunks(card._supportcode >> 32, 2)
                for arch in archetypes
                if arch["id"] == chunk
            ]

            for arch in card.archetypes:
                self.arch_data[arch].cards.append(card.id)
            for arch in card.support:
                self.arch_data[arch].support.append(card.id)
            for arch in card.related:
                self.arch_data[arch].related.append(card.id)

    def _build_set_db(self, _):
        self.set_data = {}
