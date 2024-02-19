from sqlalchemy import func
from .enums import *
from .sqlclasses import *

card_filter_params = [
    {
        "key": "name",
        "column": func.lower(Texts.name).op("=="),
    },
    {
        "key": "id",
        "column": Datas.id.op("=="),
        "valuetype": int,
    },
    {
        "key": "race",
        "column": Datas.race.op("=="),
        "valuetype": Race,
    },
    {
        "key": "attribute",
        "column": Datas.attribute.op("=="),
        "valuetype": Attribute,
    },
    {
        "key": "atk",
        "column": Datas.atk.op("=="),
        "valuetype": int,
    },
    {
        "key": "def",
        "column": Datas.def_.op("=="),
        "valuetype": int,
    },
    {
        "key": "level",
        "column": Datas.level.op("&")(0x0000FFFF).op("=="),
        "valuetype": int,
    },
    {
        "key": "scale",
        "column": Datas.level.op(">>")(24).op("=="),
        "valuetype": int,
        "condition": Datas.type.op("&")(Type.Pendulum.value),
    },
    {
        "key": "koid",
        "column": Koids.koid.op("=="),
        "valuetype": int,
    },
    {
        "key": "type",
        "column": Datas.type.op("&"),
        "valuetype": Type,
    },
    {
        "key": "category",
        "column": Datas.category.op("&"),
        "valuetype": Category,
    },
    {
        "key": "genre",
        "column": Datas.genre.op("&"),
        "valuetype": Genre,
    },
    {
        "key": "linkmarker",
        "column": Datas.def_.op("&"),
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
        "column": func.lower(Setcodes.name).op("=="),
    },
    {
        "key": "id",
        "column": Setcodes.id.op("=="),
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
        "column": func.lower(Packs.name).op("=="),
    },
    {
        "key": "abbr",
        "column": func.lower(Packs.abbr).op("=="),
    },
    {
        "key": "id",
        "column": Packs.id.op("=="),
        "valuetype": int,
    },
    {
        "key": "in_name",
        "column": lambda x: func.lower(Packs.name).ilike("%" + x + "%"),
    },
]