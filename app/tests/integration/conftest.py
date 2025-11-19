"""
Integration test configuration and fixtures.

Provides shared fixtures for integration tests with proper database setup.
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
def seeded_database(client, db_session):
    """Seed database with sample data for integration tests."""
    # Create patients
    patients_data = [
        {"name": "John Smith", "date_of_birth": date(1979, 3, 15)},
        {"name": "Jane Doe", "date_of_birth": date(1985, 7, 22)},
        {"name": "Robert Johnson", "date_of_birth": date(1992, 11, 8)},
    ]

    patients = []
    for data in patients_data:
        patient = Patient(**data)
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        patients.append(patient)

    # Create notes for first patient
    notes_data = [
        {
            "patient_id": patients[0].id,
            "content": """SOAP Note - Encounter Date: 2024-01-15
Patient: patient--001

S: 45 y/o male presenting with chest pain x 2 hours. Sharp, substernal, radiates to left arm. Associated with diaphoresis and nausea. No relief with rest. Hx of HTN, hyperlipidemia. Smoker 1 ppd x 20 years.

O:
Vitals:
BP: 145/92 mmHg
HR: 102 bpm, irregular
RR: 22 breaths/min
SpO2: 94% on RA
Temp: 98.6°F

General: Diaphoretic, appears anxious
CV: Tachycardic, irregular rhythm, no murmurs
Lungs: Clear to auscultation bilaterally
ECG: ST elevation in leads V1-V4

A:
Acute ST-elevation myocardial infarction (STEMI) - anterior wall

P:
Activate cardiac cath lab
Aspirin 325mg chewed
Heparin bolus and drip per protocol
Morphine 4mg IV for pain
Cardiology consult STAT
NPO status

Signed:
Dr. Sarah Chen, MD
Emergency Medicine""",
            "note_timestamp": datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
        },
        {
            "patient_id": patients[0].id,
            "content": """SOAP Note - Encounter Date: 2024-01-16
Patient: patient--001

S: Post-cath day 1. Patient reports significant improvement in chest pain. Mild soreness at femoral access site. No dyspnea, no palpitations. Tolerated clear liquids.

O:
Vitals:
BP: 128/78 mmHg
HR: 72 bpm, regular
RR: 16 breaths/min
SpO2: 98% on 2L NC

Access site: Small ecchymosis, no hematoma, distal pulses intact
CV: RRR, no murmurs
Lungs: CTA bilaterally

A:
STEMI s/p successful PCI to LAD with DES
Post-procedure recovery progressing well

P:
Continue dual antiplatelet therapy
Start cardiac rehab education
Advance diet as tolerated
Plan discharge tomorrow if stable
Follow-up with cardiology in 2 weeks

Signed:
Dr. Michael Torres, MD
Cardiology""",
            "note_timestamp": datetime(2024, 1, 16, 8, 0, tzinfo=timezone.utc)
        }
    ]

    for data in notes_data:
        note = Note(**data)
        db_session.add(note)

    db_session.commit()

    return {"patients": patients, "client": client, "db": db_session}
