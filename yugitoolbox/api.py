from flask import Flask, request
from flask_restful import Resource, Api

from .yugidb import YugiDB
from .card import Card

app = Flask(__name__)
api = Api(app)


class YugiDBResource(Resource):
    def __init__(self, yugidb_instance):
        self.yugidb: YugiDB = yugidb_instance

    def get(self):
        card_id = request.args.get("id")
        if card_id:
            try:
                card_id = int(card_id)
                card = self.yugidb.get_card_by_id(card_id)
                return card.to_dict()
            except ValueError:
                return {"message": "Invalid card ID"}, 400
        else:
            return {"message": "Card ID not provided"}, 400

    def post(self):
        data = request.get_json()
        if data and "id" in data and "name":
            try:
                card_id = int(data["id"])
                card_name = data["name"]
                self.yugidb._card_data[card_id] = Card(id=card_id, name=card_name)
                return {"message": "Card added successfully"}, 201
            except ValueError:
                return {"message": "Invalid card ID"}, 400
        else:
            return {"message": "Invalid data provided"}, 400


api.add_resource(YugiDBResource, "/yugidb")

if __name__ == "__main__":
    app.run(debug=True)
