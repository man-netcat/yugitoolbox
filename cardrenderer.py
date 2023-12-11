from __future__ import annotations

import os
import textwrap
from io import BytesIO
from typing import TYPE_CHECKING

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

from .enums import *

if TYPE_CHECKING:
    from .card import Card

IMG_BASE_URL = "https://images.ygoprodeck.com/images/cards_cropped/%s.jpg"
CARD_SIZE = (813, 1185)


class Renderer:
    layers = []
    image: Image.Image

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
        elif card.has_edtype(EDType.Fusion):
            frame = "Frames/Fusion.png"
        elif card.has_type(Type.Ritual):
            frame = "Frames/Ritual.png"
        elif card.has_edtype(EDType.Synchro):
            frame = "Frames/Synchro.png"
        elif card.has_edtype(EDType.Xyz):
            frame = "Frames/Xyz.png"
        elif card.has_type(Type.Trap):
            frame = "Frames/Trap.png"
        elif card.has_type(Type.Spell):
            frame = "Frames/Spell.png"
        elif card.has_edtype(EDType.Link):
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
        if card.has_type(Type.Pendulum):
            Renderer.layers.append("Common/Pendulum_Medium/Pendulum_Effect_Bar.png")
            Renderer.layers.append("Common/Pendulum_Medium/Pendulum_Box_Medium.png")
        elif card.has_edtype(EDType.Xyz):
            Renderer.layers.append("Common/Artwork_Box_Xyz.png")
        elif card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Artwork_Box_Skill.png")
        elif card.has_edtype(EDType.Link):
            Renderer.layers.append("Common/Artwork_Box_LNKD.png")
        else:
            Renderer.layers.append("Common/Artwork_Box.png")

        if card.has_edtype(EDType.Xyz):
            Renderer.layers.append("Common/Card_Frame_Bevel_Xyz.png")
        elif card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Card_Frame_Bevel_Skill.png")
        else:
            Renderer.layers.append("Common/Card_Frame_Bevel.png")

        if card.has_edtype(EDType.Xyz):
            Renderer.layers.append("Common/Name_Box_Xyz.png")
        elif card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Name_Box_Skill.png")
        else:
            Renderer.layers.append("Common/Name_Box.png")

        if card.has_category(Category.SkillCard):
            Renderer.layers.append("Common/Effect_Box_Skill.png")
        elif not card.has_type(Type.Pendulum):
            Renderer.layers.append("Common/Effect_Box.png")

        Renderer.layers.append("Common/Border.png")
        import random

        Renderer.layers.append(f"Stickers/Holo_Sticker_{random.randint(1, 4)}.png")
        if (card.has_edtype(EDType.Xyz) or card.is_dark_synchro) and not card.has_type(
            Type.Pendulum
        ):
            Renderer.layers.append("Text/Limitation/White/Creator.png")
        else:
            Renderer.layers.append("Text/Limitation/Black/Creator.png")

    @staticmethod
    def get_attribute(card: Card):
        if card.is_skill:
            return
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
    def get_art(card: Card):
        art_url = IMG_BASE_URL % card.id
        alias_url = IMG_BASE_URL % card.alias
        art_path = os.path.join("yugitoolbox/assets/Art", f"{card.id}.png")
        custom_art_path = os.path.join("yugitoolbox/assets/CustomArt", f"{card.id}.png")
        if os.path.exists(art_path):
            Renderer.layers.append(f"Art/{card.id}.png")
            return
        if os.path.exists(custom_art_path):
            art_img = Image.open(custom_art_path).convert("RGBA")
        else:
            response = requests.get(art_url, stream=True)
            if not response.ok:
                response = requests.get(alias_url, stream=True)
                if not response.ok:
                    return
            art_img = Image.open(BytesIO(response.content)).convert("RGBA")
        card_size = CARD_SIZE
        if card.has_type(Type.Pendulum):
            bbox = (55, 212, 759, 739)
            new_width = 704
            aspect_ratio = art_img.width / art_img.height
            new_height = int(new_width / aspect_ratio)
            art_img = art_img.resize((new_width, new_height), Image.LANCZOS)
            art_img = ImageOps.fit(
                art_img,
                (bbox[2] - bbox[0], bbox[3] - bbox[1]),
                centering=(0.0, 0.0),
            )
        else:
            bbox = (98, 217, 716, 835)
            new_size = (618, 618)
            art_img = art_img.resize(new_size, Image.LANCZOS)
        background = Image.new("RGBA", card_size, (255, 255, 255, 0))
        background.paste(art_img, (bbox[0], bbox[1]))
        background.save(art_path, format="PNG")
        Renderer.layers.append(f"Art/{card.id}.png")

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
    def get_property(card: Card):
        icon = None
        if card.has_property(Property.Continuous):
            icon = "Property/Continuous.png"
        elif card.has_property(Property.Counter):
            icon = "Property/Counter.png"
        elif card.has_property(Property.QuickPlay):
            icon = "Property/QuickPlay.png"
        elif card.has_property(Property.Field):
            icon = "Property/Field.png"
        elif card.has_property(Property.QuickPlay):
            icon = "Property/QuickPlay.png"
        elif card.has_property(Property.Ritual):
            icon = "Property/Ritual.png"

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

        if card.has_edtype(EDType.Link):
            Renderer.layers.append("Text/Link-.png")
        else:
            Renderer.layers.append("Text/Def__Bar.png")
        Renderer.layers.append("Text/Atk__Bar.png")
        Renderer.layers.append("Text/Status_Bar.png")

    @staticmethod
    def process_layers(card: Card):
        Renderer.layers = []

        Renderer.get_frame(card)
        Renderer.get_art(card)
        Renderer.get_common(card)
        Renderer.get_attribute(card)

        if card.has_any_type([Type.Spell, Type.Trap]):
            Renderer.get_property(card)
        elif card.is_dark_synchro:
            Renderer.get_neg_level(card)
        elif card.has_edtype(EDType.Xyz):
            Renderer.get_rank(card)
        elif card.has_edtype(EDType.Link):
            Renderer.get_linkmarkers(card)
        else:
            Renderer.get_level(card)
        if card.has_type(Type.Pendulum):
            Renderer.layers.append("Common/Pendulum_Medium/Pendulum_Scales.png")
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
    def draw_card_name(card: Card):
        font_path = "yugitoolbox/assets/Fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf"
        font_size = 93
        text_position = (64, 52)

        if (
            card.has_any_type([Type.Spell, Type.Trap])
            or card.has_any_edtype([EDType.Xyz, EDType.Link])
            or card.is_dark_synchro
        ):
            text_color = "#FFF"
        else:
            text_color = "#000"

        max_width = 600
        temp_image = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_image)

        card_font = ImageFont.truetype(font=font_path, size=font_size)
        text_bbox = temp_draw.textbbox(text_position, card.name, font=card_font)

        text_width = text_bbox[2] - text_bbox[0]
        width_scale = max(1, text_width / max_width)

        text_layer_width = int(813 * width_scale)
        text_layer = Image.new("RGBA", (text_layer_width, 1185), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)

        text_draw.text(
            xy=(text_position[0] * width_scale, text_position[1]),
            text=card.name,
            fill=text_color,
            font=card_font,
        )

        stretched_text_layer = text_layer.resize(CARD_SIZE, Image.LANCZOS)
        Renderer.image = Image.alpha_composite(Renderer.image, stretched_text_layer)

    @staticmethod
    def draw_text_segment(text, font_path, font_size, bbox, colour):
        font = ImageFont.truetype(font=font_path, size=font_size)
        layer = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
        draw_layer = ImageDraw.Draw(layer)
        draw_layer.text(xy=(bbox[0], bbox[1]), text=text, fill=colour, font=font)
        Renderer.image = Image.alpha_composite(Renderer.image, layer)

    @staticmethod
    def draw_segments(card: Card):
        if not card.has_type(Type.Monster) and not card.is_skill:
            return
        # Race/Type
        Renderer.draw_text_segment(
            card.type_str,
            "yugitoolbox/assets/Fonts/Yu-Gi-Oh! ITC Stone Serif Small Caps Bold.ttf",
            31,
            (65, 888),
            "#000",
        )
        if card.is_skill:
            return
        # ATK
        Renderer.draw_text_segment(
            str(card.atk) if card.atk >= 0 else "?",
            "yugitoolbox/assets/Fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf",
            41,
            (511, 1077),
            "#000",
        )
        if card.has_edtype(EDType.Link):
            Renderer.draw_text_segment(
                str(card.level),
                "yugitoolbox/assets/Fonts/RoGSanSrfStd-Bd.otf",
                24,
                (722, 1083),
                "#000",
            )
            pass
        else:
            # DEF
            Renderer.draw_text_segment(
                str(card.def_) if card.def_ >= 0 else "?",
                "yugitoolbox/assets/Fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf",
                41,
                (676, 1077),
                "#000",
            )

        if card.has_type(Type.Pendulum):
            for x in [72, 718]:
                Renderer.draw_text_segment(
                    str(card.scale),
                    "yugitoolbox/assets/Fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf",
                    60,
                    (x, 812),
                    "#000",
                )

    @staticmethod
    def draw_effect(text, max_width, mats, font_path, font_size, bbox):
        wrapped = "\n".join(
            textwrap.wrap(
                text, max_width, break_long_words=False, break_on_hyphens=False
            )
        )
        if mats:
            wrapped = f"{mats}\n{wrapped}"
        # print(wrapped)
        temp_image = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
        temp_layer = ImageDraw.Draw(temp_image)
        font = ImageFont.truetype(font=font_path, size=font_size)
        textbbox = temp_layer.textbbox(bbox, wrapped, font=font)
        text_width = textbbox[2] - textbbox[0]
        layer = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
        draw_layer = ImageDraw.Draw(layer)
        draw_layer.text(xy=(bbox[0], bbox[1]), text=wrapped, fill="#000", font=font)
        stretched_layer = layer.resize(CARD_SIZE, Image.LANCZOS)
        Renderer.image = Image.alpha_composite(Renderer.image, stretched_layer)

    @staticmethod
    def draw_card_text(card: Card):
        if card.is_skill:
            return
        sections = card.text.split("\n")
        mats = None
        pendtext = None
        text = ""
        match len(sections):
            case 1:
                text = sections[0]
            case 2:
                mats, text = sections
            case 4:
                _, pendtext, _, text = sections
            case 5:
                _, pendtext, _, mats, text = sections

        if card.has_type(Type.Normal) and not card.has_type(Type.Token):
            font_path = (
                "yugitoolbox/assets/Fonts/Yu-Gi-Oh! ITC Stone Serif LT Italic.ttf"
            )
        else:
            font_path = "yugitoolbox/assets/Fonts/Yu-Gi-Oh! Matrix Book.ttf"
        if card.has_type(Type.Monster):
            bbox = (65, 925)
        else:
            bbox = (65, 895)
        Renderer.draw_effect(text, 78, mats, font_path, 19, bbox)
        if card.has_type(Type.Pendulum):
            Renderer.draw_effect(pendtext, 62, None, font_path, 19, (128, 751))

    @staticmethod
    def render_text(card: Card):
        Renderer.draw_card_name(card)
        Renderer.draw_segments(card)
        Renderer.draw_card_text(card)

    @staticmethod
    def render_card(card: Card, dir: str = "out"):
        Renderer.process_layers(card)

        if not os.path.isdir(dir):
            os.makedirs(dir)

        Renderer.image = Renderer.build_template()
        Renderer.render_text(card)

        out_path = os.path.join(dir, f"{card.id}.png")
        Renderer.image.save(out_path, "PNG")
