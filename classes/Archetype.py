from dataclasses import dataclass

from .Card import Card


@dataclass
class Archetype:
    name: str
    archetype_cards: list[Card]
    support_cards: list[Card]
    related_cards: list[Card]
