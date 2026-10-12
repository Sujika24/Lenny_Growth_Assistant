from fastapi import APIRouter
from app.core.config import settings
from app.providers.factory import ProviderFactory
from app.rag.vector_store import TranscriptVectorStore
from app.rag.loader import TranscriptLoader
from app.schemas.config import SystemConfigResponse, KnowledgeStatus

router = APIRouter(prefix="/api/v1/config", tags=["Configuration"])


@router.get("", response_model=SystemConfigResponse)
async def get_system_config():
    providers_info = await ProviderFactory.get_providers_info()

    store = TranscriptVectorStore()
    vs_status = store.get_status()

    loader = TranscriptLoader(settings.transcripts_data_dir)
    total_episodes = len(loader.discover_transcripts())

    knowledge_status = KnowledgeStatus(
        indexed_chunks=vs_status["indexed_chunks"],
        total_episodes=total_episodes,
        is_ready=vs_status["is_ready"],
        persist_dir=vs_status["persist_dir"]
    )

    return SystemConfigResponse(
        active_provider=settings.default_provider,
        providers=providers_info,
        knowledge_status=knowledge_status
    )
