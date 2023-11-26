from __future__ import annotations

import base64
import zlib
from collections import Counter
from dataclasses import dataclass
from itertools import permutations
from typing import ItemsView

from .archetype import Archetype
from .card import Card


@dataclass()
class Deck:
    name: str
    main: list[tuple[Card, int]]
    extra: list[tuple[Card, int]]
    side: list[tuple[Card, int]]
    isvalid: bool

    def __str__(self) -> str:
        def format_deck_section(
            cards: list[tuple[Card, int]], section_name: str
        ) -> str:
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

    @staticmethod
    def from_omegacode(code: str, name: str = "") -> Deck:
        from yugitoolbox import yugidb

        def decode_card_tuples(start: int, end: int) -> list[tuple[Card, int]]:
            return [
                (yugidb.get_cards_by_value(by="id", value=card_id)[0], count)
                for card_id, count in Counter(
                    int.from_bytes(bytes_arr[i : i + 4], byteorder="little")
                    for i in range(start, end, 4)
                ).items()
            ]

        bytes_arr = zlib.decompress(base64.b64decode(code), -8)
        main_size, side_size = bytes_arr[:2]

        main_extra = decode_card_tuples(2, 2 + 4 * main_size)
        main = [
            (card, count)
            for card, count in main_extra
            if not card.is_extra_deck_monster()
        ]
        extra = [
            (card, count) for card, count in main_extra if card.is_extra_deck_monster()
        ]
        side = decode_card_tuples(2 + 4 * main_size, 2 + 4 * main_size + 4 * side_size)
        isvalid = all(
            [
                sum([count for _, count in main]) >= 40,
                sum([count for _, count in main]) <= 60,
                sum([count for _, count in extra]) <= 15,
                sum([count for _, count in side]) <= 15,
            ]
        ) and all([count <= 3 for _, count in main + extra + side])

        return Deck(name, main, extra, side, isvalid)

    def small_world_triples(self) -> list[tuple[Card, ...]]:
        md_cards = [
            card for card, _ in self.main + self.side if card.is_main_deck_monster()
        ]

        valids = [
            triple
            for triple in permutations(md_cards, 3)
            if Card.compare_small_world(*triple)
        ]

        return valids

    def get_archetype_counts(self) -> ItemsView[Archetype, int]:
        from yugitoolbox import yugidb

        return Counter(
            yugidb.get_archetype_by_id(archid)
            for card, card_count in self.all_cards()
            for archid in card.archetypes * card_count
        ).items()

    def get_archetype_ratios(self) -> list[tuple[Archetype, float]]:
        return [
            (arch, count / self.total_cards() * 100)
            for arch, count in self.get_archetype_counts()
        ]

    def total_main(self) -> int:
        return sum(count for _, count in self.main)

    def total_extra(self) -> int:
        return sum(count for _, count in self.extra)

    def total_side(self) -> int:
        return sum(count for _, count in self.side)

    def all_cards(self) -> list[tuple[Card, int]]:
        return self.main + self.extra + self.side

    def total_cards(self) -> int:
        return sum(count for _, count in self.all_cards())
