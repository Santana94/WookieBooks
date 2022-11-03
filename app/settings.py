from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Woolkie Books"
    media_path: str = "media/"

    class Config:
        env_file = ".env"


settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
