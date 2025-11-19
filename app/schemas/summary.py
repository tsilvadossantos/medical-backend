"""
Summary schema module.

Defines Pydantic models for patient summary response data.
"""
from typing import Optional
from pydantic import BaseModel


class PatientHeading(BaseModel):
    """
    Schema for patient summary heading.

    Contains basic patient identifiers for quick reference.
    """
    name: str
    age: int
    mrn: str


class SummaryResponse(BaseModel):
    """
    Schema for patient summary response.

    Contains patient heading and generated summary narrative.
    """
    heading: PatientHeading
    summary: str
    note_count: int


class SummaryOptions(BaseModel):
    """
    Schema for summary generation options.

    Allows customization of the generated summary.
    """
    audience: Optional[str] = "clinician"
    max_length: Optional[int] = 500
