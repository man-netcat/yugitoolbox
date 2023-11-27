from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, ItemsView

if TYPE_CHECKING:
    from .archetype import Archetype
    from .card import Card
    from .yugidb import YugiDB


@dataclass()
class Set:
    id: int
    name: str
    abbr: str
    tcgdate: int
    ocgdate: int
    contents: list[int]
    db: YugiDB

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbr}): {self.contents}"

    def __repr__(self) -> str:
        return self.name

    def get_cards(self) -> list[Card]:
        return [self.db.get_card_by_id(id) for id in self.contents]

    def get_archetype_counts(self) -> ItemsView[Archetype, int]:
        return Counter(
            self.db.get_archetype_by_id(archid)
            for card in self.db.get_cards_by_ids(self.contents)
            for archid in set(card.archetypes + card.support)
        ).items()

    def get_archetype_ratios(self) -> list[tuple[Archetype, float]]:
        return [
            (archid, count / self.set_total() * 100)
            for archid, count in self.get_archetype_counts()
        ]

    def set_total(self) -> int:
        return len(self.contents)
