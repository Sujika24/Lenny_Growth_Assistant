import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.session_service import SessionService
from app.schemas.chat import EssayRequest, ChatResponse
from app.schemas.session import SessionCreate
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.artifact import ArtifactCreate, ArtifactResponse
from app.rag.vector_store import TranscriptVectorStore
from app.providers.factory import ProviderFactory
from app.agents.tools import AgentTools

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/essays", tags=["Essays"])


@router.post("", response_model=ChatResponse)
async def generate_essay(request: EssayRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    if not session_id:
        new_session = SessionService.create_session(
            db,
            SessionCreate(
                title=f"Essay: {request.topic[:35]}",
                provider=request.provider or "ollama",
                model_name=request.model_name or "llama3.2:3b"
            )
        )
        session_id = new_session.id
    else:
        existing_session = SessionService.get_session(db, session_id)
        if not existing_session:
            raise HTTPException(status_code=404, detail="Session not found")

    # Record user trigger message
    user_msg = SessionService.add_message(
        db,
        MessageCreate(
            session_id=session_id,
            role="user",
            content=f"Generate a Ship 30 for 30 essay on: {request.topic}"
        )
    )

    try:
        vector_store = TranscriptVectorStore()
        session = SessionService.get_session(db, session_id)
        provider = ProviderFactory.get_provider(request.provider or session.provider)
        tools = AgentTools(vector_store, provider)

        # Retrieve grounded context
        context, citations = tools.retrieve(request.topic, top_k=5)

        # Generate essay
        essay_content = await tools.generate_essay(
            topic=request.topic,
            context=context,
            model_name=request.model_name or session.model_name
        )

        title = f"Ship 30 for 30 Essay: {request.topic[:40].strip()}"
        summary_msg = (
            f"I have crafted a ~1,250-word **Ship 30 for 30** deep-dive essay on **{request.topic}** "
            "grounded in Lenny's Podcast transcripts. You can preview, copy, or download it in the Artifact panel."
        )

        assistant_msg = SessionService.add_message(
            db,
            MessageCreate(
                session_id=session_id,
                role="assistant",
                content=summary_msg,
                citations=citations
            )
        )

        artifact = SessionService.add_artifact(
            db,
            ArtifactCreate(
                session_id=session_id,
                message_id=assistant_msg.id,
                title=title,
                artifact_type="markdown",
                content=essay_content
            )
        )

        return ChatResponse(
            session_id=session_id,
            message=MessageResponse.model_validate(assistant_msg),
            artifact=ArtifactResponse.model_validate(artifact)
        )

    except Exception as e:
        logger.error(f"Essay generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
