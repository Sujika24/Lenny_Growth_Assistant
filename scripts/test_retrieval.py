import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.rag.vector_store import TranscriptVectorStore

store = TranscriptVectorStore()
matches = store.search("How does Brian Chesky prioritize features and roadmaps?", top_k=3)
print(f"Matches returned: {len(matches)}")
for chunk, cit in matches:
    print(f"Guest: {cit.guest}")
    print(f"Title: {cit.title}")
    print(f"Snippet: {cit.snippet[:140]}...")
    print(f"Similarity: {chunk.get('similarity')}")
    print("-" * 50)
