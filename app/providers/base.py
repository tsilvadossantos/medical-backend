"""
Base LLM provider module.

Defines the abstract interface for LLM providers.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Defines the interface that all LLM providers must implement
    to ensure consistent behavior across different AI services.
    """

    @abstractmethod
    def generate_summary(
        self,
        patient_name: str,
        age: int,
        notes_text: str,
        audience: str = "clinician",
        max_length: int = 500
    ) -> str:
        """
        Generate a patient summary using the LLM.

        Parameters:
            patient_name: Patient's full name
            age: Patient's age in years
            notes_text: Concatenated text of all patient notes
            audience: Target audience (clinician or family)
            max_length: Maximum length of summary in characters

        Returns:
            Generated summary text
        """
        pass

    def _build_prompt(
        self,
        patient_name: str,
        age: int,
        notes_text: str,
        audience: str,
        max_length: int
    ) -> str:
        """
        Build the prompt for summary generation.

        Parameters:
            patient_name: Patient's full name
            age: Patient's age in years
            notes_text: Concatenated text of all patient notes
            audience: Target audience
            max_length: Maximum length of summary

        Returns:
            Formatted prompt string
        """
        audience_instruction = (
            "Use clinical terminology appropriate for healthcare professionals."
            if audience == "clinician"
            else "Use plain language suitable for family members without medical background."
        )

        return f"""Generate a concise patient summary based on the following medical notes.

Patient: {patient_name}, {age} years old

{audience_instruction}

The summary should:
- Highlight key diagnoses and conditions
- Note current medications
- Summarize important observations and assessments
- Outline the treatment plan
- Be no longer than {max_length} characters

Medical Notes:
{notes_text}

Summary:"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass
