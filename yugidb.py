from __future__ import annotations

import os
import pickle
import sqlite3
from abc import abstractmethod
from collections import Counter
from typing import Callable, ItemsView, ValuesView

from .archetype import Archetype
from .card import Card
from .enums import OT, Type
from .set import Set


class YugiDB:
    card_data: dict[int, Card]
    arch_data: dict[int, Archetype]
    set_data: dict[int, Set]
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
            self.card_data = pickle.load(file)
        with open(self.archpkl, "rb") as file:
            self.arch_data = pickle.load(file)
        with open(self.setspkl, "rb") as file:
            self.set_data = pickle.load(file)

    def save_pickles(self):
        print(f"Pickling pickles for {self.name}...")
        with open(self.cardpkl, "wb") as file:
            pickle.dump(self.card_data, file)
        with open(self.archpkl, "wb") as file:
            pickle.dump(self.arch_data, file)
        with open(self.setspkl, "wb") as file:
            pickle.dump(self.set_data, file)

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
            for card in self.get_cards()
            if not card.id == 111004001
            and (card.script != 1.0 or card.script == None)
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

    def get_set_archetype_counts(self, set_: Set) -> ItemsView[Archetype, int]:
        return Counter(
            self.get_archetype_by_id(archid)
            for card in self.get_cards_by_ids(set_.contents)
            for archid in set(card.archetypes + card.support)
        ).items()

    def get_set_archetype_ratios(self, set_: Set) -> list[tuple[Archetype, float]]:
        return [
            (archid, count / set_.set_total() * 100)
            for archid, count in self.get_set_archetype_counts(set_)
        ]

    def clean(self):
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
        new.card_data = db1.card_data | db2.card_data
        new.arch_data = db1.arch_data | db2.arch_data
        new.set_data = db1.set_data | db2.set_data
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
