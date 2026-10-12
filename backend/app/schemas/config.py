from typing import List, Optional
from pydantic import BaseModel


class ProviderInfo(BaseModel):
    id: str
    name: str
    is_available: bool
    models: List[str]
    default_model: str
    description: str


class KnowledgeStatus(BaseModel):
    indexed_chunks: int
    total_episodes: int
    is_ready: bool
    persist_dir: str


class SystemConfigResponse(BaseModel):
    active_provider: str
    providers: List[ProviderInfo]
    knowledge_status: KnowledgeStatus
