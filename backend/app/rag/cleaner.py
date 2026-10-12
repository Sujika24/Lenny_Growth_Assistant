import re


class TranscriptCleaner:
    # Common sponsor patterns in Lenny's Podcast
    SPONSOR_PATTERNS = [
        r"This episode is brought to you by.*?(?=\n\n[A-Z][a-zA-Z\s]+(?:\([0-9:]+\))?:|\n\n##|\Z)",
        r"Thank you to our sponsors?.*?(?=\n\n[A-Z][a-zA-Z\s]+(?:\([0-9:]+\))?:|\n\n##|\Z)",
        r"Today's episode is brought to you by.*?(?=\n\n[A-Z][a-zA-Z\s]+(?:\([0-9:]+\))?:|\n\n##|\Z)",
        r"A quick word from our sponsors?.*?(?=\n\n[A-Z][a-zA-Z\s]+(?:\([0-9:]+\))?:|\n\n##|\Z)",
    ]

    @classmethod
    def clean(cls, text: str) -> str:
        """
        Cleans raw transcript content by removing sponsor ads,
        normalizing excessive newlines, and preserving speaker dialogue.
        """
        if not text:
            return ""

        cleaned = text
        # Remove sponsor mentions
        for pattern in cls.SPONSOR_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)

        # Remove header anchors like ## Transcript or # Title
        cleaned = re.sub(r"^#+\s+.*$", "", cleaned, flags=re.MULTILINE)

        # Normalize multiple blank lines to double newline
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()
