from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ArtifactBase(BaseModel):
    title: str
    artifact_type: str  # 'markdown', 'html'
    content: str


class ArtifactCreate(ArtifactBase):
    session_id: str
    message_id: Optional[str] = None


class ArtifactResponse(ArtifactBase):
    id: str
    session_id: str
    message_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
