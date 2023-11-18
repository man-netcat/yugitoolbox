from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    name: str
    id: int
    type: list[str]
    race: list[str]
    attribute: list[str]
    category: list[str]
    level: int
    scale: int
    atk: int
    def_: int
    linkmarkers: list[str]
    text: str
    archetypes: list[str]
    support: list[str]
    related: list[str]
    ot: int

    def has_atk_equ_def(self) -> bool:
        return "Monster" in self.type and self.atk == self.def_

    def is_trap_monster(self) -> bool:
        return "Trap" in self.type and self.level != 0

    def is_dark_synchro(self) -> bool:
        return "DarkCard" in self.category and "Synchro" in self.type

    def is_rush_maximum(self) -> bool:
        return "RushMax" in self.category

    def is_rush_legendary(self) -> bool:
        return "RushLegendary" in self.category

    def is_rush(self) -> bool:
        return (
            "RushCard" in self.category
            or self.is_rush_legendary()
            or self.is_rush_maximum()
        )

    def is_ocg_only(self) -> bool:
        return self.ot == 1

    def is_tcg_only(self) -> bool:
        return self.ot == 2

    def is_legal(self) -> bool:
        return self.ot == 3

    def is_illegal(self) -> bool:
        return self.ot == 4

    def is_beta(self) -> bool:
        return "BetaCard" in self.category

    def is_skill_card(self) -> bool:
        return "SkillCard" in self.category

    def is_god_card(self) -> bool:
        return any([x in self.category for x in ["RedGod", "BlueGod", "YellowGod"]])

    def is_pre_errata(self) -> bool:
        return "PreErrata" in self.category

    def is_extra_deck_monster(self) -> bool:
        return any(
            [x in self.type for x in ["Synchro", "Token", "Xyz", "Link", "Fusion"]]
        )

    def is_main_deck_monster(self) -> bool:
        return "Monster" in self.type and not self.is_extra_deck_monster()
