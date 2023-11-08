import datetime
import sqlite3
from pathlib import Path

import requests
import pandas as pd


class CardDB(object):
    card_types = {1: "Monster", 4: "Trap", 2: "Spell"}
    monster_types = {
        0x1: "Warrior",
        0x2: "Spellcaster",
        0x4: "Fairy",
        0x8: "Fiend",
        0x10: "Zombie",
        0x20: "Machine",
        0x40: "Aqua",
        0x80: "Pyro",
        0x100: "Rock",
        0x200: "WingedBeast",
        0x400: "Plant",
        0x800: "Insect",
        0x1000: "Thunder",
        0x2000: "Dragon",
        0x4000: "Beast",
        0x8000: "BeastWarrior",
        0x10000: "Dinosaur",
        0x20000: "Fish",
        0x40000: "SeaSerpent",
        0x80000: "Reptile",
        0x100000: "Psychic",
        0x200000: "DivineBeast",
        0x400000: "CreatorGod",
        0x800000: "Wyrm",
        0x1000000: "Cyberse",
    }
    last_updated = None

    def __init__(self):
        if not CardDB.can_connect():
            return
        self.search_dict = {}
        self.cards = {}
        self.cards_by_name = {}
        self.archetypes = {}
        self.representors = {}
        self.tcg_date = ""
        self.ocg_date = ""
        con = sqlite3.connect("db/OmegaDB.cdb")
        cursor = con.execute(
            "SELECT * FROM setcodes WHERE (officialcode > 0 AND betacode=officialcode) OR (officialcode=0 AND betacode>0);"
        )
        for row in cursor:
            add = row[0] if row[0] != 0 else row[1]
            if add not in self.archetypes.values():
                self.archetypes[str(row[2])] = add
                if row[3] != 0:
                    self.representors[str(row[2])] = row[3]

        cursor = con.execute(
            "SELECT id,name,setcode,type,race,support,genre,desc FROM datas INNER JOIN texts USING(id);"
        )
        for row in cursor:
            from card import Card

            archetypes = []
            support = []
            related_to = []
            setcode = row[2]
            while setcode > 0:
                code = setcode & 0xFFFF
                for key in self.archetypes:
                    key_code = self.archetypes[key]
                    if (
                        key_code & 0xFFF == code & 0xFFF
                        and key_code & 0xF000 == code & 0xF000
                    ):
                        archetypes.append(key)
                setcode >>= 16
            setcode = [row[5] & 0xFFFFFFFF, row[5] >> 32]
            for c in setcode:
                temp = c
                while temp > 0:
                    code = temp & 0xFFFF
                    for key in self.archetypes:
                        key_code = self.archetypes[key]
                        if (
                            key_code & 0xFFF == code & 0xFFF
                            and key_code & 0xF000 == code & 0xF000
                        ):
                            if c == setcode[0]:
                                support.append(key)
                            else:
                                related_to.append(key)
                            break
                    temp >>= 16
            card_type = ""
            monster_type = ""
            for c_type in CardDB.card_types:
                if row[3] & c_type != 0:
                    card_type = CardDB.card_types[c_type]
                    break
            if card_type == "Monster":
                for m_type in CardDB.monster_types:
                    if row[4] & m_type != 0:
                        monster_type = CardDB.monster_types[m_type]
                        break

            self.cards[row[0]] = Card(
                row[0],
                row[1],
                support,
                archetypes,
                related_to,
                card_type,
                monster_type,
                row[6],
                row[3],
                row[7],
            )
            name = self.cards[row[0]].name.lower()
            if name in self.cards_by_name:
                if self.cards[row[0]].id < self.cards_by_name[name].id:
                    self.cards_by_name[name] = self.cards[row[0]]
            else:
                self.cards_by_name[name] = self.cards[row[0]]
        cursor = con.execute("SELECT * FROM banlists WHERE id<3;")
        for row in cursor:
            if row[0] == 1:
                self.ocg_date = datetime.datetime.strptime(
                    str(row[1])[4:], "%d.%m.%Y"
                ).strftime("%Y-%m-%d")
            if row[0] == 2:
                self.tcg_date = datetime.datetime.strptime(
                    str(row[1])[4:], "%d.%m.%Y"
                ).strftime("%Y-%m-%d")
        self.create_search_dict()
        self.set_data = pd.read_sql_query("SELECT * FROM packs", con)
        self.card_packs = pd.read_sql_query("SELECT * FROM relations", con)
        con.close()

    def get_card(self, id: int):
        if id in self.cards:
            return self.cards[id]
        return None

    @staticmethod
    def can_connect():
        my_file = Path("db/OmegaDB.cdb")
        if not my_file.is_file():
            if not CardDB.latest_db():
                return False
        try:
            con = sqlite3.connect("db/OmegaDB.cdb")
            con.close()
            return True
        except:
            return False

    @staticmethod
    def latest_db():
        from Configs import Config

        CardDB.last_updated = datetime.datetime.utcnow()
        r = requests.get(
            "https://duelistsunite.org/omega/Database.hash", allow_redirects=True
        )
        if r.status_code >= 400:
            return False
        if "database_hash" not in Config.get_data():
            Config.get_data()["database_hash"] = r.text
            Config.save()
            r = requests.get(
                "https://duelistsunite.org/omega/OmegaDB.cdb", allow_redirects=True
            )
            if r.status_code >= 400:
                return False
            with open("db/OmegaDB.cdb", "wb") as f:
                f.write(r.content)
        else:
            if Config.get_data()["database_hash"] != r.text:
                Config.get_data()["database_hash"] = r.text
                Config.save()
                r = requests.get(
                    "https://duelistsunite.org/omega/OmegaDB.cdb", allow_redirects=True
                )
                if r.status_code >= 400:
                    return False
                with open("db/OmegaDB.cdb", "wb") as f:
                    f.write(r.content)
            else:
                return False
        return True

    def create_search_dict(self):
        self.search_dict = {}
        for card in self.cards.values():
            if card.id < 10000:
                continue
            i = 0
            name = card.name.lower()
            no_space = name.replace(" ", "")
            while i < len(no_space):
                word = no_space[i : i + 2]
                if word != "":
                    self.search_dict.setdefault(word, set()).add(name)
                i += 1
            # for word in name.split(" "):
            #     if word == "":
            #         continue
            #     if word[0] not in self.search_dict:
            #         self.search_dict[word[0]] = set()
            #     self.search_dict[word[0]].add(name)

        for key in self.search_dict:
            self.search_dict[key] = sorted(self.search_dict[key])

    def get_names_group(self, name: str):
        ret = None
        name = name.lower().replace(" ", "")
        i = 0
        while i < len(name):
            word = name[i : i + 2]
            if word != "":
                if word in self.search_dict:
                    if ret is None:
                        ret = set()
                    ret.update(self.search_dict[word])
            i += 1
        ret = sorted(ret)
        return ret

    def get_ids_for_names(self, names):
        ret = []
        for name in names:
            card = self.cards_by_name.get(name, None)
            if card:
                ret.append((card.name, card.id))
        return ret
