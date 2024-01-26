from fastapi import FastAPI, HTTPException, Depends
from DataBase.Base import Base, engine, get_db
from DataBase.models import Menu, Submenu, Dish
from DataBase.schemas import MenuCreate, SubmenuCreate, DishCreate
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from config import DB_URL
import uuid

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Menu App')


# menus
@app.post('/api/v1/menus', status_code=201)
async def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):
    with db as session:
        menu_id = str(uuid.uuid4())
        db_menu = Menu(id=menu_id, title=menu.title, description=menu.description)
        session.add(db_menu)
        session.commit()
        session.refresh(db_menu)
        return db_menu.__dict__


@app.get('/api/v1/menus')
async def get_menus(db: Session = Depends(get_db)):
    with db as session:
        menus = session.query(Menu).all()
        return menus


@app.get('/api/v1/menus/{menu_id}')
async def get_menu(menu_id: str, db: Session = Depends(get_db)):
    with db as session:
        menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail="menu not found")
        submenus = session.query(Submenu).filter(Submenu.menu_id == menu_id).all()
        submenus_count = len(submenus)
        dishes_count = sum(
            session.query(func.count(Dish.id)).filter(Dish.submenu_id == submenu.id).scalar() for submenu in submenus)
        menu_dict = {
            "id": menu.id,
            "title": menu.title,
            "description": menu.description,
            "submenus_count": submenus_count,
            "dishes_count": dishes_count
        }
        return menu_dict


@app.patch('/api/v1/menus/{menu_id}')
async def update_menu(menu_id: str, menu: MenuCreate, db: Session = Depends(get_db)):
    with db as session:
        db_menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if not db_menu:
            raise HTTPException(status_code=404, detail="menu not found")
        db_menu.title = menu.title
        db_menu.description = menu.description
        session.commit()
        menu_dict = {
            "id": menu_id,
            "title": db_menu.title,
            "description": db_menu.description,
        }
        return menu_dict


@app.delete('/api/v1/menus/{menu_id}')
async def delete_menu(menu_id: str, db: Session = Depends(get_db)):
    with db as session:
        db_menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if not db_menu:
            raise HTTPException(status_code=404, detail="menu not found")
        session.delete(db_menu)
        session.commit()
        return {"message": "Menu deleted successfully"}


# submenus
@app.get('/api/v1/menus/{menu_id}/submenus')
async def get_submenus(menu_id: str, db: Session = Depends(get_db)):
    with db as session:
        menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if not menu:
            return []
            # raise HTTPException(status_code=404, detail="menu not found")
        submenus = session.query(Submenu).filter(Submenu.menu_id == menu_id).all()
        return submenus


@app.post('/api/v1/menus/{menu_id}/submenus', status_code=201)
async def create_submenu(menu_id: str, submenu: SubmenuCreate, db: Session = Depends(get_db)):
    with db as session:
        menu = session.query(Menu).filter(Menu.id == menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail="menu not found")
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
async def get_submenu(submenu_id: str, db: Session = Depends(get_db)):
    with db as session:
        submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        if submenu is None:
            raise HTTPException(status_code=404, detail="submenu not found")
        dishes = session.query(Dish).filter(Dish.submenu_id == submenu_id).all()
        dishes_count = len(dishes)
        submenu_dict = {
            "id": submenu.id,
            "title": submenu.title,
            "description": submenu.description,
            "dishes_count": dishes_count
        }
        return submenu_dict


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def update_submenu(submenu_id: str, submenu: SubmenuCreate, db: Session = Depends(get_db)):
    with db as session:
        db_submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        if not db_submenu:
            raise HTTPException(status_code=404, detail="submenu not found")
        db_submenu.title = submenu.title
        db_submenu.description = submenu.description
        session.commit()
        submenu_dict = {
            "id": submenu_id,
            "title": db_submenu.title,
            "description": db_submenu.description,
        }
        return submenu_dict


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def delete_submenu(submenu_id: str, db: Session = Depends(get_db)):
    with db as session:
        db_submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        if not db_submenu:
            raise HTTPException(status_code=404, detail="submenu not found")
        session.delete(db_submenu)
        session.commit()
        return {"message": "Submenu deleted successfully"}


# dish
@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', status_code=201)
async def create_dish(submenu_id: str, dish: DishCreate, db: Session = Depends(get_db)):
    with db as session:
        db_submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        #if not db_submenu:
            #raise HTTPException(status_code=404, detail="submenu not found")
        dish_id = str(uuid.uuid4())
        db_dish = Dish(id=dish_id,
                       title=dish.title,
                       description=dish.description,
                       price=dish.price,
                       submenu_id=submenu_id)
        session.add(db_dish)
        session.commit()
        session.refresh(db_dish)
        return db_dish.__dict__


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')
async def get_dishes(submenu_id: str, db: Session = Depends(get_db)):
    with db as session:
        submenu = session.query(Submenu).filter(Submenu.id == submenu_id).first()
        if submenu is None:
            return []
            # raise HTTPException(status_code=404, detail="submenu not found")
        dishes = session.query(Dish).filter(Dish.submenu_id == submenu_id).all()
        return dishes


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def get_dish(submenu_id: str, dish_id: str, db: Session = Depends(get_db)):
    with db as session:
        dish = session.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if dish is None:
            raise HTTPException(status_code=404, detail="dish not found")
        dish_dict = {
            "id": dish_id,
            "title": dish.title,
            "description": dish.description,
            "price": dish.price,
            "submenu_id": submenu_id
        }
        return dish_dict


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def update_dish(submenu_id: str, dish_id: str, dish: DishCreate, db: Session = Depends(get_db)):
    with db as session:
        db_dish = session.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if db_dish is None:
            raise HTTPException(status_code=404, detail="dish not found")
        db_dish.title = dish.title
        db_dish.description = dish.description
        db_dish.price = dish.price
        session.commit()
        dish_dict = {
            "id": dish_id,
            "title": db_dish.title,
            "description": db_dish.description,
            "price": db_dish.price
        }
        return dish_dict


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def delete_dish(submenu_id: str, dish_id: str, db: Session = Depends(get_db)):
    with db as session:
        db_dish = session.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if db_dish is None:
            raise HTTPException(status_code=404, detail="dish not found")
        session.delete(db_dish)
        session.commit()
        return {"message": "Dish deleted successfully"}
