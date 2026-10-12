import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.core.config import settings
    from app.database.database import init_db, get_engine
    from app.main import app
    from app.rag.loader import TranscriptLoader
    from app.rag.vector_store import TranscriptVectorStore

    print(f"Loaded settings. App env: {settings.app_env}")
    init_db()
    print("Database tables initialized successfully.")

    loader = TranscriptLoader(settings.transcripts_data_dir)
    transcripts = loader.discover_transcripts()
    print(f"Discovered {len(transcripts)} podcast transcripts in {settings.transcripts_data_dir}")

    store = TranscriptVectorStore()
    status = store.get_status()
    print(f"ChromaDB status: {status}")

    print("ALL CORE BACKEND MODULES VERIFIED SUCCESSFULLY!")
except Exception as e:
    print(f"FAILED TO VERIFY: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
