"""
Test configuration and fixtures.

Provides shared test fixtures and database setup for all tests.
"""
import pytest
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.patient import Patient
from app.models.note import Note

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create database session for direct database operations."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_patient(db_session):
    """Create a sample patient."""
    patient = Patient(
        name="John Doe",
        date_of_birth=date(1990, 5, 15)
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def sample_patient_with_notes(db_session):
    """Create a sample patient with notes."""
    patient = Patient(
        name="Jane Smith",
        date_of_birth=date(1985, 3, 20)
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    notes = [
        Note(
            patient_id=patient.id,
            content="""Subjective:
Patient reports headache for 2 days.

Objective:
Vitals normal. No neurological deficits.

Assessment:
Tension headache.

Plan:
Ibuprofen 400mg PRN. Follow up if persists.""",
            note_timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        ),
        Note(
            patient_id=patient.id,
            content="Follow-up: Headache resolved.",
            note_timestamp=datetime(2024, 1, 20, 14, 30, tzinfo=timezone.utc)
        )
    ]

    for note in notes:
        db_session.add(note)

    db_session.commit()
    return patient


@pytest.fixture
def multiple_patients(db_session):
    """Create multiple patients for pagination tests."""
    patients = []
    for i in range(15):
        patient = Patient(
            name=f"Patient {i+1:02d}",
            date_of_birth=date(1980 + i, 1, 1)
        )
        db_session.add(patient)
        patients.append(patient)

    db_session.commit()
    for p in patients:
        db_session.refresh(p)
    return patients
