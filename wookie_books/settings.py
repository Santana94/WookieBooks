from functools import lru_cache

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wookie_books.models import Base


class Settings(BaseSettings):
    app_name: str = "Woolkie Books"
    media_path: str = "media/"
    secret_key: str
    algorith: str
    sql_alchemy_database_url: str
    access_toke_expire_minutes = 30

    class Config:
        env_file = ".env"


# DATABASE
sql_alchemy_base_url = Settings().sql_alchemy_database_url
engine_args = {}
if "sqlite" in sql_alchemy_base_url:
    engine_args = {"connect_args": {"check_same_thread": False}}
engine = create_engine(sql_alchemy_base_url, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# AUTHENTICATION
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# DEPENDENCY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache()
def get_settings():
    return Settings()


# APP INITIALIZATION
app = FastAPI()
