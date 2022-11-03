from typing import List, Union

from pydantic import BaseModel


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
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    books: List[Book] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
