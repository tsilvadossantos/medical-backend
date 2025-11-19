"""
Ollama LLM provider module.

Implements LLM provider using local Ollama service.
"""
import logging
import httpx
from app.providers.base import LLMProvider
from app.core.settings import settings

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """
    LLM provider implementation using Ollama.

    Connects to a local or remote Ollama instance for
    free, self-hosted LLM inference.
    """

    def __init__(self):
        """
        Initialize Ollama provider with configuration from settings.
        """
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.temperature = settings.OLLAMA_TEMPERATURE
        self.top_p = settings.OLLAMA_TOP_P
        self.top_k = settings.OLLAMA_TOP_K
        self.num_ctx = settings.OLLAMA_NUM_CTX
        self.num_predict = settings.OLLAMA_NUM_PREDICT
        self.timeout = settings.OLLAMA_TIMEOUT

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "ollama"

    def generate_summary(
        self,
        patient_name: str,
        age: int,
        notes_text: str,
        audience: str = "clinician",
        max_length: int = 500
    ) -> str:
        """
        Generate a patient summary using Ollama.

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

        # Build options from configuration
        options = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "num_ctx": self.num_ctx,
            "num_predict": self.num_predict if self.num_predict else max_length // 2
        }

        try:
            with httpx.Client(timeout=float(self.timeout)) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": options
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
