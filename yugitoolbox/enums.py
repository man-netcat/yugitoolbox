from enum import IntEnum, IntFlag


class Type(IntFlag):
    Monster = 0x1
    Spell = 0x2
    Trap = 0x4
    Normal = 0x10
    Ritual = 0x80
    Tuner = 0x1000
    Pendulum = 0x1000000
    TrapMonster = 0x100
    SpSummon = 0x2000000
    Fusion = 0x40
    Synchro = 0x2000
    Xyz = 0x800000
    Link = 0x4000000
    Token = 0x4000
    Spirit = 0x200
    Union = 0x400
    Gemini = 0x800
    Flip = 0x200000
    Toon = 0x400000
    Effect = 0x20
    QuickPlay = 0x10000
    Continuous = 0x20000
    Equip = 0x40000
    Field = 0x80000
    Counter = 0x100000


class LinkMarker(IntFlag):
    BottomLeft = 0x01
    Bottom = 0x02
    BottomRight = 0x04
    Left = 0x08
    # Center = 0x10
    Right = 0x20
    TopLeft = 0x40
    Top = 0x80
    TopRight = 0x100


class Race(IntFlag):
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
    Highdragon = 0x10000000
    OmegaPsychic = 0x20000000
    CelestialKnight = 0x40000000
    Galaxy = 0x80000000


class Attribute(IntFlag):
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


class Genre(IntFlag):
    STDestroy = 0x1
    DestroyMonster = 0x2
    Banish = 0x4
    Graveyard = 0x8
    BacktoHand = 0x10
    BacktoDeck = 0x20
    DestroyHand = 0x40
    DestroyDeck = 0x80
    Draw = 0x100
    Search = 0x200
    Recovery = 0x400
    Position = 0x800
    Control = 0x1000
    ChangeATKDEF = 0x2000
    Piercing = 0x4000
    RepeatAttack = 0x8000
    LimitAttack = 0x10000
    DirectAttack = 0x20000
    SpecialSummon = 0x40000
    Token = 0x80000
    TypeRelated = 0x100000
    AttributeRelated = 0x200000
    DamageLP = 0x400000
    RecoverLP = 0x800000
    Destroy = 0x1000000
    Select = 0x2000000
    Counter = 0x4000000
    Gamble = 0x8000000
    FusionRelated = 0x10000000
    TunerRelated = 0x20000000
    XyzRelated = 0x40000000
    NegateEffect = 0x80000000
    RitualRelated = 0x100000000
    PendulumRelated = 0x200000000
    LinkRelated = 0x400000000
    HandTrap = 0x800000000


class Status(IntEnum):
    OCG = 1
    TCG = 2
    Legal = 3
    Illegal = 4
