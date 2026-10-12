import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.session_service import SessionService
from app.schemas.chat import ArtifactGenerateRequest, ChatResponse
from app.schemas.session import SessionCreate
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.artifact import ArtifactCreate, ArtifactResponse
from app.rag.vector_store import TranscriptVectorStore
from app.providers.factory import ProviderFactory
from app.agents.tools import AgentTools

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/artifacts", tags=["Artifacts"])


@router.post("", response_model=ChatResponse)
async def generate_artifact(request: ArtifactGenerateRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    if not session_id:
        new_session = SessionService.create_session(
            db,
            SessionCreate(
                title=f"Artifact: {request.prompt[:35]}",
                provider=request.provider or "ollama",
                model_name=request.model_name or "llama3.2:3b"
            )
        )
        session_id = new_session.id
    else:
        existing_session = SessionService.get_session(db, session_id)
        if not existing_session:
            raise HTTPException(status_code=404, detail="Session not found")

    user_msg = SessionService.add_message(
        db,
        MessageCreate(
            session_id=session_id,
            role="user",
            content=f"Create a {request.artifact_type.upper()} artifact: {request.prompt}"
        )
    )

    try:
        vector_store = TranscriptVectorStore()
        session = SessionService.get_session(db, session_id)
        provider = ProviderFactory.get_provider(request.provider or session.provider)
        tools = AgentTools(vector_store, provider)

        context, citations = tools.retrieve(request.prompt, top_k=4)

        title, content = await tools.create_artifact(
            prompt=request.prompt,
            artifact_type=request.artifact_type,
            context=context,
            model_name=request.model_name or session.model_name
        )

        display_title = request.title or title

        assistant_msg = SessionService.add_message(
            db,
            MessageCreate(
                session_id=session_id,
                role="assistant",
                content=f"I have created the artifact **{display_title}** ({request.artifact_type.upper()}). You can preview and inspect it in the Artifact panel.",
                citations=citations
            )
        )

        artifact = SessionService.add_artifact(
            db,
            ArtifactCreate(
                session_id=session_id,
                message_id=assistant_msg.id,
                title=display_title,
                artifact_type=request.artifact_type.lower(),
                content=content
            )
        )

        return ChatResponse(
            session_id=session_id,
            message=MessageResponse.model_validate(assistant_msg),
            artifact=ArtifactResponse.model_validate(artifact)
        )

    except Exception as e:
        logger.error(f"Artifact generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = SessionService.get_artifact(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact
