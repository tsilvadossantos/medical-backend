"""
Database initialization module.

Provides functions to create tables and seed initial data.
"""
import logging
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine
from app.models.patient import Patient
from app.models.note import Note

logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize database by creating all tables.

    Creates all tables defined in SQLAlchemy models if they don't exist.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def seed_sample_data(db: Session):
    """
    Seed the database with sample patient data and notes.

    Creates sample patients with SOAP notes if the database is empty,
    useful for development and testing purposes.

    Parameters:
        db: SQLAlchemy database session
    """
    if db.query(Patient).count() > 0:
        logger.info("Database already contains data, skipping seed")
        return

    # Create sample patients
    patient1 = Patient(
        name="John Smith",
        date_of_birth=date(1985, 3, 15)
    )
    patient2 = Patient(
        name="Jane Doe",
        date_of_birth=date(1990, 7, 22)
    )
    patient3 = Patient(
        name="Robert Johnson",
        date_of_birth=date(1978, 11, 8)
    )

    db.add_all([patient1, patient2, patient3])
    db.flush()  # Get IDs assigned

    # Create sample SOAP notes for patient 1 (John Smith)
    notes_patient1 = [
        Note(
            patient_id=patient1.id,
            content="""SOAP Note - Encounter Date: 2024-01-15
Patient: patient--001

S: 39 y/o male presenting with chest pain x 2 hours. Sharp, substernal, radiates to left arm. Associated with diaphoresis and nausea. No relief with rest. Hx of HTN, hyperlipidemia. Smoker 1 ppd x 15 years.

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
            note_timestamp=datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
        ),
        Note(
            patient_id=patient1.id,
            content="""SOAP Note - Encounter Date: 2024-01-16
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
            note_timestamp=datetime(2024, 1, 16, 8, 0, tzinfo=timezone.utc)
        )
    ]

    # Create sample SOAP notes for patient 2 (Jane Doe)
    notes_patient2 = [
        Note(
            patient_id=patient2.id,
            content="""SOAP Note - Encounter Date: 2024-01-18
Patient: patient--002

S: 34 y/o female with type 2 DM presents for routine follow-up. Reports increased thirst and frequent urination x 1 week. Admits to dietary non-compliance during recent holidays. Denies chest pain, SOB, or LE swelling.

O:
Vitals:
BP: 138/84 mmHg
HR: 72 bpm, regular
Wt: 185 lbs (up 3 lbs from last visit)

General: Well-appearing, NAD
CV: RRR, no murmurs
EXT: No edema, peripheral pulses 2+ bilat
Labs: HbA1c 8.2% (previous 7.4%), FBG 186 mg/dL

A:
Type 2 diabetes mellitus - poorly controlled
Hypertension - at goal
Obesity

P:
Increase Metformin to 1000mg BID
Add Glipizide 5mg daily
Reinforce dietary counseling
Recheck HbA1c in 3 months
Continue Lisinopril 20mg daily

Signed:
Dr. James Wilson, MD
Internal Medicine""",
            note_timestamp=datetime(2024, 1, 18, 10, 30, tzinfo=timezone.utc)
        )
    ]

    # Create sample SOAP notes for patient 3 (Robert Johnson)
    notes_patient3 = [
        Note(
            patient_id=patient3.id,
            content="""SOAP Note - Encounter Date: 2024-01-20
Patient: patient--003

S: 46 y/o male presents with 2-week hx of progressive lower back pain. Pain is dull, constant, rated 6/10. Worse with prolonged sitting. No radiation to legs. No bowel/bladder changes. No recent trauma.

O:
Vitals:
BP: 128/82 mmHg
HR: 76 bpm
Temp: 98.4°F

Spine: Mild paraspinal muscle tenderness L3-L5. No step-off. SLR negative bilaterally.
Neuro: Strength 5/5 LE bilat. DTRs 2+ and symmetric. Sensation intact.

A:
Mechanical low back pain - likely muscular strain

P:
Ibuprofen 600mg TID with food x 7 days
Ice/heat alternating PRN
Stretching exercises - handout provided
Physical therapy referral if not improved in 2 weeks
Return if symptoms worsen or neurological changes develop

Signed:
Dr. Jennifer Lee, MD
Family Medicine""",
            note_timestamp=datetime(2024, 1, 20, 14, 30, tzinfo=timezone.utc)
        )
    ]

    # Add all notes
    db.add_all(notes_patient1 + notes_patient2 + notes_patient3)
    db.commit()

    logger.info(f"Seeded 3 sample patients with {len(notes_patient1) + len(notes_patient2) + len(notes_patient3)} notes")
