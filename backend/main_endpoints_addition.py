# Add these endpoints to the end of main.py

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

@app.post("/medical-sessions/{session_id}/complete")
def complete_medical_session(session_id: int, db: Session = Depends(get_db)):
    session = medical_sessions.complete_medical_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Medical session not found")
    return {"message": "Medical session completed successfully"}

@app.post("/appointments/{appointment_id}/start-session")
def start_medical_session(appointment_id: int, db: Session = Depends(get_db)):
    from . import models
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check if session already exists
    existing_session = db.query(models.MedicalSession).filter(
        models.MedicalSession.appointment_id == appointment_id
    ).first()
    
    if existing_session:
        return {"session_id": existing_session.session_id, "message": "Session already exists"}
    
    # Create new session
    session_data = schemas.MedicalSessionCreate(appointment_id=appointment_id)
    session = medical_sessions.create_medical_session(
        db, session_data, appointment.patient_id, appointment.doctor_id
    )
    
    # Update appointment status to "in_progress"
    appointment.status = "in_progress"
    db.commit()
    
    return {"session_id": session.session_id, "message": "Medical session started"}