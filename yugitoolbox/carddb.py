from __future__ import annotations

import math
import os
import pickle
import sqlite3
from datetime import datetime
from typing import Callable

import pandas as pd
import requests

from .archetype import Archetype
from .card import Card
from .masks import *
from .set import Set

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"
DB_DIR = "db"
DATE_UNAVAILABLE = 253402214400


class CardDB:
    _instance = None
    archetype_data: dict[str, Archetype] = {}
    card_data: dict[int, Card] = {}
    set_data: dict[str, Set] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CardDB, cls).__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return

        self._initialised = True
        CardDB._update_db()
        CardDB._load_objects()

    @staticmethod
    def _build_card_db(con):
        def make_datetime(timestamp: int):
            try:
                dt = datetime.fromtimestamp(timestamp)
            except:
                dt = None
            return dt

        cards: list[dict] = pd.read_sql_query(
            "SELECT * FROM datas INNER JOIN texts USING(id)",
            con,
        ).to_dict(orient="records")
        CardDB.card_data: dict[int, Card] = {}

        for card in cards:
            card_type = apply_mask(card["type"], type_mask)
            card_race = race_mask.get(card["race"], "")
            card_attribute = attribute_mask.get(card["attribute"], "")
            card_category = apply_mask(card["category"], category_mask)

            if card["type"] & 0x1000000:
                card_lscale, card_rscale, card_level = parse_pendulum(card["level"])
            else:
                card_lscale, card_rscale, card_level = 0, 0, card["level"]

            if card["type"] & 0x4000000:
                card_def = 0
                card_markers = apply_mask(card["def"], linkmarker_mask)
            else:
                card_def = card["def"]
                card_markers = []

            card_data = Card(
                card["name"],
                card["id"],
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
            )
            CardDB.card_data[card["id"]] = card_data

    @staticmethod
    def _build_archetype_db(con):
        archetypes = pd.read_sql_query(
            """
            SELECT name,
                CASE
                    WHEN officialcode > 0 THEN officialcode
                    ELSE betacode
                END AS archetype_code
            FROM setcodes
            WHERE (officialcode > 0 AND betacode = officialcode) OR (officialcode = 0 AND betacode > 0);
            """,
            con,
        ).to_dict(orient="records")

        CardDB.archetype_data = {
            arch["name"]: Archetype(arch["name"], [], [], []) for arch in archetypes
        }

        def split_chunks(n: int, nchunks: int):
            return [(n >> (16 * i)) & 0xFFFF for i in range(nchunks)]

        for card in CardDB.card_data.values():
            card.archetypes = [
                arch["name"]
                for chunk in split_chunks(card.archcode, 4)
                for arch in archetypes
                if arch["archetype_code"] == chunk
            ]
            card.support = [
                arch["name"]
                for chunk in split_chunks(card.supportcode, 2)
                for arch in archetypes
                if arch["archetype_code"] == chunk
            ]
            card.related = [
                arch["name"]
                for chunk in split_chunks(card.supportcode >> 32, 2)
                for arch in archetypes
                if arch["archetype_code"] == chunk
            ]

            for arch in card.archetypes:
                CardDB.archetype_data[arch].cards.append(card)
            for arch in card.support:
                CardDB.archetype_data[arch].support.append(card)
            for arch in card.related:
                CardDB.archetype_data[arch].related.append(card)

    @staticmethod
    def _build_set_db(con):
        sets = pd.read_sql_query(
            """
                SELECT
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

        CardDB.set_data = {
            set["name"]: Set(
                set["name"], set["abbr"], set["tcgdate"], set["ocgdate"], []
            )
            for set in sets
        }

        for card in CardDB.card_data.values():
            card.sets = [
                set["name"] for set in sets if str(card.id) in set["cardids"].split(",")
            ]

            for set in card.sets:
                CardDB.set_data[set].contents.append(card)

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
            CardDB._build_objects()
        with open("db/cards.pkl", "rb") as file:
            CardDB.card_data = pickle.load(file)
        with open("db/archetypes.pkl", "rb") as file:
            CardDB.archetype_data = pickle.load(file)
        with open("db/sets.pkl", "rb") as file:
            CardDB.set_data = pickle.load(file)

    @staticmethod
    def _build_pickles():
        print("pickling pickles...")
        if not os.path.exists("db"):
            os.mkdir("db")
        with open("db/cards.pkl", "wb") as file:
            pickle.dump(CardDB.card_data, file)
        with open("db/archetypes.pkl", "wb") as file:
            pickle.dump(CardDB.archetype_data, file)
        with open("db/sets.pkl", "wb") as file:
            pickle.dump(CardDB.set_data, file)

    @staticmethod
    def _build_objects():
        with sqlite3.connect("db/cards.db") as con:
            print("building card db...")
            CardDB._build_card_db(con)
            print("building archetype db...")
            CardDB._build_archetype_db(con)
            print("building set db...")
            CardDB._build_set_db(con)
        CardDB._build_pickles()

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
        CardDB._build_objects()

    def get_cards(self):
        return self.card_data.values()

    def get_archetypes(self):
        return self.archetype_data.values()

    def get_sets(self):
        return self.set_data.values()

    def get_card_by_id(self, id: int):
        return self.card_data[id]

    def get_cards_by_id(self, ids: list[int]):
        return [self.get_card_by_id(id) for id in ids]

    def get_cards_by_value(self, by: str, value: str | int):
        if by not in Card.__dataclass_fields__.keys():
            raise RuntimeError(
                f"'by' not in [{', '.join(Card.__dataclass_fields__.keys())}]"
            )
        return [
            card
            for card in self.card_data.values()
            if isinstance(getattr(card, by), (list, str))
            and value in getattr(card, by)
            or getattr(card, by) == value
        ]

    def get_cards_by_values(self, by: str, values: list[int] | list[str]):
        return [self.get_cards_by_value(by, value) for value in values]

    def get_cards_by_query(self, query: Callable[[Card], bool]):
        return [card for card in self.card_data.values() if query(card)]

    def get_set_by_name(self, name: str):
        return CardDB.set_data[name]

    def get_archetype_by_name(self, name: str):
        return CardDB.archetype_data[name]

    def get_related_cards(
        self, given_archetypes: list[str], given_cards: list[str] = []
    ) -> list[Card]:
        return [
            card
            for card in self.card_data.values()
            if any(card_name in card.text for card_name in given_cards)
            or any(
                arch in set(card.related + card.support + card.archetypes)
                for arch in given_archetypes
            )
        ]

    def get_unscripted(self, include_skillcards: bool = False) -> list[Card]:
        return [
            card
            for card in card_db.card_data.values()
            if not card.id == 111004001
            if not card.scripted
            and any([type in card.type for type in ["Spell", "Trap", "Effect"]])
            and not card.alias
            and (not card.is_illegal() or (include_skillcards and card.is_skill_card()))
        ]


card_db = CardDB()
