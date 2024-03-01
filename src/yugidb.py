import os
from typing import Callable

from sqlalchemy import and_, create_engine, false, func, inspect, or_
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
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
    def __init__(self, connection_string: str):
        self.name = os.path.basename(connection_string)
        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.has_koids = self.has_table("koids")
        self.has_packs = all(self.has_table(x) for x in ["packs", "relations"])
        self.has_rarities = self.has_table("rarities")

    def has_table(self, table_name: str):
        return inspect(self.engine).has_table(table_name)

    def _build_query(
        self,
        params: dict[str, int | str | list[IntFlag] | IntFlag],
        key: str,
        column,
        valuetype: type = str,
        condition=True,
        special={},
    ):
        values = params.get(key)

        if not values:
            return None

        if not isinstance(values, str):
            if issubclass(valuetype, IntFlag):
                if isinstance(values, list):
                    values = ",".join([value.name.lower() for value in values])
                elif isinstance(values, IntFlag):
                    values = str(values.name.lower())
                else:
                    raise TypeError("Invalid type for value")
            elif isinstance(values, int):
                values = str(values)
            else:
                raise TypeError("Invalid type for value")

        values = values.lower()

        def _build_subquery(value: str):
            negated = value.startswith("~")
            value = value.lstrip("~")

            ops = ["!=", ">=", "<=", ">", "<"]
            op = next((x for x in ops if value.startswith(x)), "==")
            value = value.lstrip("><=!")

            if value in special:
                # Handle special query values
                subquery = special[value]
            elif valuetype == "substr":
                # Handle substring queries
                subquery = column.ilike(f"%{value}%")
            elif valuetype == str:
                # Handle exact string queries
                subquery = column.op("==")(str(value))
            elif valuetype == int:
                # Handle integer queries
                subquery = column.op(op)(int(value))
            elif issubclass(valuetype, IntFlag):
                # Handle queries for specific types
                type_modifier = {
                    k.casefold(): v for k, v in valuetype.__members__.items()
                }
                subquery = column.op("&")(type_modifier[value])
            else:
                raise TypeError("Invalid type for value")

            # Check if value is negated
            if negated:
                subquery = ~subquery

            return subquery

        # Apply AND to values
        def map_and_values(values):
            return and_(*map(_build_subquery, values.split(",")))

        # Apply OR to values
        query = or_(*map(map_and_values, values.split("|")))

        # AND with condition
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
            items.append(Koids.koid)

        if self.has_rarities:
            items.append(Rarities.tcgrarity)

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
            self._build_query(params, **filter_param)
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
        try:
            result = query.one()
        except MultipleResultsFound:
            result = query.all()[0]
        except NoResultFound:
            return None

        return self._make_card(result)

    def write_card_to_database(self, card: Card):
        try:
            # Check if the card ID already exists in the Datas table
            card_data = self.session.query(Datas).filter_by(id=card.id).one_or_none()

            if card_data:
                # Update existing record
                card_data.type = card._typedata
                card_data.race = card._racedata
                card_data.attribute = card._attributedata
                card_data.category = card._categorydata
                card_data.genre = card._genredata
                card_data.level = card._leveldata
                card_data.atk = card._atkdata
                card_data.def_ = card._defdata
                card_data.tcgdate = card._tcgdatedata
                card_data.ocgdate = card._ocgdatedata
                card_data.ot = card.status
                card_data.support = card._supportcode
                card_data.alias = card.alias
                card_data.script = card._scriptdata
            else:
                # Insert new record into Datas table
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

            # Insert or update data in the Texts table
            text_data = self.session.query(Texts).filter_by(id=card.id).one_or_none()
            if text_data:
                text_data.name = card.name
                text_data.desc = card._textdata
            else:
                new_text = Texts(id=card.id, name=card.name, desc=card._textdata)
                self.session.add(new_text)

            # Insert or update data in the Koids table if available
            if self.has_koids:
                koid_data = (
                    self.session.query(Koids).filter_by(id=card.id).one_or_none()
                )
                if koid_data:
                    koid_data.koid = card._koiddata
                else:
                    new_koid = Koids(id=card.id, koid=card._koiddata)
                    self.session.add(new_koid)

            # Insert or update data in the Rarities table if available
            if self.has_rarities:
                rarity_data = (
                    self.session.query(Rarities).filter_by(id=card.id).one_or_none()
                )
                if rarity_data:
                    rarity_data.tcgrarity = card._raritydata
                else:
                    new_rarity = Rarities(id=card.id, tcgrarity=card._raritydata)
                    self.session.add(new_rarity)

            # Commit changes to the database
            self.session.commit()
            print(f"Data for {card.name} successfully written to the database.")
        except (IntegrityError, NoResultFound) as e:
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
            self._build_query(params, **filter_param)
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

    def get_card_sets(self, cardorid: Card | int) -> list[Set]:
        if isinstance(cardorid, Card):
            id = cardorid.id
        elif isinstance(cardorid, int):
            id = cardorid
        query = self.set_query.filter(Relations.cardid == id)
        results = query.all()
        return self._make_set_list(results)

    def get_sets_by_value(self, key: str, value: str):
        return self.get_sets_by_values({key: value})

    def get_sets_by_values(self, params: dict) -> list[Set]:
        params = {k.lower(): v for k, v in params.items()}
        filters = [
            self._build_query(params, **filter_param)
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
