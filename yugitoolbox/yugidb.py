from __future__ import annotations

import os
import pickle
import sqlite3
from abc import abstractmethod
from collections import Counter
from typing import Callable, ItemsView, Optional, ValuesView

from .archetype import Archetype
from .card import Card
from .enums import OT, Type
from .set import Set


class YugiDB:
    _card_data: dict[int, Card]
    _arch_data: dict[int, Archetype]
    _set_data: dict[int, Set]
    name: str
    dbpath: str

    def __init__(self, rebuild_pkl=False):
        if type(self) == YugiDB:
            return

        self.dbdir = os.path.dirname(self.dbpath)
        self.cardpkl = os.path.join(self.dbdir, "cards.pkl")
        self.setspkl = os.path.join(self.dbdir, "sets.pkl")
        self.archpkl = os.path.join(self.dbdir, "archetypes.pkl")

        if not os.path.exists(self.dbdir):
            os.makedirs(self.dbdir)

        if rebuild_pkl or not all(
            os.path.exists(file)
            for file in [
                self.cardpkl,
                self.setspkl,
                self.archpkl,
            ]
        ):
            self._build_objects()
        else:
            self._load_objects()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _build_objects(self):
        with sqlite3.connect(self.dbpath) as con:
            print(f"Building card db for {self.name}...")
            self._build_card_db(con)
            print(f"Building archetype db for {self.name}...")
            self._build_archetype_db(con)
            print(f"Building set db for {self.name}...")
            self._build_set_db(con)
        self.save_pickles()

    def _load_objects(self):
        with open(self.cardpkl, "rb") as file:
            self._card_data = pickle.load(file)
        with open(self.archpkl, "rb") as file:
            self._arch_data = pickle.load(file)
        with open(self.setspkl, "rb") as file:
            self._set_data = pickle.load(file)

    def save_pickles(self):
        print(f"Pickling pickles for {self.name}...")
        with open(self.cardpkl, "wb") as file:
            pickle.dump(self._card_data, file)
        with open(self.archpkl, "wb") as file:
            pickle.dump(self._arch_data, file)
        with open(self.setspkl, "wb") as file:
            pickle.dump(self._set_data, file)

    @property
    def cards(self) -> ValuesView[Card]:
        return self._card_data.values()

    @property
    def archetypes(self) -> ValuesView[Archetype]:
        return self._arch_data.values()

    @property
    def sets(self) -> ValuesView[Set]:
        return self._set_data.values()

    def get_card_by_id(self, id: int) -> Card:
        return self._card_data[id]

    def get_cards_by_ids(self, ids: list[int]) -> list[Card]:
        return [self.get_card_by_id(id) for id in ids if id in self._card_data]

    def get_cards_by_value(self, by: str, value: str | int) -> list[Card]:
        return [
            c
            for c in self.cards
            if isinstance(getattr(c, by), int)
            and getattr(c, by) == value
            or value in getattr(c, by)
        ]

    def get_cards_by_values(
        self, by: str, values: list[int] | list[str]
    ) -> list[list[Card]]:
        return [self.get_cards_by_value(by, value) for value in values]

    def get_cards_by_query(self, query: Callable[[Card], bool]):
        return [card for card in self.cards if query(card)]

    def get_cards_fuzzy(self, fuzzy_string: str) -> list[tuple[Card, float]]:
        from jaro import jaro_winkler_metric

        return sorted(
            [
                (card, jaro_winkler_metric(card.name, fuzzy_string))
                for card in self.cards
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:20]

    def get_set_by_id(self, id: int) -> Set:
        return self._set_data[id]

    def get_sets_by_ids(self, ids: list[int]) -> list[Set]:
        return [self.get_set_by_id(id) for id in ids if id in self._set_data]

    def get_sets_by_value(self, by: str, value: str | int) -> list[Set]:
        return [
            s
            for s in self.sets
            if isinstance(getattr(s, by), int)
            and getattr(s, by) == value
            or value in getattr(s, by)
        ]

    def get_sets_by_values(
        self, by: str, values: list[int] | list[str]
    ) -> list[list[Set]]:
        return [self.get_sets_by_value(by, value) for value in values]

    def get_archetype_by_id(self, id: int) -> Archetype:
        return self._arch_data[id]

    def get_archetypes_by_ids(self, ids: list[int]) -> list[Archetype]:
        return [self.get_archetype_by_id(id) for id in ids if id in self._arch_data]

    def get_archetypes_by_value(self, by: str, value: str | int) -> list[Archetype]:
        return [
            a
            for a in self.archetypes
            if isinstance(getattr(a, by), int)
            and getattr(a, by) == value
            or value in getattr(a, by)
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
            for card in self.cards
            if any(card_name in card._text for card_name in given_cards)
            or any(
                arch_name
                in [
                    arch.name
                    for arch in self.get_archetypes_by_ids(card.combined_archetypes)
                ]
                for arch_name in given_archetypes
            )
        ]

    def get_unscripted(self, include_skillcards: bool = False) -> list[Card]:
        return [
            card
            for card in self.cards
            if not card.id == 111004001
            and (card._script != 1.0 or card._script == None)
            and any(
                card.has_type(type)
                for type in [
                    Type.Spell,
                    Type.Trap,
                    Type.Effect,
                ]
            )
            and not card.alias
            and (not card.ot == OT.Illegal or (include_skillcards and card.is_skill))
        ]

    def get_card_archetypes(self, card: Card) -> list[Archetype]:
        return [self.get_archetype_by_id(id) for id in card.archetypes]

    def get_card_support(self, card: Card) -> list[Archetype]:
        return [self.get_archetype_by_id(id) for id in card.support]

    def get_card_related(self, card: Card) -> list[Archetype]:
        return [self.get_archetype_by_id(id) for id in card.related]

    def get_card_sets(self, card: Card) -> list[Set]:
        return [self.get_set_by_id(id) for id in card.sets]

    def get_archetype_cards(self, arch: Archetype) -> list[Card]:
        return [self.get_card_by_id(id) for id in arch.members]

    def get_archetype_support(self, arch: Archetype) -> list[Card]:
        return [self.get_card_by_id(id) for id in arch.support]

    def get_archetype_related(self, arch: Archetype) -> list[Card]:
        return [self.get_card_by_id(id) for id in arch.related]

    def get_set_cards(self, set: Set) -> list[Card]:
        return [self.get_card_by_id(id) for id in set.contents]

    def get_set_archetype_counts(self, s: Set) -> ItemsView[Archetype, int]:
        return Counter(
            self.get_archetype_by_id(archid)
            for card in self.get_cards_by_ids(s.contents)
            for archid in set(card.archetypes + card.support)
            if card is not None
        ).items()

    def get_set_archetype_ratios(self, s: Set) -> list[tuple[Archetype, float]]:
        return [
            (archid, count / s.set_total * 100)
            for archid, count in self.get_set_archetype_counts(s)
        ]

    def clean_dir(self):
        for file_name in os.listdir(self.dbdir):
            file_path = os.path.join(self.dbdir, file_name)
            file_path = file_path.replace("\\", "/")
            if file_path != self.dbpath:
                os.remove(file_path)

    @staticmethod
    def merge(db1: YugiDB, db2: YugiDB, new_name: str, db_path: str):
        new = YugiDB()
        new.name = new_name
        new.dbpath = db_path
        new._card_data = db1._card_data | db2._card_data
        new._arch_data = db1._arch_data | db2._arch_data
        new._set_data = db1._set_data | db2._set_data
        return new

    @abstractmethod
    def _build_card_db(self, con):
        pass

    @abstractmethod
    def _build_archetype_db(self, con):
        pass

    @abstractmethod
    def _build_set_db(self, con):
        pass
