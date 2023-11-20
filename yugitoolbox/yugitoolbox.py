from __future__ import annotations

import base64
import os
import pickle
import sqlite3
import zlib
from collections import Counter
from dataclasses import dataclass
from itertools import permutations
from typing import Callable

import pandas as pd
import requests

from .masks import *

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"
DB_DIR = "db"
DATE_UNAVAILABLE = 253402214400


@dataclass()
class Archetype:
    name: str
    cards: list[Card]
    support: list[Card]
    related: list[Card]

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return self.name


@dataclass()
class Set:
    name: str
    abbr: str
    tcgdate: int
    ocgdate: int
    contents: list[Card]

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return self.name


@dataclass()
class Deck:
    name: str
    main: list[tuple[Card, int]]
    extra: list[tuple[Card, int]]
    side: list[tuple[Card, int]]

    def __str__(self) -> str:
        reprstr = "Main Deck:\n"
        for card in self.main:
            reprstr += f"{card[0]} x{card[1]}\n"
        reprstr += "\nExtra Deck:\n"
        for card in self.extra:
            reprstr += f"{card[0]} x{card[1]}\n"
        reprstr += "\nSide Deck:\n"
        for card in self.side:
            reprstr += f"{card[0]} x{card[1]}\n"
        return reprstr

    @staticmethod
    def from_omegacode(code: str, name: str = ""):
        def decode_card_tuples(start: int, end: int):
            return [
                (carddb.get_cards_by_value(by="id", value=card_id)[0], count)
                for card_id, count in Counter(
                    int.from_bytes(bytes_arr[i : i + 4], byteorder="little")
                    for i in range(start, end, 4)
                ).items()
            ]

        bytes_arr = zlib.decompress(base64.b64decode(code), -8)
        main_size, side_size = bytes_arr[:2]

        main_extra = decode_card_tuples(2, 2 + 4 * main_size)
        main = [card for card in main_extra if card[0].is_main_deck_monster()]
        extra = [card for card in main_extra if card[0].is_extra_deck_monster()]
        side = decode_card_tuples(2 + 4 * main_size, 2 + 4 * main_size + 4 * side_size)

        return Deck(name, main, extra, side)

    def small_world_triples(self) -> list[tuple[Card, ...]]:
        md_cards = [
            card[0] for card in self.main + self.side if card[0].is_main_deck_monster()
        ]

        valids = [
            triple
            for triple in permutations(md_cards, 3)
            if Card.compare_small_world(*triple)
        ]

        return valids


@dataclass()
class Card:
    name: str
    id: int
    type: list[str]
    race: str
    attribute: str
    category: list[str]
    level: int
    lscale: int
    rscale: int
    atk: int
    def_: int
    linkmarkers: list[str]
    text: str
    archetypes: list[Archetype]
    support: list[Archetype]
    related: list[Archetype]
    sets: list[Set]
    tcgdate: int
    ocgdate: int
    ot: int
    archcode: int
    supportcode: int

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def has_atk_equ_def(self) -> bool:
        return "Monster" in self.type and self.atk == self.def_

    def is_trap_monster(self) -> bool:
        return "Trap" in self.type and self.level != 0

    def is_dark_synchro(self) -> bool:
        return "DarkCard" in self.category and "Synchro" in self.type

    def is_rush_maximum(self) -> bool:
        return "RushMax" in self.category

    def is_rush_legendary(self) -> bool:
        return "RushLegendary" in self.category

    def is_rush(self) -> bool:
        return (
            "RushCard" in self.category
            or self.is_rush_legendary()
            or self.is_rush_maximum()
        )

    def is_ocg_only(self) -> bool:
        return self.ot == 1

    def is_tcg_only(self) -> bool:
        return self.ot == 2

    def is_legal(self) -> bool:
        return self.ot == 3

    def is_illegal(self) -> bool:
        return self.ot == 4

    def is_beta(self) -> bool:
        return "BetaCard" in self.category

    def is_skill_card(self) -> bool:
        return "SkillCard" in self.category

    def is_god_card(self) -> bool:
        return any([x in self.category for x in ["RedGod", "BlueGod", "YellowGod"]])

    def is_pre_errata(self) -> bool:
        return "PreErrata" in self.category

    def is_extra_deck_monster(self) -> bool:
        return any(
            [x in self.type for x in ["Synchro", "Token", "Xyz", "Link", "Fusion"]]
        )

    def is_main_deck_monster(self) -> bool:
        return "Monster" in self.type and not self.is_extra_deck_monster()

    @staticmethod
    def compare_small_world(handcard: "Card", deckcard: "Card", addcard: "Card"):
        return all(
            [
                sum(
                    [
                        card1.attribute == card2.attribute,
                        card1.race == card2.race,
                        card1.atk == card2.atk,
                        card1.def_ == card2.def_,
                        card1.level == card2.level,
                    ]
                )
                == 1
                for card1, card2 in zip([handcard, deckcard], [deckcard, addcard])
            ]
        )


