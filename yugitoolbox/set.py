from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, ItemsView, Optional

if TYPE_CHECKING:
    from .archetype import Archetype
    from .card import Card
    from .yugidb import YugiDB


@dataclass()
class Set:
    id: int
    name: str
    abbr: str
    _tcgdate: int = 0
    _ocgdate: int = 0
    contents: list[int] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbr}): {self.contents}"

    def __repr__(self) -> str:
        return self.name

    @property
    def ocgdate(self) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(self._ocgdate)
        except:
            return datetime.max

    @ocgdate.setter
    def ocgdate(self, value: int | datetime) -> None:
        self._ocgdate = self._convert_to_timestamp(value)

    @property
    def tcgdate(self) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(self._tcgdate)
        except:
            return datetime.max

    @tcgdate.setter
    def tcgdate(self, value: int | datetime) -> None:
        self._tcgdate = self._convert_to_timestamp(value)

    def _convert_to_timestamp(self, value: int | datetime) -> int:
        if isinstance(value, int):
            return value
        elif isinstance(value, datetime):
            return int(value.timestamp())
        else:
            raise ValueError("Invalid input. Use int or datetime objects.")

    def get_cards(self, db: YugiDB) -> list[Card]:
        return [db.get_card_by_id(id) for id in self.contents]

    def get_archetype_counts(self, db: YugiDB) -> ItemsView[Archetype, int]:
        return Counter(
            db.get_archetype_by_id(archid)
            for card in db.get_cards_by_ids(self.contents)
            for archid in set(card.archetypes + card.support)
        ).items()

    def get_archetype_ratios(self, db: YugiDB) -> list[tuple[Archetype, float]]:
        return [
            (archid, count / self.set_total() * 100)
            for archid, count in self.get_archetype_counts(db)
        ]

    def set_total(self) -> int:
        return len(self.contents)
