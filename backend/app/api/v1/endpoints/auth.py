from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, Token, UserCreate, UserRead
from app.services.auth_service import authenticate_user, build_token_response, register_user
from app.core.security import decode_token

router = APIRouter()


@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Token:

    return register_user(db, payload)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    return authenticate_user(db, payload.email, payload.password)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> Token:
    token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    user = db.get(User, int(token_payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return build_token_response(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Client should discard the JWT tokens."}
