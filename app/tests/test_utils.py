"""
Utils tests.

Tests for utility functions.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from app.utils.soap_parser import parse_soap_note, is_valid_soap, SOAPNote
from app.utils.llm_client import generate_summary, _generate_rule_based
from app.utils.time_utils import utc_now, format_timestamp


class TestSOAPParser:
    """Tests for SOAP parser utility."""

    def test_parse_soap_note_valid(self):
        """Test parsing valid SOAP note."""
        content = """Subjective:
Patient reports headache.

Objective:
Vitals normal.

Assessment:
Tension headache.

Plan:
Ibuprofen PRN."""

        result = parse_soap_note(content)

        assert result is not None
        assert "headache" in result.subjective
        assert "Vitals" in result.objective
        assert "Tension" in result.assessment
        assert "Ibuprofen" in result.plan

    def test_parse_soap_note_abbreviated(self):
        """Test parsing SOAP note with abbreviated markers."""
        content = """S:
Headache

O:
Normal exam

A:
Migraine

P:
Rest"""

        result = parse_soap_note(content)

        assert result is not None
        assert "Headache" in result.subjective

    def test_parse_soap_note_invalid(self):
        """Test parsing invalid note."""
        content = "This is just a plain text note without SOAP format."

        result = parse_soap_note(content)

        assert result is None

    def test_is_valid_soap_true(self):
        """Test valid SOAP detection."""
        content = "Subjective:\nTest\nObjective:\nTest"

        assert is_valid_soap(content) is True

    def test_is_valid_soap_false(self):
        """Test invalid SOAP detection."""
        content = "Plain text"

        assert is_valid_soap(content) is False

    def test_soap_note_dataclass(self):
        """Test SOAPNote dataclass."""
        note = SOAPNote(
            subjective="S",
            objective="O",
            assessment="A",
            plan="P"
        )

        assert note.subjective == "S"
        assert note.objective == "O"
        assert note.assessment == "A"
        assert note.plan == "P"


class TestLLMClient:
    """Tests for LLM client utility."""

    @patch('app.utils.llm_client.get_llm_provider')
    def test_generate_summary_success(self, mock_get_provider):
        """Test successful summary generation."""
        mock_provider = MagicMock()
        mock_provider.name = "test"
        mock_provider.generate_summary.return_value = "LLM summary"
        mock_get_provider.return_value = mock_provider

        result = generate_summary("John", 35, "Notes", "clinician", 500)

        assert result == "LLM summary"

    @patch('app.utils.llm_client.get_llm_provider')
    def test_generate_summary_fallback(self, mock_get_provider):
        """Test fallback to rule-based on error."""
        mock_get_provider.side_effect = Exception("Provider error")

        result = generate_summary(
            "John", 35,
            "Subjective:\nHeadache\nAssessment:\nMigraine\nPlan:\nRest",
            "clinician", 500
        )

        assert "John" in result
        assert "35 years old" in result

    def test_generate_rule_based_with_soap(self):
        """Test rule-based generation with SOAP content."""
        notes = """Subjective:
Patient reports chest pain.

Assessment:
Possible angina.

Plan:
ECG ordered."""

        result = _generate_rule_based("John Doe", 45, notes, "clinician")

        assert "John Doe" in result
        assert "45 years old" in result
        assert "Assessment:" in result
        assert "Plan:" in result

    def test_generate_rule_based_no_soap(self):
        """Test rule-based generation without SOAP content."""
        notes = "Random clinical note without SOAP format"

        result = _generate_rule_based("John Doe", 45, notes, "clinician")

        assert "could not be parsed" in result

    def test_generate_rule_based_partial_soap(self):
        """Test rule-based with partial SOAP sections."""
        notes = """Subjective:
Chief complaint is headache.

Plan:
Follow up in 1 week."""

        result = _generate_rule_based("Jane", 30, notes, "family")

        assert "Jane" in result
        assert "Plan:" in result


class TestTimeUtils:
    """Tests for time utility functions."""

    def test_utc_now(self):
        """Test getting current UTC time."""
        result = utc_now()

        assert result.tzinfo is not None
        assert result.tzinfo == timezone.utc

    def test_format_timestamp(self):
        """Test formatting timestamp."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

        result = format_timestamp(dt)

        assert "2024-01-15" in result
        assert "10:30:00" in result


class TestIntegrationLLMClient:
    """Integration tests for LLM client."""

    @patch('app.utils.llm_client.get_llm_provider')
    def test_full_soap_processing(self, mock_get_provider):
        """Test processing complete SOAP note."""
        mock_provider = MagicMock()
        mock_provider.name = "test"
        mock_provider.generate_summary.return_value = "Complete summary"
        mock_get_provider.return_value = mock_provider

        notes = """Subjective:
45-year-old male with chest pain for 2 hours.

Objective:
BP 145/92, HR 98, ECG shows ST elevation.

Assessment:
Acute STEMI.

Plan:
Activate cath lab, aspirin, heparin."""

        result = generate_summary("John Smith", 45, notes, "clinician", 500)

        assert result == "Complete summary"
        mock_provider.generate_summary.assert_called_once()
