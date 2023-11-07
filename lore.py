from Configs import *
import pandas as pd

db = Config.cards_db()
db.latest_db()

import json

with open("data/lores.json", "r") as lore_file:
    lores = json.load(lore_file)

with open("data/sets.txt") as set_file:
    set_names = set_file.read().splitlines()

# archetypes = set()
# for card in db.cards.values():
#     for archetype in card.archetypes:
#         archetypes.add(archetype)

# print(archetypes)

with pd.ExcelWriter("out/lore.xlsx", engine="xlsxwriter") as writer:
    for lore in lores:
        card_ids = []
        for card in db.cards.values():
            if any(
                any(
                    archetype in archetypes
                    for archetypes in [card.related_to, card.support, card.archetypes]
                )
                for archetype in lore["archetypes"]
            ) or any(card_name in card.text for card_name in lore["cards"]):
                card_ids.append(card.id)

        df = db.card_packs[db.card_packs["cardid"].isin(card_ids)]
        df = df.merge(db.set_data, left_on="packid", right_on="id", how="left")
        df = df[["cardid", "abbr", "name"]]
        df = df[df["name"].isin(set_names)].reset_index(drop=True)
        df["name"] = pd.Categorical(df["name"], categories=set_names, ordered=True)
        df = df.sort_values(by="name")
        df["cardname"] = [db.get_card(id).name for id in df["cardid"]]
        df = df[~df.duplicated(subset="cardname", keep="first")]
        df = df[["cardid", "cardname", "abbr"]]
        df = df.reset_index(drop=True)

        df.to_excel(writer, sheet_name=lore["name"], index=False)
