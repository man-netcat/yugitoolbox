from __future__ import annotations

import os
from typing import TYPE_CHECKING

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
                group_dict[obj.name] = make_dict(obj)
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
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            print_dict_tree(value, indent + 1)
        else:
            print("  " * indent + f"{key}: {value}")


def build_image(layers: dict[str, dict | PixelLayer | TypeLayer], card: Card):
    if Type.Monster in card.type:
        pass
    elif Type.Trap in card.type:
        pass
    elif Type.Spell in card.type:
        pass


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