class CardDB:
    _instance = None
    archetype_data: list[Archetype] = []
    card_data: dict[int, "Card"] = {}
    set_data: list[Set] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CardDB, cls).__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return

        self._initialised = True
        CardDB._update()
        CardDB._load_pickles()
        print("initialised db.")

    @staticmethod
    def _build_card_db(con):
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
                card["tcgdate"],
                card["ocgdate"],
                card["ot"],
                card["setcode"],
                card["support"],
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

        def split_chunks(n: int, nchunks: int):
            return [(n >> (16 * i)) & 0xFFFF for i in range(nchunks)]

        for card in CardDB.card_data.values():
            card.archetypes = [
                Archetype(archetype["name"], [], [], [])
                for chunk in split_chunks(card.archcode, 4)
                for archetype in archetypes
                if archetype["archetype_code"] == chunk
            ]
            card.support = [
                Archetype(archetype["name"], [], [], [])
                for chunk in split_chunks(card.supportcode, 2)
                for archetype in archetypes
                if archetype["archetype_code"] == chunk
            ]
            card.related = [
                Archetype(archetype["name"], [], [], [])
                for chunk in split_chunks(card.supportcode >> 32, 2)
                for archetype in archetypes
                if archetype["archetype_code"] == chunk
            ]

            for archetype in card.archetypes + card.support + card.related:
                archetype.cards.append(card)

            CardDB.archetype_data.extend(card.archetypes + card.support + card.related)

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

        for card in CardDB.card_data.values():
            card.sets = [
                Set(set["name"], set["abbr"], set["tcgdate"], set["ocgdate"], [])
                for set in sets
                if str(card.id) in set["cardids"].split(",")
            ]

            for card_set in card.sets:
                card_set.contents.append(card)

            CardDB.set_data.extend(card.sets)

    @staticmethod
    def _load_pickles():
        with open("pickles/cards.pkl", "rb") as file:
            CardDB.card_data = pickle.load(file)
        with open("pickles/archetypes.pkl", "rb") as file:
            CardDB.archetype_data = pickle.load(file)
        with open("pickles/sets.pkl", "rb") as file:
            CardDB.set_data = pickle.load(file)

    @staticmethod
    def _build_pickles():
        print("pickling pickles...")
        if not os.path.exists("pickles"):
            os.mkdir("pickles")
        with open("pickles/cards.pkl", "wb") as file:
            pickle.dump(CardDB.card_data, file)
        with open("pickles/archetypes.pkl", "wb") as file:
            pickle.dump(CardDB.archetype_data, file)
        with open("pickles/sets.pkl", "wb") as file:
            pickle.dump(CardDB.set_data, file)

    @staticmethod
    def _build_objects():
        print("building objects...")
        with sqlite3.connect("db/cards.db") as con:
            print("building card db...")
            CardDB._build_card_db(con)
            print("building archetype db...")
            CardDB._build_archetype_db(con)
            print("building set db...")
            CardDB._build_set_db(con)
        CardDB._build_pickles()

    @staticmethod
    def _update():
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

        if os.path.exists("db/cards.db"):
            if os.path.exists("db/cards.hash"):
                with open("db/cards.hash") as f:
                    old_hash = f.read()
            else:
                old_hash = None
            download(hash_url, hash_path)
            with open("db/cards.hash") as f:
                new_hash = f.read()
            if old_hash == new_hash:
                return
            else:
                print("downloading up-to-date db...")
                download(db_url, db_path)
                CardDB._build_objects()
        else:
            print("downloading up-to-date db...")
            download(db_url, db_path)
            download(hash_url, hash_path)
            CardDB._build_objects()

    def get_card_by_id(self, id: int):
        return self.card_data[id]

    def get_cards_by_id(self, ids: list[int]):
        return [self.get_card_by_id(id) for id in ids]

    def get_cards_by_value(self, by: str, value: str | int):
        if by not in Card.__dataclass_fields__.keys():
            raise RuntimeError(
                f"'by' not in {', '.join(Card.__dataclass_fields__.keys())}"
            )
        return [
            card
            for card in self.card_data.values()
            if isinstance(getattr(card, by), (list, str))
            and value in getattr(card, by)
            or getattr(card, by) == value
        ]

    def get_cards_by_values(self, by: str, values: list[int | str]):
        return [self.get_cards_by_value(by, value) for value in values]

    def get_cards_by_query(self, query: Callable[[Card], bool]):
        return [card for card in self.card_data.values() if query(card)]

    def related_cards(self, given_archetypes: list[str], given_cards: list[str] = []):
        return [
            card
            for card in self.card_data.values()
            if any(card_name in card.text for card_name in given_cards)
            or any(
                archetype
                in [
                    archetype.name
                    for archetype in set(card.related)
                    | set(card.support)
                    | set(card.archetypes)
                ]
                for archetype in given_archetypes
            )
        ]


carddb = CardDB()
