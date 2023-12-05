from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from PIL.Image import Image
from psd_tools import PSDImage
from psd_tools.api.layers import Group, PixelLayer, TypeLayer

from .enums import *

if TYPE_CHECKING:
    from .card import Card


def init_layers(psd: PSDImage | Group):
    def make_invisible(group: PSDImage | Group):
        for obj in group:
            obj.visible = False
            if isinstance(obj, Group):
                make_invisible(obj)

    def make_dict(group: PSDImage | Group):
        group_dict = {}
        for obj in group:
            if isinstance(obj, Group):
                group_dict[obj.name] = (make_dict(obj), obj)
            elif isinstance(obj, (TypeLayer, PixelLayer)):
                group_dict[obj.name] = obj
            else:
                raise RuntimeError("Unsupported Type in PSD.")
        return group_dict

    make_invisible(psd)
    layers = make_dict(psd)
    return layers


def print_dict_tree(dictionary, indent=0):
    for key, value in dictionary.items():
        if isinstance(value, tuple):
            print("  " * indent + f"{key}:")
            print_dict_tree(value[0], indent + 1)
        else:
            print("  " * indent + f"{key}: {value}")


def build_image(layers: dict[str, Any], card: Card):
    if Type.Monster in card.type:
        if card.is_dark_synchro():
            frame = "Dark Synchro"
        elif Category.YellowGod in card.category:
            frame = "Ra"
        elif Category.RedGod in card.category:
            frame = "Slifer"
        elif Category.BlueGod in card.category:
            frame = "Obelisk"
        elif Type.Token in card.type:
            frame = "Token"
        elif Type.Link in card.type:
            frame = "Link"
        elif Type.Xyz in card.type:
            frame = "XYZ"
        elif Type.Synchro in card.type:
            frame = "Synchro"
        elif Type.Fusion in card.type:
            frame = "Fusion"
        elif Type.Ritual in card.type:
            frame = "Ritual"
        elif Type.Effect in card.type:
            frame = "Effect"
        elif Type.Normal in card.type:
            frame = "Normal"
        else:
            frame = "Unsupported"
        layers["Frames"][0][frame].visible = True
        layers["Frames"][1].visible = True

        layers["Attributes"][0][card.attribute.name].visible = True
        layers["Attributes"][1].visible = True

        layers["Level"][0][f"Level {card.level}"].visible = True
        layers["Level"][1].visible = True

    elif Type.Trap in card.type:
        pass
    elif Type.Spell in card.type:
        if Category.SkillCard in card.category:
            layers["Frames"][0]["Skill"].visible = True
            layers["Frames"][1].visible = True
        else:
            pass

    elif Type.Token in card.type:
        # Legendary Dragon
        if card.id in [10000050, 10000060, 10000070]:
            frame = "Legendary Dragon"
        else:
            frame = "Unsupported"
        layers["Frames"][0][frame].visible = True
        layers["Frames"][1].visible = True


def render_card(card: Card, dir: str):
    template_path = os.path.join(os.path.dirname(__file__), "res/template.psd")
    psd = PSDImage.open(template_path)

    layers = init_layers(psd)
    # print_dict_tree(layers)

    build_image(layers, card)

    img = psd.composite(force=True)
    if isinstance(img, Image):
        img.save(os.path.join(dir, f"{card.id}.png"))
    else:
        raise RuntimeError("Failed to Save Image.")
