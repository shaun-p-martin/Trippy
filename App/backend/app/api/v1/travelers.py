from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_traveler
from app.db.session import get_db
from app.models import Traveler
from app.schemas.traveler import TravelerPublic, TravelerUpdate

router = APIRouter(prefix="/travelers", tags=["travelers"])


@router.get("/me", response_model=TravelerPublic)
def get_me(traveler: Traveler = Depends(get_current_traveler)) -> Traveler:
    return traveler


@router.patch("/me", response_model=TravelerPublic)
def update_me(
    body: TravelerUpdate,
    traveler: Traveler = Depends(get_current_traveler),
    db: Session = Depends(get_db),
) -> Traveler:
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(traveler, key, value)
    db.add(traveler)
    db.commit()
    db.refresh(traveler)
    return traveler
