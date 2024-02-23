import logging
import os
from typing import Callable

from sqlalchemy import and_, create_engine, false, func, inspect, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from .archetype import Archetype
from .card import Card
from .constants import *
from .enums import *
from .set import Set
from .sqlclasses import *
from .util import handle_no_result

Cardquery = Callable[[Card], bool]


class YugiDB:
    def __init__(self, connection_string: str, debug=False):
        self.name = os.path.basename(connection_string)
        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        if debug:
            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

        self.has_koids = self.has_table("koids")
        self.has_packs = all(self.has_table(x) for x in ["packs", "relations"])
        self.has_rarities = self.has_table("rarities")

    def has_table(self, table_name: str):
        return inspect(self.engine).has_table(table_name)

    def _build_filter(
        self,
        params: dict[str],
        key: str,
        column,
        valuetype: type = str,
        condition=True,
        special={},
    ):
        values: int | list | str | IntFlag = params.get(key)

        # Handle special queries
        if isinstance(values, str):
            for specialvalue, query in special.items():
                if values.lower() == specialvalue:
                    return query

        if not values:
            return None

        if not isinstance(values, str):
            if issubclass(valuetype, IntFlag):
                if type(values) == list:
                    values = ",".join([value.name.lower() for value in values])
                else:
                    values = str(values.name.lower())
            elif isinstance(values, int):
                values = str(values)
            else:
                raise TypeError("Invalid type for value")

        if valuetype in [str, "substr"]:
            type_modifier = func.lower
        elif valuetype == int:
            type_modifier = int
        elif issubclass(valuetype, IntFlag):
            type_modifier = {
                k.casefold(): v for k, v in valuetype.__members__.items()
            }.__getitem__
        else:
            raise TypeError("Invalid type for value")

        def apply_modifier(value: str):
            negated = value.startswith("~")
            value = value.lstrip("~")

            op = next((x for x in [">=", "<=", ">", "<"] if value.startswith(x)), "==")
            value = value.lstrip("><=")

            if valuetype == "substr":
                modified_value = type_modifier(f"%{value}%")
                modifier = column.ilike(modified_value)
            elif issubclass(valuetype, IntFlag):
                modified_value = type_modifier(value)
                modifier = column.op("&")(modified_value)
            else:
                modified_value = type_modifier(value)
                modifier = column.op(op)(modified_value)

            # Check if value is negated
            if negated:
                modifier = ~modifier

            return modifier

        # Build query, first applying AND, then applying OR
        query = or_(
            *[
                and_(*[apply_modifier(value) for value in values_or.split(",")])
                for values_or in values.split("|")
            ]
        )

        # Apply condition
        query = and_(condition, query)

        return query

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

        if self.has_rarities:
            items.append(Rarities.tcgrarity.label("tcgrarity"))

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

        if self.has_rarities:
            query = query.outerjoin(Rarities, Datas.id == Rarities.id)

        return query

    def _make_card(self, result) -> Card:
        return Card(*result)

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

    def get_cards_by_value(self, key: str, value: str):
        return self.get_cards_by_values({key: value})

    def get_cards_by_values(self, params: dict) -> list[Card]:
        params = {k.lower(): v for k, v in params.items()}
        filters = [
            self._build_filter(params, **filter_param)
            for filter_param in card_filter_params
            if filter_param["key"] in params
        ]

        if not filters:
            return []

        query = self.card_query.filter(*filters)
        results = query.all()
        return self._make_card_list(results)

    @handle_no_result
    def get_card_by_id(self, card_id):
        query = self.card_query.filter(Datas.id == int(card_id))
        result = query.one()
        return self._make_card(result)

    def get_cards_by_ids(self, card_ids):
        query = self.card_query.filter(Datas.id.in_(card_ids))
        results = query.all()
        return self._make_card_list(results)

    @handle_no_result
    def get_card_by_name(self, card_name):
        query = self.card_query.filter(func.lower(Texts.name) == card_name.lower())
        result = query.one()
        return self._make_card(result)

    def get_cards_by_query(self, query: Cardquery) -> list[Card]:
        return [card for card in self.cards if query(card)]

    def write_card_to_database(self, card: Card):
        try:
            # Inserting data into Datas table
            new_data = Datas(
                id=card.id,
                type=card._typedata,
                race=card._racedata,
                attribute=card._attributedata,
                category=card._categorydata,
                genre=card._genredata,
                level=card._leveldata,
                atk=card._atkdata,
                def_=card._defdata,
                tcgdate=card._tcgdatedata,
                ocgdate=card._ocgdatedata,
                ot=card.status,
                support=card._supportcode,
                alias=card.alias,
                script=card._scriptdata,
            )
            self.session.add(new_data)

            # Inserting data into Texts table
            new_text = Texts(id=card.id, name=card.name, desc=card._textdata)
            self.session.add(new_text)

            # Inserting data into Koids table if available
            if self.has_koids:
                new_koid = Koids(id=card.id, koid=card._koiddata)
                self.session.add(new_koid)

            # Inserting data into Rarities table if available
            if self.has_rarities:
                new_rarity = Rarities(id=card.id, tcgrarity=card._raritydata)
                self.session.add(new_rarity)

            # Commit changes to the database
            self.session.commit()
            print("Card data successfully written to the database.")
        except IntegrityError as e:
            self.session.rollback()
            print(f"Failed to write card data to the database: {e}")

    ################# Archetype Functions #################

    @property
    def arch_query(self):
        items = [Setcodes.id, Setcodes.name]
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
            *result,
            _members_data=members_results.cardids,
            _support_data=support_results.cardids,
            _related_data=related_results.cardids,
        )

    @property
    def archetypes(self) -> list[Archetype]:
        results = self.arch_query.all()
        return self._make_arch_list(results)

    def get_card_archetypes(self, card: Card) -> list[Archetype]:
        query = self.arch_query.filter(Setcodes.id.in_(card.archetypes))
        results = query.all()
        return self._make_arch_list(results)

    def get_archetypes_by_value(self, key: str, value: str):
        return self.get_archetypes_by_values({key: value})

    def get_archetypes_by_values(self, params: dict) -> list[Archetype]:
        params = {k.lower(): v for k, v in params.items()}
        filters = [
            self._build_filter(params, **filter_param)
            for filter_param in archetype_filter_params
            if filter_param["key"] in params
        ]

        if not filters:
            return []

        query = self.arch_query.filter(*filters)
        results = query.all()
        return self._make_arch_list(results)

    @handle_no_result
    def get_archetype_by_id(self, arch_id: int):
        query = self.arch_query.filter(Setcodes.id == int(arch_id))
        result = query.one()
        return self._make_archetype(result)

    @handle_no_result
    def get_archetype_by_name(self, arch_name: str):
        query = self.arch_query.filter(func.lower(Setcodes.name) == arch_name.lower())
        result = query.one()
        return self._make_archetype(result)

    ################# Set Functions #################

    @property
    def set_query(self):
        if self.has_packs:
            query = (
                self.session.query(
                    Packs.id,
                    Packs.name,
                    Packs.abbr,
                    Packs.tcgdate,
                    Packs.ocgdate,
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
        return Set(*result)

    @property
    def sets(self) -> list[Set]:
        if not self.has_packs:
            return []
        results = self.set_query.all()
        return self._make_set_list(results)

    def get_card_sets(self, card: Card) -> list[Set]:
        query = self.set_query.filter(Relations.cardid == card.id)
        results = query.all()
        return self._make_set_list(results)

    def get_sets_by_value(self, key: str, value: str):
        return self.get_sets_by_values({key: value})

    def get_sets_by_values(self, params: dict) -> list[Set]:
        params = {k.lower(): v for k, v in params.items()}
        filters = [
            self._build_filter(params, **filter_param)
            for filter_param in set_filter_params
            if filter_param["key"] in params
        ]

        if not filters:
            return []

        query = self.set_query.filter(*filters)
        results = query.all()
        return self._make_set_list(results)

    @handle_no_result
    def get_set_by_id(self, set_id: int):
        query = self.set_query.filter(Packs.id == int(set_id))
        result = query.one()
        return self._make_set(result)

    @handle_no_result
    def get_set_by_name(self, set_name: str):
        query = self.set_query.filter(func.lower(Packs.name) == set_name.lower())
        result = query.one()
        return self._make_set(result)
