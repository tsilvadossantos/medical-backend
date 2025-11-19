"""
OpenAI LLM provider module.

Implements LLM provider using OpenAI API.
"""
import logging
from openai import OpenAI
from app.providers.base import LLMProvider
from app.core.settings import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    LLM provider implementation using OpenAI API.

    Connects to OpenAI's API for GPT-based inference.
    """

    def __init__(self):
        """
        Initialize OpenAI provider with API key from settings.
        """
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "openai"

    def generate_summary(
        self,
        patient_name: str,
        age: int,
        notes_text: str,
        audience: str = "clinician",
        max_length: int = 500
    ) -> str:
        """
        Generate a patient summary using OpenAI.

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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical assistant that creates clear, accurate patient summaries."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length // 2,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
