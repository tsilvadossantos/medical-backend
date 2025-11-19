"""
Anthropic LLM provider module.

Implements LLM provider using Anthropic Claude API.
"""
import logging
import httpx
from app.providers.base import LLMProvider
from app.core.settings import settings

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    LLM provider implementation using Anthropic Claude API.

    Connects to Anthropic's API for Claude-based inference.
    """

    def __init__(self):
        """
        Initialize Anthropic provider with API key from settings.
        """
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "anthropic"

    def generate_summary(
        self,
        patient_name: str,
        age: int,
        notes_text: str,
        audience: str = "clinician",
        max_length: int = 500
    ) -> str:
        """
        Generate a patient summary using Anthropic Claude.

        Parameters:
            patient_name: Patient's full name
            age: Patient's age in years
            notes_text: Concatenated text of all patient notes
            audience: Target audience (clinician or family)
            max_length: Maximum length of summary in characters

        Returns:
            Generated summary text
        """
        prompt = self._build_prompt(patient_name, age, notes_text, audience, max_length)

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": max_length // 2,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "system": "You are a medical assistant that creates clear, accurate patient summaries."
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["content"][0]["text"].strip()

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
