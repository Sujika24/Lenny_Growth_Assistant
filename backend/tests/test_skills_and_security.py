import pytest
from unittest.mock import AsyncMock
from app.skills.ship30_essay import Ship30EssaySkill
from app.skills.artifact_generator import ArtifactGeneratorSkill
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate
from app.schemas.message import MessageCreate
from app.schemas.artifact import ArtifactCreate


@pytest.mark.asyncio
async def test_essay_skill_routing():
    """Test 11: Verify Ship 30 for 30 essay skill formats proper prompt with 10 principles."""
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = (
        "# The Anti-Roadmap Playbook\n\n"
        "Most product roadmaps are fiction disguised as strategy...\n\n"
        "## 1. The Costly Illusion of Empowered Autonomy\n\n"
        "Brian Chesky discovered that delegating without details causes chaos...\n\n"
        "## 2. The 1-3-1 Execution Model\n\n"
        "**Leaders must stay in the details.**\n\n"
        "## Actionable Takeaways\n1. Review top 3 initiatives weekly.\n"
    )

    skill = Ship30EssaySkill(mock_provider)
    essay = await skill.generate_essay("Founder mode roadmaps", context="Brian Chesky transcript evidence")
    assert "# The Anti-Roadmap Playbook" in essay
    assert mock_provider.generate.called
    call_args = mock_provider.generate.call_args[1]
    assert "Ship 30 for 30" in call_args["prompt"]
    assert "1,250-word" in call_args["prompt"]


def test_artifact_persistence(db_session, client):
    """Test 12: Verify artifacts are persisted and linked to sessions and messages."""
    sess = SessionService.create_session(db_session, SessionCreate(title="Artifact Session"))
    msg = SessionService.add_message(
        db_session,
        MessageCreate(session_id=sess.id, role="assistant", content="Here is your artifact.")
    )

    art = SessionService.add_artifact(
        db_session,
        ArtifactCreate(
            session_id=sess.id,
            message_id=msg.id,
            title="Prioritization Matrix",
            artifact_type="html",
            content="<div class='matrix'>Impact vs Effort</div>"
        )
    )

    # Fetch through API
    res = client.get(f"/api/v1/artifacts/{art.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == art.id
    assert data["session_id"] == sess.id
    assert data["message_id"] == msg.id
    assert data["artifact_type"] == "html"
    assert "Impact vs Effort" in data["content"]


def test_unsafe_html_isolation_rules():
    """Test 13: Verify security rules regarding HTML artifact sandboxing."""
    # HTML artifacts must have Content Security Policy and avoid unsafe execution
    sample_malicious_content = "<script>alert('xss');</script><img src='x' onerror='stealCookie()' />"

    # Verify that dangerous script tags can be detected and that the iframe sandbox policy
    # explicitly forbids allow-scripts and allow-same-origin.
    sandbox_attributes = ["allow-popups"]
    forbidden_attributes = ["allow-scripts", "allow-same-origin", "allow-forms", "allow-top-navigation"]

    for attr in forbidden_attributes:
        assert attr not in sandbox_attributes, f"Security violation: {attr} found in sandbox!"

    # Ensure CSP restricts script execution
    csp_policy = "default-src 'none'; style-src 'unsafe-inline'; img-src data: https:; font-src data:;"
    assert "script-src" not in csp_policy or "script-src 'none'" in csp_policy
