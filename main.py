from fastapi import FastAPI, HTTPException
from DataBase.Base import Base
from DataBase.Menu import Menu, Submenu, Dish
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL
from pydantic import BaseModel

app = FastAPI(
    title='Menu App'
)

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)


class MenuCreate(BaseModel):
    title: str
    description: str


@app.post('/api/v1/menus')
async def create_menu(menu: MenuCreate):
    session = Session()
    db_menu = Menu(title=menu.title, description=menu.description)
    session.add(db_menu)
    session.commit()
    session.refresh(db_menu)
    session.close()
    return db_menu
