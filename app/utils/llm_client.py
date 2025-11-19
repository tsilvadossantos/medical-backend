"""
LLM client module.

Provides integration with configured LLM provider for generating patient summaries.
Falls back to rule-based generation if provider is unavailable.
"""
import logging
from app.providers import get_llm_provider

logger = logging.getLogger(__name__)


def generate_summary(
    patient_name: str,
    age: int,
    notes_text: str,
    audience: str = "clinician",
    max_length: int = 500
) -> str:
    """
    Generate a patient summary using configured LLM provider or rule-based approach.

    Attempts to use the configured LLM provider for summary generation.
    Falls back to rule-based extraction if the provider fails.

    Parameters:
        patient_name: Patient's full name
        age: Patient's age in years
        notes_text: Concatenated text of all patient notes
        audience: Target audience (clinician or family)
        max_length: Maximum length of summary in characters

    Returns:
        Generated summary text
    """
    try:
        provider = get_llm_provider()
        logger.info(f"Using {provider.name} provider for summary generation")
        return provider.generate_summary(
            patient_name, age, notes_text, audience, max_length
        )
    except Exception as e:
        logger.warning(f"LLM generation failed, using fallback: {e}")
        return _generate_rule_based(patient_name, age, notes_text, audience)


def _generate_rule_based(
    patient_name: str,
    age: int,
    notes_text: str,
    audience: str
) -> str:
    """
    Generate summary using rule-based extraction.

    Extracts key information from SOAP-formatted notes using
    pattern matching and keyword identification.

    Parameters:
        patient_name: Patient's full name
        age: Patient's age in years
        notes_text: Concatenated text of all patient notes
        audience: Target audience

    Returns:
        Rule-based summary text
    """
    sections = {
        "subjective": [],
        "objective": [],
        "assessment": [],
        "plan": []
    }

    current_section = None
    for line in notes_text.split("\n"):
        line_lower = line.lower().strip()
        if "subjective" in line_lower:
            current_section = "subjective"
        elif "objective" in line_lower:
            current_section = "objective"
        elif "assessment" in line_lower:
            current_section = "assessment"
        elif "plan" in line_lower:
            current_section = "plan"
        elif current_section and line.strip():
            sections[current_section].append(line.strip())

    summary_parts = [f"Patient {patient_name}, {age} years old."]

    if sections["assessment"]:
        assessments = " ".join(sections["assessment"][:3])
        summary_parts.append(f"Assessment: {assessments}")

    if sections["plan"]:
        plans = " ".join(sections["plan"][:3])
        summary_parts.append(f"Plan: {plans}")

    if sections["subjective"]:
        chief = sections["subjective"][0] if sections["subjective"] else ""
        if chief:
            summary_parts.append(f"Chief complaint: {chief}")

    if not any(sections.values()):
        summary_parts.append(
            "Clinical notes are available but could not be parsed into SOAP format. "
            "Please review individual notes for details."
        )

    return " ".join(summary_parts)
