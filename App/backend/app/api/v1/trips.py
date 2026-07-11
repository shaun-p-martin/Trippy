import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_traveler, get_tripmate_for_trip, require_role
from app.db.session import get_db
from app.models import Traveler, Trip, Tripmate, TripStop
from app.models.enums import InviteStatus, TripmateRole
from app.schemas.trip import (
    InviteCreate,
    InviteCreateResponse,
    TripCreate,
    TripDetail,
    TripStopCreate,
    TripStopRead,
    TripStopUpdate,
    TripSummary,
    TripUpdate,
    TripmateRead,
    TripmateRoleUpdate,
)

router = APIRouter(tags=["trips"])


def _display_for_mate(mate: Tripmate) -> str | None:
    if mate.traveler is None:
        return mate.invite_email
    t = mate.traveler
    if t.display_name:
        return t.display_name
    name = f"{t.first_name} {t.last_name}".strip()
    return name or t.email


def _trip_summary(trip: Trip, role: TripmateRole) -> TripSummary:
    return TripSummary(
        id=trip.id,
        name=trip.name,
        description=trip.description,
        start_date=trip.start_date,
        end_date=trip.end_date,
        is_archived=trip.is_archived,
        my_role=role,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )


def _admin_count(db: Session, trip_id: UUID) -> int:
    return (
        db.query(Tripmate)
        .filter(
            Tripmate.trip_id == trip_id,
            Tripmate.role == TripmateRole.administrator,
            Tripmate.invite_status == InviteStatus.accepted,
        )
        .count()
    )


@router.get("/trips", response_model=list[TripSummary])
def list_trips(
    traveler: Traveler = Depends(get_current_traveler),
    db: Session = Depends(get_db),
) -> list[TripSummary]:
    mates = (
        db.query(Tripmate)
        .options(joinedload(Tripmate.trip))
        .filter(Tripmate.traveler_id == traveler.id, Tripmate.invite_status == InviteStatus.accepted)
        .all()
    )
    return [_trip_summary(m.trip, m.role) for m in mates if m.trip is not None]


