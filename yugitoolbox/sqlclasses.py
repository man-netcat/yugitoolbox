from sqlalchemy import BLOB, Column, ForeignKey, Integer, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class Datas(Base):
    __tablename__ = "datas"

    id = Column(Integer, primary_key=True, nullable=False, default=0)
    ot = Column(Integer, nullable=False, default=0)
    alias = Column(Integer, nullable=False, default=0)
    type = Column(Integer, nullable=False, default=0)
    atk = Column(Integer, nullable=False, default=0)
    def_ = Column("def", Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=0)
    race = Column(Integer, nullable=False, default=0)
    attribute = Column(Integer, nullable=False, default=0)
    category = Column(Integer, nullable=False, default=0)
    genre = Column(Integer, nullable=False, default=0)
    script = Column(BLOB)
    # Datas.setcode is a 64-bit value consisting of 4 16-bit values,
    # each representing a Setcode.id.
    setcode = Column(Integer, nullable=False, default=0)
    # Similarly to Datas.setcode, Datas.support is a 64-bit value consisting of 4 16-bit values,
    # The first 2 values represent "support", the last two values represent "related".
    # All of them correspond to Setcode.id
    support = Column(Integer, nullable=False, default=0)
    ocgdate = Column(Integer, nullable=False, default=253402207200)
    tcgdate = Column(Integer, nullable=False, default=253402207200)

    @hybrid_property
    def archetypes(self):
        return [self.setcode.op(">>")(x).op("&")(0xFFFF) for x in [0, 16, 32, 48]]

    @hybrid_property
    def supportarchs(self):
        return [self.support.op(">>")(x).op("&")(0xFFFF) for x in [0, 16]]

    @hybrid_property
    def relatedarchs(self):
        return [self.support.op(">>")(x).op("&")(0xFFFF) for x in [36, 48]]


class Texts(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, nullable=False, default=0)
    name = Column(Text, nullable=False, default="")
    desc = Column(Text, nullable=False, default="")


class Koids(Base):
    __tablename__ = "koids"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    koid = Column(Integer, nullable=False, default=0)


class Setcodes(Base):
    __tablename__ = "setcodes"

    officialcode = Column(Integer, nullable=False, primary_key=True)
    betacode = Column(Integer, nullable=False, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    # Setcodes.cardid is the id of the card representing the archetype
    cardid = Column(Integer, nullable=False, default=0)

    @hybrid_property
    def id(self):
        return func.coalesce(self.officialcode, self.betacode)


class Packs(Base):
    __tablename__ = "packs"

    id = Column(Integer, primary_key=True, nullable=False)
    abbr = Column(Text)
    name = Column(Text)
    ocgdate = Column(Integer, nullable=False, default=253402214400)
    tcgdate = Column(Integer, nullable=False, default=253402214400)


class Relations(Base):
    __tablename__ = "relations"

    cardid = Column(
        Integer,
        ForeignKey("datas.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    packid = Column(
        Integer,
        ForeignKey("packs.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
