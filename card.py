from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from functools import reduce
from operator import or_
from typing import TYPE_CHECKING, Optional

from .enums import *

if TYPE_CHECKING:
    from .archetype import Archetype
    from .set import Set
    from .yugidb import YugiDB


@dataclass
class Card:
    id: int
    name: str
    _type: int = 0
    _race: int = 0
    _attribute: int = 0
    _category: int = 0
    _genre: int = 0
    _level: int = 0
    atk: int = 0
    _def: int = 0
    _text: str = ""
    sets: list[int] = field(default_factory=list)
    _tcgdate: int = 0
    _ocgdate: int = 0
    ot: int = 0
    _archcode: int = 0
    _supportcode: int = 0
    alias: int = 0
    script: str = ""
    koid: int = 0

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        if self.has_type(Type.Monster):
            return f"{self.name} ({self.id}): {self.attribute.name} {self.level_str} {self.type_str}"
        else:
            return f"{self.name} ({self.id}): {self.type_str}"

    def __repr__(self) -> str:
        return self.name

    @property
    def text(self) -> str:
        return self._text.replace("'''", "")

    @text.setter
    def text(self, new):
        self._text = new

    @property
    def level_str(self) -> str:
        # Determine the level type
        level_type = (
            "Level -"
            if self.is_dark_synchro
            else "Rank "
            if self.has_edtype(EDType.Xyz)
            else "Link "
            if self.has_edtype(EDType.Link)
            else "Level "
        )

        # Construct the level string
        level_string = (
            f"{level_type}{self.level}" if self.level >= 0 else f"{level_type}?"
        )

        # Append Scale for Pendulum type
        if self.has_type(Type.Pendulum):
            level_string += f", Scale {self.scale}"

        return level_string

    @property
    def type_str(self) -> str:
        def split_camel_case(s: str) -> str:
            import re

            return " ".join(re.findall(r"[A-Z][a-z]*", s))

        # Skill type
        if self.is_skill:
            return "[Skill]"

        # Monster type
        if self.has_type(Type.Monster):
            type_names = [
                type.name
                for type in self.type
                if type not in [Type.Token, Type.Monster, Type.SpSummon]
            ]
            type_string = f"[{split_camel_case(self.race.name)}"
            type_string += f"/{self.ability.name}" if self.has_ability() else ""
            type_string += f"/{self.edtype.name}" if self.has_edtype() else ""
            type_string += f"/{'/'.join(type_names)}]"
        elif (
            self.has_any_type([Type.Spell, Type.Trap]) and not self.is_legendary_dragon
        ):
            # Spell or Trap type
            type_string = f"[{self.property_.name} {'Spell' if self.has_type(Type.Spell) else 'Trap'}]"
        else:
            type_string = ""

        # Modify for Dark Synchro
        if self.is_dark_synchro:
            type_string = type_string.replace("Synchro", "Dark Synchro")

        return type_string

    @property
    def type(self) -> list[Type]:
        return self._enum_values(self._type, Type)

    @type.setter
    def type(self, new: Type | list[Type]) -> None:
        self._turn_off_flags(Type)
        if isinstance(new, Type):
            self._type |= new
        elif isinstance(new, list):
            self._type |= reduce(or_, new)
        else:
            raise ValueError("Invalid type assignment")

    @property
    def category(self) -> list[Category]:
        return self._enum_values(self._category, Category)

    @category.setter
    def category(self, new: Category | list[Category]) -> None:
        if isinstance(new, Category):
            self._category = new
        elif isinstance(new, list):
            self._category = reduce(or_, new)
        else:
            raise ValueError("Invalid type assignment")

    @property
    def genre(self) -> list[Genre]:
        return self._enum_values(self._genre, Genre)

    @genre.setter
    def genre(self, new: Genre | list[Genre]) -> None:
        if isinstance(new, Genre):
            self._genre = new
        elif isinstance(new, list):
            self._genre = reduce(or_, new)
        else:
            raise ValueError("Invalid type assignment")

    @property
    def level(self) -> int:
        if self.has_type(Type.Pendulum):
            return self._level & 0x0000FFFF
        return self._level

    @level.setter
    def level(self, new: int):
        if self.has_type(Type.Pendulum):
            self._level = self.scale << 24 | self.scale << 16 | new
        else:
            self._level = new

    @property
    def rank(self) -> int:
        return self.level

    @rank.setter
    def rank(self, new: int):
        self.level = new

    @property
    def linkrating(self) -> int:
        return self.level

    @linkrating.setter
    def linkrating(self, new: int):
        self.level = new

    @property
    def scale(self) -> int:
        if self.has_type(Type.Pendulum):
            return self._level >> 24
        return 0

    @scale.setter
    def scale(self, new: int):
        if self.has_type(Type.Pendulum):
            self._level = new << 24 | new << 16 | self.level

    @property
    def def_(self) -> int:
        if self.has_edtype(EDType.Link):
            return 0
        return self._def

    @def_.setter
    def def_(self, new: int):
        if not self.has_edtype(EDType.Link):
            self._def = new

    @property
    def linkmarkers(self) -> list[LinkMarker]:
        if self.has_edtype(EDType.Link):
            return self._enum_values(self._def, LinkMarker)
        return []

    @linkmarkers.setter
    def linkmarkers(self, new: LinkMarker | list[LinkMarker]) -> None:
        if not self.has_edtype(EDType.Link):
            return
        if isinstance(new, LinkMarker):
            self._def = new
        elif isinstance(new, list):
            self._def = reduce(or_, new)
        else:
            raise ValueError("Invalid type assignment")

    def append_linkmarker(self, marker: LinkMarker) -> None:
        if not self.has_edtype(EDType.Link):
            return

        current_markers = self._enum_values(self._def, LinkMarker)
        current_markers.append(marker)

        self._def = reduce(or_, current_markers)

    @property
    def race(self) -> Race:
        return Race(self._race)

    @race.setter
    def race(self, new: int | Race):
        self._race = new

    @property
    def edtype(self):
        if not self.has_type(Type.Monster):
            raise RuntimeError("Card is not a Monster card.")
        try:
            return EDType(self._enum_values(self._type, EDType)[0])
        except:
            return EDType.MainDeck

    @edtype.setter
    def edtype(self, new: int | EDType):
        if not self.has_type(Type.Monster):
            return
        self._turn_off_flags(EDType)
        self._type |= new

    @property
    def property_(self):
        if not self.has_any_type([Type.Spell, Type.Trap]):
            raise RuntimeError("Card is not a Monster card.")
        try:
            return Property(self._enum_values(self._type, Property)[0])
        except:
            return Property.Normal

    @property_.setter
    def property_(self, new: int | Property):
        if not self.has_any_type([Type.Spell, Type.Trap]):
            return
        self._turn_off_flags(Property)
        self._type |= new

    @property
    def ability(self):
        if not self.has_type(Type.Monster):
            raise RuntimeError("Card is not a Monster card.")
        try:
            return Ability(self._enum_values(self._type, Ability)[0])
        except:
            return Ability.NoAbility

    @ability.setter
    def ability(self, new: int | Ability):
        if not self.has_type(Type.Monster):
            return
        self._turn_off_flags(Ability)
        self._type |= new

    @property
    def attribute(self) -> Attribute:
        return Attribute(self._attribute)

    @attribute.setter
    def attribute(self, new: int | Attribute):
        self._attribute = new

    @property
    def ocgdate(self) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(self._ocgdate)
        except:
            return datetime.max

    @ocgdate.setter
    def ocgdate(self, new: int | datetime) -> None:
        if isinstance(new, datetime):
            self._ocgdate = self._convert_to_timestamp(new)
        elif isinstance(new, int):
            self._ocgdate = new

    @property
    def tcgdate(self) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(self._tcgdate)
        except:
            return datetime.max

    @tcgdate.setter
    def tcgdate(self, new: int | datetime) -> None:
        if isinstance(new, datetime):
            self._tcgdate = self._convert_to_timestamp(new)
        elif isinstance(new, int):
            self._tcgdate = new

    def _convert_to_timestamp(self, value: int | datetime) -> int:
        if isinstance(value, int):
            return value
        elif isinstance(value, datetime):
            return int(value.timestamp())
        else:
            raise ValueError("Invalid input. Use int or datetime objects.")

    def _turn_off_flags(self, enum_class):
        for flag in enum_class:
            self._type &= ~flag

    def _enum_values(self, value: int, enum_class) -> list:
        return [enum_member for enum_member in enum_class if value & enum_member]

    def has_type(self, type: Type) -> bool:
        return bool(self._type & type)

    def has_any_type(self, types: list[Type]) -> bool:
        return any(self.has_type(type) for type in types)

    def has_all_types(self, types: list[Type]) -> bool:
        return all(self.has_type(type) for type in types)

    def has_any_edtype(self, edtypes: list[EDType]) -> bool:
        return any(self.has_edtype(edtype) for edtype in edtypes)

    def has_all_edtypes(self, edtypes: list[EDType]) -> bool:
        return all(self.has_edtype(edtype) for edtype in edtypes)

    def has_category(self, category: Category) -> bool:
        return bool(self._category & category)

    def has_any_category(self, categories: list[Category]) -> bool:
        return any(self.has_category(category) for category in categories)

    def has_all_categories(self, categories: list[Category]) -> bool:
        return all(self.has_category(category) for category in categories)

    def has_genre(self, genre: Genre) -> bool:
        return bool(self._genre & genre)

    def has_any_genre(self, genres: list[Genre]) -> bool:
        return any(self.has_genre(genre) for genre in genres)

    def has_all_genres(self, genres: list[Genre]) -> bool:
        return all(self.has_genre(genre) for genre in genres)

    def has_linkmarker(self, linkmarker: LinkMarker) -> bool:
        if self.has_edtype(EDType.Link):
            return bool(self._def & linkmarker)
        return False

    def has_any_linkmarkers(self, linkmarkers: list[LinkMarker]) -> bool:
        if self.has_edtype(EDType.Link):
            return any(self.has_linkmarker(linkmarker) for linkmarker in linkmarkers)
        return False

    def has_all_linkmarkers(self, linkmarkers: list[LinkMarker]) -> bool:
        if self.has_edtype(EDType.Link):
            return all(self.has_linkmarker(linkmarker) for linkmarker in linkmarkers)
        return False

    def has_property(self, property: Property) -> bool:
        if not self.has_any_type([Type.Spell, Type.Trap]):
            return False
        if property == Property.Normal:
            return not any([self._type & p for p in Property])
        else:
            return bool(self._type & property)

    def has_ability(self, ability: Optional[Ability] = None) -> bool:
        if not self.has_type(Type.Monster):
            return False
        if ability == None:
            # Return true if card has an ability at all
            return self.ability != Ability.NoAbility
        if ability == Ability.NoAbility:
            return not any([self._type & a for a in Ability])
        else:
            return bool(self._type & ability)

    def has_edtype(self, edtype: Optional[EDType] = None) -> bool:
        if not self.has_type(Type.Monster):
            return False
        if edtype == None:
            # Return true if card has an edtype at all
            return self.edtype != EDType.MainDeck
        if edtype == EDType.MainDeck:
            return not any([self._type & a for a in EDType])
        else:
            return bool(self._type & edtype)

    @staticmethod
    def _split_chunks(n: int, nchunks: int):
        return [v for v in [(n >> (16 * i)) & 0xFFFF for i in range(nchunks)] if v != 0]

    @property
    def archetypes(self) -> list[int]:
        return Card._split_chunks(self._archcode, 4)

    @archetypes.setter
    def archetypes(self, values: list[int]):
        if len(values) < 4:
            while len(values) != 4:
                values.append(0)
        else:
            raise ValueError("Card can not have more than 4 member archetypes.")
        self._archcode = sum((value << (16 * i)) for i, value in enumerate(values))

    @property
    def support(self) -> list[int]:
        return Card._split_chunks(self._supportcode, 2)

    @support.setter
    def support(self, values: list[int]):
        if len(values) < 2:
            while len(values) != 2:
                values.append(0)
        else:
            raise ValueError("Card can not have more than 2 support archetypes.")
        self._supportcode = sum((value << (16 * i)) for i, value in enumerate(values))

    @property
    def related(self) -> list[int]:
        return Card._split_chunks(self._supportcode >> 32, 2)

    @related.setter
    def related(self, values: list[int]):
        if len(values) < 2:
            while len(values) != 2:
                values.append(0)
        else:
            raise ValueError("Card can not have more than 2 related archetypes.")
        self._supportcode = (self._supportcode & 0xFFFFFFFF) | (
            sum((value << (16 * i)) for i, value in enumerate(values)) << 32
        )

    def get_archetypes(self, db: YugiDB) -> list[Archetype]:
        return [db.get_archetype_by_id(id) for id in self.archetypes if id != 0]

    def get_support(self, db: YugiDB) -> list[Archetype]:
        return [db.get_archetype_by_id(id) for id in self.support if id != 0]

    def get_related(self, db: YugiDB) -> list[Archetype]:
        return [db.get_archetype_by_id(id) for id in self.related if id != 0]

    def get_sets(self, db: YugiDB) -> list["Set"]:
        return [db.get_set_by_id(id) for id in self.sets]

    @property
    def has_atk_equ_def(self) -> bool:
        return self.has_type(Type.Monster) and self.atk == self._def

    @property
    def is_trap_monster(self) -> bool:
        return self.has_type(Type.Trap) and self.level != 0

    @property
    def is_dark_synchro(self) -> bool:
        return self.has_category(Category.DarkCard) and self.has_edtype(EDType.Synchro)

    @property
    def is_legendary_dragon(self) -> bool:
        return any(self.id == x for x in [10000050, 10000060, 10000070])

    @property
    def is_rush(self) -> bool:
        return any(
            self.has_category(x)
            for x in [
                Category.RushCard,
                Category.RushMax,
                Category.RushLegendary,
            ]
        )

    @property
    def is_beta(self) -> bool:
        return self.has_category(Category.BetaCard)

    @property
    def is_skill(self) -> bool:
        return self.has_category(Category.SkillCard)

    @property
    def is_god(self) -> bool:
        return any(
            self.has_category(x)
            for x in [
                Category.RedGod,
                Category.BlueGod,
                Category.YellowGod,
            ]
        )

    @property
    def is_pre_errata(self) -> bool:
        return self.has_category(Category.PreErrata)

    @staticmethod
    def compare_small_world(handcard: Card, deckcard: Card, addcard: Card) -> bool:
        return all(
            sum(
                [
                    card1._attribute == card2._attribute,
                    card1._race == card2._race,
                    card1.atk == card2.atk,
                    card1._def == card2._def,
                    card1.level == card2.level,
                ]
            )
            == 1
            for card1, card2 in [[handcard, deckcard], [deckcard, addcard]]
        )

    @property
    def combined_archetypes(self) -> list[int]:
        return list(set(self.archetypes + self.support + self.related))

    @property
    def get_script(self) -> Optional[str]:
        import requests

        base_url = "https://raw.githubusercontent.com/Fluorohydride/ygopro-scripts/master/c%s.lua"
        r = requests.get(base_url % self.id)
        return r.text if r.ok else None

    def get_trivia(self) -> Optional[str]:
        from urllib.parse import quote

        import requests
        from bs4 import BeautifulSoup
        from fake_useragent import UserAgent

        ua = UserAgent()
        base_url = "https://yugipedia.com/wiki/Card_Trivia:%s"
        card_url = base_url % quote(self.name)
        r = requests.get(card_url, headers={"User-Agent": ua.random})
        if not r.ok:
            return None
        soup = BeautifulSoup(r.content, "html.parser")
        result = soup.select_one("#mw-content-text > div")
        if not result:
            return None
        div_elements = result.find_all("div")
        for div_element in div_elements:
            div_element.extract()

        return result.text if result else None

    def get_rulings(self) -> Optional[tuple[str, str]]:
        # TODO: finish this
        konami_rush_db_base_url = "https://www.db.yugioh-card.com/rushdb/card_search.action?ope=2&cid=%s&request_locale=ja"
        konami_rush_faq_base_url = "https://www.db.yugioh-card.com/rushdb/faq_search.action?ope=4&cid=%s&request_locale=ja"
        konami_db_base_url = "https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=%s&request_locale=%s"
        ygorganisation_base_url = "https://db.ygorganization.com/card#%s:%s"

        if self.koid:
            if self.is_rush:
                database_url = konami_rush_db_base_url % self.koid
                faq_url = konami_rush_faq_base_url % self.koid
            else:
                if self.ot == OT.OCG:
                    db_locale = "ja"
                else:
                    db_locale = "en"
                database_url = konami_db_base_url % (self.koid, db_locale)
                faq_url = ygorganisation_base_url % (self.koid, "en")
            return database_url, faq_url

    def render(self, dir="out"):
        from .cardrenderer import Renderer

        Renderer.render_card(self, dir)
