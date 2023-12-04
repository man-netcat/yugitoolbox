from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
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
    tcgdate: int = 0
    ocgdate: int = 0
    contents: list[int] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbr}): {self.contents}"

    def __repr__(self) -> str:
        return self.name

    def get_cards(self, db: YugiDB) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.contents]

    def get_archetype_counts(self, db: YugiDB) -> ItemsView[Archetype, int]:
        return Counter(
            db.get_archetype_by_id(archid)
            for card in db.get_cards_by_ids(self.contents)
            for archid in set(card.archetypes + card.support)
        ).items()

    def get_archetype_ratios(self, db: YugiDB) -> list[tuple[Archetype, float]]:
        return [
            (archid, count / self.set_total() * 100)
            for archid, count in self.get_archetype_counts(db)
        ]

    def set_total(self) -> int:
        return len(self.contents)
