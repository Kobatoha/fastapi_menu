from fastapi import FastAPI, HTTPException, Path
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


class SubmenuCreate(BaseModel):
    title: str
    description: str


# menus
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


@app.get('/api/v1/menus/{menu_id}')
async def get_menu(menu_id: str):
    with Session() as session:
        menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if menu is None:
            raise HTTPException(status_code=404, detail="menu not found")
        print(menu.title, menu.description, menu.id)
        return menu


@app.patch('/api/v1/menus/{menu_id}')
async def update_menu(menu_id: str, menu: MenuCreate):
    with Session() as session:
        db_menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if db_menu is None:
            raise HTTPException(status_code=404, detail="menu not found")
        db_menu.title = menu.title
        db_menu.description = menu.description
        session.commit()
        print(db_menu.title, db_menu.description, db_menu.id)
        return db_menu


@app.delete('/api/v1/menus/{menu_id}')
async def delete_menu(menu_id: str):
    with Session() as session:
        db_menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if db_menu is None:
            raise HTTPException(status_code=404, detail="menu not found")
        session.delete(db_menu)
        session.commit()
        return {"message": "Menu deleted successfully"}


# submenus
@app.get('/api/v1/menus/{menu_id}/submenus')
async def get_submenus(menu_id: str):
    with Session() as session:
        menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if menu is None:
            raise HTTPException(status_code=404, detail="menu not found")
        submenus = session.query(Submenu).filter(Submenu.menu_id == menu_id).all()
        return submenus


@app.post('/api/v1/menus/{menu_id}/submenus', status_code=201)
async def create_submenu(menu_id: str, submenu: SubmenuCreate):
    with Session() as session:
        submenu_id = str(uuid.uuid4())
        db_submenu = Submenu(id=submenu_id,
                             title=submenu.title,
                             description=submenu.description,
                             menu_id=menu_id)
        session.add(db_submenu)
        session.commit()
        session.refresh(db_submenu)
        return db_submenu.__dict__


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def get_submenu(submenu_id: str):
    with Session() as session:
        submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        if submenu is None:
            raise HTTPException(status_code=404, detail="submenu not found")
        print(submenu.id, submenu.title, submenu.description)
        return submenu


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def update_submenu(submenu_id: str, submenu: SubmenuCreate):
    with Session() as session:
        db_submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail="submenu not found")
        db_submenu.title = submenu.title
        db_submenu.description = submenu.description
        session.commit()
        print(db_submenu.id, db_submenu.title, db_submenu.description)
        return db_submenu


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def delete_submenu(submenu_id: str):
    with Session() as session:
        db_submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail="submenu not found")
        session.delete(db_submenu)
        session.commit()
        return {"message": "Submenu deleted successfully"}
