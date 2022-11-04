from datetime import timedelta

from fastapi import Depends, HTTPException, status, UploadFile
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from wookie_books import settings, schemas, repository, models, utils


def get_current_user(secret_key: str, algorith: str, db: Session, token: str = Depends(settings.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorith])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = repository.get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(user: models.User, password: str):
    if not user:
        return False
    if not utils.verify_password(password, user.hashed_password):
        return False
    return user


def get_access_token_for_authenticated_user(
    db: Session, username: str, password: str, access_toke_expire_minutes: int, secret_key: str, algorith: str
):
    user = repository.get_user_by_username(db=db, username=username)
    user = authenticate_user(user=user, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=access_toke_expire_minutes)
    access_token = utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires, secret_key=secret_key,
        algorith=algorith
    )
    return {"access_token": access_token, "token_type": "bearer"}


def create_user(db: Session, user: schemas.UserCreate):
    db_user = repository.get_user_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return repository.create_user(db=db, user=user)


def update_user(db: Session, user: schemas.UserUpdate, db_user: models.User):
    return repository.update_user(db=db, db_user=db_user, user_data=user.dict(exclude_unset=True))


def get_users(db: Session, skip: int, limit: int):
    users = repository.get_users(db=db, skip=skip, limit=limit)
    return users


def get_user(db: Session, user_id: int):
    db_user = repository.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def create_user_book(db: Session, book: schemas.BookCreate, user_id: int, cover_image: UploadFile, media_path: str):
    return repository.create_user_book(
        db=db, book=book, user_id=user_id, cover_image=cover_image, media_path=media_path
    )


def get_books(skip: int, limit: int, db: Session):
    return repository.get_books(db=db, skip=skip, limit=limit)


def get_book(book_id: int, db: Session):
    db_book = repository.get_book(db=db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book
