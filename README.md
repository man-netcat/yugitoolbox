# YugiToolbox
Database wrapper and tools for Yu-Gi-Oh! databases.

## Supports
- YGO Omega database
- Custom card databases

## Features
- Searching cards, archetypes and sets by several attributes
- Creating deck objects from Omega code or YDKE
- Writes data to .pkl files for fast accessing
- Creating a custom card DB and writing it back to an Sqlite DB for use in simulators
- Render card images

## How to use

### Search features
```py
>>> from yugitoolbox import OmegaDB
>>> db = OmegaDB()
>>> card = db.get_card_by_id(10497636)
>>> print(card)
War Rock Meteoragon (10497636): EARTH Level 7 [Warrior/Effect]
>>> db.get_card_archetypes(card)
[War Rock]
>>> card.race.name
'Warrior'
>>> arch = db.get_archetypes_by_value("name", "War Rock")[0]
>>> arch.name
'War Rock'
>>> db.get_archetype_cards(arch)
[War Rock Meteoragon, War Rock Meteoragon, War Rock Bashileos, War Rock Bashileos, War Rock Generations, War Rock Gactos, War Rock Mountain, War Rock Orpis, War Rock Big Blow, War Rock Wento, War Rock Dignity, War Rock Ordeal, War Rock Skyler, War Rock Skyler, War Rock Medium, War Rock Fortia, War Rock Spirit, War Rock Mammud]
>>> db.get_card_sets(card)
[Lightning Overdrive, World Premiere Pack 2021]
```

### Custom DB
```py
>>> from yugitoolbox import CustomDB
>>> customdb = CustomDB("Ancient Warriors DB", "db/ancientwarriors/ancientwarriors.db")
>>> for card in customdb.cards:
...     print(card)
... 
Ancient Warriors - Heroic Zhao Long (210000229): WIND Level 4 [Beast Warrior/Effect]
Ancient Warriors - Fabulous Zhang Jun (210708231): FIRE Level 6 [Beast Warrior/Effect]
Ancient Warriors - Headstrong Xiahou Rang (211306220): FIRE Level 7 [Beast Warrior/Effect]
Ancient Warriors - Majestic Yuan Ben (212806202): LIGHT Level 8 [Beast Warrior/Effect]
Ancient Warriors - Talented Cao Zi (212906226): FIRE Level 4 [Beast Warrior/Effect]
```

### Writing CustomDB object to Sqlite DB
```py
>>> customdb.write_to_database()
```

### Rendering card images
Note: this is a work in progress.
```py
>>> for card in customdb.get_cards():
...     card.render()
```
Examples:

![Stardust Dragon](https://raw.githubusercontent.com/man-netcat/yugitoolbox/main/example_renders/44508094.png)
![Hundred Eyes Dragon](https://raw.githubusercontent.com/man-netcat/yugitoolbox/main/example_renders/100000150.png)

Custom card render example:

![Ancient Warriors - Majestic Yuan Ben](https://raw.githubusercontent.com/man-netcat/yugitoolbox/main/example_renders/212806202.png)

