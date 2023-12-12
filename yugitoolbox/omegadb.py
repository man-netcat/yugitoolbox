from __future__ import annotations

import os

import pandas as pd
import requests

from .archetype import Archetype
from .card import Card
from .set import Set
from .yugidb import YugiDB

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"


class OmegaDB(YugiDB):
    initialised = False

    def __init__(
        self,
        skip_update: bool = False,
        force_update: bool = False,
        rebuild_pkl: bool = False,
    ):
        self.name = "OmegaDB"
        self.dbpath = "db/omega/omega.db"
        downloaded = False
        if not OmegaDB.initialised:
            if not skip_update:
                downloaded = self._download_omegadb(force_update)
            OmegaDB.initialised = True
        super().__init__(rebuild_pkl=rebuild_pkl or downloaded)

    def _download_omegadb(self, force_update: bool = False):
        def download(url: str, path: str):
            r = requests.get(url, allow_redirects=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)

        db_url = os.path.join(OMEGA_BASE_URL, "OmegaDB.cdb")
        hash_url = os.path.join(OMEGA_BASE_URL, "Database.hash")
        dbdir = os.path.dirname(self.dbpath)
        hashpath = os.path.join(dbdir, "omega.hash")

        if not os.path.exists(dbdir):
            os.makedirs(dbdir)

        if os.path.exists(self.dbpath) and not force_update:
            if os.path.exists(hashpath):
                with open(hashpath) as f:
                    old_hash = f.read()
            else:
                old_hash = None

            try:
                download(hash_url, hashpath)
            except requests.ConnectionError:
                print("Failed to get current Hash, skipping update.")
                return False

            with open(hashpath) as f:
                new_hash = f.read()

            if old_hash == new_hash:
                return False
            else:
                print("A new version of the Omega database is available.")
                user_response = input(
                    "Do you want to update the database? (y/n): "
                ).lower()
                if user_response != "y":
                    print("Skipping database update.")
                    return False

        print("Downloading up-to-date db...")
        download(db_url, self.dbpath)
        download(hash_url, hashpath)
        return True

    def _build_card_db(self, con):
        values = ",".join(
            [
                "datas.id",
                "datas.ot",
                "datas.alias",
                "datas.setcode as _archcode",
                "datas.type as _type",
                "datas.atk",
                "datas.def as _def",
                "datas.level as _level",
                "datas.race as _race",
                "datas.attribute as _attribute",
                "datas.category as _category",
                "datas.genre as _genre",
                "datas.script",
                "datas.support as _supportcode",
                "datas.ocgdate as _ocgdate",
                "datas.tcgdate as _tcgdate",
                "texts.name",
                "texts.desc as _text",
                "koids.koid",
            ]
        )

        cards: list[dict] = pd.read_sql_query(
            f"""
            SELECT {values}
            FROM datas
            INNER JOIN texts
            USING(id)
            LEFT JOIN koids
            USING(id)
            """,
            con,
        ).to_dict(orient="records")

        self.card_data = {card["id"]: Card(**card) for card in cards}

    def _build_archetype_db(self, con):
        archetypes: list[dict] = pd.read_sql_query(
            """
            SELECT name,
                CASE
                    WHEN officialcode > 0 THEN officialcode
                    ELSE betacode
                END AS id 
            FROM setcodes
            WHERE (officialcode > 0 AND betacode = officialcode) OR (officialcode = 0 AND betacode > 0);
            """,
            con,
        ).to_dict(orient="records")

        self.arch_data: dict[int, Archetype] = {
            arch["id"]: Archetype(**arch) for arch in archetypes
        }

        for card in self.card_data.values():
            for archid in card.archetypes:
                if archid == 0 or archid not in self.arch_data:
                    continue
                self.arch_data[archid].members.append(card.id)
            for archid in card.support:
                if archid == 0 or archid not in self.arch_data:
                    continue
                self.arch_data[archid].support.append(card.id)
            for archid in card.related:
                if archid == 0 or archid not in self.arch_data:
                    continue
                self.arch_data[archid].related.append(card.id)

    def _build_set_db(self, con):
        sets: list[dict] = pd.read_sql_query(
            """
            SELECT
                packs.id,
                packs.abbr,
                packs.name,
                packs.ocgdate as _ocgdate,
                packs.tcgdate as _tcgdate,
                GROUP_CONCAT(relations.cardid) AS cardids
            FROM
                packs
            JOIN
                relations ON packs.id = relations.packid
            GROUP BY
                packs.name;
            """,
            con,
        ).to_dict(orient="records")

        self.set_data: dict[int, Set] = {
            set["id"]: Set(
                id=set["id"],
                name=set["name"],
                abbr=set["abbr"],
                _tcgdate=set["_tcgdate"],
                _ocgdate=set["_ocgdate"],
                contents=[
                    int(id)
                    for id in set["cardids"].split(",")
                    if int(id) in self.card_data
                ],
            )
            for set in sets
        }

        for set in self.set_data.values():
            for cardid in set.contents:
                self.card_data[cardid].sets.append(set.id)
