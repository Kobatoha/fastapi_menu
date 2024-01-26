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
    db_session.query(Dish).delete()
    db_session.query(Submenu).delete()
    db_session.query(Menu).delete()
    db_session.commit()


def test_create_menu(client):
    response = client.post(
        "/api/v1/menus",
        json={"title": "My menu title 1", "description": "My menu description 1"},
    )
    assert response.status_code == 201


def test_create_submenu(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    response = client.post(
        f"/api/v1/menus/{menu.id}/submenus",
        json={"title": "My submenu title 1", "description": "My submenu description 1", "menu_id": f"{menu.id}"},
    )
    assert response.status_code == 201


def test_create_dish(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    response = client.post(
        f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes",
        json={"title": "My dish title 1",
              "description": "My dish description 1",
              "submenu_id": f"{submenu.id}",
              "price": "3.22"},
    )
    assert response.status_code == 201


def test_get_dishes(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    dishes = db_session.query(Dish).filter_by(submenu_id=submenu.id).all()

    response = client.get(f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes")

    assert response.status_code == 200
    assert len(dishes) == 1

    assert dishes[0].title == "My dish title 1"
    assert dishes[0].description == "My dish description 1"
    assert dishes[0].id is not None
    assert dishes[0].submenu_id == submenu.id
    assert dishes[0].price == '3.22'


def test_get_dish(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    dish = db_session.query(Dish).filter_by(submenu_id=submenu.id).first()
    response = client.get(f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes/{dish.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": f"{dish.id}",
        "title": "My dish title 1",
        "description": "My dish description 1",
        "price": "3.22",
        "submenu_id": f"{submenu.id}"
    }


def test_update_dish(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    dish = db_session.query(Dish).filter_by(submenu_id=submenu.id).order_by(Dish.id.desc()).first()

    response = client.patch(
        f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes/{dish.id}",
        json={"title": "My updated dish title 1", "description": "My updated dish description 1", "price": "4.88"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": f"{dish.id}",
        "title": "My updated dish title 1",
        "description": "My updated dish description 1",
        "price": "4.88",
    }


def test_delete_dish(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    dish = db_session.query(Dish).filter_by(submenu_id=submenu.id).order_by(Dish.id.desc()).first()

    response = client.delete(f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes/{dish.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Dish deleted successfully"}


def test_read_dishes(client, db_session):
    submenu = db_session.query(Submenu).order_by(Submenu.id.desc()).first()
    dishes = db_session.query(Dish).filter_by(submenu_id=submenu.id).all()

    response = client.get(f"/api/v1/menus/{submenu.menu_id}/submenus/{submenu.id}/dishes")

    assert response.status_code == 200
    assert len(dishes) == 0
