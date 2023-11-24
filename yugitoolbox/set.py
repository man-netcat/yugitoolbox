from collections import Counter
from dataclasses import dataclass
from typing import ItemsView

from .archetype import Archetype
from .card import Card


@dataclass()
class Set:
    id: int
    name: str
    abbr: str
    tcgdate: int
    ocgdate: int
    contents: list[Card]

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbr}): {self.contents}"

    def __repr__(self) -> str:
        return self.name

    def get_archetype_counts(self) -> ItemsView[Archetype, int]:
        from yugitoolbox import yugidb

        return Counter(
            yugidb.get_archetype_by_id(archid)
            for card in self.contents
            for archid in set(card.archetypes + card.support)
        ).items()

    def get_archetype_ratios(self) -> list[tuple[Archetype, float]]:
        return [
            (archid, count / self.set_total() * 100)
            for archid, count in self.get_archetype_counts()
        ]

    def set_total(self) -> int:
        return len(self.contents)
