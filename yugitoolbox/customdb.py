from __future__ import annotations

import os
import sqlite3

import pandas as pd

from .archetype import Archetype
from .card import Card
from .yugidb import YugiDB

SQL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql")


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
                "texts.desc as _text",
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

        self._card_data = {card["id"]: Card(**card) for card in cards}

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

        for card in self._card_data.values():
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
        self._set_data = {}

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

        custom_db._card_data = {card.id: card for card in card_data}
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

    def write_to_database(self):
        print(self.dbpath)
        db_directory = os.path.dirname(self.dbpath)
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)
        con = sqlite3.connect(self.dbpath)
        cur = con.cursor()

        cur.executescript("DROP TABLE IF EXISTS datas;")
        cur.executescript("DROP TABLE IF EXISTS texts;")
        cur.executescript("DROP TABLE IF EXISTS setcodes;")
        schema = os.path.join(SQL_DIR, "customdb.sql")

        with open(schema, "r") as file:
            sql_script = file.read()
        cur.executescript(sql_script)

        cur.executemany(
            """
        INSERT INTO datas (
            id, ot, alias, setcode, type, atk, def, level, race, attribute, 
            category, genre, script, support, ocgdate, tcgdate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                (
                    card.id,
                    card.ot,
                    card.alias,
                    card._archcode,
                    card._type,
                    card.atk,
                    card._def,
                    card._level,
                    card._race,
                    card._attribute,
                    card._category,
                    card._genre,
                    card.script,
                    card._supportcode,
                    card._ocgdate,
                    card._tcgdate,
                )
                for card in self._card_data.values()
            ],
        )
        cur.executemany(
            """
        INSERT INTO texts (id, name, desc) VALUES (?, ?, ?)
        """,
            [(card.id, card.name, card._text) for card in self._card_data.values()],
        )
        cur.executemany(
            """
        INSERT INTO setcodes (name, officialcode) VALUES (?, ?)
        """,
            [(arch.name, arch.id) for arch in self.arch_data.values()],
        )

        con.commit()
        con.close()
