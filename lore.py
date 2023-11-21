import json
from typing import Any

import pandas as pd

from yugitoolbox import card_db


def collect_lore_data(lore: dict[str, Any], set_names: list[str]):
    cards = card_db.related_cards(lore["archetypes"], lore["cards"])
    data = [
        {
            "id": card.id,
            "name": card.name,
            "set": min(
                [card_db.get_set_by_name(set) for set in card.sets if set in set_names],
                key=lambda x: x.tcgdate,
            ),
        }
        for card in cards
        if len([set for set in card.sets if set in set_names]) > 0
    ]
    data_sorted = sorted(data, key=lambda x: x["set"].tcgdate)
    for card in data_sorted:
        card["set"] = card["set"].abbr
    return data_sorted


def main():
    with open("data/lores.json", "r") as lore_file:
        lores: list[dict[str, Any]] = json.load(lore_file)

    with open("data/sets.txt") as set_file:
        set_names = set_file.read().splitlines()

    with pd.ExcelWriter("out/lore.xlsx", engine="xlsxwriter") as writer:
        for lore in lores:
            data = collect_lore_data(lore, set_names)
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=lore["name"], index=False)


if __name__ == "__main__":
    main()
