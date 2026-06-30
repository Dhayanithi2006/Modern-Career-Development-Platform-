from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.assistant import AssistantMessage, AssistantSession
from app.models.user import User
from app.schemas.ai import AssistantSessionCreate, MessageCreate
from app.services.assistant_service import answer_message, create_session as create_assistant_session, list_sessions as list_assistant_sessions

router = APIRouter()


@router.post("/sessions")
def create_session(payload: AssistantSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    session = create_assistant_session(db, current_user, payload.title)
    return {"id": session.id, "user_id": current_user.id, "title": session.title}


@router.get("/sessions")
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return [{"id": session.id, "title": session.title, "created_at": session.created_at} for session in list_assistant_sessions(db, current_user)]


@router.get("/sessions/{session_id}")
def get_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    session = db.get(AssistantSession, session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant session not found")
    messages = db.scalars(select(AssistantMessage).where(AssistantMessage.session_id == session_id).order_by(AssistantMessage.created_at.asc())).all()
    return {
        "id": session.id,
        "messages": [{"id": message.id, "role": message.role, "content": message.content, "citations": message.citations} for message in messages],
    }


@router.post("/sessions/{session_id}/messages")
def send_message(session_id: int, payload: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    message = answer_message(db, current_user, session_id, payload.content)
    return {"session_id": message.session_id, "user_id": current_user.id, "reply": message.content, "citations": message.citations}
