import os
import shutil
from typing import Literal

import requests

from yugitoolbox.yugidb import YugiDB

OMEGA_BASE_URL = "https://duelistsunite.org/omega/"


class OmegaDB(YugiDB):
    def __init__(self, update: Literal["skip", "force", "auto"] = None, debug=False):
        self.dbpath = "db/omega/omega.db"
        self.dbpath_old = "db/omega/omega_old.db"
        self.update = update
        self.download()
        self.connection_string = f"sqlite:///{self.dbpath}"
        super().__init__(self.connection_string, debug=debug)

    def download(self):
        def download(url: str, path: str):
            r = requests.get(url, allow_redirects=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)

        db_url = os.path.join(OMEGA_BASE_URL, "OmegaDB.cdb")
        hash_url = os.path.join(OMEGA_BASE_URL, "Database.hash")
        self.dbdir = os.path.dirname(self.dbpath)
        hashpath = os.path.join(self.dbdir, "omega.hash")
        hashpath_old = os.path.join(self.dbdir, "omega_old.hash")

        if not os.path.exists(self.dbdir):
            os.makedirs(self.dbdir)

        if os.path.exists(self.dbpath) and self.update == "skip":
            return

        if os.path.exists(self.dbpath) and self.update != "force":
            shutil.copy(self.dbpath, self.dbpath_old)
            if os.path.exists(hashpath):
                shutil.copy(hashpath, hashpath_old)
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
            elif self.update != "auto":
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


if __name__ == "__main__":
    db = OmegaDB()
    db.download()
