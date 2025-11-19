"""
Note model module.

Defines the SQLAlchemy ORM model for patient medical notes.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Note(Base):
    """
    SQLAlchemy model representing a patient medical note.

    Stores medical notes associated with a patient, including
    the note content and the timestamp when the note was taken.
    """

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    note_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    patient = relationship("Patient", back_populates="notes")

    # Composite index for common query pattern: filter by patient, sort by timestamp
    __table_args__ = (
        Index('ix_notes_patient_timestamp', 'patient_id', 'note_timestamp'),
    )
