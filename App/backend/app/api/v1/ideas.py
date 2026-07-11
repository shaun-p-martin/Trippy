from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_traveler, get_tripmate_for_trip, require_role
from app.db.session import get_db
from app.models import Idea, IdeaComment, IdeaReaction, Traveler, Trip, Tripmate
from app.models.enums import ROLE_RANK, IdeaType, ReactionType, TripmateRole
from app.schemas.idea import (
    CommentCreate,
    CommentRead,
    IdeaCreate,
    IdeaRead,
    IdeaUpdate,
    ReactionToggleResponse,
)

router = APIRouter(tags=["ideas"])


def _display(traveler: Traveler | None) -> str | None:
    if traveler is None:
        return None
    if traveler.display_name:
        return traveler.display_name
    name = f"{traveler.first_name} {traveler.last_name}".strip()
    return name or traveler.email


def _can_edit_content(mate: Tripmate, created_by_id: UUID) -> bool:
    if mate.role == TripmateRole.administrator:
        return True
    if mate.traveler_id == created_by_id and ROLE_RANK[mate.role] >= ROLE_RANK[TripmateRole.contributor]:
        return True
    return False


def _get_idea_for_trip(db: Session, trip_id: UUID, idea_id: UUID) -> Idea:
    idea = (
        db.query(Idea)
        .options(joinedload(Idea.created_by), joinedload(Idea.reactions), joinedload(Idea.comments))
        .filter(Idea.id == idea_id, Idea.trip_id == trip_id)
        .first()
    )
    if idea is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    return idea


def _idea_read(idea: Idea, traveler_id: UUID) -> IdeaRead:
    types: list[IdeaType] = []
    for raw in idea.idea_types or []:
        try:
            types.append(IdeaType(raw) if not isinstance(raw, IdeaType) else raw)
        except ValueError:
            continue
    return IdeaRead(
        id=idea.id,
        trip_id=idea.trip_id,
        name=idea.name,
        description=idea.description,
        location_text=idea.location_text,
        apple_maps_url=idea.apple_maps_url,
        google_maps_url=idea.google_maps_url,
        idea_types=types,
        official_website=idea.official_website,
        contact_phone=idea.contact_phone,
        contact_email=idea.contact_email,
        created_by_id=idea.created_by_id,
        created_by_display=_display(idea.created_by),
        reaction_count=len(idea.reactions or []),
        comment_count=len(idea.comments or []),
        reacted_by_me=any(r.traveler_id == traveler_id for r in (idea.reactions or [])),
        created_at=idea.created_at,
        updated_at=idea.updated_at,
    )


def _comment_read(comment: IdeaComment) -> CommentRead:
    return CommentRead(
        id=comment.id,
        idea_id=comment.idea_id,
        parent_id=comment.parent_id,
        content=comment.content,
        created_by_id=comment.created_by_id,
        created_by_display=_display(comment.created_by),
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.get("/trips/{trip_id}/ideas", response_model=list[IdeaRead])
def list_ideas(
    idea_type: IdeaType | None = Query(default=None),
    trip_mate: tuple[Trip, Tripmate] = Depends(get_tripmate_for_trip),
    db: Session = Depends(get_db),
    traveler: Traveler = Depends(get_current_traveler),
) -> list[IdeaRead]:
    trip, _ = trip_mate
    ideas = (
        db.query(Idea)
        .options(joinedload(Idea.created_by), joinedload(Idea.reactions), joinedload(Idea.comments))
        .filter(Idea.trip_id == trip.id)
        .order_by(Idea.created_at.desc())
        .all()
    )
    results = [_idea_read(idea, traveler.id) for idea in ideas]
    if idea_type is not None:
        results = [i for i in results if idea_type in i.idea_types]
    return results


@router.post("/trips/{trip_id}/ideas", response_model=IdeaRead, status_code=status.HTTP_201_CREATED)
def create_idea(
    body: IdeaCreate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.contributor)),
    db: Session = Depends(get_db),
    traveler: Traveler = Depends(get_current_traveler),
) -> IdeaRead:
    trip, _ = trip_mate
    idea = Idea(
        trip_id=trip.id,
        name=body.name,
        description=body.description,
        location_text=body.location_text,
        apple_maps_url=body.apple_maps_url,
        google_maps_url=body.google_maps_url,
        idea_types=[t.value for t in body.idea_types],
        official_website=body.official_website,
        contact_phone=body.contact_phone,
        contact_email=str(body.contact_email) if body.contact_email else None,
        created_by_id=traveler.id,
    )
    db.add(idea)
    db.commit()
    idea = _get_idea_for_trip(db, trip.id, idea.id)
    return _idea_read(idea, traveler.id)


@router.get("/trips/{trip_id}/ideas/{idea_id}", response_model=IdeaRead)
def get_idea(
    idea_id: UUID,
    trip_mate: tuple[Trip, Tripmate] = Depends(get_tripmate_for_trip),
    db: Session = Depends(get_db),
    traveler: Traveler = Depends(get_current_traveler),
) -> IdeaRead:
    trip, _ = trip_mate
    idea = _get_idea_for_trip(db, trip.id, idea_id)
    return _idea_read(idea, traveler.id)


