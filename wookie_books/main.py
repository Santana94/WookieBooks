from typing import List

import uvicorn
from fastapi import Depends
from fastapi import UploadFile
from sqlalchemy.orm import Session

from wookie_books import schemas, services
from wookie_books import settings
from wookie_books.settings import app


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: schemas.PasswordRequestForm = Depends(), db: Session = Depends(settings.get_db),
    settings_variables: settings.Settings = Depends(settings.get_settings)
):
    return services.get_access_token_for_authenticated_user(
        db=db, username=form_data.username, password=form_data.password, secret_key=settings_variables.secret_key,
        access_toke_expire_minutes=settings_variables.access_toke_expire_minutes, algorith=settings_variables.algorith
    )


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(settings.get_db)):
    return services.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(settings.get_db)):
    return services.get_users(db=db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(settings.get_db)):
    return services.get_user(db=db, user_id=user_id)


@app.patch("/current_user/", response_model=schemas.User)
def update_user(
    user: schemas.UserUpdate, db: Session = Depends(settings.get_db),
    token: str = Depends(settings.oauth2_scheme), settings_variables: settings.Settings = Depends(settings.get_settings)
):
    db_user = services.get_current_user(
        db=db, token=token, algorith=settings_variables.algorith, secret_key=settings_variables.secret_key
    )
    return services.update_user(db=db, user=user, db_user=db_user)


@app.delete("/current_user/")
def delete_user(
    db: Session = Depends(settings.get_db), token: str = Depends(settings.oauth2_scheme),
    settings_variables: settings.Settings = Depends(settings.get_settings)
):
    db_user = services.get_current_user(
        db=db, token=token, algorith=settings_variables.algorith, secret_key=settings_variables.secret_key
    )
    services.delete_user(db=db, db_user=db_user)
    return "User deleted successfully!"


@app.post("/users/{user_id}/books/", response_model=schemas.Book)
def create_book_for_user(
    cover_image: UploadFile, book: schemas.BookCreate = Depends(), db: Session = Depends(settings.get_db),
    token: str = Depends(settings.oauth2_scheme), settings_variables: settings.Settings = Depends(settings.get_settings)
):
    db_user = services.get_current_user(
        db=db, token=token, algorith=settings_variables.algorith, secret_key=settings_variables.secret_key
    )
    return services.create_user_book(
        db=db, book=book, user_id=db_user.id, cover_image=cover_image, media_path=settings_variables.media_path
    )


@app.get("/books/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(settings.get_db)):
    return services.get_books(skip=skip, limit=limit, db=db)


@app.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(settings.get_db)):
    return services.get_book(book_id=book_id, db=db)


@app.delete("/books/{book_id}")
def delete_book(
    book_id: int, db: Session = Depends(settings.get_db), token: str = Depends(settings.oauth2_scheme),
    settings_variables: settings.Settings = Depends(settings.get_settings)
):
    db_book = services.get_book(book_id=book_id, db=db)
    db_user = services.get_current_user(
        db=db, token=token, algorith=settings_variables.algorith, secret_key=settings_variables.secret_key
    )
    services.delete_book(db_book=db_book, db_user=db_user, db=db)
    return "Book deleted successfully!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
