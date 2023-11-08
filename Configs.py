import json

from card_db import CardDB


class Config:
    data = None
    _cards_db = None

    @staticmethod
    def cards_db() -> CardDB:
        if Config._cards_db is None:
            Config.load_cards_db()
        return Config._cards_db

    @staticmethod
    def load_cards_db():
        Config._cards_db = CardDB()

    @staticmethod
    def get_data(key=None):
        if not Config.data:
            Config.load()
        return (
            Config.data
            if key is None
            else Config.data[key]
            if key in Config.data
            else None
        )

    @staticmethod
    def set_data(key, data, save=True):
        if not Config.data:
            Config.load()
        Config.data[key] = data
        if save:
            Config.save()
        return data

    @staticmethod
    def load():
        try:
            with open("config/config.json", "r+") as f:
                Config.data = json.load(f)
        except:
            Config.data = {"server status msg": "", "server status": False}
            Config.save()

    @staticmethod
    def save():
        with open("config/config.json", "w+") as f:
            json.dump(Config.data, f, indent=4)
