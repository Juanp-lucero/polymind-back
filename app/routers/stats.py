from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.stats import StatisticsResponse
from app.services.stats_service import get_user_statistics


router = APIRouter(
    prefix="/stats",
    tags=["Estadísticas"]
)


@router.get("/", response_model=StatisticsResponse)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_statistics(db, current_user.id)