@router.patch("/trips/{trip_id}/ideas/{idea_id}", response_model=IdeaRead)
def update_idea(
    idea_id: UUID,
    body: IdeaUpdate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.contributor)),
    db: Session = Depends(get_db),
    traveler: Traveler = Depends(get_current_traveler),
) -> IdeaRead:
    trip, mate = trip_mate
    idea = _get_idea_for_trip(db, trip.id, idea_id)
    if not _can_edit_content(mate, idea.created_by_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit this idea")

    data = body.model_dump(exclude_unset=True)
    if "idea_types" in data and data["idea_types"] is not None:
        data["idea_types"] = [t.value if isinstance(t, IdeaType) else t for t in data["idea_types"]]
    if "contact_email" in data and data["contact_email"] is not None:
        data["contact_email"] = str(data["contact_email"])
    for key, value in data.items():
        setattr(idea, key, value)
    db.add(idea)
    db.commit()
    idea = _get_idea_for_trip(db, trip.id, idea_id)
    return _idea_read(idea, traveler.id)


@router.delete("/trips/{trip_id}/ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(
    idea_id: UUID,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.contributor)),
    db: Session = Depends(get_db),
) -> None:
    trip, mate = trip_mate
    idea = _get_idea_for_trip(db, trip.id, idea_id)
    if not _can_edit_content(mate, idea.created_by_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete this idea")
    db.delete(idea)
    db.commit()


@router.get("/trips/{trip_id}/ideas/{idea_id}/comments", response_model=list[CommentRead])
def list_comments(
    idea_id: UUID,
    trip_mate: tuple[Trip, Tripmate] = Depends(get_tripmate_for_trip),
    db: Session = Depends(get_db),
) -> list[CommentRead]:
    trip, _ = trip_mate
    _get_idea_for_trip(db, trip.id, idea_id)
    comments = (
        db.query(IdeaComment)
        .options(joinedload(IdeaComment.created_by))
        .filter(IdeaComment.idea_id == idea_id)
        .order_by(IdeaComment.created_at.asc())
        .all()
    )
    return [_comment_read(c) for c in comments]


@router.post(
    "/trips/{trip_id}/ideas/{idea_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    idea_id: UUID,
    body: CommentCreate,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.commenter)),
    db: Session = Depends(get_db),
    traveler: Traveler = Depends(get_current_traveler),
) -> CommentRead:
    trip, _ = trip_mate
    _get_idea_for_trip(db, trip.id, idea_id)

    if body.parent_id is not None:
        parent = (
            db.query(IdeaComment)
            .filter(IdeaComment.id == body.parent_id, IdeaComment.idea_id == idea_id)
            .first()
        )
        if parent is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent comment not found")

    comment = IdeaComment(
        idea_id=idea_id,
        parent_id=body.parent_id,
        content=body.content,
        created_by_id=traveler.id,
    )
    db.add(comment)
    db.commit()
    comment = (
        db.query(IdeaComment)
        .options(joinedload(IdeaComment.created_by))
        .filter(IdeaComment.id == comment.id)
        .first()
    )
    assert comment is not None
    return _comment_read(comment)


@router.delete(
    "/trips/{trip_id}/ideas/{idea_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    idea_id: UUID,
    comment_id: UUID,
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.commenter)),
    db: Session = Depends(get_db),
) -> None:
    trip, mate = trip_mate
    _get_idea_for_trip(db, trip.id, idea_id)
    comment = (
        db.query(IdeaComment)
        .filter(IdeaComment.id == comment_id, IdeaComment.idea_id == idea_id)
        .first()
    )
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if not _can_edit_content(mate, comment.created_by_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete this comment")
    db.delete(comment)
    db.commit()


@router.post(
    "/trips/{trip_id}/ideas/{idea_id}/reactions",
    response_model=ReactionToggleResponse,
)
def toggle_reaction(
    idea_id: UUID,
    reaction_type: ReactionType = Query(default=ReactionType.like),
    trip_mate: tuple[Trip, Tripmate] = Depends(require_role(TripmateRole.commenter)),
    db: Session = Depends(get_db),
    traveler: Traveler = Depends(get_current_traveler),
) -> ReactionToggleResponse:
    trip, _ = trip_mate
    idea = _get_idea_for_trip(db, trip.id, idea_id)

    existing = (
        db.query(IdeaReaction)
        .filter(
            IdeaReaction.idea_id == idea.id,
            IdeaReaction.traveler_id == traveler.id,
            IdeaReaction.reaction_type == reaction_type,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        reacted = False
    else:
        db.add(
            IdeaReaction(
                idea_id=idea.id,
                traveler_id=traveler.id,
                reaction_type=reaction_type,
            )
        )
        db.commit()
        reacted = True

    count = db.query(IdeaReaction).filter(IdeaReaction.idea_id == idea.id).count()
    return ReactionToggleResponse(
        idea_id=idea.id,
        reaction_type=reaction_type,
        reacted=reacted,
        reaction_count=count,
    )
