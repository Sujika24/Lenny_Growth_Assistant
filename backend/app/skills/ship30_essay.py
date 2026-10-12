import logging
from typing import Dict, Any, List
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

SHIP_30_ESSAY_PROMPT = """
You are an elite digital writer and product strategist trained in the Ship 30 for 30 writing methodology by Dickie Bush and Nicolas Cole.

Your task is to write a comprehensive, approximately 1,250-word deep-dive essay based on the topic and grounded podcast evidence provided below.

TOPIC: {topic}

RETRIEVED TRANSCRIPT EVIDENCE:
{context}

OFFICIAL SHIP 30 FOR 30 STRUCTURAL BLUEPRINT:
1. Compelling Title: Make it punchy, outcome-oriented, and impossible to ignore (e.g., "The Anti-Roadmap Playbook: Why Great Founders Stay in the Details").
2. Strong Opening Hook: 2-3 short sentences. A pattern interrupt that challenges standard industry dogmas.
3. Clear Problem / Tension: The costly mistake product leaders and founders make today. Why the status quo is broken.
4. Insights Grounded in Transcript Evidence: Synthesize core principles directly from the podcast guests mentioned in the evidence (quote or reference their exact philosophies without hallucinating).
5. Logical Narrative Progression: Flow from the systemic breakdown, to the mental model shift, to the step-by-step execution.
6. Skimmable Headings: Use punchy, intriguing subheads. Follow the 1-3-1 rhythm (one strong statement, short 3-sentence elaboration, one clincher).
7. Selective Bold Emphasis: Bold key takeaways so a fast skimmer captures 80% of the value in 45 seconds.
8. Real-World Case Studies: Bring in concrete company stories mentioned in the retrieved transcripts.
9. Actionable Lessons: Provide 3-5 concrete, tactical practices a product manager or founder can deploy immediately.
10. Memorable Concluding Takeaway: A sharp, sticky final summary that reframes how the reader views their work.

IMPORTANT GUIDELINES:
- Calibrate the length to be approximately 1,250 words (aim for 1,100 to 1,350 words).
- Do NOT invent guests or quotes not present in the retrieved evidence. If certain details are absent, focus on general first-principles product wisdom from the retrieved concepts.
- Format cleanly in Markdown with headers (##, ###), bullet lists, and bold callouts.
"""


class Ship30EssaySkill:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def generate_essay(self, topic: str, context: str, model_name: str = None) -> str:
        prompt = SHIP_30_ESSAY_PROMPT.format(topic=topic, context=context or "General product strategy principles.")
        system_instruction = (
            "You are a master digital writer specializing in Ship 30 for 30 high-impact essays. "
            "Write thorough, structured, and insight-dense essays without corporate fluff."
        )
        return await self.provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            model_name=model_name,
            temperature=0.7,
            timeout=120
        )
