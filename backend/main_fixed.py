# Add these missing endpoints to main.py after the existing endpoints

# Complete the existing endpoints first
@app.put("/admin/doctor/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor_endpoint(
    doctor_id: int, doctor_data: schemas.DoctorCreate, db: Session = Depends(get_db)
):
    return admin_dashboard.edit_doctor(db, doctor_id, doctor_data)

@app.delete("/admin/doctor/{doctor_id}")
def remove_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    return admin_dashboard.remove_doctor(db, doctor_id)

# Get all patients list
@app.get("/admin/patients-list")
def get_all_patients_list_endpoint(db: Session = Depends(get_db)):
    return admin_patients.get_all_patients_list(db)

@app.get("/admin/patient/{patient_id}")
def get_patient_endpoint(patient_id: int, db: Session = Depends(get_db)):
    patient = admin_patients.get_patient_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/admin/patient/{patient_id}", response_model=schemas.PatientResponse)
def update_patient_endpoint(
    patient_id: int, patient_data: schemas.PatientCreate, db: Session = Depends(get_db)
):
    patient = admin_patients.edit_patient(db, patient_id, patient_data)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.delete("/admin/patient/{patient_id}")
def remove_patient_endpoint(patient_id: int, db: Session = Depends(get_db)):
    result = admin_patients.remove_patient(db, patient_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/admin/appointments-list", response_model=List[AdminAppointmentResponse])
def get_all_appointments_endpoint(db: Session = Depends(get_db)):
    return admin_appointments.get_all_appointments(db)

@app.get("/admin/appointment/{appointment_id}", response_model=AdminAppointmentResponse)
def get_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    appointment = admin_appointments.get_appointment_by_id(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.post("/admin/appointment")
def create_appointment_endpoint(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return admin_appointments.create_appointment(db, appointment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/admin/appointment/{appointment_id}", response_model=AdminAppointmentResponse)
def update_appointment_endpoint(
    appointment_id: int, appointment_data: AppointmentUpdate, db: Session = Depends(get_db)
):
    appointment = admin_appointments.edit_appointment(db, appointment_id, appointment_data)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.delete("/admin/appointment/{appointment_id}")
def remove_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    result = admin_appointments.remove_appointment(db, appointment_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/admin/available-doctors/{appointment_time}")
def get_available_doctors_endpoint(appointment_time: datetime, db: Session = Depends(get_db)):
    return admin_appointments.get_available_doctors(db, appointment_time)

# Doctor endpoints
@app.get("/doctor/dashboard-info/{username}", response_model=schemas.DoctorHeaderResponse)
def get_doctor_dashboard_info(username: str, db: Session = Depends(get_db)):
    doctor = doctor_dashboard_header.get_doctor_dashboard_info(db, username)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.get("/doctor/appointments/{username}", response_model=schemas.DoctorDashboardResponse)
def get_doctor_appointments(username: str, db: Session = Depends(get_db)):
    doctor = doctor_dashboard.get_doctor_by_name(db, username)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    appointments = doctor_dashboard.get_doctor_appointments(db, doctor.id)
    return doctor_dashboard.format_dashboard_response(appointments)

@app.put("/doctor/appointment/{appointment_id}")
def update_doctor_appointment(
    appointment_id: int, 
    update_data: schemas.AppointmentUpdate, 
    db: Session = Depends(get_db)
):
    try:
        # Convert string datetime to Python datetime if provided
        new_datetime = datetime.strptime(update_data.appointment_time, "%Y-%m-%d %H:%M:%S") if update_data.appointment_time else None
        
        result = doctor_dashboard.update_appointment(
            db, 
            appointment_id, 
            new_datetime=new_datetime,
            new_status=update_data.status
        )
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return {"status": "success", "message": "Appointment updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/doctor/profile/{username}")
def get_doctor_profile(username: str, db: Session = Depends(get_db)):
    doctor = doctor_profiles.get_doctor_profile(db, username)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor_profiles.format_profile_response(doctor)

@app.get("/doctor/all-appointments/{username}")
def get_all_doctor_appointments(username: str, db: Session = Depends(get_db)):
    doctor = doctor_appointments.get_doctor_by_name(db, username)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    appointments = doctor_appointments.get_all_doctor_appointments(db, doctor.id)
    return doctor_appointments.format_appointments_response(appointments)

@app.get("/doctor/patients/{username}")
def get_doctor_patients(username: str, db: Session = Depends(get_db)):
    doctor = doctor_patients.get_doctor_by_name(db, username)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    patients = doctor_patients.get_doctor_patients(db, doctor.id)
    return doctor_patients.format_patients_response(patients)

@app.get("/api/patient/{patient_id}")
def get_patient_detail(patient_id: int, db: Session = Depends(get_db)):
    patient_data = patient_detail.get_patient_detail(db, patient_id)
    if not patient_data:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_data

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
    
    existing_session = db.query(models.MedicalSession).filter(
        models.MedicalSession.appointment_id == appointment_id
    ).first()
    
    if existing_session:
        return {"session_id": existing_session.session_id, "message": "Session already exists"}
    
    session_data = schemas.MedicalSessionCreate(appointment_id=appointment_id)
    session = medical_sessions.create_medical_session(
        db, session_data, appointment.patient_id, appointment.doctor_id
    )
    
    appointment.status = "in_progress"
    db.commit()
    
    return {"session_id": session.session_id, "message": "Medical session started"}

@app.get("/doctor/{doctor_id}/active-sessions")
def get_doctor_active_sessions(doctor_id: int, db: Session = Depends(get_db)):
    sessions = medical_sessions.get_active_sessions_by_doctor(db, doctor_id)
    return [
        medical_sessions.format_medical_session_response(session, db)
        for session in sessions
    ]

@app.get("/patient/{patient_id}/medical-history")
def get_patient_complete_history(patient_id: int, db: Session = Depends(get_db)):
    sessions = medical_sessions.get_patient_medical_history(db, patient_id)
    return [
        medical_sessions.format_medical_session_response(session, db)
        for session in sessions
    ]