from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import get_current_user, require_roles
from backend.database import get_db
from backend.schemas.rating import ProviderRatingSummary, RatingCreate, RatingResponse

router = APIRouter(prefix="/ratings", tags=["ratings"])


def provider_rating_summary(db: Session, provider_id: int) -> dict:
    average, count = (
        db.query(func.avg(models.Rating.score), func.count(models.Rating.id))
        .filter(models.Rating.provider_id == provider_id)
        .one()
    )
    return {
        "provider_id": provider_id,
        "average_rating": round(float(average), 1) if average is not None else None,
        "rating_count": int(count or 0),
    }


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def submit_rating(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("user", "admin")),
):
    service_request = (
        db.query(models.ServiceRequest)
        .filter(models.ServiceRequest.id == data.request_id)
        .first()
    )
    if not service_request:
        raise HTTPException(status_code=404, detail="Service request not found")
    if service_request.status != "completed":
        raise HTTPException(status_code=400, detail="You can rate only completed charging sessions")
    if not service_request.provider_id:
        raise HTTPException(status_code=400, detail="This request does not have a provider to rate")
    if current_user.role != "admin" and service_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can rate only your own charging sessions")

    rating_user_id = service_request.user_id if current_user.role == "admin" else current_user.id
    rating = (
        db.query(models.Rating)
        .filter(models.Rating.request_id == service_request.id)
        .first()
    )
    if rating:
        rating.score = data.score
        rating.comment = data.comment
    else:
        rating = models.Rating(
            request_id=service_request.id,
            user_id=rating_user_id,
            provider_id=service_request.provider_id,
            score=data.score,
            comment=data.comment,
        )
        db.add(rating)

    db.commit()
    db.refresh(rating)
    return rating


@router.get("/provider/{provider_id}", response_model=ProviderRatingSummary)
def get_provider_rating_summary(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    provider = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider_rating_summary(db, provider_id)


@router.get("/mine", response_model=list[RatingResponse])
def get_my_ratings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("user", "admin")),
):
    query = db.query(models.Rating)
    if current_user.role != "admin":
        query = query.filter(models.Rating.user_id == current_user.id)
    return query.order_by(models.Rating.created_at.desc()).all()
