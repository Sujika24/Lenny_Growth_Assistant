import logging
from typing import List, Dict, Any, Tuple
from app.rag.vector_store import TranscriptVectorStore
from app.schemas.message import Citation
from app.skills.ship30_essay import Ship30EssaySkill
from app.skills.artifact_generator import ArtifactGeneratorSkill
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)


# Standard Tool Schemas for Anthropic Agent SDK Tool Calling
ANTHROPIC_TOOLS = [
    {
        "name": "search_transcripts",
        "description": "Searches Lenny's Podcast transcripts for relevant evidence on product management, growth, and startup strategy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query or topic to look up in the podcast transcripts."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of transcript chunks to retrieve (default: 4)."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "generate_ship30_essay",
        "description": "Generates a structured, approximately 1,250-word digital essay following the Ship 30 for 30 framework.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The core topic or thesis for the Ship 30 essay."
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "create_artifact",
        "description": "Generates a side-by-side artifact (either Markdown document or self-contained HTML/CSS component).",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Description of the artifact to generate."
                },
                "artifact_type": {
                    "type": "string",
                    "enum": ["markdown", "html"],
                    "description": "The format: 'markdown' for docs/PRDs/checklists, 'html' for dashboards/matrices/cards."
                }
            },
            "required": ["prompt", "artifact_type"]
        }
    }
]


class AgentTools:
    def __init__(self, vector_store: TranscriptVectorStore, provider: LLMProvider):
        self.vector_store = vector_store
        self.provider = provider
        self.essay_skill = Ship30EssaySkill(provider)
        self.artifact_skill = ArtifactGeneratorSkill(provider)

    def retrieve(self, query: str, top_k: int = 4) -> Tuple[str, List[Citation]]:
        """Executes semantic search and formats context string with citations."""
        matches = self.vector_store.search(query, top_k=top_k)
        if not matches:
            return "", []

        context_parts = []
        citations: List[Citation] = []

        for chunk_info, citation in matches:
            citations.append(citation)
            guest = citation.guest
            title = citation.title
            text = chunk_info["text"]
            context_parts.append(
                f"[Source: {guest} in '{title}']\n{text}"
            )

        context_str = "\n\n---\n\n".join(context_parts)
        return context_str, citations

    async def generate_essay(self, topic: str, context: str = "", model_name: str = None) -> str:
        """Runs the Ship 30 for 30 essay generation skill."""
        return await self.essay_skill.generate_essay(topic=topic, context=context, model_name=model_name)

    async def create_artifact(
        self,
        prompt: str,
        artifact_type: str = "markdown",
        context: str = "",
        model_name: str = None
    ) -> Tuple[str, str]:
        """Runs the Artifact generation skill."""
        return await self.artifact_skill.generate_artifact(
            prompt=prompt,
            artifact_type=artifact_type,
            context=context,
            model_name=model_name
        )
