import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.rag.vector_store import TranscriptVectorStore
from app.providers.factory import ProviderFactory
from app.core.config import settings
from app.agents.tools import AgentTools, ANTHROPIC_TOOLS
from app.schemas.message import Citation

logger = logging.getLogger(__name__)

GROUNDED_SYSTEM_PROMPT = """
You are THE LENNY GROWTH ASSISTANT, an intelligent product management and growth advisor grounded in Lenny's Podcast transcripts.

CORE OPERATIONAL RULES:
1. GROUNDED TRUTH: Base your answer on the retrieved transcript evidence provided below. Attribute specific principles, frameworks, and stories to the guests who shared them (e.g. Brian Chesky, Marty Cagan, Elena Verna, Shreyas Doshi).
2. ZERO FABRICATION: Never invent guest names, podcast episodes, or quotes.
3. HONEST LIMITATIONS: If the retrieved transcript evidence does not contain sufficient information to answer the question, explicitly acknowledge this limitation:
   "Based on Lenny's Podcast transcripts currently in my knowledge base, I don't have enough direct evidence to answer this specifically. Here is what is related from the available discussions: ..."
4. ACTIONABLE CLARITY: Synthesize the advice with clear, structured bullet points, key takeaways, and practical PM/Growth application.
5. CONTEXT PRESERVATION: If this is a follow-up question, preserve continuity with the conversation history.

RETRIEVED TRANSCRIPT EVIDENCE:
{context}
"""


