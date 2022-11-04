from fastapi import Depends, HTTPException, status
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
