from sqlalchemy import and_, func, or_

from .enums import *
from .sqlclasses import *

card_filter_params = [
    {
        "key": "name",
        "column": Texts.name,
    },
    {
        "key": "id",
        "column": Datas.id,
        "valuetype": int,
    },
    {
        "key": "race",
        "column": Datas.race,
        "valuetype": Race,
        "special": {
            "?": and_(Datas.race == 0, Datas.type.op("&")(Type.Monster.value)),
        },
    },
    {
        "key": "attribute",
        "column": Datas.attribute,
        "valuetype": Attribute,
        "special": {
            "?": and_(Datas.attribute == 0, Datas.type.op("&")(Type.Monster.value)),
        },
    },
    {
        "key": "atk",
        "column": Datas.atk,
        "valuetype": int,
        "special": {
            "def": and_(
                Datas.atk == Datas.def_, Datas.type.op("&")(Type.Monster.value)
            ),
            "?": Datas.atk == -2,
        },
    },
    {
        "key": "def",
        "column": Datas.def_,
        "valuetype": int,
        "special": {
            "atk": and_(
                Datas.atk == Datas.def_, Datas.type.op("&")(Type.Monster.value)
            ),
            "?": Datas.def_ == -2,
        },
    },
    {
        "key": "level",
        "column": Datas.level.op("&")(0x0000FFFF),
        "valuetype": int,
        "special": {
            "?": Datas.level == -2,
        },
        # "condition": ~or_(Datas.type.op("&")(x.value) for x in [Type.Xyz, Type.Link]),
    },
    # {
    #     "key": "rank",
    #     "column": Datas.level.op("&")(0x0000FFFF),
    #     "valuetype": int,
    #     "condition": Datas.type.op("&")(Type.Xyz.value),
    # },
    # {
    #     "key": "link",
    #     "column": Datas.level.op("&")(0x0000FFFF),
    #     "valuetype": int,
    #     "condition": Datas.type.op("&")(Type.Link.value),
    # },
    {
        "key": "scale",
        "column": Datas.level.op(">>")(24),
        "valuetype": int,
        "condition": Datas.type.op("&")(Type.Pendulum.value),
    },
    {
        "key": "koid",
        "column": Koids.koid,
        "valuetype": int,
    },
    {
        "key": "type",
        "column": Datas.type,
        "valuetype": Type,
    },
    {
        "key": "category",
        "column": Datas.category,
        "valuetype": Category,
    },
    {
        "key": "genre",
        "column": Datas.genre,
        "valuetype": Genre,
    },
    {
        "key": "linkmarker",
        "column": Datas.def_,
        "valuetype": LinkMarker,
        "condition": Datas.type.op("&")(Type.Link.value),
    },
    {
        "key": "in_name",
        "column": Texts.name,
        "valuetype": "substr",
    },
    {
        "key": "mentions",
        "column": Texts.desc,
        "valuetype": "substr",
    },
]

archetype_filter_params = [
    {
        "key": "name",
        "column": Setcodes.name,
    },
    {
        "key": "id",
        "column": Setcodes.id,
        "valuetype": int,
    },
    {
        "key": "in_name",
        "column": Setcodes.name,
        "valuetype": "substr",
    },
]


set_filter_params = [
    {
        "key": "name",
        "column": Packs.name,
    },
    {
        "key": "abbr",
        "column": Packs.abbr,
    },
    {
        "key": "id",
        "column": Packs.id,
        "valuetype": int,
    },
    {
        "key": "in_name",
        "column": Packs.name,
        "valuetype": "substr",
    },
]
