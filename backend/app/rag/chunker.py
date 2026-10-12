import hashlib
from typing import List, Dict, Any


class TranscriptChunker:
    def __init__(self, target_chars: int = 3200, overlap_chars: int = 500):
        self.target_chars = target_chars
        self.overlap_chars = overlap_chars

    def chunk_transcript(self, episode_meta: Dict[str, Any], text: str) -> List[Dict[str, Any]]:
        """
        Splits clean transcript text into overlapping chunks,
        preserving speaker continuity and generating content hashes.
        """
        if not text:
            return []

        chunks: List[Dict[str, Any]] = []
        paragraphs = text.split("\n\n")

        current_paragraphs: List[str] = []
        current_length = 0
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            current_paragraphs.append(para)
            current_length += len(para) + 2

            if current_length >= self.target_chars:
                chunk_text = "\n\n".join(current_paragraphs)
                chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
                chunk_id = f"{episode_meta.get('slug', 'ep')}-{chunk_idx:04d}"

                chunks.append({
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_idx,
                    "text": chunk_text,
                    "content_hash": chunk_hash,
                    "guest": str(episode_meta.get("guest", "Lenny's Guest")),
                    "title": str(episode_meta.get("title", "Lenny's Podcast")),
                    "youtube_url": str(episode_meta.get("youtube_url", "")),
                    "publish_date": str(episode_meta.get("publish_date", "")),
                    "file_path": str(episode_meta.get("file_path", "")),
                })
                chunk_idx += 1

                # Slide window with overlap
                overlap_acc: List[str] = []
                overlap_len = 0
                for p in reversed(current_paragraphs):
                    overlap_acc.insert(0, p)
                    overlap_len += len(p) + 2
                    if overlap_len >= self.overlap_chars:
                        break

                current_paragraphs = overlap_acc
                current_length = overlap_len

        # Final trailing chunk if any paragraphs remain
        if current_paragraphs:
            chunk_text = "\n\n".join(current_paragraphs)
            chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
            chunk_id = f"{episode_meta.get('slug', 'ep')}-{chunk_idx:04d}"
            chunks.append({
                "chunk_id": chunk_id,
                "chunk_index": chunk_idx,
                "text": chunk_text,
                "content_hash": chunk_hash,
                "guest": str(episode_meta.get("guest", "Lenny's Guest")),
                "title": str(episode_meta.get("title", "Lenny's Podcast")),
                "youtube_url": str(episode_meta.get("youtube_url", "")),
                "publish_date": str(episode_meta.get("publish_date", "")),
                "file_path": str(episode_meta.get("file_path", "")),
            })

        return chunks
