from __future__ import annotations

from enum import IntFlag
from operator import or_
from typing import Callable

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from .archetype import Archetype
from .card import Card
from .set import Set
from .sqlclasses import *


class YugiDB:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    ################# Card Functions #################

    @property
    def card_query(self):
        return (
            self.session.query(
                Datas.id.label("id"),
                Texts.name.label("name"),
                Texts.desc.label("text"),
                Datas.type.label("type"),
                Datas.race.label("race"),
                Datas.attribute.label("attribute"),
                Datas.category.label("category"),
                Datas.genre.label("genre"),
                Datas.level.label("level"),
                Datas.atk.label("atk"),
                Datas.def_.label("def"),
                Datas.tcgdate.label("tcgdate"),
                Datas.ocgdate.label("ocgdate"),
                Datas.ot.label("status"),
                Datas.setcode.label("archcode"),
                Datas.support.label("supportcode"),
                Datas.alias.label("alias"),
                Koids.koid.label("koid"),
                Datas.script.label("script"),
            )
            .join(Texts, Datas.id == Texts.id)
            .join(Koids, Datas.id == Koids.id)
        )

    @property
    def cards(self) -> list[Card]:
        return self._make_cards_list(self.card_query.all())

    def _make_card(self, result) -> Card:
        return Card(*result)

    def _make_cards_list(self, results) -> list[Card]:
        return [self._make_card(result) for result in results]

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
            Setcodes.name,
            Setcodes.id,
        )

    def _make_arch_list(self, results) -> list[Archetype]:
        return [self._make_archetype(result) for result in results]

    def _make_archetype(self, result) -> Archetype:
        return Archetype(
            id=result.id,
            name=result.name,
            members=[c.id for c in self.cards if result.id in c.archetypes],
            support=[c.id for c in self.cards if result.id in c.support],
            related=[c.id for c in self.cards if result.id in c.related],
        )

    @property
    def archetypes(self) -> list[Archetype]:
        return self._make_arch_list(self.arch_query.all())

    def get_archetypes_by_values(self, search_values: dict) -> list[Archetype]:
        filters = {
            "name": Setcodes.name == search_values.get("name"),
            "id": Setcodes.id == int(search_values.get("id", 0)),
        }

        query = self.arch_query.filter(*(f for f in filters.values() if f is not None))
        results = self.session.execute(query).fetchall()
        return self._make_arch_list(results)

    ################# Set Functions #################

    @property
    def set_query(self):
        return (
            self.session.query(
                Packs.id,
                Packs.abbr,
                Packs.name,
                Packs.ocgdate,
                Packs.tcgdate,
                func.group_concat(Relations.cardid).label("cardids"),
            )
            .join(Relations, Packs.id == Relations.packid)
            .group_by(Packs.name)
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
            _ocgdate=result.ocgdate,
            _tcgdate=result.tcgdate,
            contents=[int(card_id) for card_id in result.cardids.split(",")],
        )

    def get_card_sets(self, card: Card) -> list[Set]:
        query = self.set_query.filter(Relations.cardid == card.id)
        results = self.session.execute(query).fetchall()
        return self._make_set_list(results)

    def get_sets_by_values(self, search_values: dict) -> list[Set]:
        filters = {
            "name": Packs.name == search_values.get("name"),
            "abbr": Packs.abbr == search_values.get("abbr"),
            "id": Packs.id == int(search_values.get("id", 0)),
        }

        query = self.set_query.filter(*(f for f in filters.values() if f is not None))
        results = self.session.execute(query).fetchall()
        return self._make_set_list(results)

    ################# Name/id Map Functions #################

    def get_card_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.card_query).fetchall()
        return {card.name: card.id for card in results}

    def get_archetype_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.arch_query).fetchall()
        return {
            archetype.name: archetype.id for archetype in results if archetype.id != 0
        }

    def get_set_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.set_query).fetchall()
        return {set.name: set.id for set in results}
