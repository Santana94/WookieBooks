import os
import shutil
from datetime import datetime

from fastapi import UploadFile

from app.settings import settings


def hash_password(password: str):
    return password + "notreallyhashed"


def get_file_path(input_file: UploadFile) -> str:
    file_path = f"{settings.media_path}{input_file.filename}"
    if os.path.isfile(file_path):
        file_path = f"{file_path}-{datetime.now()}"
    return file_path


def write_file_to_media(input_file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(input_file.file, buffer)
