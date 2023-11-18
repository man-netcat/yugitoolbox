import os
import sqlite3
from typing import Callable

import pandas as pd
import requests

from resources.masks import *

from .Card import Card

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"
DB_DIR = "db"


class CardDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CardDB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        CardDB._update()
        with sqlite3.connect("db/cards.db") as con:
            CardDB.set_data = pd.read_sql_query("SELECT * FROM packs", con)
            CardDB.card_packs = pd.read_sql_query("SELECT * FROM relations", con)
            CardDB._populate_archetypes(con)
            CardDB._populate_cards(con)

    @staticmethod
    def _populate_archetypes(con):
        df = pd.read_sql_query(
            "SELECT * FROM setcodes WHERE (officialcode>0 AND betacode=officialcode) OR (officialcode=0 AND betacode>0)",
            con,
        )
        CardDB.archetypes = dict(
            zip(
                df["name"],
                df.apply(
                    lambda row: row["officialcode"]
                    if row["officialcode"] != 0
                    else row["betacode"],
                    axis=1,
                ),
            )
        )

    @staticmethod
    def _populate_cards(con):
        df = pd.read_sql_query(
            "SELECT * FROM datas INNER JOIN texts USING(id)",
            con,
        )
        cards: list[dict] = df.to_dict(orient="records")
        CardDB.card_data: list[Card] = []
        for card in cards:
            card_type = apply_mask(card["type"], type_mask)
            card_race = race_mask.get(card["race"], "")
            card_attribute = attribute_mask.get(card["attribute"], "")
            card_category = apply_mask(card["category"], category_mask)
            if card["type"] & 0x1000000:
                card_scale, _, card_level = parse_pendulum(card["level"])
            else:
                card_scale, card_level = 0, card["level"]
            if card["type"] & 0x4000000:
                card_def = 0
                card_markers = apply_mask(card["def"], linkmarker_mask)
            else:
                card_def = card["def"]
                card_markers = []

            card_archetypes, card_support, card_related = CardDB._get_archetypes(card)
            card = Card(
                card["name"],
                card["id"],
                card_type,
                card_race,
                card_attribute,
                card_category,
                card_level,
                card_scale,
                card["atk"],
                card_def,
                card_markers,
                card["desc"],
                card_archetypes,
                card_support,
                card_related,
                card["ot"],
            )
            CardDB.card_data.append(card)

    @staticmethod
    def _get_archetypes(card):
        def split_chunks(n: int, nchunks: int):
            return [(n >> (16 * i)) & 0xFFFF for i in range(nchunks)]

        card_setcode = card["setcode"]
        card_support = card["support"]
        archetypes = [
            k
            for chunk in split_chunks(card_setcode, 4)
            for k, v in CardDB.archetypes.items()
            if v == chunk
        ]
        support = [
            k
            for chunk in split_chunks(card_support, 2)
            for k, v in CardDB.archetypes.items()
            if v == chunk
        ]
        related_to = [
            k
            for chunk in split_chunks(card_support >> 32, 2)
            for k, v in CardDB.archetypes.items()
            if v == chunk
        ]
        return archetypes, support, related_to

    @staticmethod
    def _update():
        def dl(url, path):
            r = requests.get(url, allow_redirects=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)

        db_url = os.path.join(OMEGA_BASE_URL, "OmegaDB.cdb")
        db_path = os.path.join(DB_DIR, "cards.db")
        hash_url = os.path.join(OMEGA_BASE_URL, "Database.hash")
        hash_path = os.path.join(DB_DIR, "cards.hash")

        if os.path.exists("db/cards.db"):
            if os.path.exists("db/cards.hash"):
                with open("db/cards.hash") as f:
                    old_hash = f.read()
            else:
                old_hash = None
            dl(hash_url, hash_path)
            with open("db/cards.hash") as f:
                new_hash = f.read()
            if old_hash == new_hash:
                return
            else:
                dl(db_url, db_path)
        else:
            dl(db_url, db_path)
            dl(hash_url, hash_path)

    def get_cards_by_id(self, ids: list[int]):
        return [card for card in self.card_data if card.id in ids]

    def get_cards_by_field(self, by: str, value):
        if by not in Card.__dataclass_fields__.keys():
            raise RuntimeError(
                f"by not in {', '.join(Card.__dataclass_fields__.keys())}"
            )
        return [
            card
            for card in self.card_data
            if isinstance(getattr(card, by), (list, str))
            and value in getattr(card, by)
            or getattr(card, by) == value
        ]

    def get_cards_by_query(self, query: Callable[[Card], bool]):
        return [card for card in self.card_data if query(card)]

    def related_cards(self, given_archetypes: list[str], given_cards: list[str] = []):
        return [
            card
            for card in self.card_data
            if any(card_name in card.text for card_name in given_cards)
            or any(
                archetype
                in set(card.related) | set(card.support) | set(card.archetypes)
                for archetype in given_archetypes
            )
        ]


carddb = CardDB()
