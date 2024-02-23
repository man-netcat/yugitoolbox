from .omegadb import OmegaDB
from itertools import product
from .enums import *


def rescue_hedgehog(
    db,
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
