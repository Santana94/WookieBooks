import os
import shutil
from datetime import datetime, timedelta
from typing import Union

from fastapi import UploadFile
from jose import jwt
from sqlalchemy.orm import Session

from app import repository
from app import settings


def verify_password(plain_password: str, hashed_password: str):
    return settings.pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return settings.pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = repository.get_user_by_username(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.variables.secret_key, algorithm=settings.variables.algorith
    )
    return encoded_jwt


def get_file_path(input_file: UploadFile):
    file_path = f"{settings.variables.media_path}{input_file.filename}"
    if os.path.isfile(file_path):
        file_path = f"{file_path}-{datetime.now()}"
    return file_path


def write_file_to_media(input_file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(input_file.file, buffer)
