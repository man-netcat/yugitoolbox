import pandas as pd
from card_db import CardDB

db = CardDB()

import json

with open("data/lores.json", "r") as lore_file:
    lores = json.load(lore_file)

with open("data/sets.txt") as set_file:
    set_names = set_file.read().splitlines()

with pd.ExcelWriter("out/lore.xlsx", engine="xlsxwriter") as writer:
    for lore in lores:
        cards = db.related_cards(lore["archetypes"], lore["cards"])
        card_ids = [card.id for card in cards]
        df = db.card_packs[db.card_packs["cardid"].isin(card_ids)]
        df = df.merge(db.set_data, left_on="packid", right_on="id", how="left")
        df = df[df["name"].isin(set_names)]
        df["name"] = pd.Categorical(df["name"], categories=set_names, ordered=True)
        df["cardname"] = [
            db.get_cards(by="id", value=id)[0].name for id in df["cardid"]
        ]
        df = df.sort_values(by=["name", "cardname"])
        df = df[~df.duplicated(subset="cardname", keep="first")]
        df = df[["cardid", "cardname", "abbr"]]
        df = df.reset_index(drop=True)

        df.to_excel(writer, sheet_name=lore["name"], index=False)
