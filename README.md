# YugiToolbox
Database wrapper and tools for Yu-Gi-Oh! databases.

## Supports
- YGO Omega database
- Custom card databases

## Features
- Searching cards, archetypes and sets by several attributes
- Creating deck objects from Omega code or YDKE
- Writes data to .pkl files for fast accessing

## How to use
### Search features
```py
>>> from yugitoolbox import OmegaDB
>>> db = OmegaDB()
>>> card = db.get_card_by_id(10497636)
>>> print(card)
War Rock Meteoragon (10497636): Level 7 EARTH Warrior Effect Monster
>>> card.get_archetypes(db)
[War Rock]
>>> card.get_race()
'Warrior'
>>> arch = db.get_archetypes_by_value("name", "War Rock")[0]
>>> arch.name
'War Rock'
>>> arch.get_cards(db) 
[War Rock Meteoragon, War Rock Meteoragon, War Rock Bashileos, War Rock Bashileos, War Rock Generations, War Rock Gactos, War Rock Mountain, War Rock Orpis, War Rock Big Blow, War Rock Wento, War Rock Dignity, War Rock Ordeal, War Rock Skyler, War Rock Skyler, War Rock Medium, War Rock Fortia, War Rock Spirit, War Rock Mammud]
>>> card.get_sets(db) 
[Lightning Overdrive, World Premiere Pack 2021]
```
### Custom DB
```py
>>> from yugitoolbox import CustomDB
>>> customdb = CustomDB("Ancient Warriors DB", "db/ancientwarriors/ancientwarriors.db")
>>> for card in customdb.get_cards():
...     print(card)
... 
Ancient Warriors - Heroic Zhao Long (210000229): Level 4 WIND BeastWarrior Effect Monster
Ancient Warriors - Fabulous Zhang Jun (210708231): Level 6 FIRE BeastWarrior Effect Monster
Ancient Warriors - Headstrong Xiahou Rang (211306220): Level 7 FIRE BeastWarrior Effect Monster
Ancient Warriors - Majestic Yuan Ben (212806202): Level 8 LIGHT BeastWarrior Effect Monster
Ancient Warriors - Talented Cao Zi (212906226): Level 4 FIRE BeastWarrior Effect Monster
```

## Roadmap
- Writing back to sqlite database
- Rendering card images

