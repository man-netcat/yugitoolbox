from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Data(Base):
    __tablename__ = "datas"

    id = Column(Integer, primary_key=True)
    status = Column(Integer, name="ot")
    alias = Column(Integer)
    _archcode = Column(Integer, name="setcode")
    _type = Column(Integer, name="type")
    atk = Column(Integer)
    _def = Column(Integer, name="def")
    _level = Column(Integer, name="level")
    _race = Column(Integer, name="race")
    _attribute = Column(Integer, name="attribute")
    _category = Column(Integer, name="category")
    _genre = Column(Integer, name="genre")
    _script = Column(Integer, name="script")
    _supportcode = Column(Integer, name="support")
    _ocgdate = Column(Integer, name="ocgdate")
    _tcgdate = Column(Integer, name="tcgdate")

    relations = relationship("Relation", back_populates="card")


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String, name="desc")


class Koid(Base):
    __tablename__ = "koids"

    id = Column(Integer, primary_key=True)
    _koid = Column(Integer, name="koid")


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
