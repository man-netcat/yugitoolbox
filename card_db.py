import datetime
import sqlite3
import os
import requests
import pandas as pd
from dataclasses import dataclass
from masks import *

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"
DB_DIR = "db"


@dataclass
class Card:
    name: str
    id: int
    type: list[str]
    race: list[str]
    attribute: list[str]
    category: list[str]
    level: int
    scale: int
    atk: int
    def_: int
    linkmarkers: list[str]
    text: str
    archetypes: list[str]
    support: list[str]
    related: list[str]

    def __str__(self) -> str:
        return str(self.__dataclass_fields__)


class CardDB:
    def __init__(self):
        CardDB._update()
        with sqlite3.connect("db/cards.db") as con:
            CardDB.set_data = pd.read_sql_query("SELECT * FROM packs", con)
            CardDB.card_packs = pd.read_sql_query("SELECT * FROM relations", con)
            print("Populating archetypes...")
            CardDB._populate_archetypes(con)
            print("Populating cards...")
            CardDB._populate_cards(con)
            print("Database ready")

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
            card_race = apply_mask(card["race"], race_mask)
            card_attribute = apply_mask(card["attribute"], attribute_mask)
            card_category = apply_mask(card["category"], category_mask)
            if card["type"] & type_mask["Pendulum"]:
                card_lscale, _, card_level = parse_pendulum(card["level"])
            else:
                card_lscale, _, card_level = 0, 0, card["level"]
            if card["type"] & type_mask["Link"]:
                card_def = 0
                card_markers = apply_mask(card["def"], linkmarker_mask)
            else:
                card_def = card["def"]
                card_markers = []

            card_archetypes, card_support, card_related = CardDB._get_archetypes(card)
            card_data = Card(
                card["name"],
                card["id"],
                card_type,
                card_race,
                card_attribute,
                card_category,
                card_level,
                card_lscale,
                card["atk"],
                card_def,
                card_markers,
                card["desc"],
                card_archetypes,
                card_support,
                card_related,
            )
            CardDB.card_data.append(card_data)

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
            for k, v in CardDB.archetypes.items()
            for chunk in split_chunks(card_support >> 32, 2)
            if v == chunk
        ]
        return archetypes, support, related_to

    def get_cards(self, by: str, value):
        """
        Filter the list of cards based on a specified attribute value.

        Parameters:
        - by: Attribute to search by
        - value: Value to search for

        Returns:
        - List of cards that match the specified attribute value
        """
        return [
            obj
            for obj in self.card_data
            if isinstance(getattr(obj, by), list)
            and value in getattr(obj, by)
            or getattr(obj, by) == value
        ]

    def related_cards(self, given_archetypes: list[str], given_cards: list[str] = []):
        return [
            card
            for card in self.card_data
            if any(
                [
                    archetype
                    in set(card.related) | set(card.support) | set(card.archetypes)
                    for archetype in given_archetypes
                ]
            )
            or any(card_name in card.text for card_name in given_cards)
        ]

    @staticmethod
    def _update():
        def dl(url, path):
            print(f"Downloading {url}...")
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