@router.post("/trips", response_model=TripDetail, status_code=status.HTTP_201_CREATED)
def create_trip(
    body: TripCreate,
    traveler: Traveler = Depends(get_current_traveler),
    db: Session = Depends(get_db),
) -> TripDetail:
    trip = Trip(
        name=body.name,
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date,
        created_by_id=traveler.id,
    )
    db.add(trip)
    db.flush()

    mate = Tripmate(
        trip_id=trip.id,
        traveler_id=traveler.id,
        role=TripmateRole.administrator,
        invite_email=traveler.email,
        invite_status=InviteStatus.accepted,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(mate)
    db.commit()
    db.refresh(trip)

    return TripDetail(
        **_trip_summary(trip, TripmateRole.administrator).model_dump(),
        created_by_id=trip.created_by_id,
    )


@router.get("/trips/{trip_id}", response_model=TripDetail)
def get_trip(
    trip_mate: tuple[Trip, Tripmate] = Depends(get_tripmate_for_trip),
) -> TripDetail:
    trip, mate = trip_mate
    return TripDetail(
        **_trip_summary(trip, mate.role).model_dump(),
        created_by_id=trip.created_by_id,
    )


@router.patch("/trips/{trip_id}", response_model=TripDetail)
def update_trip(
    body: TripUpdate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> TripDetail:
    trip, mate = trip_mate
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(trip, key, value)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return TripDetail(
        **_trip_summary(trip, mate.role).model_dump(),
        created_by_id=trip.created_by_id,
    )


@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_trip(
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> None:
    trip, _ = trip_mate
    trip.is_archived = True
    db.add(trip)
    db.commit()


@router.get("/trips/{trip_id}/stops", response_model=list[TripStopRead])
def list_stops(
    trip_mate: tuple[Trip, Tripmate] = Depends(get_tripmate_for_trip),
    db: Session = Depends(get_db),
) -> list[TripStopRead]:
    trip, _ = trip_mate
    stops = (
        db.query(TripStop)
        .options(joinedload(TripStop.mate_dates))
        .filter(TripStop.trip_id == trip.id)
        .order_by(TripStop.sort_order)
        .all()
    )
    results: list[TripStopRead] = []
    for stop in stops:
        arrivals = [d.arrival_date for d in stop.mate_dates if d.arrival_date]
        departures = [d.departure_date for d in stop.mate_dates if d.departure_date]
        results.append(
            TripStopRead(
                id=stop.id,
                trip_id=stop.trip_id,
                location_name=stop.location_name,
                sort_order=stop.sort_order,
                earliest_arrival=min(arrivals) if arrivals else None,
                latest_departure=max(departures) if departures else None,
                created_at=stop.created_at,
                updated_at=stop.updated_at,
            )
        )
    return results


@router.post("/trips/{trip_id}/stops", response_model=TripStopRead, status_code=status.HTTP_201_CREATED)
def create_stop(
    body: TripStopCreate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> TripStopRead:
    trip, _ = trip_mate
    stop = TripStop(trip_id=trip.id, location_name=body.location_name, sort_order=body.sort_order)
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return TripStopRead(
        id=stop.id,
        trip_id=stop.trip_id,
        location_name=stop.location_name,
        sort_order=stop.sort_order,
        earliest_arrival=None,
        latest_departure=None,
        created_at=stop.created_at,
        updated_at=stop.updated_at,
    )


@router.patch("/trips/{trip_id}/stops/{stop_id}", response_model=TripStopRead)
def update_stop(
    stop_id: UUID,
    body: TripStopUpdate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> TripStopRead:
    trip, _ = trip_mate
    stop = db.query(TripStop).filter(TripStop.id == stop_id, TripStop.trip_id == trip.id).first()
    if stop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(stop, key, value)
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return TripStopRead(
        id=stop.id,
        trip_id=stop.trip_id,
        location_name=stop.location_name,
        sort_order=stop.sort_order,
        earliest_arrival=None,
        latest_departure=None,
        created_at=stop.created_at,
        updated_at=stop.updated_at,
    )


@router.delete("/trips/{trip_id}/stops/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(
    stop_id: UUID,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> None:
    trip, _ = trip_mate
    stop = db.query(TripStop).filter(TripStop.id == stop_id, TripStop.trip_id == trip.id).first()
    if stop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    db.delete(stop)
    db.commit()


@router.get("/trips/{trip_id}/tripmates", response_model=list[TripmateRead])
def list_tripmates(
    trip_mate: tuple[Trip, Tripmate] = Depends(get_tripmate_for_trip),
    db: Session = Depends(get_db),
) -> list[TripmateRead]:
    trip, _ = trip_mate
    mates = (
        db.query(Tripmate)
        .options(joinedload(Tripmate.traveler))
        .filter(Tripmate.trip_id == trip.id)
        .all()
    )
    return [
        TripmateRead(
            id=m.id,
            trip_id=m.trip_id,
            traveler_id=m.traveler_id,
            role=m.role,
            invite_email=m.invite_email,
            invite_status=m.invite_status,
            joined_at=m.joined_at,
            traveler_display=_display_for_mate(m),
        )
        for m in mates
    ]


@router.post(
    "/trips/{trip_id}/tripmates/invite",
    response_model=InviteCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def invite_tripmate(
    body: InviteCreate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> InviteCreateResponse:
    trip, _ = trip_mate
    email = body.email.lower()

    existing_traveler = db.query(Traveler).filter(Traveler.email == email).first()
    if existing_traveler:
        existing_mate = (
            db.query(Tripmate)
            .filter(Tripmate.trip_id == trip.id, Tripmate.traveler_id == existing_traveler.id)
            .first()
        )
        if existing_mate and existing_mate.invite_status != InviteStatus.revoked:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a tripmate")

    token = secrets.token_urlsafe(24)
    mate = Tripmate(
        trip_id=trip.id,
        traveler_id=existing_traveler.id if existing_traveler else None,
        role=body.role,
        invite_email=email,
        invite_token=token,
        invite_status=InviteStatus.pending,
    )
    db.add(mate)
    db.commit()
    db.refresh(mate)
    if existing_traveler:
        mate.traveler = existing_traveler

    read = TripmateRead(
        id=mate.id,
        trip_id=mate.trip_id,
        traveler_id=mate.traveler_id,
        role=mate.role,
        invite_email=mate.invite_email,
        invite_status=mate.invite_status,
        joined_at=mate.joined_at,
        traveler_display=_display_for_mate(mate),
    )
    return InviteCreateResponse(tripmate=read, invite_token=token)


@router.patch("/trips/{trip_id}/tripmates/{mate_id}", response_model=TripmateRead)
def update_tripmate_role(
    mate_id: UUID,
    body: TripmateRoleUpdate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> TripmateRead:
    trip, _ = trip_mate
    mate = db.query(Tripmate).filter(Tripmate.id == mate_id, Tripmate.trip_id == trip.id).first()
    if mate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tripmate not found")

    if (
        mate.role == TripmateRole.administrator
        and body.role != TripmateRole.administrator
        and mate.invite_status == InviteStatus.accepted
        and _admin_count(db, trip.id) <= 1
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote the last administrator",
        )

    mate.role = body.role
    db.add(mate)
    db.commit()
    db.refresh(mate)
    mate = (
        db.query(Tripmate)
        .options(joinedload(Tripmate.traveler))
        .filter(Tripmate.id == mate.id)
        .first()
    )
    assert mate is not None
    return TripmateRead(
        id=mate.id,
        trip_id=mate.trip_id,
        traveler_id=mate.traveler_id,
        role=mate.role,
        invite_email=mate.invite_email,
        invite_status=mate.invite_status,
        joined_at=mate.joined_at,
        traveler_display=_display_for_mate(mate),
    )


@router.delete("/trips/{trip_id}/tripmates/{mate_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tripmate(
    mate_id: UUID,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.administrator)),
    db: Session = Depends(get_db),
) -> None:
    trip, _ = trip_mate
    mate = db.query(Tripmate).filter(Tripmate.id == mate_id, Tripmate.trip_id == trip.id).first()
    if mate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tripmate not found")

    if (
        mate.role == TripmateRole.administrator
        and mate.invite_status == InviteStatus.accepted
        and _admin_count(db, trip.id) <= 1
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the last administrator",
        )

    mate.invite_status = InviteStatus.revoked
    mate.invite_token = None
    db.add(mate)
    db.commit()


@router.post("/invites/{token}/accept", response_model=TripmateRead)
def accept_invite(
    token: str,
    traveler: Traveler = Depends(get_current_traveler),
    db: Session = Depends(get_db),
) -> TripmateRead:
    mate = db.query(Tripmate).filter(Tripmate.invite_token == token).first()
    if mate is None or mate.invite_status != InviteStatus.pending:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    if mate.invite_email and mate.invite_email.lower() != traveler.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invite email does not match authenticated traveler",
        )

    existing = (
        db.query(Tripmate)
        .filter(
            Tripmate.trip_id == mate.trip_id,
            Tripmate.traveler_id == traveler.id,
            Tripmate.invite_status == InviteStatus.accepted,
        )
        .first()
    )
    if existing and existing.id != mate.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a tripmate")

    mate.traveler_id = traveler.id
    mate.invite_status = InviteStatus.accepted
    mate.joined_at = datetime.now(timezone.utc)
    mate.invite_token = None
    db.add(mate)
    db.commit()
    db.refresh(mate)
    mate = (
        db.query(Tripmate)
        .options(joinedload(Tripmate.traveler))
        .filter(Tripmate.id == mate.id)
        .first()
    )
    assert mate is not None
    return TripmateRead(
        id=mate.id,
        trip_id=mate.trip_id,
        traveler_id=mate.traveler_id,
        role=mate.role,
        invite_email=mate.invite_email,
        invite_status=mate.invite_status,
        joined_at=mate.joined_at,
        traveler_display=_display_for_mate(mate),
    )
