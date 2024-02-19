from dataclasses import dataclass, field


@dataclass()
class Archetype:
    id: int
    name: str
    _members_data: str = ""
    _support_data: str = ""
    _related_data: str = ""

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return f"{self.name}\nMembers: {self.members}\nSupport: {self.support}\nRelated: {self.related}"

    def __contains__(self, card_id: int) -> bool:
        return card_id in self.combined_cards

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "members": self.members,
            "support": self.support,
            "related": self.related,
        }

    @property
    def members(self):
        if not self._members_data:
            return []
        return [int(card_id) for card_id in self._members_data.split(",")]

    @property
    def support(self):
        if not self._support_data:
            return []
        return [int(card_id) for card_id in self._support_data.split(",")]

    @property
    def related(self):
        if not self._related_data:
            return []
        return [int(card_id) for card_id in self._related_data.split(",")]

    @property
    def combined_cards(self) -> list[int]:
        return list(set(self.members + self.support + self.related))
