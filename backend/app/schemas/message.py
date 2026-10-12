from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class Citation(BaseModel):
    guest: str
    title: str
    episode_url: Optional[str] = None
    publish_date: Optional[str] = None
    chunk_id: Optional[str] = None
    snippet: str


class MessageBase(BaseModel):
    role: str
    content: str
    citations: Optional[List[Citation]] = []


class MessageCreate(MessageBase):
    session_id: str


class MessageResponse(MessageBase):
    id: str
    session_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
