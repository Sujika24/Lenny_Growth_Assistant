import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.session import SessionModel
from app.models.message import MessageModel
from app.models.artifact import ArtifactModel
from app.schemas.session import SessionCreate, SessionUpdate
from app.schemas.message import MessageCreate
from app.schemas.artifact import ArtifactCreate

logger = logging.getLogger(__name__)


class SessionService:
    @staticmethod
    def create_session(db: Session, session_in: SessionCreate) -> SessionModel:
        db_session = SessionModel(
            title=session_in.title or "New Conversation",
            provider=session_in.provider or "ollama",
            model_name=session_in.model_name or "llama3.2:3b",
            user_id=session_in.user_id or "anonymous"
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[SessionModel]:
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()

    @staticmethod
    def list_sessions(db: Session, user_id: str = "anonymous") -> List[SessionModel]:
        return (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user_id)
            .order_by(SessionModel.updated_at.desc())
            .all()
        )

    @staticmethod
    def update_session(db: Session, session_id: str, update_in: SessionUpdate) -> Optional[SessionModel]:
        db_session = SessionService.get_session(db, session_id)
        if not db_session:
            return None
        if update_in.title is not None:
            db_session.title = update_in.title
        if update_in.provider is not None:
            db_session.provider = update_in.provider
        if update_in.model_name is not None:
            db_session.model_name = update_in.model_name
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        db_session = SessionService.get_session(db, session_id)
        if not db_session:
            return False
        db.delete(db_session)
        db.commit()
        return True

    @staticmethod
    def add_message(db: Session, message_in: MessageCreate) -> MessageModel:
        citations_data = [c.model_dump() if hasattr(c, "model_dump") else c for c in message_in.citations] if message_in.citations else []
        db_msg = MessageModel(
            session_id=message_in.session_id,
            role=message_in.role,
            content=message_in.content,
            citations=citations_data
        )
        db.add(db_msg)
        # Update session timestamp
        session = SessionService.get_session(db, message_in.session_id)
        if session:
            from datetime import datetime, timezone
            session.updated_at = datetime.now(timezone.utc)
            # Auto-update session title from first user message if generic
            if session.title == "New Conversation" and message_in.role == "user":
                session.title = message_in.content[:42].strip() + ("..." if len(message_in.content) > 42 else "")
        db.commit()
        db.refresh(db_msg)
        return db_msg

    @staticmethod
    def get_messages(db: Session, session_id: str) -> List[MessageModel]:
        return (
            db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.asc())
            .all()
        )

    @staticmethod
    def add_artifact(db: Session, artifact_in: ArtifactCreate) -> ArtifactModel:
        db_art = ArtifactModel(
            session_id=artifact_in.session_id,
            message_id=artifact_in.message_id,
            title=artifact_in.title,
            artifact_type=artifact_in.artifact_type,
            content=artifact_in.content
        )
        db.add(db_art)
        db.commit()
        db.refresh(db_art)
        return db_art

    @staticmethod
    def get_artifact(db: Session, artifact_id: str) -> Optional[ArtifactModel]:
        return db.query(ArtifactModel).filter(ArtifactModel.id == artifact_id).first()
