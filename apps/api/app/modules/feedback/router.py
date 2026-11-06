from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import ProductFeedback, User
from app.schemas.common import MessageOut
from app.services.analytics import track

router = APIRouter(tags=["feedback"])


class FeedbackIn(BaseModel):
    message: str = Field(min_length=5, max_length=5000)
    category: str = Field(default="general", max_length=64)
    email: EmailStr | None = None


@router.post("/feedback", response_model=MessageOut)
def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)) -> MessageOut:
    row = ProductFeedback(
        user_id=None,
        email=str(payload.email) if payload.email else None,
        category=payload.category,
        message=payload.message,
        status="open",
    )
    db.add(row)
    track(db, event_name="beta_feedback_submitted", properties={"category": payload.category})
    db.commit()
    return MessageOut(message="Thanks — feedback received for the beta.")


@router.post("/feedback/authenticated", response_model=MessageOut)
def submit_feedback_auth(
    payload: FeedbackIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageOut:
    row = ProductFeedback(
        user_id=user.id,
        email=str(payload.email) if payload.email else user.email,
        category=payload.category,
        message=payload.message,
        status="open",
    )
    db.add(row)
    track(db, user_id=user.id, event_name="beta_feedback_submitted", properties={"category": payload.category})
    db.commit()
    return MessageOut(message="Thanks — feedback received for the beta.")
