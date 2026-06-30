from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import StudentProfile
from app.models.skill import Skill, StudentSkill
from app.models.user import User
from app.schemas.profile import ProfileRead, ProfileUpsert, SkillCreate, SkillRead

router = APIRouter()


@router.get("/me", response_model=ProfileRead | None)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalar(select(StudentProfile).where(StudentProfile.user_id == current_user.id))


@router.put("/me", response_model=ProfileRead)
def upsert_profile(payload: ProfileUpsert, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    if profile is None:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/skills", response_model=SkillRead)
def add_skill(payload: SkillCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    normalized = payload.name.strip().lower()
    skill = db.scalar(select(Skill).where(Skill.normalized_name == normalized))
    if skill is None:
        skill = Skill(name=payload.name.strip(), normalized_name=normalized, category=payload.category)
        db.add(skill)
        db.flush()
    student_skill = StudentSkill(user_id=current_user.id, skill_id=skill.id, proficiency_level=payload.proficiency_level)
    db.add(student_skill)
    db.commit()
    return SkillRead(id=skill.id, name=skill.name, category=skill.category, proficiency_level=student_skill.proficiency_level)


@router.get("/skills", response_model=list[SkillRead])
def list_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Skill, StudentSkill).join(StudentSkill, StudentSkill.skill_id == Skill.id).where(StudentSkill.user_id == current_user.id)
    ).all()
    return [SkillRead(id=skill.id, name=skill.name, category=skill.category, proficiency_level=student_skill.proficiency_level) for skill, student_skill in rows]


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    student_skill = db.scalar(
        select(StudentSkill).where(StudentSkill.user_id == current_user.id, StudentSkill.skill_id == skill_id)
    )
    if student_skill:
        db.delete(student_skill)
        db.commit()
    return {"message": "Skill removed"}
