from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from .enums import *

if TYPE_CHECKING:
    from .card import Card


class Renderer:
    layers = []

    @staticmethod
    def get_frame(card: Card):
        frame = ""
        if card.has_category(Category.SkillCard):
            frame = "Frames/Skill.png"
        elif card.has_category(Category.RedGod):
            frame = "Frames/Slifer.png"
        elif card.has_category(Category.BlueGod):
            frame = "Frames/Obelisk.png"
        elif card.has_category(Category.YellowGod):
            frame = "Frames/Ra.png"
        elif card.is_dark_synchro:
            frame = "Frames/Dark_Synchro.png"
        elif card.is_legendary_dragon:
            frame = "Frames/Legendary_Dragon.png"
        elif card.has_type(Type.Fusion):
            frame = "Frames/Fusion.png"
        elif card.has_type(Type.Ritual):
            frame = "Frames/Ritual.png"
        elif card.has_type(Type.Synchro):
            frame = "Frames/Synchro.png"
        elif card.has_type(Type.Xyz):
            frame = "Frames/Xyz.png"
        elif card.has_type(Type.Trap):
            frame = "Frames/Trap.png"
        elif card.has_type(Type.Spell):
            frame = "Frames/Spell.png"
        elif card.has_type(Type.Link):
            frame = "Frames/Link.png"
        elif card.has_type(Type.Token):
            frame = "Frames/Token.png"
        elif card.has_type(Type.Normal):
            frame = "Frames/Normal.png"
        elif card.has_type(Type.Effect):
            frame = "Frames/Effect.png"
        Renderer.layers.append(frame)
        if card.has_type(Type.Pendulum):
            Renderer.layers.append("Frames/Pendulum.png")

    @staticmethod
    def get_common(card: Card):
        if card.has_type(Type.Xyz):
            Renderer.layers.append("Common/Artwork_Box_Xyz.png")
        elif card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Artwork_Box_Skill.png")
        elif card.has_type(Type.Link):
            Renderer.layers.append("Common/Artwork_Box_LNKD.png")
        else:
            Renderer.layers.append("Common/Artwork_Box.png")

        if card.has_type(Type.Xyz):
            Renderer.layers.append("Common/Card_Frame_Bevel_Xyz.png")
        elif card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Card_Frame_Bevel_Skill.png")
        else:
            Renderer.layers.append("Common/Card_Frame_Bevel.png")

        if card.has_type(Type.Xyz):
            Renderer.layers.append("Common/Name_Box_Xyz.png")
        elif card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Name_Box_Skill.png")
        else:
            Renderer.layers.append("Common/Name_Box.png")

        if card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Effect_Box_Skill.png")
        else:
            Renderer.layers.append("Common/Effect_Box.png")

        Renderer.layers.append("Common/Border.png")
        import random

        Renderer.layers.append(f"Stickers/Holo_Sticker_{random.randint(1, 4)}.png")
        Renderer.layers.append("Text/Limitation/Black/Creator.png")

    @staticmethod
    def get_attribute(card: Card):
        attr = ""
        if card.has_type(Type.Spell) and card.has_category(Category.SkillCard):
            attr = "Attributes/SPELL.png"
        elif card.has_type(Type.Trap):
            attr = "Attributes/TRAP.png"
        elif card.attribute != Attribute.Unknown:
            attr = f"Attributes/{card.attribute.name}.png"
        else:
            return
        Renderer.layers.append(attr)

    @staticmethod
    def get_neg_level(card: Card):
        neg_level = f"Negative_Level/Negative_Level_{card.level}.png"
        Renderer.layers.append(neg_level)

    @staticmethod
    def get_rank(card: Card):
        rank = f"Rank/Rank_{card.level}.png"
        Renderer.layers.append(rank)

    @staticmethod
    def get_linkmarkers(card: Card):
        active = [linkmarker.name for linkmarker in card.linkmarkers]
        inactive = [
            linkmarker.name
            for linkmarker in LinkMarker
            if not card.has_linkmarker(linkmarker)
        ]
        for marker in active:
            Renderer.layers.append(f"Link_Arrows/{marker}Active.png")
            Renderer.layers.append(f"Link_Arrows/{marker}Glow.png")
        for marker in inactive:
            Renderer.layers.append(f"Link_Arrows/{marker}Normal.png")
            Renderer.layers.append(f"Link_Arrows/{marker}Shadow.png")

    @staticmethod
    def get_level(card: Card):
        if card.level > 0:
            level = f"Level/Level_{card.level}.png"
            Renderer.layers.append(level)

    @staticmethod
    def get_st_icon(card: Card):
        icon = None
        if card.has_type(Type.Continuous):
            icon = "ST_Icons/Continuous.png"
        elif card.has_type(Type.Counter):
            icon = "ST_Icons/Counter.png"
        elif card.has_type(Type.QuickPlay):
            icon = "ST_Icons/QuickPlay.png"
        elif card.has_type(Type.Field):
            icon = "ST_Icons/Field.png"
        elif card.has_type(Type.QuickPlay):
            icon = "ST_Icons/QuickPlay.png"
        elif card.has_type(Type.Ritual):
            icon = "ST_Icons/Ritual.png"

        if card.has_category(Category.SkillCard):
            return

        text = None
        if icon:
            Renderer.layers.append(icon)
            if card.has_type(Type.Spell):
                text = "Text/Spell_Card_w_Icon.png"
            elif card.has_type(Type.Trap):
                text = "Text/Trap_Card_w_Icon.png"
        else:
            if card.has_type(Type.Spell):
                text = "Text/Spell_Card.png"
            elif card.has_type(Type.Trap):
                text = "Text/Trap_Card.png"
        Renderer.layers.append(text)

    @staticmethod
    def get_atk_def_link(card: Card):
        if not card.has_type(Type.Monster):
            return

        if card.has_type(Type.Link):
            Renderer.layers.append("Text/Link-.png")
        else:
            Renderer.layers.append("Text/Def__Bar.png")
        Renderer.layers.append("Text/Atk__Bar.png")
        Renderer.layers.append("Text/Status_Bar.png")

    @staticmethod
    def process_layers(card: Card):
        Renderer.layers = []

        Renderer.get_frame(card)
        Renderer.get_common(card)
        Renderer.get_attribute(card)

        if any(card.has_type(x) for x in [Type.Spell, Type.Trap]):
            Renderer.get_st_icon(card)
        elif card.is_dark_synchro:
            Renderer.get_neg_level(card)
        elif card.has_type(Type.Xyz):
            Renderer.get_rank(card)
        elif card.has_type(Type.Link):
            Renderer.get_linkmarkers(card)
        else:
            Renderer.get_level(card)
        Renderer.get_atk_def_link(card)

    @staticmethod
    def build_template():
        extended_path = os.path.join("yugitoolbox/assets", Renderer.layers[0])
        base_image = Image.open(extended_path).convert("RGBA")
        for image_path in Renderer.layers[1:]:
            extended_path = os.path.join("yugitoolbox/assets", image_path)
            overlay = Image.open(extended_path).convert("RGBA")
            base_image = Image.alpha_composite(base_image, overlay)
        return base_image

    @staticmethod
    def draw_text(text, font_path, font_size, image, bbox):
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, font_size)
        draw.multiline_text((bbox[0], bbox[1]), text, "#000", font)

    @staticmethod
    def render_text(card: Card, image: Image.Image):
        pass
        # Renderer.draw_text(
        #     typestr,
        #     "yugitoolbox/assets/Fonts/Yu-Gi-Oh! ITC Stone Serif Small Caps Bold.ttf",
        #     22,
        #     image,
        #     [70, 900, 740, 1100],
        # )
        # Renderer.draw_text(
        #     card.text,
        #     "yugitoolbox/assets/Fonts/Yu-Gi-Oh! Matrix Book.ttf",
        #     20,
        #     image,
        #     [70, 900, 740, 1100],
        # )

    @staticmethod
    def render_card(card: Card, dir: str = "out"):
        Renderer.process_layers(card)

        for layer in Renderer.layers:
            print(layer)

        if not os.path.isdir(dir):
            os.makedirs(dir)

        image = Renderer.build_template()
        Renderer.render_text(card, image)

        out_path = os.path.join(dir, f"{card.id}.png")
        image.save(out_path, "PNG")
