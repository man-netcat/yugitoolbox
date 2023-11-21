from __future__ import annotations

import base64
import zlib
from collections import Counter
from dataclasses import dataclass
from itertools import permutations

from .card import Card
from .carddb import card_db

from .masks import *


@dataclass()
class Deck:
    name: str
    main: list[tuple[Card, int]]
    extra: list[tuple[Card, int]]
    side: list[tuple[Card, int]]

    def __str__(self) -> str:
        reprstr = "Main Deck:\n"
        for card in self.main:
            reprstr += f"{card[0]} x{card[1]}\n"
        reprstr += "\nExtra Deck:\n"
        for card in self.extra:
            reprstr += f"{card[0]} x{card[1]}\n"
        reprstr += "\nSide Deck:\n"
        for card in self.side:
            reprstr += f"{card[0]} x{card[1]}\n"
        return reprstr

    @staticmethod
    def from_omegacode(code: str, name: str = ""):
        def decode_card_tuples(start: int, end: int):
            return [
                (card_db.get_cards_by_value(by="id", value=card_id)[0], count)
                for card_id, count in Counter(
                    int.from_bytes(bytes_arr[i : i + 4], byteorder="little")
                    for i in range(start, end, 4)
                ).items()
            ]

        bytes_arr = zlib.decompress(base64.b64decode(code), -8)
        main_size, side_size = bytes_arr[:2]

        main_extra = decode_card_tuples(2, 2 + 4 * main_size)
        main = [card for card in main_extra if card[0].is_main_deck_monster()]
        extra = [card for card in main_extra if card[0].is_extra_deck_monster()]
        side = decode_card_tuples(2 + 4 * main_size, 2 + 4 * main_size + 4 * side_size)

        return Deck(name, main, extra, side)

    def small_world_triples(self) -> list[tuple[Card, ...]]:
        md_cards = [
            card[0] for card in self.main + self.side if card[0].is_main_deck_monster()
        ]

        valids = [
            triple
            for triple in permutations(md_cards, 3)
            if Card.compare_small_world(*triple)
        ]

        return valids
