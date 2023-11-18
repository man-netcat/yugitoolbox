import base64
import zlib
from collections import Counter
from dataclasses import dataclass
from itertools import permutations

from .Card import Card
from .CardDB import carddb


@dataclass(frozen=True)
class Deck:
    name: str
    main: list[tuple[Card, int]]
    side: list[tuple[Card, int]]

    def __str__(self) -> str:
        reprstr = "Main/Extra Deck:\n"
        for card in self.main:
            reprstr += f"{card[0]} x{card[1]}\n"
        reprstr += "\nSide Deck:\n"
        for card in self.side:
            reprstr += f"{card[0]} x{card[1]}\n"
        return reprstr

    @staticmethod
    def from_omegacode(code: str, name: str = ""):
        """
        Creates a Deck instance from an Omega Code.

        Parameters:
        - code (str): The Omega Code representing the deck.
        - name (str): Optional name for the deck (default is an empty string).

        Returns:
        - Deck: A Deck instance created from the Omega Code.
        """

        def decode_card_tuples(start: int, end: int):
            """
            Decodes card tuples from a range of bytes.

            Parameters:
            - start (int): The starting index of the byte range.
            - end (int): The ending index of the byte range.

            Returns:
            - List[Tuple[Card, int]]: List of tuples containing cards and their counts.
            """
            return [
                (carddb.get_cards_by_value(by="id", value=card_id)[0], count)
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

    def small_world_triples(self) -> list[tuple[Card, ...]]:
        """
        Generates valid triples of cards for the Small World strategy.

        Returns:
        - list[tuple[Card, ...]]: List of tuples containing triples of cards that satisfy the Small World strategy.
        """
        md_cards = [
            card[0] for card in self.main + self.side if card[0].is_main_deck_monster()
        ]

        valids = [
            triple
            for triple in permutations(md_cards, 3)
            if Card.compare_small_world(*triple)
        ]

        return valids
