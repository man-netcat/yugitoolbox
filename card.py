class Card:
    def __init__(
        self,
        _id=0,
        name="",
        support=[],
        archetypes=[],
        related_to=[],
        card_type="",
        monster_type="",
        genre=0,
        type=0,
        text=None,
    ):
        self.id = _id
        self.name = name
        self.archetypes = archetypes
        self.support = support
        self.related_to = related_to
        self.copies = 1
        self.monster_type = monster_type
        self.card_type = card_type
        self.genre = genre
        self.type = type
        self.text = text
