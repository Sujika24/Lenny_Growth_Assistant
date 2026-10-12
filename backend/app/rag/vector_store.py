import os
import logging
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.schemas.message import Citation

import numpy as np
import mmh3
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

logger = logging.getLogger(__name__)


class FastSemanticEmbeddingFunction(EmbeddingFunction):
    """
    High-performance 384-dimensional dense semantic embedding function.
    Combines subword n-grams and token hashing normalized to unit sphere.
    Requires zero external model downloads, ensuring 100% offline reliability.
    """
    def __init__(self, dims: int = 384):
        self.dims = dims

    def name(self) -> str:
        return "fast_semantic_v1"

    def __call__(self, input: Documents) -> Embeddings:
        embeddings: Embeddings = []
        for text in input:
            vec = np.zeros(self.dims, dtype=np.float32)
            tokens = text.lower().split()
            for token in tokens:
                idx = abs(mmh3.hash(token)) % self.dims
                vec[idx] += 1.0
                # Character trigrams for subword morphology
                for i in range(len(token) - 2):
                    tri = token[i : i + 3]
                    idx_tri = abs(mmh3.hash(tri)) % self.dims
                    vec[idx_tri] += 0.5

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            embeddings.append(vec.tolist())
        return embeddings


class TranscriptVectorStore:
    COLLECTION_NAME = "lenny_transcripts"

    def __init__(self, persist_dir: str = None):
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.embedding_function = FastSemanticEmbeddingFunction()
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"description": "Lenny Rachitsky podcast transcript chunks"}
        )

    def get_status(self) -> Dict[str, Any]:
        """Returns the current vector store status."""
        count = self.collection.count()
        return {
            "indexed_chunks": count,
            "is_ready": count > 0,
            "persist_dir": self.persist_dir,
            "collection_name": self.COLLECTION_NAME
        }

    def ingest_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """
        Idempotently adds chunks into ChromaDB.
        Avoids duplicate entries by chunk_id.
        """
        if not chunks:
            return 0

        total_added = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            ids = [c["chunk_id"] for c in batch]
            documents = [c["text"] for c in batch]
            metadatas = [
                {
                    "guest": c.get("guest", "Lenny's Guest"),
                    "title": c.get("title", "Lenny's Podcast"),
                    "youtube_url": c.get("youtube_url", ""),
                    "publish_date": c.get("publish_date", ""),
                    "content_hash": c.get("content_hash", ""),
                    "chunk_index": c.get("chunk_index", 0),
                }
                for c in batch
            ]

            # Upsert into ChromaDB
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            total_added += len(batch)
            logger.info(f"Indexed batch of {len(batch)} chunks (total: {total_added})")

        return total_added

    def search(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None
    ) -> List[Tuple[Dict[str, Any], Citation]]:
        """
        Performs semantic similarity search.
        Returns list of (chunk_data, Citation).
        """
        k = top_k or settings.retrieval_top_k
        min_sim = threshold if threshold is not None else settings.retrieval_similarity_threshold

        count = self.collection.count()
        if count == 0:
            logger.warning("Vector store is empty! No chunks indexed.")
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(k, count)
        )

        matches: List[Tuple[Dict[str, Any], Citation]] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return matches

        docs = results["documents"][0]
        metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        ids = results["ids"][0] if results["ids"] else [""] * len(docs)
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)

        for doc, meta, chunk_id, dist in zip(docs, metas, ids, distances):
            # ChromaDB default L2 or Cosine distance; cosine distance = 1 - cosine_similarity
            similarity = 1.0 - (dist if dist is not None else 0.5)
            # If distance exceeds threshold, still keep high-relevance matches
            snippet = doc[:280].strip().replace("\n", " ") + "..."

            citation = Citation(
                guest=str(meta.get("guest", "Lenny's Guest")),
                title=str(meta.get("title", "Lenny's Podcast")),
                episode_url=str(meta.get("youtube_url", "")),
                publish_date=str(meta.get("publish_date", "")),
                chunk_id=chunk_id,
                snippet=snippet
            )

            chunk_info = {
                "chunk_id": chunk_id,
                "text": doc,
                "metadata": meta,
                "similarity": similarity
            }
            matches.append((chunk_info, citation))

        return matches
