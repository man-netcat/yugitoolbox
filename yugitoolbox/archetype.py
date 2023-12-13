from dataclasses import dataclass, field


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

    @property
    def combined_cards(self) -> list[int]:
        return list(set(self.members + self.support + self.related))
