from fastapi import FastAPI
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Woolkie Books"
    media_path: str = "media/"


settings = Settings()
app = FastAPI()
