from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .card import Card


@dataclass()
class Archetype:
    id: int
    name: str
    cards: list[int]
    support: list[int]
    related: list[int]

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def combined_cards(self) -> list[int]:
        return list(set(self.cards + self.support + self.related))

    def get_cards(self, db) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.cards]

    def get_support(self, db) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.support]

    def get_related(self, db) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.related]
