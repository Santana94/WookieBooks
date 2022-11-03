from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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
engine = create_engine(
    Settings().sql_alchemy_database_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
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


def get_settings():
    settings = Settings()
    yield settings


# APP INITIALIZATION
app = FastAPI()
