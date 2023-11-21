from itertools import combinations

from yugitoolbox import Card, card_db


def numbers_eveil(card: Card):
    if "Number" not in card.name and "Xyz" not in card.type:
        raise RuntimeError("Card isn't a Number Xyz monster.")

    def extract_number_value(card: Card):
        return int("".join(filter(str.isdigit, card.name)))

    number_value = extract_number_value(card)
    number_xyz_cards = sorted(
        [
            card
            for card in card_db.get_cards_by_value("type", "Xyz")
            if "Number" in card.name and not "XX" in card.name
        ],
        key=lambda x: x.name,
    )

    return [
        combo
        for combo in combinations(number_xyz_cards, 4)
        if len(set(card.level for card in combo)) == 4
        and sum(extract_number_value(card) for card in combo) == number_value
    ]


def main():
    for combo in numbers_eveil(card_db.get_card_by_id(90126061)):
        print([card.name for card in combo])


if __name__ == "__main__":
    main()
