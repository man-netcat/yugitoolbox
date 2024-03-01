from .enums import *
from .card import Card
from typing import Literal


class CardBuilder:
    @staticmethod
    def build_monster_card(
        id: int,
        name: str,
        text: str,
        attribute: Attribute,
        race: Race,
        atk: int,
        level: int = 0,
        rank: int = 0,
        def_: int = 0,
        linkmarkers: list[LinkMarker] = [],
        effect: bool = True,
        supertype: Literal[
            Type.Ritual,
            Type.Fusion,
            Type.Synchro,
            Type.Xyz,
            Type.Link,
            Type.Token,
            None,
        ] = None,
        ability: Literal[
            Type.Toon,
            Type.Gemini,
            Type.Flip,
            Type.Spirit,
            Type.Union,
            Type.SpSummon,
            None,
        ] = None,
        scale: int = -2,
        dark_synchro: bool = False,
        archetypes=[],
    ):
        card = Card(id=id, name=name)
        card.attribute = attribute
        card.race = race
        card.atk = atk
        card.text = text

        card.type = Type.Monster
        if effect:
            card.append_type(Type.Effect)

        if supertype and ability:
            raise TypeError(
                "A Card cannot simultaneously have a Supertype and an Ability."
            )

        if supertype:
            if supertype not in [
                Type.Ritual,
                Type.Fusion,
                Type.Synchro,
                Type.Xyz,
                Type.Link,
                Type.Token,
            ]:
                raise TypeError("Invalid Supertype.")
            card.append_type(supertype)

        if ability:
            if ability not in [
                Type.Toon,
                Type.Gemini,
                Type.Flip,
                Type.Spirit,
                Type.Union,
                Type.SpSummon,
            ]:
                raise TypeError("Invalid Ability.")
            card.append_type(ability)

        if scale >= 0:
            card.append_type(Type.Pendulum)
            card.scale = scale

        if supertype == Type.Xyz:
            card.level = rank
        else:
            card.level = level

        if supertype == Type.Link:
            if not len(linkmarkers) >= 1:
                raise ValueError("Number of LinkMarkers must be at least 1.")
            card.linkmarkers = linkmarkers
            card.level = len(linkmarkers)
        else:
            card.def_ = def_

        if supertype == Type.Synchro and dark_synchro:
            card.append_category(Category.DarkCard)

        card.archetypes = archetypes

        return card

    @staticmethod
    def build_spelltrap(
        id: int,
        name: str,
        text: str,
        type: Type,
        property: Type,
    ):
        card = Card(id=id, name=name)
        card.text = text

        if type == Type.Spell:
            if property not in [
                Type.Ritual,
                Type.QuickPlay,
                Type.Continuous,
                Type.Equip,
                Type.Field,
            ]:
                raise TypeError("Invalid Property")
            card.type = [Type.Spell, property]
        elif type == Type.Trap:
            if property not in [
                Type.Continuous,
                Type.Counter,
            ]:
                raise TypeError("Invalid Property")
            card.type = [Type.Trap, property]
        else:
            raise TypeError("Invalid Type")

        return card
