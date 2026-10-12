import re
import logging
from typing import Dict, Any, Tuple
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

HTML_PROMPT = """
You are a world-class UI designer and frontend engineer.
Create an interactive, self-contained HTML/CSS visual artifact based on the user's request and podcast context.

REQUEST: {prompt}
CONTEXT: {context}

REQUIREMENTS:
1. Return ONLY the raw HTML code inside a single `<!DOCTYPE html><html>...</html>` document. Do NOT wrap in markdown backticks or extra commentary.
2. Include all CSS in a `<style>` block in the `<head>`.
3. Design Aesthetics:
   - Modern, professional, dark-slate theme: backgrounds `#0B0F19` and `#1E293B`, accents in `#8B5CF6` (violet), `#06B6D4` (cyan), and `#10B981` (emerald).
   - High contrast, elegant typography (`system-ui`, `Inter`, `sans-serif`), subtle borders (`1px solid #334155`), and smooth rounded cards.
   - Fully responsive for mobile and desktop preview.
4. Security constraint: Do NOT include external script tags or unsafe event handlers. Keep all styling in CSS.
"""

MARKDOWN_PROMPT = """
You are a senior product management advisor.
Generate a structured, professional Markdown document (e.g. PRD, Strategy Document, Framework, or Execution Plan) based on the user request and context.

REQUEST: {prompt}
CONTEXT: {context}

REQUIREMENTS:
1. Return clean, formatted Markdown with clear headings (`#`, `##`, `###`), tables, bullet points, and bold emphasis.
2. Ground all advice in concrete product management methodologies.
3. Keep it tactical, actionable, and ready to share with executive stakeholders.
"""


class ArtifactGeneratorSkill:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def generate_artifact(
        self,
        prompt: str,
        artifact_type: str = "markdown",
        context: str = "",
        model_name: str = None
    ) -> Tuple[str, str]:
        """
        Generates artifact content and extracts an appropriate title.
        Returns: (title, content)
        """
        is_html = artifact_type.lower() == "html"
        system_instruction = (
            "You are an expert artifact author specializing in product frameworks, UI artifacts, and PRDs."
        )

        if is_html:
            query = HTML_PROMPT.format(prompt=prompt, context=context)
            content = await self.provider.generate(
                prompt=query,
                system_instruction=system_instruction,
                model_name=model_name,
                temperature=0.6,
                timeout=90
            )
            # Clean markdown codeblocks if model wrapped in ```html
            clean_content = re.sub(r"^```(?:html)?\s*", "", content.strip(), flags=re.IGNORECASE)
            clean_content = re.sub(r"\s*```$", "", clean_content.strip())

            # Title extraction
            title_match = re.search(r"<title>(.*?)</title>", clean_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "Product Dashboard Widget"
            return title, clean_content
        else:
            query = MARKDOWN_PROMPT.format(prompt=prompt, context=context)
            content = await self.provider.generate(
                prompt=query,
                system_instruction=system_instruction,
                model_name=model_name,
                temperature=0.6,
                timeout=90
            )
            clean_content = content.strip()
            # Extract first heading as title
            heading_match = re.search(r"^#+\s+(.+)$", clean_content, re.MULTILINE)
            title = heading_match.group(1).strip() if heading_match else "Strategy Document"
            return title, clean_content
