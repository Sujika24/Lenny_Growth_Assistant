import pytest
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate
from app.schemas.message import MessageCreate


def test_session_creation(client):
    """Test 1: Verify session creation returns valid UUID and defaults."""
    res = client.post("/api/v1/sessions", json={"title": "PM Prioritization Chat", "provider": "ollama"})
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    assert data["title"] == "PM Prioritization Chat"
    assert data["provider"] == "ollama"


def test_session_isolation(client, db_session):
    """Test 2: Verify messages in Session A are never leaked into Session B."""
    # Create Session A
    sess_a = SessionService.create_session(db_session, SessionCreate(title="Session A"))
    # Create Session B
    sess_b = SessionService.create_session(db_session, SessionCreate(title="Session B"))

    # Add message to Session A
    SessionService.add_message(
        db_session,
        MessageCreate(session_id=sess_a.id, role="user", content="Secret PM strategy A")
    )
    # Add message to Session B
    SessionService.add_message(
        db_session,
        MessageCreate(session_id=sess_b.id, role="user", content="Public PM strategy B")
    )

    # Retrieve messages for Session A
    res_a = client.get(f"/api/v1/sessions/{sess_a.id}/messages")
    assert res_a.status_code == 200
    msgs_a = res_a.json()
    assert len(msgs_a) == 1
    assert msgs_a[0]["content"] == "Secret PM strategy A"

    # Retrieve messages for Session B
    res_b = client.get(f"/api/v1/sessions/{sess_b.id}/messages")
    assert res_b.status_code == 200
    msgs_b = res_b.json()
    assert len(msgs_b) == 1
    assert msgs_b[0]["content"] == "Public PM strategy B"
    assert "Secret PM strategy A" not in [m["content"] for m in msgs_b]


def test_conversation_persistence(client, db_session):
    """Test 3: Verify multi-turn conversation persists in database."""
    sess = SessionService.create_session(db_session, SessionCreate(title="Persistence Test"))

    # Turn 1
    SessionService.add_message(
        db_session,
        MessageCreate(session_id=sess.id, role="user", content="What is founder mode?")
    )
    SessionService.add_message(
        db_session,
        MessageCreate(session_id=sess.id, role="assistant", content="Founder mode is staying close to the details.")
    )

    # Turn 2
    SessionService.add_message(
        db_session,
        MessageCreate(session_id=sess.id, role="user", content="Who discussed this?")
    )

    # Reopen session detail
    res = client.get(f"/api/v1/sessions/{sess.id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data["messages"]) == 3
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][1]["role"] == "assistant"
    assert data["messages"][2]["content"] == "Who discussed this?"


def test_database_error_handling(client):
    """Test 14: Verify graceful 404 and structured error on invalid/non-existent session."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/api/v1/sessions/{fake_id}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Session not found"
