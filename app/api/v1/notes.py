"""
Notes endpoints module.

Provides endpoints for managing patient medical notes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.note_service import NoteService
from app.schemas.note import NoteCreate, NoteResponse, NoteListResponse

router = APIRouter(prefix="/patients/{patient_id}/notes", tags=["notes"])


@router.get("", response_model=NoteListResponse)
def list_patient_notes(patient_id: int, db: Session = Depends(get_db)):
    """
    Get all notes for a patient.

    Parameters:
        patient_id: The patient's unique identifier

    Returns:
        List of patient notes

    Raises:
        HTTPException: 404 if patient not found
    """
    service = NoteService(db)
    notes = service.get_patient_notes(patient_id)
    if notes is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return notes


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(
    patient_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new note for a patient.

    Parameters:
        patient_id: The patient's unique identifier
        note_data: Note data including content and timestamp

    Returns:
        Newly created note

    Raises:
        HTTPException: 404 if patient not found
    """
    service = NoteService(db)
    note = service.create_note(patient_id, note_data)
    if note is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(patient_id: int, note_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific note.

    Parameters:
        patient_id: The patient's unique identifier
        note_id: The note's unique identifier

    Raises:
        HTTPException: 404 if note not found
    """
    service = NoteService(db)
    if not service.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Note not found")


@router.delete("", status_code=200)
def delete_all_patient_notes(patient_id: int, db: Session = Depends(get_db)):
    """
    Delete all notes for a patient.

    Parameters:
        patient_id: The patient's unique identifier

    Returns:
        Count of deleted notes

    Raises:
        HTTPException: 404 if patient not found
    """
    service = NoteService(db)
    deleted = service.delete_patient_notes(patient_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"deleted": deleted}
