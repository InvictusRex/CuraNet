from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from .. import models, schemas


def create_medical_session(db: Session, session_data: schemas.MedicalSessionCreate, patient_id: int, doctor_id: int):
    """Create a new medical session"""
    db_session = models.MedicalSession(
        appointment_id=session_data.appointment_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        chief_complaint=session_data.chief_complaint,
        session_notes=session_data.session_notes,
        status=models.SessionStatus.active
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_medical_session(db: Session, session_id: int):
    """Get medical session by ID"""
    return db.query(models.MedicalSession).filter(models.MedicalSession.session_id == session_id).first()


def get_active_sessions_by_doctor(db: Session, doctor_id: int):
    """Get all active medical sessions for a doctor"""
    return db.query(models.MedicalSession).filter(
        and_(
            models.MedicalSession.doctor_id == doctor_id,
            models.MedicalSession.status == models.SessionStatus.active
        )
    ).all()


def get_patient_medical_history(db: Session, patient_id: int):
    """Get complete medical history for a patient"""
    return db.query(models.MedicalSession).filter(
        models.MedicalSession.patient_id == patient_id
    ).order_by(models.MedicalSession.session_date.desc()).all()


def update_medical_session(db: Session, session_id: int, session_data: schemas.MedicalSessionUpdate):
    """Update medical session"""
    db_session = db.query(models.MedicalSession).filter(models.MedicalSession.session_id == session_id).first()
    if db_session:
        if session_data.chief_complaint is not None:
            db_session.chief_complaint = session_data.chief_complaint
        if session_data.session_notes is not None:
            db_session.session_notes = session_data.session_notes
        if session_data.status is not None:
            db_session.status = models.SessionStatus(session_data.status)
        
        db_session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session


def complete_medical_session(db: Session, session_id: int):
    """Mark medical session as completed"""
    db_session = db.query(models.MedicalSession).filter(models.MedicalSession.session_id == session_id).first()
    if db_session:
        db_session.status = models.SessionStatus.completed
        db_session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session


# Vital Signs CRUD
def add_vital_signs(db: Session, session_id: int, vital_data: schemas.VitalSignCreate):
    """Add vital signs to a medical session"""
    db_vital = models.VitalSign(
        session_id=session_id,
        **vital_data.dict(exclude_unset=True)
    )
    db.add(db_vital)
    db.commit()
    db.refresh(db_vital)
    return db_vital


def get_session_vital_signs(db: Session, session_id: int):
    """Get all vital signs for a session"""
    return db.query(models.VitalSign).filter(models.VitalSign.session_id == session_id).all()


# Symptoms CRUD
def add_symptom(db: Session, session_id: int, symptom_data: schemas.SymptomCreate):
    """Add symptom to a medical session"""
    db_symptom = models.Symptom(
        session_id=session_id,
        symptom_description=symptom_data.symptom_description,
        severity=models.SeverityLevel(symptom_data.severity),
        duration=symptom_data.duration,
        notes=symptom_data.notes
    )
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


def get_session_symptoms(db: Session, session_id: int):
    """Get all symptoms for a session"""
    return db.query(models.Symptom).filter(models.Symptom.session_id == session_id).all()


# Prescriptions CRUD
def add_prescription(db: Session, session_id: int, prescription_data: schemas.PrescriptionCreate):
    """Add prescription to a medical session"""
    db_prescription = models.Prescription(
        session_id=session_id,
        **prescription_data.dict()
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription


def get_session_prescriptions(db: Session, session_id: int):
    """Get all prescriptions for a session"""
    return db.query(models.Prescription).filter(models.Prescription.session_id == session_id).all()


# Diagnoses CRUD
def add_diagnosis(db: Session, session_id: int, diagnosis_data: schemas.DiagnosisCreate):
    """Add diagnosis to a medical session"""
    db_diagnosis = models.Diagnosis(
        session_id=session_id,
        diagnosis_code=diagnosis_data.diagnosis_code,
        diagnosis_description=diagnosis_data.diagnosis_description,
        diagnosis_type=models.DiagnosisType(diagnosis_data.diagnosis_type),
        confidence_level=models.ConfidenceLevel(diagnosis_data.confidence_level),
        notes=diagnosis_data.notes
    )
    db.add(db_diagnosis)
    db.commit()
    db.refresh(db_diagnosis)
    return db_diagnosis


def get_session_diagnoses(db: Session, session_id: int):
    """Get all diagnoses for a session"""
    return db.query(models.Diagnosis).filter(models.Diagnosis.session_id == session_id).all()


# Treatment Plans CRUD
def add_treatment_plan(db: Session, session_id: int, treatment_data: schemas.TreatmentPlanCreate):
    """Add treatment plan to a medical session"""
    db_treatment = models.TreatmentPlan(
        session_id=session_id,
        treatment_description=treatment_data.treatment_description,
        start_date=treatment_data.start_date,
        end_date=treatment_data.end_date,
        follow_up_required=treatment_data.follow_up_required,
        follow_up_date=treatment_data.follow_up_date,
        notes=treatment_data.notes,
        status=models.TreatmentStatus.active
    )
    db.add(db_treatment)
    db.commit()
    db.refresh(db_treatment)
    return db_treatment


def get_session_treatment_plans(db: Session, session_id: int):
    """Get all treatment plans for a session"""
    return db.query(models.TreatmentPlan).filter(models.TreatmentPlan.session_id == session_id).all()


def format_medical_session_response(session: models.MedicalSession, db: Session):
    """Format medical session for API response"""
    # Get patient and doctor names
    patient = db.query(models.Patient).filter(models.Patient.id == session.patient_id).first()
    doctor = db.query(models.Doctor).filter(models.Doctor.id == session.doctor_id).first()
    
    # Get all related data
    vital_signs = get_session_vital_signs(db, session.session_id)
    symptoms = get_session_symptoms(db, session.session_id)
    prescriptions = get_session_prescriptions(db, session.session_id)
    diagnoses = get_session_diagnoses(db, session.session_id)
    treatment_plans = get_session_treatment_plans(db, session.session_id)
    
    return {
        "session_id": session.session_id,
        "appointment_id": session.appointment_id,
        "patient_id": session.patient_id,
        "doctor_id": session.doctor_id,
        "session_date": session.session_date.isoformat() if session.session_date else None,
        "status": session.status.value if session.status else None,
        "chief_complaint": session.chief_complaint,
        "session_notes": session.session_notes,
        "patient_name": patient.name if patient else "Unknown",
        "doctor_name": doctor.name if doctor else "Unknown",
        "vital_signs": [
            {
                "vital_id": vs.vital_id,
                "blood_pressure": f"{vs.blood_pressure_systolic}/{vs.blood_pressure_diastolic}" if vs.blood_pressure_systolic and vs.blood_pressure_diastolic else None,
                "heart_rate": vs.heart_rate,
                "temperature": float(vs.temperature) if vs.temperature else None,
                "respiratory_rate": vs.respiratory_rate,
                "oxygen_saturation": vs.oxygen_saturation,
                "weight": float(vs.weight) if vs.weight else None,
                "height": float(vs.height) if vs.height else None,
                "recorded_at": vs.recorded_at.isoformat() if vs.recorded_at else None
            } for vs in vital_signs
        ],
        "symptoms": [
            {
                "symptom_id": s.symptom_id,
                "description": s.symptom_description,
                "severity": s.severity.value if s.severity else None,
                "duration": s.duration,
                "notes": s.notes,
                "recorded_at": s.recorded_at.isoformat() if s.recorded_at else None
            } for s in symptoms
        ],
        "prescriptions": [
            {
                "prescription_id": p.prescription_id,
                "medication_name": p.medication_name,
                "dosage": p.dosage,
                "frequency": p.frequency,
                "duration": p.duration,
                "instructions": p.instructions,
                "prescribed_date": p.prescribed_date.isoformat() if p.prescribed_date else None
            } for p in prescriptions
        ],
        "diagnoses": [
            {
                "diagnosis_id": d.diagnosis_id,
                "code": d.diagnosis_code,
                "description": d.diagnosis_description,
                "type": d.diagnosis_type.value if d.diagnosis_type else None,
                "confidence": d.confidence_level.value if d.confidence_level else None,
                "notes": d.notes,
                "diagnosed_at": d.diagnosed_at.isoformat() if d.diagnosed_at else None
            } for d in diagnoses
        ],
        "treatment_plans": [
            {
                "plan_id": t.plan_id,
                "description": t.treatment_description,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "status": t.status.value if t.status else None,
                "follow_up_required": t.follow_up_required,
                "follow_up_date": t.follow_up_date.isoformat() if t.follow_up_date else None,
                "notes": t.notes
            } for t in treatment_plans
        ]
    }