from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.roadmap import Roadmap
from app.models.user import User
from app.schemas.ai import RoadmapCreate
from app.services.roadmap_service import generate_roadmap as generate_roadmap_service

router = APIRouter()


@router.post("/generate")
def generate_roadmap(payload: RoadmapCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    roadmap = generate_roadmap_service(db, current_user, payload.target_role, payload.duration_weeks)
    return {"id": roadmap.id, "title": roadmap.title, "target_role": roadmap.target_role, "duration_weeks": roadmap.duration_weeks, **roadmap.roadmap_json}


@router.get("")
def list_roadmaps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, object]]:
    roadmaps = db.scalars(select(Roadmap).where(Roadmap.user_id == current_user.id).order_by(Roadmap.created_at.desc())).all()
    return [{"id": item.id, "title": item.title, "target_role": item.target_role, "duration_weeks": item.duration_weeks, **item.roadmap_json} for item in roadmaps]


@router.get("/{roadmap_id}")
def get_roadmap(roadmap_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    roadmap = db.get(Roadmap, roadmap_id)
    if roadmap is None or roadmap.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return {"id": roadmap.id, "title": roadmap.title, "target_role": roadmap.target_role, "duration_weeks": roadmap.duration_weeks, **roadmap.roadmap_json}


@router.delete("/{roadmap_id}")
def delete_roadmap(roadmap_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    roadmap = db.get(Roadmap, roadmap_id)
    if roadmap and roadmap.user_id == current_user.id:
        db.delete(roadmap)
        db.commit()
    return {"message": "Roadmap deleted"}
