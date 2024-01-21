from dataclasses import dataclass, field
from datetime import datetime
from functools import reduce
from math import isnan
from operator import or_
from typing import Optional

from fake_useragent import UserAgent

from .enums import *

ua = UserAgent()


@dataclass
class Card:
    id: int
    name: str
    _textdata: str = ""
    _typedata: int = 0
    _racedata: int = 0
    _attributedata: int = 0
    _categorydata: int = 0
    _genredata: int = 0
    _leveldata: int = 0
    _atkdata: int = 0
    _defdata: int = 0
    _tcgdatedata: int = 0
    _ocgdatedata: int = 0
    status: int = 0
    _archcode: int = 0
    _supportcode: int = 0
    alias: int = 0
    _scriptdata: str = ""
    _koiddata: int = 0
    sets: list = field(default_factory=[])

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        try:
            if self.has_type(Type.Monster):
                return f"{self.name} ({self.id}): {self.attribute.name} {self.level_str} {self.type_str}"
            else:
                return f"{self.name} ({self.id}): {self.type_str}"
        except:
            return "None"

    def __repr__(self) -> str:
        return self.name

    # TODO: clean up your mess
    def to_dict(self):
        def convert_enum(value):
            return (
                value.name
                if isinstance(value, IntFlag)
                else [v.name if isinstance(v, IntFlag) else v for v in value]
                if isinstance(value, list)
                else value
            )

        fields = {
            field: convert_enum(getattr(self, field))
            for field in self.__dataclass_fields__
            if not field.startswith("_")
        }

        properties = {
            prop: convert_enum(getattr(self, prop))
            for prop in self.__class__.__dict__
            if isinstance(getattr(self.__class__, prop), property)
            and prop not in ["tcgdate", "ocgdate"]
        }

        return fields | properties

    @property
    def text(self) -> str:
        return self._textdata.replace("'''", "")

    @text.setter
    def text(self, new):
        self._textdata = new

    @property
    def level_str(self) -> str:
        # Determine the level type
        level_type = (
            "Level -"
            if self.is_dark_synchro
            else "Rank "
            if self.has_type(Type.Xyz)
            else "Link "
            if self.has_type(Type.Link)
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

            try:
                return " ".join(re.findall(r"[A-Z][a-z]*", s))
            except:
                return "None"

        # Skill type
        if self.is_skill:
            return "[Skill]"

        # Monster type
        type_names = [
            type.name
            for type in self.type
            if type not in [Type.SpSummon, Type.Monster, Type.Trap, Type.Spell]
        ]
        if self.has_type(Type.Monster):
            type_string = f"[{split_camel_case(self.race.name)}"
            type_string += f"/{'/'.join(type_names)}]"
        elif self.is_spelltrap and not self.is_legendary_dragon:
            type_string = f"[{type_names[0] if len(type_names) > 0 else 'Normal'}"
            type_string += f" {'Spell' if self.has_type(Type.Spell) else 'Trap'}]"
        else:
            type_string = ""

        # Modify for Dark Synchro
        if self.is_dark_synchro:
            type_string = type_string.replace("Synchro", "Dark Synchro")

        return type_string

    @property
    def type(self) -> list[Type]:
        return self._enum_values(self._typedata, Type)

    @type.setter
    def type(self, new: Type | list[Type]) -> None:
        self._turn_off_flags(Type)
        if isinstance(new, Type):
            self._typedata |= new
        elif isinstance(new, list):
            self._typedata |= reduce(or_, new)
        else:
            raise ValueError("Invalid mdtype assignment")

    def append_type(self, mdtype: Type) -> None:
        self._typedata |= mdtype

    def remove_type(self, mdtype: Type) -> None:
        self._typedata &= ~mdtype

    @property
    def category(self) -> list[Category]:
        return self._enum_values(self._categorydata, Category)

    @category.setter
    def category(self, new: Category | list[Category]) -> None:
        if isinstance(new, Category):
            self._categorydata = new
        elif isinstance(new, list):
            self._categorydata = reduce(or_, new)
        else:
            raise ValueError("Invalid type assignment")

    def append_category(self, category: Category) -> None:
        self._categorydata |= category

    def remove_category(self, category: Category) -> None:
        self._categorydata &= ~category

    @property
    def genre(self) -> list[Genre]:
        return self._enum_values(self._genredata, Genre)

    @genre.setter
    def genre(self, new: Genre | list[Genre]) -> None:
        if isinstance(new, Genre):
            self._genredata = new
        elif isinstance(new, list):
            self._genredata = reduce(or_, new)
        else:
            raise ValueError("Invalid type assignment")

    def append_genre(self, genre: Genre) -> None:
        self._genredata |= genre

    def remove_genre(self, genre: Genre) -> None:
        self._genredata &= ~genre

    @property
    def level(self) -> int:
        return self._leveldata & 0x0000FFFF

    @level.setter
    def level(self, new: int):
        self._leveldata = self.scale << 24 | self.scale << 16 | new

    @property
    def scale(self) -> int:
        return self._leveldata >> 24

    @scale.setter
    def scale(self, new: int):
        self._leveldata = new << 24 | new << 16 | self.level

    @property
    def atk(self) -> int:
        return self._atkdata

    @atk.setter
    def atk(self, new: int):
        self._atkdata = new

    @property
    def def_(self) -> int:
        if self.has_type(Type.Link):
            return 0
        return self._defdata

    @def_.setter
    def def_(self, new: int):
        if self.has_type(Type.Link):
            return
        self._defdata = new

    @property
    def linkmarkers(self) -> list[LinkMarker]:
        if self.has_type(Type.Link):
            return self._enum_values(self._defdata, LinkMarker)
        return []

    @linkmarkers.setter
    def linkmarkers(self, new: LinkMarker | list[LinkMarker]) -> None:
        if not self.has_type(Type.Link):
            return
        if isinstance(new, LinkMarker):
            self._defdata = new
        elif isinstance(new, list):
            self._defdata = reduce(or_, new)
        else:
            raise ValueError("Invalid type assignment")

    def append_linkmarker(self, marker: LinkMarker) -> None:
        if not self.has_type(Type.Link):
            return

        self._defdata |= marker

    def remove_linkmarker(self, marker: LinkMarker) -> None:
        if not self.has_type(Type.Link):
            return

        self._defdata &= ~marker

    @property
    def race(self) -> Race:
        return Race(self._racedata)

    @race.setter
    def race(self, new: int | Race):
        self._racedata = new

    @property
    def attribute(self) -> Attribute:
        return Attribute(self._attributedata)

    @attribute.setter
    def attribute(self, new: int | Attribute):
        self._attributedata = new

    @property
    def koid(self):
        if self._koiddata is not None and not isnan(self._koiddata):
            return int(self._koiddata)
        return None

    @koid.setter
    def koid(self, new: int):
        self._koiddata = new

    @property
    def ocgdate(self) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(self._ocgdatedata)
        except:
            return datetime.max

    @ocgdate.setter
    def ocgdate(self, new: int | datetime) -> None:
        if isinstance(new, datetime):
            self._ocgdatedata = self._convert_to_timestamp(new)
        elif isinstance(new, int):
            self._ocgdatedata = new

    @property
    def tcgdate(self) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(self._tcgdatedata)
        except:
            return datetime.max

    @tcgdate.setter
    def tcgdate(self, new: int | datetime) -> None:
        if isinstance(new, datetime):
            self._tcgdatedata = self._convert_to_timestamp(new)
        elif isinstance(new, int):
            self._tcgdatedata = new

    def _convert_to_timestamp(self, value: int | datetime) -> int:
        if isinstance(value, int):
            return value
        elif isinstance(value, datetime):
            return int(value.timestamp())
        else:
            raise ValueError("Invalid input. Use int or datetime objects.")

    def _turn_off_flags(self, enum_class):
        for flag in enum_class:
            self._typedata &= ~flag

    def _enum_values(self, value: int, enum_class) -> list:
        return [enum_member for enum_member in enum_class if value & enum_member]

    def has_type(self, type: Type) -> bool:
        return bool(self._typedata & type)

    def has_any_type(self, types: list[Type]) -> bool:
        return any(self.has_type(type) for type in types)

    def has_all_types(self, types: list[Type]) -> bool:
        return all(self.has_type(type) for type in types)

    def has_category(self, category: Category) -> bool:
        return bool(self._categorydata & category)

    def has_any_category(self, categories: list[Category]) -> bool:
        return any(self.has_category(category) for category in categories)

    def has_all_categories(self, categories: list[Category]) -> bool:
        return all(self.has_category(category) for category in categories)

    def has_genre(self, genre: Genre) -> bool:
        return bool(self._genredata & genre)

    def has_any_genre(self, genres: list[Genre]) -> bool:
        return any(self.has_genre(genre) for genre in genres)

    def has_all_genres(self, genres: list[Genre]) -> bool:
        return all(self.has_genre(genre) for genre in genres)

    def has_linkmarker(self, linkmarker: LinkMarker) -> bool:
        if self.has_type(Type.Link):
            return bool(self._defdata & linkmarker)
        return False

    def has_any_linkmarkers(self, linkmarkers: list[LinkMarker]) -> bool:
        if self.has_type(Type.Link):
            return any(self.has_linkmarker(linkmarker) for linkmarker in linkmarkers)
        return False

    def has_all_linkmarkers(self, linkmarkers: list[LinkMarker]) -> bool:
        if self.has_type(Type.Link):
            return all(self.has_linkmarker(linkmarker) for linkmarker in linkmarkers)
        return False

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

    @property
    def has_ability(self) -> bool:
        return any(
            self.has_type(ability)
            for ability in [
                Type.Toon,
                Type.Spirit,
                Type.Union,
                Type.Gemini,
                Type.Spirit,
            ]
        )

    @property
    def is_extradeck(self) -> bool:
        return any(
            self.has_type(edtype)
            for edtype in [
                Type.Fusion,
                Type.Synchro,
                Type.Xyz,
                Type.Link,
            ]
        )

    @property
    def has_property(self) -> bool:
        return any(
            self.has_type(property)
            for property in [
                Type.Ritual,
                Type.QuickPlay,
                Type.Continuous,
                Type.Equip,
                Type.Field,
                Type.Counter,
            ]
        )

    @property
    def has_atk_equ_def(self) -> bool:
        return self.has_type(Type.Monster) and self._atkdata == self._defdata

    @property
    def is_token(self) -> bool:
        return bool(self._typedata & Type.Token)

    @property
    def is_spelltrap(self) -> bool:
        return self.has_any_type([Type.Spell, Type.Trap])

    @property
    def is_trap_monster(self) -> bool:
        return self.has_type(Type.Trap) and self.level != 0

    @property
    def is_dark_synchro(self) -> bool:
        return self.has_category(Category.DarkCard) and self.has_type(Type.Synchro)

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
    def compare_small_world(
        handcard: "Card", deckcard: "Card", addcard: "Card"
    ) -> bool:
        from itertools import pairwise

        return all(
            sum(
                [
                    card1._attributedata == card2._attributedata,
                    card1._racedata == card2._racedata,
                    card1._atkdata == card2._atkdata,
                    card1._defdata == card2._defdata,
                    card1.level == card2.level,
                ]
            )
            == 1
            for card1, card2 in pairwise([handcard, deckcard, addcard])
        )

    def render(self, dir="out"):
        from .cardrenderer import Renderer

        renderer = Renderer()
        return renderer.render_card(self, dir)

    # NOTE: experimental stuff
    # @property
    # def script(self) -> Optional[str]:
    #     if self._script != "":
    #         return self._script

    #     base_url = "https://raw.githubusercontent.com/Fluorohydride/ygopro-scripts/master/c%s.lua"
    #     r = requests.get(base_url % self.id)
    #     if not r.ok:
    #         r = requests.get(base_url % self.alias)
    #     return r.text if r.ok else None

    # @property
    # def trivia(self) -> Optional[str]:
    #     ua = UserAgent()
    #     base_url = "https://yugipedia.com/wiki/Card_Trivia:%s"
    #     card_url = base_url % quote(self.name)
    #     r = requests.get(card_url, headers={"User-Agent": ua.random})
    #     if not r.ok:
    #         return None
    #     soup = BeautifulSoup(r.content, "html.parser")
    #     res = soup.select_one("#mw-content-text > div")
    #     if not res:
    #         return None
    #     div_elements = res.find_all("div")
    #     for div_element in div_elements:
    #         div_element.extract()

    #     return res.text if res else None
