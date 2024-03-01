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
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")


class Renderer:
    def __init__(self):
        self.layers: list[str] = []

    def _get_frame(self, card: Card):
        frame = ""
        if card.has_category(Category.SkillCard):
            frame = "Frames/Skill.png"
        elif card.has_type(Type.Trap):
            frame = "Frames/Trap.png"
        elif card.has_type(Type.Spell):
            frame = "Frames/Spell.png"
        elif card.has_category(Category.RedGod):
            frame = "Frames/Slifer.png"
        elif card.has_category(Category.BlueGod):
            frame = "Frames/Obelisk.png"
        elif card.has_category(Category.YellowGod):
            frame = "Frames/Ra.png"
        elif card.has_category(Category.DarkCard):
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
        elif card.has_type(Type.Link):
            frame = "Frames/Link.png"
        elif card.is_token:
            frame = "Frames/Token.png"
        elif card.has_type(Type.Normal):
            frame = "Frames/Normal.png"
        elif card.has_type(Type.Effect):
            frame = "Frames/Effect.png"
        self.layers.append(frame)
        if card.has_type(Type.Pendulum):
            self.layers.append("Frames/Pendulum.png")

    def _get_common(self, card: Card):
        if card.has_type(Type.Pendulum):
            self.layers.append("Common/Pendulum_Medium/Pendulum_Effect_Bar.png")
            self.layers.append("Common/Pendulum_Medium/Pendulum_Box_Medium.png")
        elif card.has_type(Type.Xyz):
            self.layers.append("Common/Artwork_Box_Xyz.png")
        elif card.has_category(Category.SkillCard):
            self.layers.append("Common/Artwork_Box_Skill.png")
        elif card.has_type(Type.Link):
            self.layers.append("Common/Artwork_Box_LNKD.png")
        else:
            self.layers.append("Common/Artwork_Box.png")

        if card.has_type(Type.Xyz):
            self.layers.append("Common/Card_Frame_Bevel_Xyz.png")
        elif card.has_category(Category.SkillCard):
            self.layers.append("Common/Card_Frame_Bevel_Skill.png")
        else:
            self.layers.append("Common/Card_Frame_Bevel.png")

        if card.has_type(Type.Xyz):
            self.layers.append("Common/Name_Box_Xyz.png")
        elif card.has_category(Category.SkillCard):
            self.layers.append("Common/Name_Box_Skill.png")
        else:
            self.layers.append("Common/Name_Box.png")

        if card.has_category(Category.SkillCard):
            self.layers.append("Common/Effect_Box_Skill.png")
        elif not card.has_type(Type.Pendulum):
            self.layers.append("Common/Effect_Box.png")

        self.layers.append("Common/Border.png")
        import random

        self.layers.append(f"Stickers/Holo_Sticker_{random.randint(1, 4)}.png")
        if (
            card.has_type(Type.Xyz) or card.has_category(Category.DarkCard)
        ) and not card.has_type(Type.Pendulum):
            self.layers.append("Text/Limitation/White/Creator.png")
        else:
            self.layers.append("Text/Limitation/Black/Creator.png")

    def _get_attribute(self, card: Card):
        if card.is_skill:
            return
        attr = ""
        if card.has_type(Type.Spell) and card.has_category(Category.SkillCard):
            attr = "Attributes/SPELL.png"
        elif card.has_type(Type.Trap):
            attr = "Attributes/TRAP.png"
        elif card.attribute:
            attr = f"Attributes/{card.attribute.name}.png"
        else:
            return
        self.layers.append(attr)

    def _get_art(self, card: Card):
        art_url = IMG_BASE_URL % card.id
        alias_url = IMG_BASE_URL % card.alias
        art_path = os.path.join(ASSET_DIR, "Art", f"{card.id}.png")
        custom_art_path = os.path.join(ASSET_DIR, "CustomArt", f"{card.id}.png")
        if os.path.exists(art_path):
            self.layers.append(f"Art/{card.id}.png")
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
        self.layers.append(f"Art/{card.id}.png")

    def _get_neg_level(self, card: Card):
        neg_level = f"Negative_Level/Negative_Level_{card.level}.png"
        self.layers.append(neg_level)

    def _get_rank(self, card: Card):
        if card.level > 0:
            rank = f"Rank/Rank_{card.level}.png"
            self.layers.append(rank)

    def _get_linkmarkers(self, card: Card):
        active = [linkmarker.name for linkmarker in card.linkmarkers]
        inactive = [
            linkmarker.name
            for linkmarker in LinkMarker
            if not card.has_linkmarker(linkmarker)
        ]
        for marker in active:
            self.layers.append(f"Link_Arrows/{marker}Active.png")
            self.layers.append(f"Link_Arrows/{marker}Glow.png")
        for marker in inactive:
            self.layers.append(f"Link_Arrows/{marker}Normal.png")
            self.layers.append(f"Link_Arrows/{marker}Shadow.png")

    def _get_level(self, card: Card):
        if card.level > 0:
            level = f"Level/Level_{card.level}.png"
            self.layers.append(level)

    def _get_property(self, card: Card):
        icon = None
        if card.has_type(Type.Continuous):
            icon = "Property/Continuous.png"
        elif card.has_type(Type.Counter):
            icon = "Property/Counter.png"
        elif card.has_type(Type.QuickPlay):
            icon = "Property/QuickPlay.png"
        elif card.has_type(Type.Field):
            icon = "Property/Field.png"
        elif card.has_type(Type.QuickPlay):
            icon = "Property/QuickPlay.png"
        elif card.has_type(Type.Ritual):
            icon = "Property/Ritual.png"

        if card.has_category(Category.SkillCard):
            return

        text = None
        if icon:
            self.layers.append(icon)
            if card.has_type(Type.Spell):
                text = "Text/Spell_Card_w_Icon.png"
            else:
                text = "Text/Trap_Card_w_Icon.png"
        else:
            if card.has_type(Type.Spell):
                text = "Text/Spell_Card.png"
            else:
                text = "Text/Trap_Card.png"
        self.layers.append(text)

    def _get_atk_def_link(self, card: Card):
        if not card.has_type(Type.Monster):
            return

        if card.has_type(Type.Link):
            self.layers.append("Text/LINK-.png")
        else:
            self.layers.append("Text/DEF__Bar.png")
        self.layers.append("Text/ATK__Bar.png")
        self.layers.append("Text/Status_Bar.png")

    def _process_layers(self, card: Card):
        self.layers = []

        self._get_frame(card)
        self._get_art(card)
        self._get_common(card)
        self._get_attribute(card)

        if card.is_spelltrap:
            self._get_property(card)
        elif card.is_dark_synchro:
            self._get_neg_level(card)
        elif card.has_type(Type.Xyz):
            self._get_rank(card)
        elif card.has_type(Type.Link):
            self._get_linkmarkers(card)
        elif not card.has_category(Category.LevelZero):
            self._get_level(card)

        if card.has_type(Type.Pendulum):
            self.layers.append("Common/Pendulum_Medium/Pendulum_Scales.png")
        self._get_atk_def_link(card)

    def _build_template(
        self,
    ):
        extended_path = os.path.join(ASSET_DIR, self.layers[0])
        base_image = Image.open(extended_path).convert("RGBA")
        for image_path in self.layers[1:]:
            extended_path = os.path.join(ASSET_DIR, image_path)
            overlay = Image.open(extended_path).convert("RGBA")
            base_image = Image.alpha_composite(base_image, overlay)
        return base_image

    def _draw_card_name(self, card: Card):
        font_path = os.path.join(
            ASSET_DIR,
            "Fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf",
        )
        font_size = 93
        text_position = (64, 52)

        if (
            card.is_spelltrap
            or card.has_any_type([Type.Xyz, Type.Link])
            or card.has_category(Category.DarkCard)
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
        self.image = Image.alpha_composite(self.image, stretched_text_layer)

    def _draw_text_segment(self, text, font_path, font_size, bbox, colour):
        font = ImageFont.truetype(font=font_path, size=font_size)
        layer = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
        draw_layer = ImageDraw.Draw(layer)
        draw_layer.text(xy=(bbox[0], bbox[1]), text=text, fill=colour, font=font)
        self.image = Image.alpha_composite(self.image, layer)

    def _draw_segments(self, card: Card):
        if card.is_spelltrap or card.is_skill:
            return
        # Race/MDType
        self._draw_text_segment(
            card.type_str,
            os.path.join(
                ASSET_DIR,
                "Fonts/Yu-Gi-Oh! ITC Stone Serif Small Caps Bold.ttf",
            ),
            31,
            (65, 888),
            "#000",
        )
        # ATK
        atkoffset = 16 * (len(str(card.atk)) if card.atk >= 0 else 1)
        atkcoord = 576 - atkoffset
        self._draw_text_segment(
            str(card.atk) if card.atk >= 0 else "?",
            os.path.join(
                ASSET_DIR,
                "Fonts/MatrixBoldSmallCaps.otf",
            ),
            34,
            (atkcoord, 1081),
            "#000",
        )
        if card.has_type(Type.Link):
            # Rating
            self._draw_text_segment(
                str(card.level),
                os.path.join(ASSET_DIR, "Fonts/RoGSanSrfStd-Bd.otf"),
                24,
                (722, 1083),
                "#000",
            )
        else:
            # DEF
            defoffset = 16 * (len(str(card.def_)) if card.def_ >= 0 else 1)
            defcoord = 741 - defoffset
            self._draw_text_segment(
                str(card.def_) if card.def_ >= 0 else "?",
                os.path.join(
                    ASSET_DIR,
                    "Fonts/MatrixBoldSmallCaps.otf",
                ),
                34,
                (defcoord, 1081),
                "#000",
            )

        # Scales
        if card.has_type(Type.Pendulum):
            for x in [72, 718]:
                self._draw_text_segment(
                    str(card.scale),
                    os.path.join(
                        ASSET_DIR,
                        "Fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf",
                    ),
                    60,
                    (x, 812),
                    "#000",
                )

    def _draw_effect(self, text, max_width, mats, font_path, font_size, bbox):
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
        self.image = Image.alpha_composite(self.image, stretched_layer)

    def _draw_card_text(self, card: Card):
        if card.is_skill:
            return
        sections = card.text.split("\n")
        mats = None
        pendtext = None
        text = ""

        # TODO: This is jank, fix this
        match len(sections):
            case 1:
                text = sections[0]
            case 2:
                mats, text = sections
            case 4:
                _, pendtext, _, text = sections
            case 5:
                _, pendtext, _, mats, text = sections

        if card.has_type(Type.Normal) and not card.is_token:
            font_path = os.path.join(
                ASSET_DIR, "Fonts/Yu-Gi-Oh! ITC Stone Serif LT Italic.ttf"
            )
        else:
            font_path = os.path.join(ASSET_DIR, "Fonts/Yu-Gi-Oh! Matrix Book.ttf")
        if card.has_type(Type.Monster):
            bbox = (65, 925)
        else:
            bbox = (65, 895)
        self._draw_effect(text, 78, mats, font_path, 19, bbox)
        if card.has_type(Type.Pendulum):
            self._draw_effect(pendtext, 62, None, font_path, 19, (128, 751))

    def _draw_card_id(self, card: Card):
        self._draw_text_segment(
            str(card.id),
            os.path.join(
                ASSET_DIR,
                "Fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf",
            ),
            32,
            (40, 1128),
            "#000",
        )

    def _render_text(self, card: Card):
        self._draw_card_name(card)
        self._draw_segments(card)
        # self._draw_card_text(card)
        self._draw_card_id(card)

    def render_card(self, card: Card, dir: str = "out"):
        self._process_layers(card)

        if not os.path.isdir(dir):
            os.makedirs(dir, exist_ok=True)

        self.image = self._build_template()
        self._render_text(card)

        out_path = os.path.join(dir, f"{card.id}.png")
        self.image.save(out_path, "PNG")
        return out_path
