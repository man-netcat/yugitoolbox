from __future__ import annotations

import os
from pprint import pprint
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
                group_dict[obj.name] = (obj, make_dict(obj))
            elif isinstance(obj, (TypeLayer, PixelLayer)):
                group_dict[obj.name] = (obj,)
            else:
                raise RuntimeError("Unsupported Type in PSD.")
        return group_dict

    make_invisible(psd)
    layers = make_dict(psd)
    return layers


def print_tree(layer_dict, indent=0, visible=False):
    for name, content in layer_dict.items():
        obj = content[0]  # Get the Layer or Group object
        class_name = obj.__class__.__name__
        string = "    " * indent + f"{obj.name} ({class_name})"
        if visible and obj.visible:
            print(string)

        if len(content) == 2:
            # If it's a Group, recursively print its subtree
            print_tree(content[1], indent + 1, visible)


def set_visible(data, strings):
    for string in strings:
        tuple = data[string]
        tuple[0].visible = True
        if len(tuple) == 2:
            data = tuple[1]


def build_monster(layers: dict[str, Any], card: Card):
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
    set_visible(layers, ["Frames", frame])
    set_visible(layers, ["Attributes", card.attribute.name])

    if card.is_dark_synchro():
        set_visible(layers, ["Negative Level", f"Negative Level {card.level}"])
    elif Type.Xyz in card.type:
        set_visible(layers, ["Rank", f"Rank {card.level}"])
    elif Type.Link:
        pass
    else:
        set_visible(layers, ["Level", f"Level {card.level}"])


def build_spell(layers: dict[str, Any], card: Card):
    if Category.SkillCard in card.category:
        set_visible(layers, ["Frames", "Skill"])
        set_visible(layers, ["Structure", "Skill ", "Effect Box"])
        set_visible(layers, ["Structure", "Skill ", "Artwork Box"])
        set_visible(layers, ["Structure", "Skill ", "Card Frame Bevel"])
        set_visible(layers, ["Structure", "Skill ", "Name Box"])
        return

    set_visible(layers, ["S/T Frames", "Spell", "Spell"])
    set_visible(layers, ["S/T Frames", "Spell", "SPELL Attribute"])

    normal = False
    type = ""
    if Type.Continuous in card.type:
        type = "Continuous Spell/Trap"
    elif Type.QuickPlay in card.type:
        type = "Quick-Play Spell"
    elif Type.Equip in card.type:
        type = "Equip Spell"
    elif Type.Field in card.type:
        type = "Field Spell"
    elif Type.Ritual in card.type:
        type = "Ritual Spell"
    else:
        normal = True

    if normal:
        set_visible(layers, ["S/T Frames", "Type/Icons", "Types", "Spell Card"])
    else:
        set_visible(layers, ["S/T Frames", "Type/Icons", "Icons", type])
        set_visible(layers, ["S/T Frames", "Type/Icons", "Types", "Spell Card w/ Icon"])
    set_visible(layers, ["S/T Frames", "Effect Spell/Trap"])


def build_trap(layers: dict[str, Any], card: Card):
    set_visible(layers, ["S/T Frames", "Trap", "Trap"])
    set_visible(layers, ["S/T Frames", "Trap", "TRAP Attribute"])
    normal = False
    type = ""
    if Type.Continuous in card.type:
        type = "Continuous Spell/Trap"
    elif Type.Counter in card.type:
        type = "Counter Trap"
    else:
        normal = True

    if normal:
        set_visible(layers, ["S/T Frames", "Type/Icons", "Types", "Trap Card"])
    else:
        set_visible(layers, ["S/T Frames", "Type/Icons", "Icons", type])
        set_visible(layers, ["S/T Frames", "Type/Icons", "Types", "Trap Card w/ Icon"])
    set_visible(layers, ["S/T Frames", "Effect Spell/Trap"])


def build_dragon(layers: dict[str, Any], card: Card):
    # Legendary Dragon
    if card.id in [10000050, 10000060, 10000070]:
        frame = "Legendary Dragon"
    else:
        frame = "Unsupported"
    set_visible(layers, ["Frames", frame])


def build_image(layers: dict[str, Any], card: Card):
    if Type.Monster in card.type:
        build_monster(layers, card)
    elif Type.Trap in card.type:
        build_trap(layers, card)
    elif Type.Spell in card.type:
        build_spell(layers, card)
    elif Type.Token in card.type:
        build_dragon(layers, card)

    set_visible(layers, ["Structure", "Common", "Effect Box"])
    set_visible(layers, ["Structure", "Common", "Artwork Line"])
    set_visible(layers, ["Structure", "Boxes", "Border"])

    if card.is_dark_synchro():
        set_visible(layers, ["Structure", "Common", "Artwork Box LNK/D.S/VRs"])
        set_visible(layers, ["Structure", "Effects", "Card Frame Bevel Xyz"])
        set_visible(layers, ["Structure", "Effects", "Name Box Xyz"])
    elif Type.Xyz in card.type:
        set_visible(layers, ["Structure", "Common", "Artwork Box XYZ"])
    elif Type.Link in card.type:
        set_visible(layers, ["Structure", "Common", "Artwork Box LNK/D.S/VRs"])
    else:
        set_visible(layers, ["Structure", "Effects", "Name Box"])
        set_visible(layers, ["Structure", "Effects", "Card Frame Bevel"])
        set_visible(layers, ["Structure", "Common", "Artwork Box"])


def render_card(card: Card, dir: str):
    template_path = os.path.join(os.path.dirname(__file__), "res/template.psd")
    psd = PSDImage.open(template_path)

    layers = init_layers(psd)

    build_image(layers, card)
    print_tree(layers, visible=True)

    img = psd.composite(force=True)
    if isinstance(img, Image):
        img.save(os.path.join(dir, f"{card.id}.png"))
    else:
        raise RuntimeError("Failed to Save Image.")
