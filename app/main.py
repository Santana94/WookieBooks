from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import repository, models, schemas, utils
from app.database import SessionLocal, engine
from app import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = repository.get_user_by_username(db=db, username=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    hashed_password = utils.hash_password(form_data.password)
    if hashed_password != user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = repository.get_user_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return repository.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = repository.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = repository.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/books/", response_model=schemas.Book)
def create_book_for_user(
    user_id: int, cover_image: UploadFile, book: schemas.BookCreate = Depends(), db: Session = Depends(get_db),
    token: str = Depends(settings.oauth2_scheme)
):
    return repository.create_user_book(db=db, book=book, user_id=user_id, cover_image=cover_image)


@app.get("/books/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = repository.get_books(db=db, skip=skip, limit=limit)
    return books


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
