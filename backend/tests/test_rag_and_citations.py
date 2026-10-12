import pytest
from app.rag.vector_store import TranscriptVectorStore
from app.rag.cleaner import TranscriptCleaner
from app.rag.chunker import TranscriptChunker


def test_invalid_request_validation(client):
    """Test 4: Verify request validation catches missing fields and returns 422."""
    # Empty chat payload
    res = client.post("/api/v1/chat", json={})
    assert res.status_code == 422

    # Malformed artifact request (missing prompt)
    res_art = client.post("/api/v1/artifacts", json={"artifact_type": "html"})
    assert res_art.status_code == 422


def test_empty_retrieval_behavior(tmp_path):
    """Test 5: Verify vector store handles queries gracefully when empty or with no matches."""
    empty_dir = str(tmp_path / "empty_chroma")
    store = TranscriptVectorStore(persist_dir=empty_dir)
    matches = store.search("Unheard of topic xyz12345", top_k=3)
    assert matches == []


def test_source_citation_preservation():
    """Test 6: Verify chunking and citation metadata preservation."""
    chunker = TranscriptChunker(target_chars=1000, overlap_chars=200)
    meta = {
        "slug": "brian-chesky",
        "guest": "Brian Chesky",
        "title": "Brian Chesky’s new playbook",
        "youtube_url": "https://www.youtube.com/watch?v=4ef0juAMqoE",
        "publish_date": "2023-11-12",
    }
    sample_text = (
        "Brian Chesky (00:00:00): Way too many founders apologize for how they want to run the company.\n\n"
        "Lenny (00:01:00): How do you run the single roadmap?"
    )
    chunks = chunker.chunk_transcript(meta, sample_text)
    assert len(chunks) >= 1
    c = chunks[0]
    assert c["guest"] == "Brian Chesky"
    assert c["title"] == "Brian Chesky’s new playbook"
    assert "https://www.youtube.com" in c["youtube_url"]
    assert c["content_hash"] is not None


def test_cleaner_removes_sponsors():
    """Verify that sponsor advertisements are stripped from transcripts."""
    raw = (
        "Brian Chesky (00:00:00): Welcome.\n\n"
        "This episode is brought to you by Sidebar. Sidebar is an executive coaching network...\n\n"
        "Lenny (00:05:00): So let's talk about product."
    )
    cleaned = TranscriptCleaner.clean(raw)
    assert "Sidebar is an executive coaching network" not in cleaned
    assert "Brian Chesky (00:00:00): Welcome." in cleaned
    assert "Lenny (00:05:00): So let's talk about product." in cleaned
