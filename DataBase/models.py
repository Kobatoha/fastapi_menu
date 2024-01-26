from sqlalchemy import create_engine, Column, String, ForeignKey, Float
from DataBase.Base import Base
import uuid
from config import DB_URL

engine = create_engine(DB_URL)


class Menu(Base):
    __tablename__ = 'menu'

    id = Column(String, default=str(uuid.uuid4()), primary_key=True)
    title = Column(String)
    description = Column(String)


class Submenu(Base):
    __tablename__ = 'submenu'

    id = Column(String, default=str(uuid.uuid4()), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    menu_id = Column(String, ForeignKey('menu.id', ondelete='CASCADE'))


class Dish(Base):
    __tablename__ = 'dish'

    id = Column(String, default=str(uuid.uuid4()), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    price = Column(String)
    submenu_id = Column(String, ForeignKey('submenu.id', ondelete='CASCADE'))


Base.metadata.create_all(engine)
