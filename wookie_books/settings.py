from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseSettings

from wookie_books.database import SessionLocal


class Settings(BaseSettings):
    app_name: str = "Woolkie Books"
    media_path: str = "media/"
    secret_key: str
    algorith: str
    access_toke_expire_minutes = 30

    class Config:
        env_file = ".env"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings():
    settings = Settings()
    yield settings
