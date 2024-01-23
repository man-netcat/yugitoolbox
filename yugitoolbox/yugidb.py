import os
from typing import Callable

from sqlalchemy import and_, create_engine, false, func, inspect, or_
from sqlalchemy.orm import sessionmaker

from .archetype import Archetype
from .card import Card
from .constants import *
from .enums import *
from .set import Set
from .sqlclasses import *


class YugiDB:
    def __init__(self, connection_string: str, debug=False):
        self.name = os.path.basename(connection_string)
        self.engine = create_engine(connection_string, echo=debug)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.has_koids = inspect(self.engine).has_table("koids")
        self.has_packs = all(
            inspect(self.engine).has_table(x) for x in ["packs", "relations"]
        )

    def _build_filter(self, params, key, column, valuetype=str, condition=True):
        values = params.get(key)

        if not values:
            return None

        if issubclass(valuetype, IntFlag):
            mapping = {k.casefold(): v for k, v in valuetype.__members__.items()}
            type_modifier = (
                lambda x: y.value if (y := mapping.get(x.casefold())) else None
            )
        elif valuetype == int:
            type_modifier = int
        elif valuetype == str:
            type_modifier = func.lower

        def apply_modifier(value):
            return column(type_modifier(value))

        query = or_(
            *[
                and_(*[apply_modifier(value) for value in value_or.split(",")])
                for value_or in values.split("|")
            ]
        )

        return and_(condition, query)

    ################# Card Functions #################

    @property
    def card_query(self):
        items = [
            Datas.id,
            Texts.name,
            Texts.desc,
            Datas.type,
            Datas.race,
            Datas.attribute,
            Datas.category,
            Datas.genre,
            Datas.level,
            Datas.atk,
            Datas.def_,
            Datas.tcgdate,
            Datas.ocgdate,
            Datas.ot,
            Datas.setcode,
            Datas.support,
            Datas.alias,
            Datas.script,
        ]

        if self.has_koids:
            items.append(Koids.koid.label("koid"))

        if self.has_packs:
            subquery = (
                self.session.query(
                    Relations.cardid, func.group_concat(Packs.id).label("sets")
                )
                .join(Packs, Relations.packid == Packs.id)
                .group_by(Relations.cardid)
                .subquery()
            )

            query = (
                self.session.query(*items, subquery.c.sets)
                .join(Texts, Datas.id == Texts.id)
                .outerjoin(subquery, Datas.id == subquery.c.cardid)
                .group_by(Datas.id, Texts.name)
            )
        else:
            query = (
                self.session.query(*items)
                .join(Texts, Datas.id == Texts.id)
                .group_by(Datas.id, Texts.name)
            )

        if self.has_koids:
            query = query.outerjoin(Koids, Datas.id == Koids.id)

        return query

    def _make_card(self, result) -> Card:
        card = Card(
            *result[:18],
            _setdata=result.sets if self.has_packs and result.sets is not None else "",
            _koiddata=result.koid if self.has_koids else 0,
        )

        return card

    def _make_card_list(self, results) -> list[Card]:
        return [self._make_card(result) for result in results]

    @property
    def cards(self) -> list[Card]:
        results = self.card_query.all()
        return self._make_card_list(results)

    def get_archetype_cards(self, arch: Archetype) -> list[Card]:
        query = self.card_query.filter(or_(val == arch.id for val in Datas.archetypes))
        results = query.all()
        return self._make_card_list(results)

    def get_set_cards(self, set: Set) -> list[Card]:
        query = self.card_query.join(Relations, Datas.id == Relations.cardid).filter(
            Relations.packid == set.id
        )
        results = query.all()
        return self._make_card_list(results)

    def get_cards_by_value(self, key: str, value):
        return self.get_cards_by_values({key: value})

    def get_cards_by_values(self, params: dict) -> list[Card]:
        filters = [
            self._build_filter(params, **filter_param)
            for filter_param in card_filter_params
            if filter_param["key"] in params
        ]

        query = self.card_query.filter(*filters)
        results = query.all()
        return self._make_card_list(results)

    def get_card_by_id(self, card_id):
        query = self.card_query.filter(Datas.id == int(card_id))
        result = query.one()
        return self._make_card(result)

    def get_cards_by_ids(self, card_ids):
        query = self.card_query.filter(Datas.id.in_(card_ids))
        results = query.all()
        return self._make_card_list(results)

    def get_card_by_name(self, card_name):
        query = self.card_query.filter(Texts.name == card_name)
        result = query.one()
        return self._make_card(result)

    def get_cards_by_query(self, query: Callable[[Card], bool]) -> list[Card]:
        return [card for card in self.cards if query(card)]

    ################# Archetype Functions #################

    @property
    def arch_query(self):
        items = [Setcodes.name, Setcodes.id]
        return self.session.query(*items)

    def _make_arch_list(self, results) -> list[Archetype]:
        return [self._make_archetype(result) for result in results]

    def _make_archetype(self, result) -> Archetype:
        if result.id == 0:
            return Archetype(result.id, result.name)

        def _member_subquery(datas_cols):
            return (
                self.session.query(func.group_concat(Datas.id, ",").label("cardids"))
                .join(Setcodes, or_(*[Setcodes.id == x for x in datas_cols]))
                .filter(
                    and_(or_(*[x == result.id for x in datas_cols]), Setcodes.id != 0)
                )
            )

        members_query = _member_subquery(Datas.archetypes)
        support_query = _member_subquery(Datas.supportarchs)
        related_query = _member_subquery(Datas.relatedarchs)

        members_results = members_query.one()
        support_results = support_query.one()
        related_results = related_query.one()

        return Archetype(
            id=result.id,
            name=result.name,
            members=members_results.cardids.split(",")
            if members_results.cardids
            else [],
            support=support_results.cardids.split(",")
            if support_results.cardids
            else [],
            related=related_results.cardids.split(",")
            if related_results.cardids
            else [],
        )

    @property
    def archetypes(self) -> list[Archetype]:
        results = self.arch_query.all()
        return self._make_arch_list(results)

    def get_card_archetypes(self, card: Card) -> list[Archetype]:
        query = self.arch_query.filter(Setcodes.id.in_(card.archetypes))
        results = query.all()
        return self._make_arch_list(results)

    def get_archetypes_by_value(self, key: str, value):
        return self.get_archetypes_by_values({key: value})

    def get_archetypes_by_values(self, params: dict) -> list[Archetype]:
        filters = [
            self._build_filter(params, **filter_param)
            for filter_param in archetype_filter_params
            if filter_param["key"] in params
        ]

        query = self.arch_query.filter(*filters)
        results = query.all()
        return self._make_arch_list(results)

    def get_archetype_by_id(self, arch_id):
        query = self.arch_query.filter(Setcodes.id == int(arch_id))
        result = query.one()
        return self._make_archetype(result)

    def get_archetype_by_name(self, arch_name):
        query = self.arch_query.filter(Setcodes.name == arch_name)
        result = query.one()
        return self._make_archetype(result)

    ################# Set Functions #################

    @property
    def set_query(self):
        if self.has_packs:
            query = (
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
        else:
            query = self.session.query(false())
        return query

    def _make_set_list(self, results) -> list[Set]:
        return [self._make_set(result) for result in results]

    def _make_set(self, result) -> Set:
        cardids = getattr(result, "cardids", "").split(",") if self.has_packs else []
        return Set(
            id=result.id,
            abbr=result.abbr,
            name=result.name,
            _ocgdate=result.ocgdate,
            _tcgdate=result.tcgdate,
            contents=[int(card_id) for card_id in cardids],
        )

    @property
    def sets(self) -> list[Set]:
        results = self.set_query.all()
        return self._make_set_list(results)

    def get_card_sets(self, card: Card) -> list[Set]:
        query = self.set_query.filter(Relations.cardid == card.id)
        results = query.all()
        return self._make_set_list(results)

    def get_sets_by_value(self, key: str, value):
        return self.get_sets_by_values({key: value})

    def get_sets_by_values(self, params: dict) -> list[Set]:
        filters = [
            self._build_filter(params, **filter_param)
            for filter_param in set_filter_params
            if filter_param["key"] in params
        ]

        query = self.set_query.filter(*filters)
        results = query.all()
        return self._make_set_list(results)

    def get_set_by_id(self, set_id):
        query = self.set_query.filter(Packs.id == int(set_id))
        result = query.one()
        return self._make_set(result)

    def get_set_by_name(self, set_name):
        query = self.set_query.filter(Packs.name == set_name)
        result = query.one()
        return self._make_set(result)

    ################# Name/id Map Functions #################

    @property
    def card_names(self) -> list[str]:
        query = self.session.query(Texts.name)
        results = query.all()
        return list(set([result.name for result in results]))

    @property
    def archetype_names(self) -> list[str]:
        query = self.session.query(Setcodes.name)
        results = query.all()
        return list(set([result.name for result in results]))

    @property
    def set_names(self) -> list[str]:
        if not self.has_packs:
            return []
        query = self.session.query(Packs.name)
        results = query.all()
        return list(set([result.name for result in results]))
