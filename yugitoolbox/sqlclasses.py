from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Data(Base):
    __tablename__ = "datas"

    id = Column(Integer, primary_key=True)
    status = Column(Integer, name="ot")
    alias = Column(Integer)
    archcode = Column(Integer, name="setcode")
    type = Column(Integer)
    atk = Column(Integer)
    def_ = Column(Integer, name="def")
    level = Column(Integer)
    race = Column(Integer)
    attribute = Column(Integer)
    category = Column(Integer)
    genre = Column(Integer)
    script = Column(Integer)
    supportcode = Column(Integer, name="support")
    ocgdate = Column(Integer)
    tcgdate = Column(Integer)

    relations = relationship("Relation", back_populates="card")


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String, name="desc")


class Koid(Base):
    __tablename__ = "koids"

    id = Column(Integer, primary_key=True)
    koid = Column(Integer, name="koid")


class SetCode(Base):
    __tablename__ = "setcodes"

    name = Column(String)
    officialcode = Column(Integer, primary_key=True)
    betacode = Column(Integer, primary_key=True)


class Pack(Base):
    __tablename__ = "packs"

    id = Column(Integer, primary_key=True)
    abbr = Column(String)
    name = Column(String)
    ocgdate = Column(Integer)
    tcgdate = Column(Integer)

    relations = relationship("Relation", back_populates="pack")


class Relation(Base):
    __tablename__ = "relations"

    id = Column(Integer, primary_key=True)
    cardid = Column(Integer, ForeignKey("datas.id"))
    packid = Column(Integer, ForeignKey("packs.id"))

    card = relationship("Data", back_populates="relations")
    pack = relationship("Pack", back_populates="relations")
