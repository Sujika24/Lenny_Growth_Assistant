from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.providers.factory import ProviderFactory
from app.rag.vector_store import TranscriptVectorStore

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Returns basic process liveness status."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Lenny Growth Assistant Backend"
    }


@router.get("/ready")
async def get_readiness(db: Session = Depends(get_db)):
    """Checks all backend dependencies: database, vector store, and LLM providers."""
    # 1. Database check
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # 2. Ollama check
    ollama_ok = False
    try:
        ollama = ProviderFactory.get_provider("ollama")
        ollama_ok = await ollama.is_available()
    except Exception:
        ollama_ok = False

    # 3. Vector Store check
    vs_status = {"indexed_chunks": 0, "is_ready": False}
    try:
        store = TranscriptVectorStore()
        vs_status = store.get_status()
    except Exception:
        pass

    all_ready = db_ok and (vs_status.get("indexed_chunks", 0) >= 0)

    return {
        "status": "ready" if all_ready else "degraded",
        "database": db_ok,
        "ollama": ollama_ok,
        "knowledge_base": vs_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
