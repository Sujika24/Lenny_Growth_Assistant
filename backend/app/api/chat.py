import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.session_service import SessionService
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.session import SessionCreate
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.artifact import ArtifactCreate, ArtifactResponse
from app.rag.vector_store import TranscriptVectorStore
from app.agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Resolve or create session
    session_id = request.session_id
    if not session_id:
        new_session = SessionService.create_session(
            db,
            SessionCreate(
                title=request.message[:40].strip(),
                provider=request.provider or "ollama",
                model_name=request.model_name or "llama3.2:3b"
            )
        )
        session_id = new_session.id
    else:
        existing_session = SessionService.get_session(db, session_id)
        if not existing_session:
            raise HTTPException(status_code=404, detail="Session not found")

    # 2. Save User Message
    user_msg = SessionService.add_message(
        db,
        MessageCreate(
            session_id=session_id,
            role="user",
            content=request.message
        )
    )

    # 3. Retrieve conversation history for context
    history_messages = SessionService.get_messages(db, session_id)
    history_payload = [
        {"role": m.role, "content": m.content}
        for m in history_messages[:-1] # exclude current user message
    ]

    # 4. Execute through Agent Orchestrator
    try:
        vector_store = TranscriptVectorStore()
        orchestrator = AgentOrchestrator(vector_store)

        session = SessionService.get_session(db, session_id)
        provider = request.provider or session.provider
        model_name = request.model_name or session.model_name

        result = await orchestrator.execute_request(
            user_message=request.message,
            conversation_history=history_payload,
            provider_name=provider,
            model_name=model_name
        )
    except Exception as e:
        logger.error(f"Chat generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # 5. Save Assistant Message with Citations
    assistant_msg = SessionService.add_message(
        db,
        MessageCreate(
            session_id=session_id,
            role="assistant",
            content=result["content"],
            citations=result["citations"]
        )
    )

    # 6. Save Artifact if generated
    saved_artifact = None
    if result.get("artifact"):
        art_info = result["artifact"]
        saved_artifact = SessionService.add_artifact(
            db,
            ArtifactCreate(
                session_id=session_id,
                message_id=assistant_msg.id,
                title=art_info["title"],
                artifact_type=art_info["artifact_type"],
                content=art_info["content"]
            )
        )

    return ChatResponse(
        session_id=session_id,
        message=MessageResponse.model_validate(assistant_msg),
        artifact=ArtifactResponse.model_validate(saved_artifact) if saved_artifact else None
    )
