"""
SOAP parser utility module.

Provides functions to parse and validate SOAP-formatted medical notes.
"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class SOAPNote:
    """
    Data class representing a parsed SOAP note.

    Contains the four standard sections of a SOAP medical note.
    """
    subjective: str
    objective: str
    assessment: str
    plan: str


def parse_soap_note(content: str) -> Optional[SOAPNote]:
    """
    Parse a SOAP-formatted note into its component sections.

    Parameters:
        content: Raw text content of the note

    Returns:
        SOAPNote object if valid SOAP format, None otherwise
    """
    sections = {
        "subjective": "",
        "objective": "",
        "assessment": "",
        "plan": ""
    }

    current_section = None
    current_content = []

    for line in content.split("\n"):
        line_lower = line.lower().strip()

        if any(marker in line_lower for marker in ["subjective", "s:"]):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "subjective"
            current_content = []
        elif any(marker in line_lower for marker in ["objective", "o:"]):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "objective"
            current_content = []
        elif any(marker in line_lower for marker in ["assessment", "a:"]):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "assessment"
            current_content = []
        elif any(marker in line_lower for marker in ["plan", "p:"]):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "plan"
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    if not any(sections.values()):
        return None

    return SOAPNote(**sections)


def is_valid_soap(content: str) -> bool:
    """
    Check if content follows SOAP format.

    Parameters:
        content: Raw text content to validate

    Returns:
        True if valid SOAP format, False otherwise
    """
    return parse_soap_note(content) is not None
