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


def test_get_submenus(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    submenu = db_session.query(Submenu).filter_by(menu_id=menu.id).all()

    response = client.get(f"/api/v1/menus/{menu.id}/submenus")

    assert response.status_code == 200
    assert len(submenu) == 1

    assert submenu[0].title == "My submenu title 1"
    assert submenu[0].description == "My submenu description 1"
    assert submenu[0].id is not None
    assert submenu[0].menu_id == menu.id


def test_get_submenu(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    submenu = db_session.query(Submenu).filter_by(menu_id=menu.id).first()
    response = client.get(f"/api/v1/menus/{menu.id}/submenus/{submenu.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": f"{submenu.id}",
        "title": "My submenu title 1",
        "description": "My submenu description 1",
        "dishes_count": 0
    }


def test_update_submenu(client, db_session):
    menu = db_session.query(Menu).order_by(Menu.id.desc()).first()
    submenu = db_session.query(Submenu).filter_by(menu_id=menu.id).order_by(Submenu.id.desc()).first()

    response = client.patch(
        f"/api/v1/menus/{menu.id}/submenus/{submenu.id}",
        json={"title": "My updated submenu title 1", "description": "My updated submenu description 1"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": f"{submenu.id}",
        "title": "My updated submenu title 1",
        "description": "My updated submenu description 1",
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


def test_clear_db(db_session):
    db_session.query(Dish).delete()
    db_session.query(Submenu).delete()
    db_session.query(Menu).delete()
    db_session.commit()
