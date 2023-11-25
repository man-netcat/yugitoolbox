from dataclasses import dataclass

from .card import Card


@dataclass()
class Archetype:
    id: int
    name: str
    cards: list[Card]
    support: list[Card]
    related: list[Card]

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def combined_cards(self) -> list[Card]:
        return list(set(self.cards + self.support + self.related))
