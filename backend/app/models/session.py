import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="New Conversation")
    user_id = Column(String(64), nullable=False, default="anonymous")
    provider = Column(String(32), nullable=False, default="ollama")
    model_name = Column(String(64), nullable=False, default="llama3.2:3b")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")
    artifacts = relationship("ArtifactModel", back_populates="session", cascade="all, delete-orphan", order_by="ArtifactModel.created_at")
