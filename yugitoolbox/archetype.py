from dataclasses import dataclass

from .card import Card


@dataclass()
class Archetype:
    id: str
    name: str
    cards: list[Card]
    support: list[Card]
    related: list[Card]

    def __hash__(self):
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name
