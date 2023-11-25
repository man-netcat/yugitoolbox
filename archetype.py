from dataclasses import dataclass


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
