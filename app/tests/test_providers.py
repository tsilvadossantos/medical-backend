"""
Provider tests.

Tests for LLM provider implementations.
"""
import pytest
from unittest.mock import patch, MagicMock
import httpx
from app.providers.base import LLMProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.factory import get_llm_provider


class TestLLMProviderBase:
    """Tests for base LLM provider."""

    def test_build_prompt_clinician(self):
        """Test building prompt for clinician audience."""

        class TestProvider(LLMProvider):
            @property
            def name(self):
                return "test"

            def generate_summary(self, *args, **kwargs):
                pass

        provider = TestProvider()
        prompt = provider._build_prompt(
            "John Doe", 35, "Test notes", "clinician", 500
        )

        assert "John Doe" in prompt
        assert "35 years old" in prompt
        assert "clinical terminology" in prompt

    def test_build_prompt_family(self):
        """Test building prompt for family audience."""

        class TestProvider(LLMProvider):
            @property
            def name(self):
                return "test"

            def generate_summary(self, *args, **kwargs):
                pass

        provider = TestProvider()
        prompt = provider._build_prompt(
            "John Doe", 35, "Test notes", "family", 500
        )

        assert "plain language" in prompt


class TestOllamaProvider:
    """Tests for Ollama provider."""

    @patch('app.providers.ollama.settings')
    def test_init(self, mock_settings):
        """Test Ollama provider initialization."""
        mock_settings.OLLAMA_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL = "llama3.2"

        provider = OllamaProvider()

        assert provider.name == "ollama"
        assert provider.base_url == "http://localhost:11434"

    @patch('app.providers.ollama.settings')
    @patch('httpx.Client')
    def test_generate_summary_success(self, mock_client_class, mock_settings):
        """Test successful summary generation."""
        mock_settings.OLLAMA_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL = "llama3.2"

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Generated summary"}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        result = provider.generate_summary("John", 35, "Notes", "clinician", 500)

        assert result == "Generated summary"

    @patch('app.providers.ollama.settings')
    @patch('httpx.Client')
    def test_generate_summary_error(self, mock_client_class, mock_settings):
        """Test summary generation error handling."""
        mock_settings.OLLAMA_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL = "llama3.2"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = httpx.HTTPError("Connection failed")
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        with pytest.raises(httpx.HTTPError):
            provider.generate_summary("John", 35, "Notes", "clinician", 500)


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    @patch('app.providers.openai_provider.settings')
    @patch('app.providers.openai_provider.OpenAI')
    def test_generate_summary_success(self, mock_openai_class, mock_settings):
        """Test successful OpenAI summary generation."""
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-3.5-turbo"

        mock_message = MagicMock()
        mock_message.content = "OpenAI summary"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider()
        result = provider.generate_summary("John", 35, "Notes", "clinician", 500)

        assert result == "OpenAI summary"
        assert provider.name == "openai"


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    @patch('app.providers.anthropic_provider.settings')
    @patch('httpx.Client')
    def test_generate_summary_success(self, mock_client_class, mock_settings):
        """Test successful Anthropic summary generation."""
        mock_settings.ANTHROPIC_API_KEY = "test-key"
        mock_settings.ANTHROPIC_MODEL = "claude-3-haiku"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Anthropic summary"}]
        }
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = AnthropicProvider()
        result = provider.generate_summary("John", 35, "Notes", "clinician", 500)

        assert result == "Anthropic summary"
        assert provider.name == "anthropic"


class TestProviderFactory:
    """Tests for provider factory."""

    @patch('app.providers.factory.settings')
    def test_get_ollama_provider(self, mock_settings):
        """Test getting Ollama provider."""
        mock_settings.LLM_PROVIDER = "ollama"
        mock_settings.OLLAMA_URL = "http://localhost:11434"
        mock_settings.OLLAMA_MODEL = "llama3.2"

        provider = get_llm_provider()

        assert provider.name == "ollama"

    @patch('app.providers.factory.settings')
    def test_get_openai_provider(self, mock_settings):
        """Test getting OpenAI provider."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-3.5-turbo"

        provider = get_llm_provider()

        assert provider.name == "openai"

    @patch('app.providers.factory.settings')
    def test_get_openai_provider_no_key(self, mock_settings):
        """Test getting OpenAI provider without API key."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = None

        with pytest.raises(ValueError, match="OPENAI_API_KEY required"):
            get_llm_provider()

    @patch('app.providers.factory.settings')
    def test_get_anthropic_provider(self, mock_settings):
        """Test getting Anthropic provider."""
        mock_settings.LLM_PROVIDER = "anthropic"
        mock_settings.ANTHROPIC_API_KEY = "test-key"
        mock_settings.ANTHROPIC_MODEL = "claude-3-haiku"

        provider = get_llm_provider()

        assert provider.name == "anthropic"

    @patch('app.providers.factory.settings')
    def test_unsupported_provider(self, mock_settings):
        """Test unsupported provider error."""
        mock_settings.LLM_PROVIDER = "unsupported"

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            get_llm_provider()
