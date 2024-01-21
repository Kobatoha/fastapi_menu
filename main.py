from fastapi import FastAPI, HTTPException
from DataBase.Base import Base
from DataBase.Menu import Menu, Submenu, Dish
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL
from pydantic import BaseModel
import uuid

app = FastAPI(
    title='Menu App'
)

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)


class MenuCreate(BaseModel):
    title: str
    description: str


@app.post('/api/v1/menus', status_code=201)
async def create_menu(menu: MenuCreate):
    with Session() as session:
        menu_id = str(uuid.uuid4())
        db_menu = Menu(id=menu_id, title=menu.title, description=menu.description)
        session.add(db_menu)
        session.commit()
        session.refresh(db_menu)
        return db_menu.__dict__


@app.get('/api/v1/menus')
async def get_menus():
    session = Session()
    menus = session.query(Menu).all()
    session.close()
    return menus
