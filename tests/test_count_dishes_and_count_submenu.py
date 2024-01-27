import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from DataBase.models import *

from DataBase.Base import Base, get_db
from main import app


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:sirok123@localhost:5433/test_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    yield TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


def test_clear_database(db_session):
    db_session.query(Menu).delete()
    db_session.commit()


'''
Проверка кол-ва блюд и подменю в меню:
POST Создает меню
POST Создает подменю
POST Создает блюдо 1
POST Создает блюдо 2
GET Просматривает определенное меню
GET Просматривает определенное подменю
DEL Удаляет подменю
GET Просматривает список подменю
GET Просматривает список блюд
GET Просматривает определенное меню
DEL Удаляет меню
GET Просматривает список меню
'''


def test_create_menu_1(client):
    response = client.post(
        "/api/v1/menus",
        json={"title": "My menu title 1", "description": "My menu description 1"},
    )
    assert response.status_code == 201
    assert response.json()["id"] is not None


def test_create_submenu_1(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    response = client.post(
        f"/api/v1/menus/{menu.id}/submenus",
        json={"title": "My submenu title 1", "description": "My submenu description 1", "menu_id": f"{menu.id}"},
    )
    assert response.status_code == 201
    assert response.json()["id"] is not None


def test_create_dish_1(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    response = client.post(
        f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes",
        json={"title": "My dish 2",
              "description": "My dish description 2",
              "submenu_id": f"{submenu.id}",
              "price": "13.50"},
    )
    assert response.status_code == 201


def test_create_dish_2(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    response = client.post(
        f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes",
        json={"title": "My dish 1",
              "description": "My dish description 1",
              "submenu_id": f"{submenu.id}",
              "price": "12.50"},
    )
    assert response.status_code == 201


def test_get_menu_1(client, db_session):
    test_menu = db_session.query(Menu).order_by(Menu.id.desc()).first()

    response = client.get(f"/api/v1/menus/{test_menu.id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": f"{test_menu.id}",
        "title": "My menu title 1",
        "description": "My menu description 1",
        "submenus_count": 1,
        "dishes_count": 2}


def test_get_submenu_1(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    submenu = db_session.query(Submenu).filter_by(menu_id=menu.id).first()
    response = client.get(f"/api/v1/menus/{menu.id}/submenus/{submenu.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": f"{submenu.id}",
        "title": "My submenu title 1",
        "description": "My submenu description 1",
        "dishes_count": 2
    }


def test_delete_submenu(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    submenu = db_session.query(Submenu).filter_by(menu_id=menu.id).order_by(Submenu.id.desc()).first()

    response = client.delete(f"/api/v1/menus/{menu.id}/submenus/{submenu.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Submenu deleted successfully"}


def test_read_submenus(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    submenu = db_session.query(Submenu).filter_by(menu_id=menu.id).all()

    response = client.get(f"/api/v1/menus/{menu.id}/submenus")

    assert response.status_code == 200
    assert len(submenu) == 0


def test_read_dishes(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    submenu = db_session.query(Submenu).filter_by(menu_id=menu.id).order_by(Submenu.id.desc()).first()

    if submenu is None:
        response = client.get(f"/api/v1/menus/{menu.id}/submenus/0/dishes")
    else:
        response = client.get(f"/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes")

    assert response.status_code == 200
    assert response.json() == []


def test_get_menu(client, db_session):
    test_menu = db_session.query(Menu).order_by(Menu.id.desc()).first()

    response = client.get(f"/api/v1/menus/{test_menu.id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": f"{test_menu.id}",
        "title": "My menu title 1",
        "description": "My menu description 1",
        "submenus_count": 0,
        "dishes_count": 0
    }


def test_delete_menu(client, db_session):
    test_menu = db_session.query(Menu).order_by(Menu.id.desc()).first()

    response = client.delete(f"/api/v1/menus/{test_menu.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Menu deleted successfully"}


def test_read_menus(client, db_session):
    response = client.get("/api/v1/menus")

    assert response.status_code == 200

    menus = db_session.query(Menu).all()
    assert len(menus) == 0
    assert response.json() == []
