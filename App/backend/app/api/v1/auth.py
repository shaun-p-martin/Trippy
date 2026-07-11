from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_subject,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models import Traveler
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.traveler import TravelerPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(Traveler).filter(Traveler.email == body.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    traveler = Traveler(
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        display_name=body.display_name,
    )
    db.add(traveler)
    db.commit()
    db.refresh(traveler)

    return TokenResponse(
        access_token=create_access_token(traveler.id),
        refresh_token=create_refresh_token(traveler.id),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    traveler = db.query(Traveler).filter(Traveler.email == body.email.lower()).first()
    if traveler is None or not verify_password(body.password, traveler.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not traveler.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    return TokenResponse(
        access_token=create_access_token(traveler.id),
        refresh_token=create_refresh_token(traveler.id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        traveler_id = get_subject(body.refresh_token, expected_type="refresh")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    traveler = db.get(Traveler, traveler_id)
    if traveler is None or not traveler.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Traveler not found or inactive")

    return TokenResponse(
        access_token=create_access_token(traveler.id),
        refresh_token=create_refresh_token(traveler.id),
    )


# Convenience re-export type for OpenAPI consumers
__all__ = ["router", "TravelerPublic"]
