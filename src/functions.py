from itertools import combinations, product

from .card import Card
from .enums import *
from .omegadb import YugiDB


def rescue_hedgehog(
    db: YugiDB,
    level: str = None,
    include_ocg_only=False,
    include_tcg_only=False,
):

    status = "3"
    if include_ocg_only:
        status += "|1"
    if include_tcg_only:
        status += "|2"

    normals = db.get_cards_by_values(
        {
            "type": "monster,normal,~fusion,~synchro,~xyz,~link,~ritual,~token",
            "level": "<=3" if level is None else level,
            "category": "~rushcard",
            "status": status,
        }
    )
    effects = db.get_cards_by_values(
        {
            "type": "monster,effect,~fusion,~synchro,~xyz,~link,~ritual,~token",
            "level": "<=3" if level is None else level,
            "category": "~rushcard",
            "status": status,
        }
    )

    pairs = [
        (normal, effect)
        for normal, effect in product(normals, effects)
        if all(
            [
                normal.level == effect.level,
                normal.race == effect.race,
                normal.attribute == effect.attribute,
            ]
        )
    ]
    return pairs


def numbers_eveil(db: YugiDB, fifth: int):
    def extract_integer(string):
        import re

        match = re.search(r"Number\s+i?[CSF]?(\d+)", string)
        if match:
            return int(match.group(1))
        return None

    number_monsters = db.get_cards_by_values(
        {
            "in_name": "Number,~Number XX,~Number ic1000,~Number C1000",
            "type": "xyz",
        }
    )

    mapping = {card: extract_integer(card.name) for card in number_monsters}

    combos = [
        combo
        for combo in combinations(number_monsters, 4)
        if (
            sum([mapping[card] for card in combo]) == fifth
            and len(set([card.level for card in combo])) == 4
        )
    ]

    return combos


def duality(db: YugiDB, card: Card):
    if not card.attribute in [Attribute.DARK, Attribute.LIGHT]:
        return []

    targets = db.get_cards_by_values(
        {
            "race": card.race,
            "level": card.level,
            "attribute": Attribute(0x30 - card.attribute),
        }
    )

    return targets
