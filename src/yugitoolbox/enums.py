from enum import IntEnum, IntFlag


class Type(IntFlag):
    NoneType = 0x0
    Monster = 0x1
    Spell = 0x2
    Trap = 0x4
    Unknown = 0x8
    Normal = 0x10
    Effect = 0x20
    Fusion = 0x40
    Ritual = 0x80
    TrapMonster = 0x100
    Spirit = 0x200
    Union = 0x400
    Gemini = 0x800
    Tuner = 0x1000
    Synchro = 0x2000
    Token = 0x4000
    Unknown2 = 0x8000
    QuickPlay = 0x10000
    Continuous = 0x20000
    Equip = 0x40000
    Field = 0x80000
    Counter = 0x100000
    Flip = 0x200000
    Toon = 0x400000
    Xyz = 0x800000
    Pendulum = 0x1000000
    SpSummon = 0x2000000
    Link = 0x4000000


class LinkMarker(IntFlag):
    BottomLeft = 0x01
    Bottom = 0x02
    BottomRight = 0x04
    Left = 0x08
    Center = 0x10
    Right = 0x20
    TopLeft = 0x40
    Top = 0x80
    TopRight = 0x100


class Race(IntFlag):
    Unknown = 0x0
    Warrior = 0x1
    Spellcaster = 0x2
    Fairy = 0x4
    Fiend = 0x8
    Zombie = 0x10
    Machine = 0x20
    Aqua = 0x40
    Pyro = 0x80
    Rock = 0x100
    WingedBeast = 0x200
    Plant = 0x400
    Insect = 0x800
    Thunder = 0x1000
    Dragon = 0x2000
    Beast = 0x4000
    BeastWarrior = 0x8000
    Dinosaur = 0x10000
    Fish = 0x20000
    SeaSerpent = 0x40000
    Reptile = 0x80000
    Psychic = 0x100000
    DivineBeast = 0x200000
    CreatorGod = 0x400000
    Wyrm = 0x800000
    Cyberse = 0x1000000
    Illusion = 0x2000000
    Cyborg = 0x4000000
    MagicalKnight = 0x8000000
    Hydragon = 0x10000000
    OmegaPsycho = 0x20000000
    CelestialKnight = 0x40000000
    Galaxy = -0x80000000


class Attribute(IntFlag):
    Unknown = 0x00
    EARTH = 0x01
    WATER = 0x02
    FIRE = 0x04
    WIND = 0x08
    LIGHT = 0x10
    DARK = 0x20
    DIVINE = 0x40


class Category(IntFlag):
    SkillCard = 0x1
    SpeedSpellCard = 0x2
    BossCard = 0x4
    BetaCard = 0x8
    ActionCard = 0x10
    CommandCard = 0x20
    DoubleScript = 0x40
    RushLegendary = 0x80
    PreErrata = 0x100
    DarkCard = 0x200
    DuelLinks = 0x400
    RushCard = 0x800
    StartCard = 0x1000
    OneCard = 0x2000
    TwoCard = 0x4000
    ThreeCard = 0x8000
    LevelZero = 0x10000
    TreatedAs = 0x20000
    BlueGod = 0x40000
    YellowGod = 0x80000
    RedGod = 0x100000
    RushMax = 0x200000
    SC = 0x400000


class OT(IntEnum):
    OCG = 1
    TCG = 2
    Legal = 3
    Illegal = 4