class AgentOrchestrator:
    def __init__(self, vector_store: TranscriptVectorStore):
        self.vector_store = vector_store

    def _detect_deterministic_intent(self, text: str) -> str:
        """
        Determines whether the user is explicitly requesting an essay,
        an artifact, or a conversational grounded answer.
        """
        lower = text.lower()
        if any(k in lower for k in ["ship 30", "write an essay", "generate an essay", "compose an essay", "1250 word"]):
            return "essay"
        if any(k in lower for k in ["html card", "html dashboard", "html widget", "html mockup", "visual framework in html"]):
            return "artifact_html"
        if any(k in lower for k in ["generate a prd", "generate prd", "create a prd", "strategy document", "generate checklist"]):
            return "artifact_markdown"
        return "chat"

    async def execute_request(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        provider_name: str = "ollama",
        model_name: str = None
    ) -> Dict[str, Any]:
        """
        Executes user request across provider and appropriate agent skill.
        Returns: {
            "content": str,
            "citations": List[Citation],
            "artifact": Optional[Dict[str, Any]]
        }
        """
        provider = ProviderFactory.get_provider(provider_name)
        tools = AgentTools(self.vector_store, provider)

        # 1. Retrieve transcript evidence
        context, citations = tools.retrieve(user_message, top_k=4)

        # 2. Check for deterministic routing
        intent = self._detect_deterministic_intent(user_message)

        # If user explicitly requested an essay
        if intent == "essay":
            essay_content = await tools.generate_essay(
                topic=user_message,
                context=context,
                model_name=model_name
            )
            # Create artifact for the essay
            title = "Ship 30 for 30 Essay: " + user_message[:40].strip()
            return {
                "content": f"I've written a Ship 30 for 30 deep-dive essay on this topic. You can read and review it in the Artifact panel on the right.\n\n### Summary\nThis piece synthesizes key transcript insights into a structured 1,250-word playbook.",
                "citations": citations,
                "artifact": {
                    "title": title,
                    "artifact_type": "markdown",
                    "content": essay_content
                }
            }

        # If user explicitly requested an HTML artifact
        if intent == "artifact_html":
            title, html_content = await tools.create_artifact(
                prompt=user_message,
                artifact_type="html",
                context=context,
                model_name=model_name
            )
            return {
                "content": f"I've generated an interactive HTML/CSS artifact for you: **{title}**. Check the Artifact Studio on the right to preview it live or inspect the code.",
                "citations": citations,
                "artifact": {
                    "title": title,
                    "artifact_type": "html",
                    "content": html_content
                }
            }

        # If user explicitly requested a Markdown artifact
        if intent == "artifact_markdown":
            title, md_content = await tools.create_artifact(
                prompt=user_message,
                artifact_type="markdown",
                context=context,
                model_name=model_name
            )
            return {
                "content": f"I've generated your strategy document: **{title}**. Open the Artifact Studio on the right to review and copy the Markdown.",
                "citations": citations,
                "artifact": {
                    "title": title,
                    "artifact_type": "markdown",
                    "content": md_content
                }
            }

        # 3. Grounded Conversational Answering
        # Check if cloud Anthropic Agent SDK tool use is selected and available
        if provider_name.lower() == "anthropic" and await provider.is_available():
            # Genuine Anthropic Claude Agent execution
            return await self._execute_anthropic_agent(
                prompt=user_message,
                conversation_history=conversation_history,
                tools=tools,
                context=context,
                citations=citations,
                model_name=model_name
            )

        # Local Ollama / Provider Adapter Execution
        history_str = ""
        if conversation_history:
            for msg in conversation_history[-4:]:
                history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"

        prompt = ""
        if history_str:
            prompt += f"CONVERSATION HISTORY:\n{history_str}\n\n"
        prompt += f"USER QUESTION: {user_message}\n\nPlease provide a detailed, grounded answer based on the transcripts above."

        system_instruction = GROUNDED_SYSTEM_PROMPT.format(
            context=context if context else "No direct transcript matches were found."
        )

        response_text = await provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            model_name=model_name,
            temperature=0.6,
            timeout=settings.ollama_timeout_seconds
        )

        # Check if the response contains markdown codeblock of a component or PRD that can be promoted to an artifact
        artifact = None
        html_block = re.search(r"```html\s*(<!DOCTYPE html>.*?)```", response_text, re.DOTALL | re.IGNORECASE)
        if html_block:
            artifact = {
                "title": "Generated UI Component",
                "artifact_type": "html",
                "content": html_block.group(1).strip()
            }

        return {
            "content": response_text,
            "citations": citations,
            "artifact": artifact
        }

    async def _execute_anthropic_agent(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]],
        tools: AgentTools,
        context: str,
        citations: List[Citation],
        model_name: str
    ) -> Dict[str, Any]:
        """
        Integrates genuinely with Anthropic Claude SDK tool-use loop.
        """
        import anthropic
        from app.core.config import settings

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        model = model_name or settings.anthropic_model

        messages = []
        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})

        system = GROUNDED_SYSTEM_PROMPT.format(context=context or "No direct transcript matches found.")

        response = await client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=messages,
            tools=ANTHROPIC_TOOLS
        )

        # If model calls a tool
        if response.stop_reason == "tool_use":
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    if tool_name == "generate_ship30_essay":
                        essay = await tools.generate_essay(tool_input.get("topic", prompt), context=context)
                        return {
                            "content": "I have created a Ship 30 for 30 essay using the agent tool.",
                            "citations": citations,
                            "artifact": {
                                "title": f"Ship 30 Essay: {tool_input.get('topic', 'Product Insight')}",
                                "artifact_type": "markdown",
                                "content": essay
                            }
                        }
                    elif tool_name == "create_artifact":
                        t, art = await tools.create_artifact(
                            tool_input.get("prompt", prompt),
                            artifact_type=tool_input.get("artifact_type", "markdown"),
                            context=context
                        )
                        return {
                            "content": f"Created artifact: **{t}**.",
                            "citations": citations,
                            "artifact": {
                                "title": t,
                                "artifact_type": tool_input.get("artifact_type", "markdown"),
                                "content": art
                            }
                        }

        # Otherwise extract text
        text_content = ""
        for block in response.content:
            if hasattr(block, "text"):
                text_content += block.text

        return {
            "content": text_content,
            "citations": citations,
            "artifact": None
        }
