import base64
import zlib
from collections import Counter
from dataclasses import dataclass

from .Card import Card
from .CardDB import carddb


@dataclass(frozen=True)
class Deck:
    name: str
    main: list[tuple[Card, int]]
    side: list[tuple[Card, int]]

    @staticmethod
    def from_omegacode(code, name: str = ""):
        def decode_card_tuples(start, end):
            return [
                (carddb.get_cards_by_field(by="id", value=card_id)[0], count)
                for card_id, count in Counter(
                    int.from_bytes(bytes_arr[i : i + 4], byteorder="little")
                    for i in range(start, end, 4)
                ).items()
            ]

        bytes_arr = zlib.decompress(base64.b64decode(code), -8)
        main_size, side_size = bytes_arr[:2]

        main = decode_card_tuples(2, 2 + 4 * main_size)
        side = decode_card_tuples(2 + 4 * main_size, 2 + 4 * main_size + 4 * side_size)

        return Deck(name, main, side)
