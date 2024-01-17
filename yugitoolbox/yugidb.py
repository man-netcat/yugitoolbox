from typing import Callable

from sqlalchemy import and_, create_engine, false, func, inspect, or_
from sqlalchemy.orm import sessionmaker

from .archetype import Archetype
from .card import Card
from .enums import *
from .set import Set
from .sqlclasses import *


class YugiDB:
    def __init__(self, connection_string: str, debug=False):
        self.engine = create_engine(connection_string, echo=debug)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.has_koids = inspect(self.engine).has_table("koids")
        self.has_packs = inspect(self.engine).has_table("packs")

    def _filter_query_builder(self, base_query, filters):
        query = base_query.filter(*filters)
        results = self.session.execute(query).fetchall()
        return self._make_cards_list(results)

    ################# Card Functions #################

    @property
    def card_query(self):
        items = [
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
            Datas.script.label("script"),
        ]
        if self.has_koids:
            items.append(Koids.koid.label("koid"))
        query = self.session.query(*items).join(Texts, Datas.id == Texts.id)
        if self.has_koids:
            query = query.join(Koids, Datas.id == Koids.id)
        return query

    def _make_card(self, result) -> Card:
        return Card(*result)

    def _make_cards_list(self, results) -> list[Card]:
        return [self._make_card(result) for result in results]

    @property
    def cards(self) -> list[Card]:
        return self._make_cards_list(self.card_query.all())

    def get_cards_by_values(self, params: dict) -> list[Card]:
        def build_filter(key, column, values, condition=None, type_modifier=None):
            if key not in params:
                return None

            def apply_modifier(value):
                return column(type_modifier(value)) if type_modifier else column(value)

            if "," in values:
                values_list = values.split(",")
                query = and_(*map(apply_modifier, values_list))
            elif "|" in values:
                values_list = values.split("|")
                query = or_(*map(apply_modifier, values_list))
            else:
                query = apply_modifier(values)

            return and_(condition, query) if condition else query

        filters = [
            build_filter(
                "name",
                Texts.name.op("=="),
                params.get("name"),
            ),
            build_filter(
                "id",
                Datas.id.op("=="),
                params.get("id", 0),
                type_modifier=int,
            ),
            build_filter(
                "race",
                Datas.race.op("=="),
                params.get("race", "_"),
                type_modifier=lambda x: Race[x].value,
            ),
            build_filter(
                "attribute",
                Datas.attribute,
                params.get("attribute", "_"),
                type_modifier=lambda x: Attribute[x].value,
            ),
            build_filter(
                "atk",
                Datas.atk,
                params.get("atk", 0),
                type_modifier=int,
            ),
            build_filter(
                "def",
                Datas.def_,
                params.get("def", 0),
                type_modifier=int,
            ),
            build_filter(
                "level",
                Datas.level.op("&")(0x0000FFFF).op("=="),
                params.get("level", 0),
                type_modifier=int,
            ),
            build_filter(
                "scale",
                Datas.level.op(">>")(24).op("=="),
                params.get("scale", 0),
                condition=Datas.type.op("&")(Type.Pendulum.value),
                type_modifier=int,
            ),
            build_filter(
                "koid",
                Koids.koid.op("=="),
                params.get("koid", 0),
                type_modifier=int,
            ),
            build_filter(
                "type",
                Datas.type.op("&"),
                params.get("type", "_"),
                type_modifier=lambda x: Type[x].value,
            ),
            build_filter(
                "category",
                Datas.category.op("&"),
                params.get("category", "_"),
                type_modifier=lambda x: Category[x].value,
            ),
            build_filter(
                "genre",
                Datas.genre.op("&"),
                params.get("genre", "_"),
                type_modifier=lambda x: Genre[x].value,
            ),
            build_filter(
                "linkmarker",
                Datas.def_.op("&"),
                params.get("linkmarker", "_"),
                condition=Datas.type.op("&")(Type.Link.value),
                type_modifier=lambda x: LinkMarker[x].value,
            ),
        ]
        return self._filter_query_builder(
            self.card_query, [filter for filter in filters if filter is not None]
        )

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

    def get_archetypes_by_values(self, params: dict) -> list[Archetype]:
        filters = [
            filter
            for key, filter in [
                ("name", Setcodes.name == params.get("name")),
                ("id", Setcodes.id == params.get("id")),
            ]
            if key in params
        ]
        return self._filter_query_builder(self.arch_query, filters)

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
        return Set(
            id=result.id,
            abbr=result.abbr,
            name=result.name,
            _ocgdate=result.ocgdate,
            _tcgdate=result.tcgdate,
            contents=[int(card_id) for card_id in result.cardids.split(",")],
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
            filter
            for key, filter in [
                ("name", Packs.name == params.get("name")),
                ("abbr", Packs.abbr == params.get("abbr")),
                ("id", Packs.id == int(params.get("id"))),
            ]
            if key in params
        ]

        return self._filter_query_builder(self.set_query, filters)

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
        if not self.has_packs:
            return {}
        results = self.session.execute(self.set_query).fetchall()
        return {set.name: set.id for set in results}
