from __future__ import annotations

import os
import sqlite3

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

        for card in self.card_data.values():
            for archid in card.archetypes:
                if archid == 0 or archid not in self.arch_data:
                    continue
                self.arch_data[archid].members.append(card.id)
            for archid in card.support:
                if archid == 0 or archid not in self.arch_data:
                    continue
                self.arch_data[archid].support.append(card.id)
            for archid in card.related:
                if archid == 0 or archid not in self.arch_data:
                    continue
                self.arch_data[archid].related.append(card.id)

    def _build_set_db(self, _):
        self.set_data = {}

    @classmethod
    def from_data(
        cls,
        name: str,
        dbpath: str,
        card_data: list[Card],
        arch_data: list[Archetype] = [],
    ):
        custom_db = cls.__new__(cls)
        custom_db.name = name
        custom_db.dbpath = dbpath

        custom_db.card_data = {card.id: card for card in card_data}
        custom_db.arch_data = {arch.id: arch for arch in arch_data}

        return custom_db

    def _finalize_initialization(self):
        self.dbdir = os.path.dirname(self.dbpath)
        self.cardpkl = os.path.join(self.dbdir, "cards.pkl")
        self.setspkl = os.path.join(self.dbdir, "sets.pkl")
        self.archpkl = os.path.join(self.dbdir, "archetypes.pkl")
        if not os.path.exists(self.dbdir):
            os.makedirs(self.dbdir)
        self.save_pickles()
