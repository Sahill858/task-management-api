from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.services.user import create_user, get_user_by_email
from app.dependencies import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)

from datetime import datetime, timedelta, timezone

from app.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.models.refresh_token import RefreshToken

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    return create_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(User).where(User.email == login_data.email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    refresh_token_record = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(refresh_token_record)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }

@router.post("/refresh")
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        user_id = decode_refresh_token(
            token_data.refresh_token
        )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    result = db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token_data.refresh_token
        )
    )

    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found",
        )

    if stored_token.is_revoked:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked",
        )

    if stored_token.expires_at < datetime.now(timezone.utc).replace(
        tzinfo=None
    ):
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
        )

    if stored_token.user_id != user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token_data.refresh_token
        )
    )

    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    if stored_token.is_revoked:
        raise HTTPException(
            status_code=401,
            detail="Refresh token already revoked",
        )

    stored_token.is_revoked = True

    db.commit()

    return {
        "message": "Logged out successfully"
    }