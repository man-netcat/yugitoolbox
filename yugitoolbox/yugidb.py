from __future__ import annotations

from typing import Callable

from sqlalchemy import Column, Integer, String, create_engine, func
from sqlalchemy.orm import class_mapper, sessionmaker

from .archetype import Archetype
from .card import Card
from .set import Set
from .sqlclasses import *


class YugiDB:
    __tablename__ = "yugidb"

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

    @property
    def card_query(self):
        return (
            self.session.query(
                Data.id,
                Text.name,
                Text.text,
                Data._type,
                Data._race,
                Data._attribute,
                Data._category,
                Data._genre,
                Data._level,
                Data.atk,
                Data._def,
                Data._tcgdate,
                Data._ocgdate,
                Data.status,
                Data._archcode,
                Data._supportcode,
                Data.alias,
                Koid._koid,
                Data._script,
            )
            .join(Text, Data.id == Text.id)
            .join(Koid, Data.id == Koid.id)
        )

    @property
    def cards(self):
        return self._make_cards_list(self.card_query.all())

    def _make_cards_list(self, results):
        return [Card(*row) for row in results]

    def get_card_by_id(self, id) -> Card:
        return self.get_cards_by_ids([id])[0]

    def get_cards_by_ids(self, ids: list[int]) -> list[Card]:
        query = self.card_query.filter(Data.id.in_(ids))
        result = self.session.execute(query.statement).fetchall()
        return [Card(*row) for row in result]

    def get_cards_by_value(self, by: str, value: str | int) -> list[Card]:
        if not hasattr(Card, by):
            raise ValueError(f"Attribute '{by}' does not exist in the Card class.")

        attribute_type = class_mapper(Card).columns[by].type.python_type

        if attribute_type == str:
            query = self.card_query.filter(getattr(Card, by) == value)
        elif attribute_type == int:
            query = self.card_query.filter(getattr(Card, by) == int(value))
        else:
            raise ValueError(f"Unsupported attribute type for '{by}'.")

        matching_cards = query.all()
        return matching_cards

    def get_cards_by_values(self, search_values: dict) -> list[Card]:
        for attribute in search_values.keys():
            if not hasattr(Card, attribute):
                raise ValueError(
                    f"Attribute '{attribute}' does not exist in the Card class."
                )

        query = self.card_query.filter(
            *[
                getattr(Card, attribute) == int(value)
                if isinstance(value, int)
                else getattr(Card, attribute) == value
                for attribute, value in search_values.items()
            ]
        )

        matching_cards = query.all()
        return matching_cards

    def get_cards_by_query(self, query: Callable[[Card], bool]) -> list[Card]:
        return [card for card in self.card_query.all() if query(card)]

    @property
    def arch_query(self):
        return self.session.query(
            SetCode.name,
            func.coalesce(SetCode.officialcode, SetCode.betacode).label("id"),
        )

    def _make_arch_list(self, results):
        return [
            Archetype(
                id=row.id,
                name=row.name,
                members=[
                    card_id
                    for card_id, *_ in self.session.execute(
                        self.card_query.filter(Data._archcode == row.id).statement
                    ).fetchall()
                ],
            )
            for row in results
            if row.id != 0
        ]

    @property
    def archetypes(self):
        return self._make_arch_list(self.arch_query.all())

    def get_archetype_by_id(self, id: int) -> Archetype:
        return self.get_archetypes_by_ids([id])[0]

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
    def sets(self):
        return self._make_set_list(self.set_query.all())

    def _make_set_list(self, results):
        return [
            Set(
                id=row.id,
                abbr=row.abbr,
                name=row.name,
                _ocgdate=row._ocgdate,
                _tcgdate=row._tcgdate,
                contents=[int(card_id) for card_id in row.cardids.split(",")],
            )
            for row in results
        ]

    def get_set_by_id(self, id: int) -> Set:
        return self.get_sets_by_ids([id])[0]

    def get_sets_by_ids(self, ids: list[int]) -> list[Set]:
        self.set_query
        query = self.set_query.filter(Pack.id.in_(ids))
        results = self.session.execute(query.statement).fetchall()
        return self._make_set_list(results)

    def get_set_by_name(self, name: str) -> Set:
        return self.get_sets_by_names([name])[0]

    def get_sets_by_names(self, names: list[str]) -> list[Set]:
        self.set_query
        query = self.set_query.filter(Pack.name.in_(names))
        results = self.session.execute(query.statement).fetchall()
        return self._make_set_list(results)

    def get_card_sets(self, card: Card) -> list[Set]:
        query = self.set_query.filter(Relation.cardid == card.id)
        results = self.session.execute(query.statement).fetchall()
        return self._make_set_list(results)
