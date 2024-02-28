# YugiToolbox
Database wrapper and tools for Yu-Gi-Oh! databases.

## Supports
- YGO Omega database
- Custom card databases

## Features
- Searching cards, archetypes and sets by several attributes
- Creating deck objects from Omega code or YDKE
- Creating a custom card DB
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
>>> from yugitoolbox import YugiDB
>>> 
>>> customdb = YugiDB("sqlite:///db/ancientwarriors.db")
>>> 
>>> for c in customdb.cards:
...     print(c)
... 
Ancient Warriors - Heroic Zhao Long (210000229): WIND Level 4 [Beast Warrior/Effect]
Ancient Warriors - Fabulous Zhang Jun (210708231): FIRE Level 6 [Beast Warrior/Effect]
Ancient Warriors - Headstrong Xiahou Rang (211306220): FIRE Level 7 [Beast Warrior/Effect]
Ancient Warriors - Majestic Yuan Ben (212806202): LIGHT Level 8 [Beast Warrior/Effect]
Ancient Warriors - Talented Cao Zi (212906226): FIRE Level 4 [Beast Warrior/Effect]
```

### Creating Custom Cards
```py
from yugitoolbox import *
db = OmegaDB("auto")

a = db.get_archetype_by_name("Graydle")

graydle_hydra = Card(id=9212239385, name="Graydle Hydra")

graydle_hydra.text = """2+ monsters, including a "Graydle" Monster
(Quick Effect): You can target up to three monsters your opponent controls. Move them to the zones this card points to.
If this card in your Monster Zone is destroyed by battle or your opponent's Spell, Trap or monster effect, place this card in the Spell & Trap zone, and if you do, take control of as many monsters your opponent controls that this card pointed to while in the monster zone and place them in the zones this card in the Spell & Trap zone points to. When this card leaves the field, destroy all cards this card pointed to in the Spell & Trap zone.
You can only use each effect of "Graydle Hydra" once per turn."""
graydle_hydra.type = [Type.Monster, Type.Link, Type.Effect]
graydle_hydra.linkmarkers = [LinkMarker.Top, LinkMarker.TopLeft, LinkMarker.TopRight]
graydle_hydra.level = len(graydle_hydra.linkmarkers)
graydle_hydra.atk = 3000
graydle_hydra.race = Race.Aqua
graydle_hydra.attribute = Attribute.WATER
graydle_hydra.archetypes = [a.id]


db.write_card_to_database(graydle_hydra)
```

### Rendering card images
Note: this is a work in progress. Rendering text is currently not fully functional.
```py
>>> for card in customdb.get_cards():
...     card.render()
```
Examples:

![Stardust Dragon](https://raw.githubusercontent.com/man-netcat/yugitoolbox/main/example_renders/44508094.png)
![Hundred Eyes Dragon](https://raw.githubusercontent.com/man-netcat/yugitoolbox/main/example_renders/100000150.png)

Custom card render example:

![Ancient Warriors - Majestic Yuan Ben](https://raw.githubusercontent.com/man-netcat/yugitoolbox/main/example_renders/212806202.png)

