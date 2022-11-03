import os
import shutil
from datetime import datetime, timedelta
from typing import Union

from fastapi import UploadFile
from jose import jwt

from wookie_books import models
from wookie_books import settings


def verify_password(plain_password: str, hashed_password: str):
    return settings.pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return settings.pwd_context.hash(password)


def authenticate_user(user: models.User, password: str):
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, secret_key: str, algorith: str, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=secret_key, algorithm=algorith)
    return encoded_jwt


def get_file_path(input_file: UploadFile, media_path: str):
    file_path = f"{media_path}{input_file.filename}"
    if os.path.isfile(file_path):
        file_path = f"{file_path}-{datetime.now()}"
    return file_path


def write_file_to_media(input_file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(input_file.file, buffer)
