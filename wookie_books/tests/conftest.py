import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from wookie_books import repository, schemas, models
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
    connection.begin()

    # bind an individual Session to the connection
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestingSessionLocal(bind=connection)

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
def base_user_password():
    return "generic"


@pytest.fixture
def base_user(db, base_user_password):
    return repository.create_user(db=db, user=schemas.UserCreate(username="base_user", password=base_user_password))


@pytest.fixture
def create_base_books(db, mocker):
    def create_books(user_id: int):
        mocker.patch("wookie_books.utils.write_file_to_media")
        return [
            repository.create_user_book(
                db=db, user_id=user_id,
                book=schemas.BookCreate(title=f"Some Title {i}", description=f"Some Description {i}", price=10 + i),
                cover_image=UploadFile(filename="something"), media_path="some_path/"
            )
            for i in range(3)
        ]
    return create_books


@pytest.fixture
def create_book(db, mocker, base_user):
    def create_base_book(user_id: int = base_user.id):
        mocker.patch("wookie_books.utils.write_file_to_media")
        return repository.create_user_book(
            db=db, user_id=user_id,
            book=schemas.BookCreate(title=f"Some Title", description=f"Some Description", price=10),
            cover_image=UploadFile(filename="something"), media_path="some_path/"
        )
    return create_base_book


@pytest.fixture
def darth_vader_password():
    return "shmi_skywalker"


@pytest.fixture
def darth_vader(db, darth_vader_password):
    return repository.create_user(db=db, user=schemas.UserCreate(username="darth_vader", password=darth_vader_password))


@pytest.fixture
def get_auth_headers(client):
    def authenticate(username: str, password: str):
        token_data = client.post("/token", data={"username": username, "password": password}).json()
        return {"Authorization": f"{token_data['token_type'].capitalize()} {token_data['access_token']}"}
    return authenticate
