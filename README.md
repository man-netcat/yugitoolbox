# YugiToolbox
Database wrapper and tools for Yu-Gi-Oh! databases.

## Supports
- YGO Omega database
- Custom card databases

## Features
- Searching cards, archetypes and sets by several attributes
- Creating deck objects from Omega code or YDKE

## How to use
```py
>>> import yugitoolbox
>>> from yugitoolbox import OmegaDB
>>> db = OmegaDB()
>>> db.get_card_by_id(10497636)   
War Rock Meteoragon
>>> card = db.get_card_by_id(10497636) 
>>> card.name
'War Rock Meteoragon'
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