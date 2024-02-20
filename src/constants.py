from sqlalchemy import func
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
    },
    {
        "key": "attribute",
        "column": Datas.attribute,
        "valuetype": Attribute,
    },
    {
        "key": "atk",
        "column": Datas.atk,
        "valuetype": int,
    },
    {
        "key": "def",
        "column": Datas.def_,
        "valuetype": int,
    },
    {
        "key": "level",
        "column": Datas.level.op("&")(0x0000FFFF),
        "valuetype": int,
    },
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
        "column": lambda x: func.lower(Texts.name).ilike("%" + x + "%"),
    },
    {
        "key": "mentions",
        "column": lambda x: func.lower(Texts.desc).ilike("%" + x + "%"),
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
        "column": lambda x: func.lower(Setcodes.name).ilike("%" + x + "%"),
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
        "column": lambda x: func.lower(Packs.name).ilike("%" + x + "%"),
    },
]
