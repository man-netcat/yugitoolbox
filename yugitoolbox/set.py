from dataclasses import dataclass


@dataclass()
class Set:
    name: str
    abbr: str
    tcgdate: int
    ocgdate: int
    contents: list[str]

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return self.name
