"""
Patient model module.

Defines the SQLAlchemy ORM model for patient records.
"""
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Patient(Base):
    """
    SQLAlchemy model representing a patient record.

    Stores patient demographic information including name and date of birth.
    Maintains created and updated timestamps for audit purposes.
    """

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    notes = relationship("Note", back_populates="patient", cascade="all, delete-orphan")
