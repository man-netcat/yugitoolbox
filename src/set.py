from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass()
class Set:
    id: int
    name: str
    abbr: str
    _tcgdate: int = 0
    _ocgdate: int = 0
    _contents_data: str = ""

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbr}): {self.contents}"

    def __repr__(self) -> str:
        return self.name

    def __contains__(self, card_id: int) -> bool:
        return card_id in self.contents

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "abbr": self.abbr,
            "contents": self.contents,
        }

    @property
    def contents(self):
        if not self._contents_data:
            return []
        return [int(card_id) for card_id in self._contents_data.split(",")]

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

    @property
    def set_total(self) -> int:
        return len(self._contents_data)
