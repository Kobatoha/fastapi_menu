from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from DataBase.Base import Base
import uuid
from config import DB_URL

engine = create_engine(DB_URL)


class Menu(Base):
    __tablename__ = 'menu'

    id = Column(String, default=str(uuid.uuid4()), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    submenu = relationship('Submenu', back_populates='menu', cascade='all, delete-orphan')


class Submenu(Base):
    __tablename__ = 'submenu'

    id = Column(String, default=str(uuid.uuid4()), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    menu_id = Column(String, ForeignKey('menu.id'), nullable=False)
    menu = relationship('Menu', back_populates='submenu')
    dishes = relationship('Dish', back_populates='submenu', cascade='all, delete-orphan')


class Dish(Base):
    __tablename__ = 'dish'

    id = Column(String, default=str(uuid.uuid4()), primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(precision=8, scale=2), nullable=False)
    submenu_id = Column(String, ForeignKey('submenu.id'), nullable=False)
    submenu = relationship('Submenu', back_populates='dishes')


Base.metadata.create_all(engine)
