from collections import Counter
from dataclasses import dataclass

from .card import Card


@dataclass()
class Set:
    name: str
    abbr: str
    tcgdate: int
    ocgdate: int
    contents: list[Card]

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbr}): {self.contents}"

    def __repr__(self) -> str:
        return self.name

    def get_archetype_counts(self) -> list[tuple[str, int]]:
        return list(
            Counter(arch for card in self.contents for arch in card.archetypes).items()
        )

    def get_archetype_ratios(self) -> list[tuple[str, float]]:
        return [
            (arch, count / self.set_total() * 100)
            for arch, count in self.get_archetype_counts()
        ]

    def set_total(self) -> int:
        return len(self.contents)
