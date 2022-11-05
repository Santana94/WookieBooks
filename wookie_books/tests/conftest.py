import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from wookie_books import repository, schemas
from wookie_books.main import app
from wookie_books.models import Base
from wookie_books.settings import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    if not database_exists:
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()

    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual Session to the connection
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestingSessionLocal(bind=connection)
    # db = Session(db_engine)

    yield db

    db.rollback()
    connection.close()


#
@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def base_users(db):
    return [
        repository.create_user(db=db, user=schemas.UserCreate(username=f"user_{i}", password="generic"))
        for i in range(3)
    ]


@pytest.fixture
def base_user(db):
    return repository.create_user(db=db, user=schemas.UserCreate(username="base_user", password="generic"))


@pytest.fixture
def darth_vader(db):
    return repository.create_user(db=db, user=schemas.UserCreate(username="darth_vader", password="shmi_skywalker"))


@pytest.fixture
def authenticate_user(client):
    def authenticate(username: str, password: str):
        return client.post("/token", data={"username": username, "password": password}).json()
    return authenticate
