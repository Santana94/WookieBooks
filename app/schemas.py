from typing import List

from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from app import repository


class BookBase(BaseModel):
    title: str
    description: str
    price: float


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    author_id: int
    cover_image: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    books: List[Book] = []

    class Config:
        orm_mode = True
