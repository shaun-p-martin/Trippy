from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import get_subject
from app.db.session import get_db
from app.models import Traveler, Tripmate, Trip
from app.models.enums import ROLE_RANK, InviteStatus, TripmateRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_traveler(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Traveler:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        traveler_id = get_subject(credentials.credentials, expected_type="access")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    traveler = db.get(Traveler, traveler_id)
    if traveler is None or not traveler.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Traveler not found or inactive")
    return traveler


def get_tripmate_for_trip(
    trip_id: UUID,
    traveler: Traveler = Depends(get_current_traveler),
    db: Session = Depends(get_db),
) -> tuple[Trip, Tripmate]:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    mate = (
        db.query(Tripmate)
        .filter(
            Tripmate.trip_id == trip_id,
            Tripmate.traveler_id == traveler.id,
            Tripmate.invite_status == InviteStatus.accepted,
        )
        .first()
    )
    if mate is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this trip")
    return trip, mate


def require_role(min_role: TripmateRole):
    def checker(
        trip_mate: tuple[Trip, Tripmate] = Depends(get_tripmate_for_trip),
    ) -> tuple[Trip, Tripmate]:
        trip, mate = trip_mate
        if ROLE_RANK[mate.role] < ROLE_RANK[min_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return trip, mate

    return checker
