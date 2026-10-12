import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(32), nullable=False)  # 'markdown', 'html'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    session = relationship("SessionModel", back_populates="artifacts")
    message = relationship("MessageModel", back_populates="artifacts")
