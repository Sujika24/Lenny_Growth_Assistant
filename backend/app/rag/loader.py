import os
import re
from pathlib import Path
from typing import List, Dict, Any, Generator
import yaml
from app.rag.cleaner import TranscriptCleaner
from app.rag.chunker import TranscriptChunker


class TranscriptLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.cleaner = TranscriptCleaner()
        self.chunker = TranscriptChunker()

    def discover_transcripts(self) -> List[Path]:
        """Finds all transcript.md files in the episodes subdirectories."""
        if not self.data_dir.exists():
            return []
        return sorted(list(self.data_dir.glob("*/transcript.md")))

    def parse_transcript_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parses YAML frontmatter and body from a transcript file.
        Fallback parser included if frontmatter library is not installed.
        """
        raw_content = file_path.read_text(encoding="utf-8", errors="replace")
        slug = file_path.parent.name

        metadata: Dict[str, Any] = {"slug": slug, "file_path": str(file_path)}
        body = raw_content

        # Extract YAML frontmatter enclosed by '---'
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_content, re.DOTALL)
        if match:
            yaml_block, body = match.groups()
            try:
                parsed_yaml = yaml.safe_load(yaml_block)
                if isinstance(parsed_yaml, dict):
                    metadata.update(parsed_yaml)
            except Exception:
                pass

        # Clean transcript text
        cleaned_body = self.cleaner.clean(body)

        return {
            "metadata": metadata,
            "raw_text": body,
            "cleaned_text": cleaned_body,
        }

    def load_and_chunk_all(self, limit: int = None) -> Generator[Dict[str, Any], None, None]:
        """
        Discovers, parses, cleans, and chunks transcripts.
        Yields chunks ready for vector indexing.
        """
        files = self.discover_transcripts()
        if limit:
            files = files[:limit]

        for file_path in files:
            try:
                parsed = self.parse_transcript_file(file_path)
                chunks = self.chunker.chunk_transcript(parsed["metadata"], parsed["cleaned_text"])
                for chunk in chunks:
                    yield chunk
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
