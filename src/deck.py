from __future__ import annotations

import base64
import zlib
from collections import Counter
from dataclasses import dataclass
from itertools import permutations
from typing import TYPE_CHECKING, ItemsView

from .enums import *

if TYPE_CHECKING:
    from .archetype import Archetype
    from .card import Card
    from .yugidb import YugiDB


MAIN_DECK_MIN_SIZE = 40
MAIN_DECK_MAX_SIZE = 60
EXTRA_DECK_MAX_SIZE = 15
SIDE_DECK_MAX_SIZE = 15


@dataclass()
class Deck:
    name: str
    main: list[tuple[Card, int]]
    extra: list[tuple[Card, int]]
    side: list[tuple[Card, int]]
    cover_card: int = 0

    def __str__(self) -> str:
        main_str = self._format_deck_section(self.main, "Main Deck")
        extra_str = self._format_deck_section(self.extra, "Extra Deck")
        side_str = self._format_deck_section(self.side, "Side Deck")

        return "\n\n".join([main_str, extra_str, side_str])

    def _format_deck_section(
        self, cards: list[tuple[Card, int]], section_name: str
    ) -> str:
        return (
            f"{section_name} ({sum([count for _, count in cards])} cards):\n"
            + "\n".join([f"  {card.name} x{count}" for card, count in cards])
        )

    def __repr__(self) -> str:
        return self.name if self.name else "Anonymous Deck"

    @property
    def is_valid(self) -> bool:
        main_size = sum(count for _, count in self.main)
        side_size = sum(count for _, count in self.side)
        extra_size = sum(count for _, count in self.extra)

        valid_main = MAIN_DECK_MIN_SIZE <= main_size <= MAIN_DECK_MAX_SIZE
        valid_extra = extra_size <= EXTRA_DECK_MAX_SIZE
        valid_side = side_size <= SIDE_DECK_MAX_SIZE

        count_valid = all(count <= 3 for _, count in self.main + self.extra + self.side)

        return valid_main and valid_extra and valid_side and count_valid

    @classmethod
    def from_omegacode(cls, db: YugiDB, code: str, name: str = ""):
        def decode_card_tuples(start, end):
            return [
                (db.get_card_by_id(card_id), count)
                for card_id, count in Counter(
                    int.from_bytes(bytes_arr[i : i + 4], byteorder="little")
                    for i in range(start, end, 4)
                ).items()
            ]

        bytes_arr = zlib.decompress(base64.b64decode(code), -8)
        deck_offset = 2
        main_size, side_size = bytes_arr[:deck_offset]

        side_offset = 2 + 4 * main_size
        main_extra = decode_card_tuples(deck_offset, side_offset)
        main = [(card, count) for card, count in main_extra if not card.is_extradeck]
        extra = [(card, count) for card, count in main_extra if card.is_extradeck]

        cover_offset = 2 + 4 * main_size + 4 * side_size
        side = decode_card_tuples(side_offset, cover_offset)
        cover_card = int.from_bytes(
            bytes_arr[cover_offset : cover_offset + 4],
            byteorder="little",
        )

        return cls(name, main, extra, side, cover_card)

    @property
    def omega_code(self):
        return base64.b64encode(
            zlib.compress(
                bytearray([self.total_main + self.total_extra, self.total_side])
                + b"".join(
                    card.id.to_bytes(4, byteorder="little") * count
                    for card, count in self.main + self.extra + self.side
                )
                + self.cover_card.to_bytes(4, byteorder="little"),
                wbits=-15,
            )
        ).decode()

    @classmethod
    def from_ydke(cls, db: YugiDB, ydke: str, name: str = ""):
        def decode_component(component):
            passcodes_bytes = base64.b64decode(component)
            passcodes = [
                int.from_bytes(passcodes_bytes[i : i + 4], byteorder="little")
                for i in range(0, len(passcodes_bytes), 4)
            ]
            card_counts = Counter(passcodes)
            return [
                (db.get_card_by_id(card_id), count)
                for card_id, count in card_counts.items()
            ]

        main, extra, side = map(decode_component, ydke[len("ydke://") :].split("!")[:3])

        return cls(name, main, extra, side)

    @property
    def ydke_code(self) -> str:
        def encode_component(cards: list[tuple[Card, int]]) -> str:
            return base64.b64encode(
                b"".join(
                    card.id.to_bytes(4, byteorder="little") * count
                    for card, count in cards
                )
            ).decode()

        return (
            "ydke://"
            + "!".join(map(encode_component, [self.main, self.extra, self.side]))
            + "!"
        )

    def small_world_triples(self) -> list[tuple[Card, Card, Card]]:
        md_cards = [card for card, _ in self.main + self.side if not card.is_extradeck]

        valids = [
            triple
            for triple in permutations(md_cards, 3)
            if Card.compare_small_world(*triple)
        ]

        return valids

    def get_archetype_counts(self, db: YugiDB) -> ItemsView[Archetype, int]:
        return Counter(
            db.get_archetype_by_id(archid)
            for card, card_count in self.all_cards
            for archid in card.archetypes * card_count
        ).items()

    def get_archetype_ratios(self, db: YugiDB) -> list[tuple[Archetype, float]]:
        return [
            (arch, count / self.total_cards * 100)
            for arch, count in self.get_archetype_counts(db)
        ]

    @property
    def total_main(self) -> int:
        return sum(count for _, count in self.main)

    @property
    def total_extra(self) -> int:
        return sum(count for _, count in self.extra)

    @property
    def total_side(self) -> int:
        return sum(count for _, count in self.side)

    @property
    def all_cards(self) -> list[tuple[Card, int]]:
        return self.main + self.extra + self.side

    @property
    def total_cards(self) -> int:
        return sum(count for _, count in self.all_cards)
