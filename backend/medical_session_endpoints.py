# Medical Session API Endpoints - Add these to main.py

# Medical Session Endpoints
@app.post("/medical-sessions/")
def create_medical_session(
    session_data: schemas.MedicalSessionCreate,
    db: Session = Depends(get_db)
):
    from . import models
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == session_data.appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    session = medical_sessions.create_medical_session(
        db, session_data, appointment.patient_id, appointment.doctor_id
    )
    return medical_sessions.format_medical_session_response(session, db)

@app.get("/medical-sessions/{session_id}")
def get_medical_session(session_id: int, db: Session = Depends(get_db)):
    session = medical_sessions.get_medical_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Medical session not found")
    return medical_sessions.format_medical_session_response(session, db)

@app.post("/medical-sessions/{session_id}/vital-signs")
def add_vital_signs(
    session_id: int,
    vital_data: schemas.VitalSignCreate,
    db: Session = Depends(get_db)
):
    vital = medical_sessions.add_vital_signs(db, session_id, vital_data)
    return {"message": "Vital signs added", "vital_id": vital.vital_id}

@app.post("/medical-sessions/{session_id}/prescriptions")
def add_prescription(
    session_id: int,
    prescription_data: schemas.PrescriptionCreate,
    db: Session = Depends(get_db)
):
    prescription = medical_sessions.add_prescription(db, session_id, prescription_data)
    return {"message": "Prescription added", "prescription_id": prescription.prescription_id}

@app.post("/medical-sessions/{session_id}/symptoms")
def add_symptom(
    session_id: int,
    symptom_data: schemas.SymptomCreate,
    db: Session = Depends(get_db)
):
    symptom = medical_sessions.add_symptom(db, session_id, symptom_data)
    return {"message": "Symptom added", "symptom_id": symptom.symptom_id}

@app.post("/medical-sessions/{session_id}/diagnoses")
def add_diagnosis(
    session_id: int,
    diagnosis_data: schemas.DiagnosisCreate,
    db: Session = Depends(get_db)
):
    diagnosis = medical_sessions.add_diagnosis(db, session_id, diagnosis_data)
    return {"message": "Diagnosis added", "diagnosis_id": diagnosis.diagnosis_id}

@app.get("/doctor/{doctor_id}/active-sessions")
def get_doctor_active_sessions(doctor_id: int, db: Session = Depends(get_db)):
    sessions = medical_sessions.get_active_sessions_by_doctor(db, doctor_id)
    return [
        medical_sessions.format_medical_session_response(session, db)
        for session in sessions
    ]

@app.post("/medical-sessions/{session_id}/complete")
def complete_medical_session(session_id: int, db: Session = Depends(get_db)):
    session = medical_sessions.complete_medical_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Medical session not found")
    return {"message": "Medical session completed successfully"}