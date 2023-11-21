from dataclasses import dataclass


@dataclass()
class Archetype:
    name: str
    cards: list[str]
    support: list[str]
    related: list[str]

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return self.name
