"""
Note schema module.

Defines Pydantic models for note data validation and serialization.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    """
    Base schema for note data.

    Contains common fields for note operations.
    """
    content: str
    note_timestamp: datetime


class NoteCreate(NoteBase):
    """
    Schema for creating a new note.

    Inherits content and timestamp from NoteBase.
    """
    pass


class NoteResponse(NoteBase):
    """
    Schema for note response data.

    Includes all note fields plus database-generated fields.
    """
    id: int
    patient_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteListResponse(BaseModel):
    """
    Schema for list of notes response.

    Contains a list of notes for a patient.
    """
    items: list[NoteResponse]
    total: int
