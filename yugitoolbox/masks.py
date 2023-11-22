type_mask = {
    0x0: "None",
    0x1: "Monster",
    0x2: "Spell",
    0x4: "Trap",
    0x8: "Unknown",
    0x10: "Normal",
    0x20: "Effect",
    0x40: "Fusion",
    0x80: "Ritual",
    0x100: "TrapMonster",
    0x200: "Spirit",
    0x400: "Union",
    0x800: "Gemini",
    0x1000: "Tuner",
    0x2000: "Synchro",
    0x4000: "Token",
    0x8000: "Unknown",
    0x10000: "QuickPlay",
    0x20000: "Continuous",
    0x40000: "Equip",
    0x80000: "Field",
    0x100000: "Counter",
    0x200000: "Flip",
    0x400000: "Toon",
    0x800000: "Xyz",
    0x1000000: "Pendulum",
    0x2000000: "SpSummon",
    0x4000000: "Link",
}

linkmarker_mask = {
    0x01: "BottomLeft",
    0x02: "Bottom",
    0x04: "BottomRight",
    0x08: "Left",
    0x10: "Center",
    0x20: "Right",
    0x40: "TopLeft",
    0x80: "Top",
    0x100: "TopRight",
}

race_mask = {
    0x0: "?",
    0x1: "Warrior",
    0x2: "Spellcaster",
    0x4: "Fairy",
    0x8: "Fiend",
    0x10: "Zombie",
    0x20: "Machine",
    0x40: "Aqua",
    0x80: "Pyro",
    0x100: "Rock",
    0x200: "Winged Beast",
    0x400: "Plant",
    0x800: "Insect",
    0x1000: "Thunder",
    0x2000: "Dragon",
    0x4000: "Beast",
    0x8000: "Beast Warrior",
    0x10000: "Dinosaur",
    0x20000: "Fish",
    0x40000: "Sea Serpent",
    0x80000: "Reptile",
    0x100000: "Psychic",
    0x200000: "Divine Beast",
    0x400000: "Creator God",
    0x800000: "Wyrm",
    0x1000000: "Cyberse",
    0x2000000: "Illusion",
    0x4000000: "Cyborg",
    0x8000000: "Magical Knight",
    0x10000000: "Hydragon",
    0x20000000: "Omega Psycho",
    0x40000000: "Celestial Knight",
    0x80000000: "Galaxy",
}

attribute_mask = {
    0x00: "?",
    0x01: "EARTH",
    0x02: "WATER",
    0x04: "FIRE",
    0x08: "WIND",
    0x10: "LIGHT",
    0x20: "DARK",
    0x40: "DIVINE",
}

category_mask = {
    0x1: "SkillCard",
    0x2: "SpeedSpellCard",
    0x4: "BossCard",
    0x8: "BetaCard",
    0x10: "ActionCard",
    0x20: "CommandCard",
    0x40: "DoubleScript",
    0x80: "RushLegendary",
    0x100: "PreErrata",
    0x200: "DarkCard",
    0x400: "DuelLinks",
    0x800: "RushCard",
    0x1000: "StartCard",
    0x2000: "OneCard",
    0x4000: "TwoCard",
    0x8000: "ThreeCard",
    0x10000: "LevelZero",
    0x20000: "TreatedAs",
    0x40000: "BlueGod",
    0x80000: "YellowGod",
    0x100000: "RedGod",
    0x200000: "RushMax",
    0x400000: "SC",
}

ot_mask = ["OCG", "TCG", "Legal", "Illegal"]


def apply_mask(value: int, mask: dict[int, str]):
    return [k for v, k in mask.items() if value & v]


def parse_pendulum(value: int):
    lscale = (value & 0xFF000000) >> 24
    rscale = (value & 0x00FF0000) >> 16
    level = value & 0x0000FFFF
    return lscale, rscale, level
