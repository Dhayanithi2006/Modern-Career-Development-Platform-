from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.dashboard_service import create_snapshot, get_dashboard_summary

router = APIRouter()


@router.get("/summary")
def dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    return get_dashboard_summary(db, current_user)


@router.get("/readiness")
def readiness(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    return get_dashboard_summary(db, current_user)


@router.get("/progress")
def progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    return get_dashboard_summary(db, current_user)


@router.post("/snapshot")
def snapshot(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    item = create_snapshot(db, current_user)
    return {"id": item.id, "overall_readiness_score": item.overall_readiness_score, "created_at": item.created_at}
