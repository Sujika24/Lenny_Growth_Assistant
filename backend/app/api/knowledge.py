import logging
from typing import Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.core.config import settings
from app.rag.loader import TranscriptLoader
from app.rag.vector_store import TranscriptVectorStore

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base"])


class IngestRequest(BaseModel):
    limit: Optional[int] = None
    batch_size: int = 50


def run_ingestion_task(limit: Optional[int] = None, batch_size: int = 50):
    logger.info(f"Starting transcript ingestion (limit={limit}, batch_size={batch_size})...")
    loader = TranscriptLoader(settings.transcripts_data_dir)
    vector_store = TranscriptVectorStore()

    chunks_batch = []
    total_ingested = 0

    for chunk in loader.load_and_chunk_all(limit=limit):
        chunks_batch.append(chunk)
        if len(chunks_batch) >= batch_size:
            vector_store.ingest_chunks(chunks_batch)
            total_ingested += len(chunks_batch)
            chunks_batch = []

    if chunks_batch:
        vector_store.ingest_chunks(chunks_batch)
        total_ingested += len(chunks_batch)

    logger.info(f"Ingestion finished! Total chunks ingested: {total_ingested}")


@router.get("/status")
def get_knowledge_status():
    store = TranscriptVectorStore()
    status = store.get_status()
    loader = TranscriptLoader(settings.transcripts_data_dir)
    total_episodes = len(loader.discover_transcripts())
    return {
        **status,
        "total_episodes": total_episodes
    }


@router.post("/ingest")
def trigger_ingestion(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingestion_task, limit=request.limit, batch_size=request.batch_size)
    return {
        "status": "ingestion_started",
        "limit": request.limit,
        "message": "Transcript ingestion launched in background."
    }
