from __future__ import annotations

import base64
import zlib
from collections import Counter
from dataclasses import dataclass
from itertools import permutations
from typing import TYPE_CHECKING, ItemsView

if TYPE_CHECKING:
    from .archetype import Archetype
    from .card import Card
    from .yugidb import YugiDB


@dataclass()
class Deck:
    name: str
    main: list[tuple[int, int]]
    extra: list[tuple[int, int]]
    side: list[tuple[int, int]]

    def __str__(self) -> str:
        def format_deck_section(cards: list[tuple[int, int]], section_name: str) -> str:
            return (
                f"{section_name} ({sum([count for _, count in cards])} cards):\n"
                + "\n".join([f"  {card} x{count}" for card, count in cards])
            )

        main_str = format_deck_section(self.main, "Main Deck")
        extra_str = format_deck_section(self.extra, "Extra Deck")
        side_str = format_deck_section(self.side, "Side Deck")

        return "\n\n".join([main_str, extra_str, side_str])

    def __repr__(self) -> str:
        return self.name if self.name else "Anonymous Deck"

    def is_valid(self) -> bool:
        return all(
            [
                sum([count for _, count in self.main]) >= 40,
                sum([count for _, count in self.main]) <= 60,
                sum([count for _, count in self.extra]) <= 15,
                sum([count for _, count in self.side]) <= 15,
            ]
        ) and all([count <= 3 for _, count in self.main + self.extra + self.side])

    @staticmethod
    def from_omegacode(db: YugiDB, code: str, name: str = "") -> Deck:
        def decode_card_tuples(start: int, end: int) -> list[tuple[int, int]]:
            return [
                (card_id, count)
                for card_id, count in Counter(
                    int.from_bytes(bytes_arr[i : i + 4], byteorder="little")
                    for i in range(start, end, 4)
                ).items()
            ]

        bytes_arr = zlib.decompress(base64.b64decode(code), -8)
        main_size, side_size = bytes_arr[:2]

        main_extra = decode_card_tuples(2, 2 + 4 * main_size)
        main = [
            (card_id, count)
            for card_id, count in main_extra
            if not db.get_card_by_id(card_id).is_extra_deck_monster
        ]
        extra = [
            (card_id, count)
            for card_id, count in main_extra
            if db.get_card_by_id(card_id).is_extra_deck_monster
        ]
        side = decode_card_tuples(2 + 4 * main_size, 2 + 4 * main_size + 4 * side_size)
        return Deck(name, main, extra, side)

    def to_omegacode(self):
        return base64.b64encode(
            zlib.compress(
                bytearray([self.total_main() + self.total_extra(), self.total_side()])
                + b"".join(
                    card_id.to_bytes(4, byteorder="big") * count
                    for card_id, count in self.main + self.extra + self.side
                ),
                wbits=-15,
            )
        ).decode()

    @staticmethod
    def from_ydke(db: YugiDB, ydke: str, name: str = "") -> Deck:
        def decode_component(component: str) -> list[tuple[int, int]]:
            passcodes_bytes = base64.b64decode(component)
            passcodes = [
                int.from_bytes(passcodes_bytes[i : i + 4], byteorder="little")
                for i in range(0, len(passcodes_bytes), 4)
            ]
            card_counts = Counter(passcodes)
            return [(card_id, count) for card_id, count in card_counts.items()]

        main, extra, side = map(decode_component, ydke[len("ydke://") :].split("!")[:3])

        return Deck(name, main, extra, side)

    def to_ydke(self) -> str:
        def encode_component(cards: list[tuple[int, int]]) -> str:
            return base64.b64encode(
                b"".join(
                    card_id.to_bytes(4, byteorder="little") * count
                    for card_id, count in cards
                )
            ).decode()

        return (
            "ydke://"
            + "!".join(map(encode_component, [self.main, self.extra, self.side]))
            + "!"
        )

    def small_world_triples(self, db: YugiDB) -> list[tuple[int, ...]]:
        md_cards = [
            card_id
            for card_id, _ in self.main + self.side
            if db.get_card_by_id(card_id).is_main_deck_monster
        ]

        valids = [
            (triple)
            for triple in permutations(md_cards, 3)
            if Card.compare_small_world(
                *[db.get_card_by_id(card_id) for card_id in triple]
            )
        ]

        return valids

    def get_archetype_counts(self, db: YugiDB) -> ItemsView[Archetype, int]:
        return Counter(
            db.get_archetype_by_id(archid)
            for card_id, card_count in self.all_cards()
            for archid in db.get_card_by_id(card_id).archetypes * card_count
        ).items()

    def get_archetype_ratios(self, db: YugiDB) -> list[tuple[Archetype, float]]:
        return [
            (arch, count / self.total_cards() * 100)
            for arch, count in self.get_archetype_counts(db)
        ]

    def total_main(self) -> int:
        return sum(count for _, count in self.main)

    def total_extra(self) -> int:
        return sum(count for _, count in self.extra)

    def total_side(self) -> int:
        return sum(count for _, count in self.side)

    def all_cards(self) -> list[tuple[int, int]]:
        return self.main + self.extra + self.side

    def total_cards(self) -> int:
        return sum(count for _, count in self.all_cards())
