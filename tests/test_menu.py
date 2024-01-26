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


def test_create_menu(client):
    response = client.post(
        "/api/v1/menus",
        json={"title": "My menu title 1", "description": "My menu description 1"},
    )
    assert response.status_code == 201
    assert response.json()["id"] is not None


def test_get_menus(client, db_session):
    response = client.get("/api/v1/menus")

    assert response.status_code == 200

    menus = db_session.query(Menu).all()
    assert len(menus) == 1
    assert menus[0].title == "My menu title 1"
    assert menus[0].description == "My menu description 1"
    assert menus[0].id is not None


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


def test_update_menu(client, db_session):
    test_menu = db_session.query(Menu).order_by(Menu.id.desc()).first()

    response = client.patch(
        f"/api/v1/menus/{test_menu.id}",
        json={"title": "My updated menu title 1", "description": "My updated menu description 1"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": f"{test_menu.id}",
        "title": "My updated menu title 1",
        "description": "My updated menu description 1"
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


def test_clear_db(db_session):
    db_session.query(Dish).delete()
    db_session.query(Submenu).delete()
    db_session.query(Menu).delete()
    db_session.commit()
