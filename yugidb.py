from __future__ import annotations

import math
import os
import pickle
import sqlite3
from datetime import datetime
from typing import Callable, ValuesView

import pandas as pd
import requests

from .archetype import Archetype
from .card import Card
from .enums import *
from .set import Set

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"
DB_DIR = "db"


class YugiDB:
    _instance = None
    arch_data: dict[int, Archetype] = {}
    card_data: dict[int, Card] = {}
    set_data: dict[int, Set] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(YugiDB, cls).__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return

        self._initialised = True
        YugiDB._update_db()
        YugiDB._load_objects()

    @staticmethod
    def _build_card_db(con):
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
        YugiDB.card_data: dict[int, Card] = {}

        for card in cards:
            card_type = apply_enum(card["type"], Type)
            card_race = Race(card["race"])
            card_attribute = Attribute(card["attribute"])
            card_category = apply_enum(card["category"], Category)

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
                int(card["koid"]) if not math.isnan(card["koid"]) else 0,
            )
            YugiDB.card_data[card["id"]] = card_data

    @staticmethod
    def _build_archetype_db(con):
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

        YugiDB.arch_data = {
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

        for card in YugiDB.card_data.values():
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
                YugiDB.arch_data[arch].cards.append(card.id)
            for arch in card.support:
                YugiDB.arch_data[arch].support.append(card.id)
            for arch in card.related:
                YugiDB.arch_data[arch].related.append(card.id)

    @staticmethod
    def _build_set_db(con):
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

        YugiDB.set_data = {
            set["id"]: Set(
                set["id"],
                set["name"],
                set["abbr"],
                set["tcgdate"],
                set["ocgdate"],
                [
                    int(id)
                    for id in set["cardids"].split(",")
                    if int(id) in YugiDB.card_data
                ],
            )
            for set in sets
        }

        for set in YugiDB.set_data.values():
            for cardid in set.contents:
                YugiDB.card_data[cardid].sets.append(set.id)

    @staticmethod
    def _load_objects():
        if not all(
            [
                os.path.exists(file)
                for file in [
                    "db/cards.pkl",
                    "db/sets.pkl",
                    "db/archetypes.pkl",
                ]
            ]
        ):
            YugiDB._build_objects()
        with open("db/cards.pkl", "rb") as file:
            YugiDB.card_data = pickle.load(file)
        with open("db/archetypes.pkl", "rb") as file:
            YugiDB.arch_data = pickle.load(file)
        with open("db/sets.pkl", "rb") as file:
            YugiDB.set_data = pickle.load(file)

    @staticmethod
    def _build_pickles():
        print("Pickling pickles...")
        if not os.path.exists("db"):
            os.mkdir("db")
        with open("db/cards.pkl", "wb") as file:
            pickle.dump(YugiDB.card_data, file)
        with open("db/archetypes.pkl", "wb") as file:
            pickle.dump(YugiDB.arch_data, file)
        with open("db/sets.pkl", "wb") as file:
            pickle.dump(YugiDB.set_data, file)

    @staticmethod
    def _build_objects():
        with sqlite3.connect("db/cards.db") as con:
            print("Building card db...")
            YugiDB._build_card_db(con)
            print("Building archetype db...")
            YugiDB._build_archetype_db(con)
            print("Building set db...")
            YugiDB._build_set_db(con)
        YugiDB._build_pickles()

    @staticmethod
    def _update_db(force_update: bool = False):
        def download(url: str, path: str):
            r = requests.get(url, allow_redirects=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)

        db_url = os.path.join(OMEGA_BASE_URL, "OmegaDB.cdb")
        db_path = os.path.join(DB_DIR, "cards.db")
        hash_url = os.path.join(OMEGA_BASE_URL, "Database.hash")
        hash_path = os.path.join(DB_DIR, "cards.hash")

        if not os.path.exists("db"):
            os.mkdir("db")

        if os.path.exists("db/cards.db") and not force_update:
            if os.path.exists("db/cards.hash"):
                with open("db/cards.hash") as f:
                    old_hash = f.read()
            else:
                old_hash = None

            try:
                download(hash_url, hash_path)
            except requests.ConnectionError:
                print("Failed to get current Hash, skipping update.")
                return

            with open("db/cards.hash") as f:
                new_hash = f.read()

            if old_hash == new_hash:
                return
            else:
                print("A new version of the database is available.")
                user_response = input(
                    "Do you want to update the database? (y/n): "
                ).lower()
                if user_response != "y":
                    print("Skipping database update.")
                    return

        print("Downloading up-to-date db...")
        download(db_url, db_path)
        download(hash_url, hash_path)
        YugiDB._build_objects()

    def get_cards(self) -> ValuesView[Card]:
        return self.card_data.values()

    def get_archetypes(self) -> ValuesView[Archetype]:
        return self.arch_data.values()

    def get_sets(self) -> ValuesView[Set]:
        return self.set_data.values()

    def get_card_by_id(self, id: int) -> Card:
        return self.card_data[id]

    def get_cards_by_ids(self, ids: list[int]) -> list[Card]:
        return [self.get_card_by_id(id) for id in ids]

    def get_cards_by_value(self, by: str, value: str | int) -> list[Card]:
        if by not in Card.__dataclass_fields__.keys():
            raise RuntimeError(
                f"'by' not in [{', '.join(Card.__dataclass_fields__.keys())}]"
            )
        return [
            card
            for card in self.get_cards()
            if isinstance(getattr(card, by), (list, str))
            and value in getattr(card, by)
            or getattr(card, by) == value
        ]

    def get_cards_by_values(
        self, by: str, values: list[int] | list[str]
    ) -> list[list[Card]]:
        return [self.get_cards_by_value(by, value) for value in values]

    def get_cards_by_query(self, query: Callable[[Card], bool]):
        return [card for card in self.get_cards() if query(card)]

    def get_cards_fuzzy(self, fuzzy_string: str) -> list[tuple[Card, float]]:
        from jaro import jaro_winkler_metric

        return sorted(
            [
                (card, jaro_winkler_metric(card.name, fuzzy_string))
                for card in self.get_cards()
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:20]

    def get_set_by_id(self, id: int) -> Set:
        return self.set_data[id]

    def get_sets_by_ids(self, ids: list[int]) -> list[Set]:
        return [self.get_set_by_id(id) for id in ids]

    def get_sets_by_value(self, by: str, value: str | int) -> list[Set]:
        if by not in Set.__dataclass_fields__.keys():
            raise RuntimeError(
                f"'by' not in [{', '.join(Set.__dataclass_fields__.keys())}]"
            )
        return [
            set
            for set in self.get_sets()
            if isinstance(getattr(set, by), (list, str))
            and value in getattr(set, by)
            or getattr(set, by) == value
        ]

    def get_sets_by_values(
        self, by: str, values: list[int] | list[str]
    ) -> list[list[Set]]:
        return [self.get_sets_by_value(by, value) for value in values]

    def get_archetype_by_id(self, id: int) -> Archetype:
        return self.arch_data[id]

    def get_archetypes_by_ids(self, ids: list[int]) -> list[Archetype]:
        return [self.get_archetype_by_id(id) for id in ids]

    def get_archetypes_by_value(self, by: str, value: str | int) -> list[Archetype]:
        if by not in Archetype.__dataclass_fields__.keys():
            raise RuntimeError(
                f"'by' not in [{', '.join(Archetype.__dataclass_fields__.keys())}]"
            )
        return [
            arch
            for arch in self.get_archetypes()
            if isinstance(getattr(arch, by), (list, str))
            and value in getattr(arch, by)
            or getattr(arch, by) == value
        ]

    def get_archetypes_by_values(
        self, by: str, values: list[int] | list[str]
    ) -> list[list[Archetype]]:
        return [self.get_archetypes_by_value(by, value) for value in values]

    def get_related_cards(
        self, given_archetypes: list[str], given_cards: list[str] = []
    ) -> list[Card]:
        return [
            card
            for card in self.get_cards()
            if any(card_name in card.text for card_name in given_cards)
            or any(
                arch_name
                in [
                    arch.name
                    for arch in yugidb.get_archetypes_by_ids(card.combined_archetypes())
                ]
                for arch_name in given_archetypes
            )
        ]

    def get_unscripted(self, include_skillcards: bool = False) -> list[Card]:
        return [
            card
            for card in self.get_cards()
            if not card.id == 111004001
            if not card.scripted
            and any(
                [
                    type in card.type
                    for type in [
                        Type.Spell,
                        Type.Trap,
                        Type.Effect,
                    ]
                ]
            )
            and not card.alias
            and (
                not card.ot == OT.Illegal
                or (include_skillcards and card.is_skill_card())
            )
        ]


yugidb = YugiDB()
