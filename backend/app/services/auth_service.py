from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.repositories.user_repository import create_user, get_user_by_email
from app.schemas.auth import Token, UserCreate


def register_user(db: Session, payload: UserCreate) -> Token:
    print("REGISTER STARTED")
    print("EMAIL:", payload.email)
    print("PASSWORD:", payload.password)
    print("PASSWORD LENGTH:", len(payload.password))

    if get_user_by_email(db, payload.email):
        print("EMAIL EXISTS")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    print("HASHING PASSWORD")

    password_hash = get_password_hash(payload.password) # getting error here

    print("HASH CREATED:", password_hash[:20])

    user = create_user(
        db,
        email=payload.email,
        password_hash=password_hash,
        full_name=payload.full_name,
    )

    print("USER CREATED:", user.id)

    return build_token_response(user)

def authenticate_user(db: Session, email: str, password: str) -> Token:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    return build_token_response(user)


def build_token_response(user) -> Token:
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user,
    )
