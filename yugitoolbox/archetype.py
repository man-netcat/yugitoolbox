from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .card import Card
    from .yugidb import YugiDB


@dataclass()
class Archetype:
    id: int
    name: str
    members: list[int] = field(default_factory=list)
    support: list[int] = field(default_factory=list)
    related: list[int] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def combined_cards(self) -> list[int]:
        return list(set(self.members + self.support + self.related))

    def get_cards(self, db: YugiDB) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.members]

    def get_support(self, db: YugiDB) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.support]

    def get_related(self, db: YugiDB) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.related]
