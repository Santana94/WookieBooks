from datetime import timedelta
from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi import UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from wookie_books import repository, models, schemas, utils
from wookie_books import settings
from wookie_books.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(settings.get_db),
    settings_variables: settings.Settings = Depends(settings.get_settings)
):
    user = repository.get_user_by_username(db=db, username=form_data.username)
    user = utils.authenticate_user(user=user, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings_variables.access_toke_expire_minutes)
    access_token = utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires, secret_key=settings_variables.secret_key,
        algorith=settings_variables.algorith
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(settings.get_db)):
    db_user = repository.get_user_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return repository.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(settings.get_db)):
    users = repository.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(settings.get_db)):
    db_user = repository.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/books/", response_model=schemas.Book)
def create_book_for_user(
    user_id: int, cover_image: UploadFile, book: schemas.BookCreate = Depends(), db: Session = Depends(settings.get_db),
    token: str = Depends(settings.oauth2_scheme), settings_variables: settings.Settings = Depends(settings.get_settings)
):
    return repository.create_user_book(
        db=db, book=book, user_id=user_id, cover_image=cover_image, media_path=settings_variables.media_path
    )


@app.get("/books/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(settings.get_db)):
    books = repository.get_books(db=db, skip=skip, limit=limit)
    return books


@app.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(settings.get_db)):
    db_book = repository.get_book(db=db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
