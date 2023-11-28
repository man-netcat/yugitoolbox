from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .enums import OT, Attribute, Category, Genre, LinkMarker, Race, Type

if TYPE_CHECKING:
    from .archetype import Archetype
    from .set import Set
    from .yugidb import YugiDB


@dataclass()
class Card:
    id: int
    name: str
    type: list[Type]
    race: Race
    attribute: Attribute
    category: list[Category]
    genre: list[Genre]
    level: int
    lscale: int
    rscale: int
    atk: int
    def_: int
    linkmarkers: list[LinkMarker]
    text: str
    archetypes: list[int]
    support: list[int]
    related: list[int]
    sets: list[int]
    tcgdate: datetime | None
    ocgdate: datetime | None
    ot: int
    archcode: int
    supportcode: int
    alias: int
    scripted: bool
    script: str
    koid: int

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        if Type.Monster in self.type:
            return f"{self.name} ({self.id}): {self._levelstr()} {self.get_attr()} {self.get_race()} {' '.join(reversed([type.name for type in self.type]))}"
        else:
            return f"{self.name} ({self.id}): {'Normal ' if len(self.type) == 1 else ''}{' '.join(reversed([type.name for type in self.type]))}"

    def __repr__(self) -> str:
        return self.name

    def _levelstr(self) -> str:
        return (
            "Rank "
            if Type.Xyz in self.type
            else "Link "
            if Type.Link in self.type
            else "Level "
        ) + (str(self.level) if self.level >= 0 else "?")

    def get_race(self) -> str:
        return self.race.name

    def get_attr(self) -> str:
        return self.attribute.name

    def get_types(self) -> list[str]:
        return [type.name for type in self.type]

    def get_categories(self) -> list[str]:
        return [category.name for category in self.category]

    def get_archetypes(self, db: YugiDB) -> list[Archetype]:
        return [db.get_archetype_by_id(id) for id in self.archetypes]

    def get_support(self, db: YugiDB) -> list[Archetype]:
        return [db.get_archetype_by_id(id) for id in self.support]

    def get_related(self, db: YugiDB) -> list[Archetype]:
        return [db.get_archetype_by_id(id) for id in self.related]

    def get_sets(self, db: YugiDB) -> list["Set"]:
        return [db.get_set_by_id(id) for id in self.sets]

    def get_linkmarkers(self) -> list[str]:
        return [marker.name for marker in self.linkmarkers]

    def has_atk_equ_def(self) -> bool:
        return Type.Monster in self.type and self.atk == self.def_

    def is_trap_monster(self) -> bool:
        return Type.Trap in self.type and self.level != 0

    def is_dark_synchro(self) -> bool:
        return Category.DarkCard in self.category and Type.Synchro in self.type

    def is_rush_maximum(self) -> bool:
        return Category.RushMax in self.category

    def is_rush_legendary(self) -> bool:
        return Category.RushLegendary in self.category

    def is_rush(self) -> bool:
        return (
            Category.RushCard in self.category
            or self.is_rush_legendary()
            or self.is_rush_maximum()
        )

    def is_beta(self) -> bool:
        return Category.BetaCard in self.category

    def is_skill_card(self) -> bool:
        return Category.SkillCard in self.category

    def is_god_card(self) -> bool:
        return any(
            [
                x in self.category
                for x in [
                    Category.RedGod,
                    Category.BlueGod,
                    Category.YellowGod,
                ]
            ]
        )

    def is_pre_errata(self) -> bool:
        return Category.PreErrata in self.category

    def is_extra_deck_monster(self) -> bool:
        return any(
            [
                x in self.type
                for x in [
                    Type.Synchro,
                    Type.Token,
                    Type.Xyz,
                    Type.Link,
                    Type.Fusion,
                ]
            ]
        )

    def is_main_deck_monster(self) -> bool:
        return Type.Monster in self.type and not self.is_extra_deck_monster()

    @staticmethod
    def compare_small_world(handcard: Card, deckcard: Card, addcard: Card) -> bool:
        return all(
            [
                sum(
                    [
                        card1.attribute == card2.attribute,
                        card1.race == card2.race,
                        card1.atk == card2.atk,
                        card1.def_ == card2.def_,
                        card1.level == card2.level,
                    ]
                )
                == 1
                for card1, card2 in zip([handcard, deckcard], [deckcard, addcard])
            ]
        )

    def combined_archetypes(self) -> list[int]:
        return list(set(self.archetypes + self.support + self.related))

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
        konami_rush_db_base_url = "https://www.db.yugioh-card.com/rushdb/card_search.action?ope=2&cid=%s&request_locale=ja"
        konami_rush_faq_base_url = "https://www.db.yugioh-card.com/rushdb/faq_search.action?ope=4&cid=%s&request_locale=ja"
        konami_db_base_url = "https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=%s&request_locale=%s"
        ygorganisation_base_url = "https://db.ygorganization.com/card#%s:%s"

        if self.koid:
            if self.is_rush():
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
