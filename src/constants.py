from sqlalchemy import and_, or_

from .enums import Attribute, Category, Genre, LinkMarker, Race, Type
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
            "?": and_(
                Datas.race.op("==")(-2),
                Datas.type.op("&")(Type.Monster),
            ),
        },
    },
    {
        "key": "attribute",
        "column": Datas.attribute,
        "valuetype": Attribute,
        "special": {
            "?": and_(
                Datas.attribute.op("==")(-2),
                Datas.type.op("&")(Type.Monster),
            ),
        },
    },
    {
        "key": "atk",
        "column": Datas.atk,
        "valuetype": int,
        "special": {
            "def": and_(
                Datas.atk == Datas.def_,
                Datas.type.op("&")(Type.Monster),
            ),
            "?": and_(
                Datas.atk.op("==")(-2),
                Datas.type.op("&")(Type.Monster),
            ),
        },
    },
    {
        "key": "def",
        "column": Datas.def_,
        "valuetype": int,
        "special": {
            "atk": and_(
                Datas.atk == Datas.def_,
                Datas.type.op("&")(Type.Monster),
            ),
            "?": and_(
                Datas.def_.op("==")(-2),
                Datas.type.op("&")(Type.Monster),
            ),
        },
    },
    {
        "key": "level",
        "column": Datas.level.op("&")(0x0000FFFF),
        "valuetype": int,
        "special": {
            "?": and_(
                Datas.level.op("==")(-2),
                Datas.type.op("&")(Type.Monster),
            ),
        },
        # "condition": ~or_(Datas.type.op("&")(x) for x in [Type.Xyz, Type.Link]),
    },
    # {
    #     "key": "rank",
    #     "column": Datas.level.op("&")(0x0000FFFF),
    #     "valuetype": int,
    #     "condition": Datas.type.op("&")(Type.Xyz),
    # },
    # {
    #     "key": "link",
    #     "column": Datas.level.op("&")(0x0000FFFF),
    #     "valuetype": int,
    #     "condition": Datas.type.op("&")(Type.Link),
    # },
    {
        "key": "scale",
        "column": Datas.level.op(">>")(24),
        "valuetype": int,
        "condition": Datas.type.op("&")(Type.Pendulum),
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
        "special": {
            "trapmonster": and_(
                Datas.type.op("&")(Type.Trap),
                Datas.level.op("!=")(0),
            ),
            "darksynchro": and_(
                Datas.category.op("&")(Category.DarkCard),
                Datas.type.op("&")(Type.Synchro),
            ),
            "maindeck": and_(
                ~or_(
                    *(
                        Datas.type.op("&")(x)
                        for x in [
                            Type.Fusion,
                            Type.Synchro,
                            Type.Xyz,
                            Type.Link,
                            Type.Token,
                        ]
                    )
                ),
                Datas.type.op("&")(Type.Monster),
            ),
            "extradeck": or_(
                *(
                    Datas.type.op("&")(x)
                    for x in [
                        Type.Fusion,
                        Type.Synchro,
                        Type.Xyz,
                        Type.Link,
                    ]
                )
            ),
        },
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
        "condition": Datas.type.op("&")(Type.Link),
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
