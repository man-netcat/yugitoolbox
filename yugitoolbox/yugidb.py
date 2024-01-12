from __future__ import annotations
from enum import IntFlag

from typing import Callable

from sqlalchemy import Column, Integer, String, create_engine, func
from sqlalchemy.orm import aliased, class_mapper, sessionmaker

from .archetype import Archetype
from .card import Card
from .set import Set
from .sqlclasses import *


class YugiDB:
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    ################# Card Functions #################

    @property
    def card_query(self):
        return (
            self.session.query(
                Data.id.label("id"),
                Text.name.label("name"),
                Text.text.label("text"),
                Data.type.label("type"),
                Data.race.label("race"),
                Data.attribute.label("attribute"),
                Data.category.label("category"),
                Data.genre.label("genre"),
                Data.level.label("level"),
                Data.atk.label("atk"),
                Data.def_.label("def"),
                Data.tcgdate.label("tcgdate"),
                Data.ocgdate.label("ocgdate"),
                Data.status.label("status"),
                Data.archcode.label("archcode"),
                Data.supportcode.label("supportcode"),
                Data.alias.label("alias"),
                Koid.koid.label("koid"),
                Data.script.label("script"),
            )
            .join(Text, Data.id == Text.id)
            .join(Koid, Data.id == Koid.id)
        )

    @property
    def cards(self) -> list[Card]:
        return self._make_cards_list(self.card_query.all())

    def _make_card(self, result) -> Card:
        return Card(*result)

    def _make_cards_list(self, results) -> list[Card]:
        return [self._make_card(result) for result in results]

    def get_card_by_id(self, id) -> Card:
        query = self.card_query.filter(Data.id == id)
        result = self.session.execute(query.statement).fetchone()
        return self._make_card(result)

    def get_cards_by_ids(self, ids: list[int]) -> list[Card]:
        query = self.card_query.filter(Data.id.in_(ids))
        results = self.session.execute(query.statement).fetchall()
        return self._make_cards_list(results)

    def get_cards_by_values(self, search_values: dict) -> list[Card]:
        return [
            c
            for key, value in search_values.items()
            for c in self.cards
            if hasattr(c, key)
            and (
                isinstance(getattr(c, key), IntFlag)
                and getattr(c, key).name.lower() == str(value).lower()
            )
            or str(getattr(c, key)).lower() == str(value).lower()
        ]

    def get_cards_by_query(self, query: Callable[[Card], bool]) -> list[Card]:
        return [card for card in self.cards if query(card)]

    ################# Archetype Functions #################

    @property
    def arch_query(self):
        return self.session.query(
            SetCode.name,
            func.coalesce(SetCode.officialcode, SetCode.betacode).label("id"),
        )

    def _make_arch_list(self, results) -> list[Archetype]:
        return [self._make_archetype(result) for result in results if result.id != 0]

    def _make_archetype(self, result) -> Archetype:
        return Archetype(id=result.id, name=result.name)

    @property
    def archetypes(self) -> list[Archetype]:
        return self._make_arch_list(self.arch_query.all())

    def get_archetype_by_id(self, id: int) -> Archetype:
        query = self.arch_query.filter(
            func.coalesce(SetCode.officialcode, SetCode.betacode) == id,
        )

        result = self.session.execute(query.statement).fetchone()
        return Archetype(id=result.id, name=result.name)

    def get_archetypes_by_ids(self, ids: list[int]) -> list[Archetype]:
        query = self.arch_query.filter(
            func.coalesce(SetCode.officialcode, SetCode.betacode).in_(ids),
        )

        results = self.session.execute(query.statement).fetchall()
        return self._make_arch_list(results)

    def get_archetype_by_name(self, name: str) -> Archetype:
        return self.get_archetypes_by_names([name])[0]

    def get_archetypes_by_names(self, names: list[str]) -> list[Archetype]:
        query = self.arch_query.filter(SetCode.name.in_(names))
        results = self.session.execute(query.statement).fetchall()
        return self._make_arch_list(results)

    ################# Set Functions #################

    @property
    def set_query(self):
        return (
            self.session.query(
                Pack.id,
                Pack.abbr,
                Pack.name,
                Pack.ocgdate.label("_ocgdate"),
                Pack.tcgdate.label("_tcgdate"),
                func.group_concat(Relation.cardid).label("cardids"),
            )
            .join(Relation, Pack.id == Relation.packid)
            .group_by(Pack.name)
        )

    @property
    def sets(self) -> list[Set]:
        return self._make_set_list(self.set_query.all())

    def _make_set_list(self, results) -> list[Set]:
        return [self._make_set(result) for result in results]

    def _make_set(self, result) -> Set:
        return Set(
            id=result.id,
            abbr=result.abbr,
            name=result.name,
            _ocgdate=result._ocgdate,
            _tcgdate=result._tcgdate,
            contents=[int(card_id) for card_id in result.cardids.split(",")],
        )

    def get_set_by_id(self, id: int) -> Set:
        query = self.set_query.filter(Pack.id == id)
        result = self.session.execute(query.statement).fetchone()
        return Set(
            id=result.id,
            abbr=result.abbr,
            name=result.name,
            _ocgdate=result._ocgdate,
            _tcgdate=result._tcgdate,
            contents=[int(card_id) for card_id in result.cardids.split(",")],
        )

    def get_sets_by_ids(self, ids: list[int]) -> list[Set]:
        query = self.set_query.filter(Pack.id.in_(ids))
        results = self.session.execute(query.statement).fetchall()
        return self._make_set_list(results)

    def get_set_by_name(self, name: str) -> Set:
        self.set_query
        query = self.set_query.filter(Pack.name == name)
        result = self.session.execute(query.statement).fetchone()
        return self._make_set(result)

    def get_sets_by_names(self, names: list[str]) -> list[Set]:
        self.set_query
        query = self.set_query.filter(Pack.name.in_(names))
        results = self.session.execute(query.statement).fetchall()
        return self._make_set_list(results)

    def get_card_sets(self, card: Card) -> list[Set]:
        query = self.set_query.filter(Relation.cardid == card.id)
        results = self.session.execute(query.statement).fetchall()
        return self._make_set_list(results)

    ################# Name/id Map Functions #################

    def get_card_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.set_query.statement).fetchall()
        return {card.name: card.id for card in results}

    def get_archetype_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.arch_query.statement).fetchall()
        return {
            archetype.name: archetype.id for archetype in results if archetype.id != 0
        }

    def get_set_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.set_query.statement).fetchall()
        return {set.name: set.id for set in results}
