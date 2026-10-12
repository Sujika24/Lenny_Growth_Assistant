from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.message import MessageResponse
from app.schemas.artifact import ArtifactResponse


class SessionBase(BaseModel):
    title: Optional[str] = "New Conversation"
    provider: Optional[str] = "ollama"
    model_name: Optional[str] = "llama3.2:3b"
    user_id: Optional[str] = "anonymous"


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None


class SessionResponse(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionDetailResponse(SessionResponse):
    messages: List[MessageResponse] = []
    artifacts: List[ArtifactResponse] = []

    model_config = ConfigDict(from_attributes=True)
