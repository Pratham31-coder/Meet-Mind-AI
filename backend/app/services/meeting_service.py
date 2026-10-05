from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.meeting import Meeting
from backend.app.schemas.meetings import MeetingCreateYouTube


def create_meeting(db: Session, source_type: str, source_ref: str, language: str, title: str | None = None) -> Meeting:
    """Create a new meeting record in the queued state."""
    db_meeting = Meeting(
        title=title,
        source_type=source_type,
        source_ref=source_ref,
        language=language,
        status="queued",
        stage="queued",
        action_items=[],
        key_decisions=[],
        open_questions=[]
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def get_meeting(db: Session, meeting_id: str) -> Meeting | None:
    """Retrieve a meeting by its ID."""
    return db.scalars(select(Meeting).where(Meeting.id == meeting_id)).first()


def get_all_meetings(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Meeting]:
    """Retrieve all meetings, ordered by creation date descending."""
    stmt = select(Meeting).order_by(Meeting.created_at.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def update_meeting(db: Session, meeting_id: str, **kwargs) -> Meeting | None:
    """
    Update specific fields on a meeting record.
    Usage: update_meeting(db, "uuid-1234", status="processing", stage="transcribing")
    """
    db_meeting = get_meeting(db, meeting_id)
    if not db_meeting:
        return None

    for key, value in kwargs.items():
        if hasattr(db_meeting, key):
            setattr(db_meeting, key, value)

    db.commit()
    db.refresh(db_meeting)
    return db_meeting
