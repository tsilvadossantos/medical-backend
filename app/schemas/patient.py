"""
Patient schema module.

Defines Pydantic models for patient data validation and serialization.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PatientBase(BaseModel):
    """
    Base schema for patient data.

    Contains common fields shared across patient operations.
    """
    name: str
    date_of_birth: date


class PatientCreate(PatientBase):
    """
    Schema for creating a new patient.

    Inherits all fields from PatientBase for patient creation requests.
    """
    pass


class PatientUpdate(BaseModel):
    """
    Schema for updating an existing patient.

    All fields are optional to support partial updates.
    """
    name: Optional[str] = None
    date_of_birth: Optional[date] = None


class PatientResponse(PatientBase):
    """
    Schema for patient response data.

    Includes all patient fields plus database-generated fields.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PatientListResponse(BaseModel):
    """
    Schema for paginated patient list response.

    Includes list of patients and pagination metadata.
    """
    items: list[PatientResponse]
    total: int
    page: int
    size: int
    pages: int
