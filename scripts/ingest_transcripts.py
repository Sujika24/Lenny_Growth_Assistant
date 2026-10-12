import sys
import os
import argparse

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import settings
from app.rag.loader import TranscriptLoader
from app.rag.vector_store import TranscriptVectorStore


def main():
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast transcripts into ChromaDB")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of episodes to index (default: all)")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for embedding indexing")
    args = parser.parse_args()

    print(f"Starting ingestion from: {settings.transcripts_data_dir}")
    loader = TranscriptLoader(settings.transcripts_data_dir)
    store = TranscriptVectorStore(settings.chroma_persist_dir)

    all_files = loader.discover_transcripts()
    print(f"Total episodes found: {len(all_files)}")
    if args.limit:
        print(f"Indexing first {args.limit} episodes for fast startup...")

    chunks_batch = []
    total_chunks = 0

    for chunk in loader.load_and_chunk_all(limit=args.limit):
        chunks_batch.append(chunk)
        if len(chunks_batch) >= args.batch_size:
            count = store.ingest_chunks(chunks_batch)
            total_chunks += count
            chunks_batch = []
            print(f"Processed {total_chunks} chunks...")

    if chunks_batch:
        count = store.ingest_chunks(chunks_batch)
        total_chunks += count

    print(f"\n[DONE] Ingestion complete! Total chunks indexed in ChromaDB: {total_chunks}")
    status = store.get_status()
    print(f"Vector Store Status: {status}")


if __name__ == "__main__":
    main()
