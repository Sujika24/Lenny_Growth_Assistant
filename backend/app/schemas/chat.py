from typing import Optional
from pydantic import BaseModel
from app.schemas.message import MessageResponse
from app.schemas.artifact import ArtifactResponse


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    message: MessageResponse
    artifact: Optional[ArtifactResponse] = None


class EssayRequest(BaseModel):
    topic: str
    session_id: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None


class ArtifactGenerateRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    artifact_type: str = "markdown"  # 'markdown' or 'html'
    session_id: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
