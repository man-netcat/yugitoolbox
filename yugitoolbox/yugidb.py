import os
from enum import Enum
from typing import Callable

from sqlalchemy import and_, create_engine, false, func, inspect, or_, true
from sqlalchemy.orm import sessionmaker

from .archetype import Archetype
from .card import Card
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

    def _build_filter(self, params, key, column, valuetype=str, condition=true()):
        values = params.get(key)

        if not values:
            return None

        if issubclass(valuetype, IntFlag):
            mapping = {k.casefold(): v for k, v in valuetype.__members__.items()}
            type_modifier = (
                lambda x: mapping.get(x.casefold()).value
                if mapping.get(x.casefold())
                else None
            )
        else:
            type_modifier = lambda x: valuetype(x)

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
            id=result.id,
            name=result.name,
            _textdata=result.desc,
            _typedata=result.type,
            _racedata=result.race,
            _attributedata=result.attribute,
            _categorydata=result.category,
            _genredata=result.genre,
            _leveldata=result.level,
            _atkdata=result.atk,
            _defdata=result.def_,
            _tcgdatedata=result.tcgdate,
            _ocgdatedata=result.ocgdate,
            status=result.ot,
            _archcode=result.setcode,
            _supportcode=result.support,
            alias=result.alias,
            _scriptdata=result.script,
            sets=[int(set_id) for set_id in result.sets.split(",")]
            if self.has_packs and result.sets is not None
            else [],
            _koiddata=result.koid if self.has_koids else 0,
        )

        return card

    def _make_cards_list(self, results) -> list[Card]:
        return [self._make_card(result) for result in results]

    @property
    def cards(self) -> list[Card]:
        return self._make_cards_list(self.card_query.all())

    def get_cards_by_values(self, params: dict) -> list[Card]:
        filters = [
            self._build_filter(params, "name", Texts.name.op("==")),
            self._build_filter(params, "id", Datas.id.op("=="), valuetype=int),
            self._build_filter(params, "race", Datas.race.op("=="), valuetype=Race),
            self._build_filter(
                params, "attribute", Datas.attribute.op("=="), valuetype=Attribute
            ),
            self._build_filter(params, "atk", Datas.atk.op("=="), valuetype=int),
            self._build_filter(params, "def", Datas.def_.op("=="), valuetype=int),
            self._build_filter(
                params, "level", Datas.level.op("&")(0x0000FFFF).op("=="), valuetype=int
            ),
            self._build_filter(
                params,
                "scale",
                Datas.level.op(">>")(24).op("=="),
                valuetype=int,
                condition=Datas.type.op("&")(Type.Pendulum.value),
            ),
            self._build_filter(params, "koid", Koids.koid.op("=="), valuetype=int),
            self._build_filter(params, "type", Datas.type.op("&"), valuetype=Type),
            self._build_filter(
                params, "category", Datas.category.op("&"), valuetype=Category
            ),
            self._build_filter(params, "genre", Datas.genre.op("&"), valuetype=Genre),
            self._build_filter(
                params,
                "linkmarker",
                Datas.def_.op("&"),
                valuetype=LinkMarker,
                condition=Datas.type.op("&")(Type.Link.value),
            ),
        ]

        query = self.card_query.filter(
            *[filter for filter in filters if filter is not None]
        )
        results = self.session.execute(query).fetchall()
        return self._make_cards_list(results)

    def get_card_by_id(self, card_id):
        query = self.card_query.filter(Datas.id == card_id)
        result = self.session.execute(query).fetchone()
        return self._make_card(result)

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
        # TODO: Add members
        return Archetype(
            id=result.id,
            name=result.name,
            members=[],
            support=[],
            related=[],
        )

    @property
    def archetypes(self) -> list[Archetype]:
        return self._make_arch_list(self.arch_query.all())

    def get_archetypes_by_values(self, params: dict) -> list[Archetype]:
        filters = [
            self._build_filter(params, "name", Setcodes.name.op("==")),
            self._build_filter(params, "id", Setcodes.id.op("=="), valuetype=int),
        ]

        query = self.arch_query.filter(
            *[filter for filter in filters if filter is not None]
        )
        results = self.session.execute(query).fetchall()
        return self._make_arch_list(results)

    def get_archetype_by_id(self, arch_id):
        query = self.arch_query.filter(Setcodes.id == int(arch_id))
        result = self.session.execute(query).fetchone()
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
        return self._make_set_list(self.set_query.all())

    def get_card_sets(self, card: Card) -> list[Set]:
        query = self.set_query.filter(Relations.cardid == card.id)
        results = self.session.execute(query).fetchall()
        return self._make_set_list(results)

    def get_sets_by_values(self, params: dict) -> list[Set]:
        filters = [
            self._build_filter(params, "name", Packs.name.op("==")),
            self._build_filter(params, "abbr", Packs.name.op("==")),
            self._build_filter(params, "id", Packs.id.op("=="), valuetype=int),
        ]

        query = self.set_query.filter(
            *[filter for filter in filters if filter is not None]
        )
        results = self.session.execute(query).fetchall()
        return self._make_set_list(results)

    def get_set_by_id(self, set_id):
        query = self.set_query.filter(Packs.id == set_id)
        result = self.session.execute(query).fetchone()
        return self._make_set(result)

    ################# Name/id Map Functions #################

    @property
    def card_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.card_query).fetchall()
        return {card.name: card.id for card in results}

    @property
    def archetype_name_id_map(self) -> dict[str, int]:
        results = self.session.execute(self.arch_query).fetchall()
        return {
            archetype.name: archetype.id for archetype in results if archetype.id != 0
        }

    @property
    def set_name_id_map(self) -> dict[str, int]:
        if not self.has_packs:
            return {}
        results = self.session.execute(self.set_query).fetchall()
        return {set.name: set.id for set in results}
