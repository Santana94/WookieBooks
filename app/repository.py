from fastapi import UploadFile
from sqlalchemy.orm import Session

from . import models, schemas, utils


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()


def create_user_book(db: Session, book: schemas.BookCreate, user_id: int, cover_image: UploadFile):
    try:
        file_path = utils.get_file_path(input_file=cover_image)
        db_book = models.Book(**book.dict(), cover_image=file_path, author_id=user_id)
        db.add(db_book)
        db.commit()
        utils.write_file_to_media(input_file=cover_image, file_path=file_path)
        db.refresh(db_book)
        return db_book
    except Exception:
        db.rollback()
    finally:
        db.close()
