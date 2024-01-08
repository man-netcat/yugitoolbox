from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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

    def __contains__(self, card_id: int) -> bool:
        return card_id in self.contents

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
        return len(self.contents)
