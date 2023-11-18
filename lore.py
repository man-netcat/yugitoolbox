import json

import pandas as pd

from classes.CardDB import carddb

with open("../data/lores.json", "r") as lore_file:
    lores = json.load(lore_file)

with open("../data/sets.txt") as set_file:
    set_names = set_file.read().splitlines()

with pd.ExcelWriter("out/lore.xlsx", engine="xlsxwriter") as writer:
    for lore in lores:
        cards = carddb.related_cards(lore["archetypes"], lore["cards"])
        card_ids = [card.id for card in cards]
