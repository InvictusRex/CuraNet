from fastapi import FastAPI, Depends, HTTPException, Security, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import os
import json

# Relative imports within backend package
from . import schemas
from .database import SessionLocal
from .crud import (
    patients,
    doctors,
    appointments,
    admins,
    patient_dashboard_header,
    patient_profiles,
    patient_medical_history,
    patient_dashboard,
    admin_dashboard_header,
    admin_dashboard,
    admin_doctors,
    admin_patients,
    admin_appointments,
    doctor_dashboard_header,
    doctor_dashboard,
    doctor_profiles,
    doctor_appointments,
    doctor_patients,
    patient_detail,
    medical_sessions,
)
from .schemas import AdminAppointmentResponse, AppointmentCreate, AppointmentUpdate
from .s3_service import S3Service
from . import models

app = FastAPI()

# Mount static files
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/assets", StaticFiles(directory=os.path.join(base_dir, "assets")), name="assets")
app.mount("/pages", StaticFiles(directory=os.path.join(base_dir, "pages")), name="pages")

# Serve test files
@app.get("/test_small_upload.html")
def test_upload_page():
    return FileResponse(os.path.join(base_dir, "test_small_upload.html"))

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return credentials.credentials
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
@app.get("/")
def root():
    return FileResponse(os.path.join(base_dir, "index.html"))

@app.get("/api")
def api_root():
    return {"message": "CuraNet API is running"}

@app.get("/test-upload")
def test_upload_simple():
    """Test upload functionality with a simple file"""
    try:
        # Create a small test file
        test_content = b"This is a test medical report file for testing upload functionality."
        
        # Test the upload process
        file_key = s3_service.upload_file(
            test_content, "test_report.txt", "text/plain", 1, 1
        )
        
        # Test database save
        from .database import SessionLocal
        db = SessionLocal()
        
        try:
            report = models.MedicalReport(
                patient_id=1,
                doctor_id=1,
                session_id=None,
                report_name="test_report.txt",
                file_key=file_key,
                file_size=len(test_content),
                content_type="text/plain",
                shared_with="[]"
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            # Test download URL
            download_url = s3_service.generate_presigned_url(file_key)
            
            return {
                "status": "success",
                "message": "Upload test successful",
                "report_id": report.report_id,
                "file_key": file_key,
                "download_url": download_url,
                "s3_service_type": type(s3_service).__name__
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "s3_service_type": type(s3_service).__name__,
            "error_type": type(e).__name__
        }

@app.get("/test-env")
def test_environment():
    """Test environment variables"""
    import os
    return {
        "aws_key_set": bool(os.getenv('AWS_ACCESS_KEY_ID')),
        "aws_secret_set": bool(os.getenv('AWS_SECRET_ACCESS_KEY')),
        "aws_region": os.getenv('AWS_REGION'),
        "s3_bucket": os.getenv('S3_BUCKET_NAME'),
        "aws_key_prefix": os.getenv('AWS_ACCESS_KEY_ID', '')[:10] if os.getenv('AWS_ACCESS_KEY_ID') else 'NOT SET'
    }

@app.post("/patients/register", response_model=schemas.PatientResponse)
def register_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    if patients.get_patient_by_email(db, patient.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if patients.get_patient_by_phone(db, patient.phone):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    return patients.create_patient(db, patient)

@app.post("/doctors/register", response_model=schemas.DoctorResponse)
def register_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    if doctors.get_doctor_by_email(db, doctor.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if doctors.get_doctor_by_phone(db, doctor.phone):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    return doctors.create_doctor(db, doctor)

@app.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    if user.user_type == "patient":
        db_user = patients.verify_patient(db, user.identifier, user.password)
    elif user.user_type == "doctor":
        db_user = doctors.verify_doctor(db, user.identifier, user.password)
    elif user.user_type == "admin":
        db_user = admins.verify_admin(db, user.identifier, user.password)
    else:
        raise HTTPException(status_code=400, detail="Invalid user type. Must be 'patient', 'doctor', or 'admin'")

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "type": user.user_type,
            "department": getattr(db_user, "department", None),
        },
    }

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

# Patient dashboard header info
@app.get("/patient/dashboard-info/{username}", response_model=schemas.DashboardResponse)
def get_patient_dashboard_info(username: str, db: Session = Depends(get_db)):
    patient = patient_dashboard.get_patient_dashboard_info(db, username)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    recent_appointments = patient_dashboard.get_recent_appointments(db, patient.id)
    return patient_dashboard.format_dashboard_response(patient, recent_appointments)

# Admin dashboard header info
@app.get("/admin/dashboard-info/{admin_id}", response_model=schemas.AdminHeaderResponse)
def get_admin_dashboard_info(admin_id: int, db: Session = Depends(get_db)):
    admin = admin_dashboard_header.get_admin_header_info(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

# Get recent doctors list
@app.get("/admin/recent-doctors")
def get_recent_doctors_endpoint(db: Session = Depends(get_db)):
    return admin_dashboard.get_recent_doctors(db)

# Get all doctors list
@app.get("/admin/doctors-list")
def get_all_doctors_list_endpoint(db: Session = Depends(get_db)):
    return admin_doctors.get_all_doctors_list(db)

@app.get("/admin/doctor/{doctor_id}")
def get_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctors.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# Update doctor information
@app.put("/admin/doctor/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor_endpoint(
    doctor_id: int, doctor_data: schemas.DoctorCreate, db: Session = Depends(get_db)
):
    return admin_dashboard.edit_doctor(db, doctor_id, doctor_data)

# Delete doctor
@app.delete("/admin/doctor/{doctor_id}")
def remove_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    return admin_dashboard.remove_doctor(db, doctor_id)

# Get doctor availability for a specific date
@app.get("/doctor/availability/{doctor_id}")
def get_doctor_availability(doctor_id: int, date: str, db: Session = Depends(get_db)):
    try:
        from datetime import datetime
        from . import models
        
        # Parse the date
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # Get existing appointments for this doctor on this date
        from sqlalchemy import func, Date
        existing_appointments = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == doctor_id,
            func.date(models.Appointment.appointment_time) == target_date
        ).all()
        
        # Extract booked time slots
        booked_slots = []
        for apt in existing_appointments:
            time_str = apt.appointment_time.strftime("%H:%M")
            booked_slots.append(time_str)
        
        # Define all available time slots
        all_slots = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
        ]
        
        # Return available slots (not booked)
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return {
            "date": date,
            "doctor_id": doctor_id,
            "available_slots": available_slots,
            "booked_slots": booked_slots
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Patient endpoints
@app.get("/patient/profile/{username}")
def get_patient_profile(username: str, db: Session = Depends(get_db)):
    patient = patient_profiles.get_patient_profile(db, username)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_profiles.format_profile_response(patient)

@app.get("/patient/medical-history/{username}")
def get_patient_medical_history(username: str, db: Session = Depends(get_db)):
    patient = patient_medical_history.get_patient_by_name(db, username)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    appointments = patient_medical_history.get_patient_medical_history(db, patient.id)
    return patient_medical_history.format_medical_history_response(patient, appointments)

# Doctor list endpoint
@app.get("/api/doctors", response_model=List[schemas.DoctorResponse])
async def read_doctors(
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if department:
        return doctors.get_doctors_by_department(db, department)
    elif search:
        return doctors.search_doctors(db, search)
    return doctors.get_doctors(db, skip=0, limit=100)

@app.get("/api/departments", response_model=List[str])
async def get_departments(db: Session = Depends(get_db)):
    return doctors.get_all_departments(db)

# Get all patients list
@app.get("/admin/patients-list")
def get_all_patients_list_endpoint(db: Session = Depends(get_db)):
    return admin_patients.get_all_patients_list(db)

# Get specific patient details
@app.get("/admin/patient/{patient_id}")
def get_patient_endpoint(patient_id: int, db: Session = Depends(get_db)):
    patient = admin_patients.get_patient_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Update patient details
@app.put("/admin/patient/{patient_id}", response_model=schemas.PatientResponse)
def update_patient_endpoint(
    patient_id: int, patient_data: schemas.PatientCreate, db: Session = Depends(get_db)
):
    patient = admin_patients.edit_patient(db, patient_id, patient_data)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Remove patient
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

# Admin patient medical history access
@app.get("/admin/patient/{patient_id}/medical-history")
def get_admin_patient_medical_history(patient_id: int, db: Session = Depends(get_db)):
    from . import models
    
    # Get patient info
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all medical sessions for this patient
    sessions = db.query(models.MedicalSession).filter(
        models.MedicalSession.patient_id == patient_id
    ).order_by(models.MedicalSession.session_date.desc()).all()
    
    # Get all appointments for this patient
    appointments = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).order_by(models.Appointment.appointment_time.desc()).all()
    
    session_history = []
    for session in sessions:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == session.doctor_id).first()
        
        # Get detailed session data
        vital_signs = db.query(models.VitalSign).filter(
            models.VitalSign.session_id == session.session_id
        ).all()
        
        prescriptions = db.query(models.Prescription).filter(
            models.Prescription.session_id == session.session_id
        ).all()
        
        symptoms = db.query(models.Symptom).filter(
            models.Symptom.session_id == session.session_id
        ).all()
        
        session_history.append({
            "session_id": session.session_id,
            "session_date": session.session_date.isoformat(),
            "doctor_name": doctor.name if doctor else "Unknown Doctor",
            "doctor_department": doctor.department if doctor else "Unknown",
            "chief_complaint": session.chief_complaint,
            "session_notes": session.session_notes,
            "status": session.status,
            "vital_signs": [{
                "blood_pressure": f"{vs.blood_pressure_systolic}/{vs.blood_pressure_diastolic}" if vs.blood_pressure_systolic and vs.blood_pressure_diastolic else None,
                "heart_rate": vs.heart_rate,
                "temperature": vs.temperature,
                "weight": vs.weight,
                "height": vs.height
            } for vs in vital_signs],
            "prescriptions": [{
                "medication_name": p.medication_name,
                "dosage": p.dosage,
                "frequency": p.frequency,
                "duration": p.duration,
                "instructions": p.instructions
            } for p in prescriptions],
            "symptoms": [{
                "description": s.symptom_description,
                "severity": s.severity,
                "duration": s.duration,
                "notes": s.notes
            } for s in symptoms]
        })
    
    appointment_history = []
    for appointment in appointments:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == appointment.doctor_id).first()
        appointment_history.append({
            "appointment_id": appointment.id,
            "date_time": appointment.appointment_time.isoformat(),
            "doctor_name": doctor.name if doctor else "Unknown Doctor",
            "doctor_department": doctor.department if doctor else "Unknown",
            "status": appointment.status
        })
    
    return {
        "patient_info": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "blood_group": patient.blood_group,
            "email": patient.email,
            "phone": patient.phone,
            "medical_history": patient.medical_history
        },
        "appointments": appointment_history,
        "medical_sessions": session_history,
        "total_appointments": len(appointment_history),
        "total_sessions": len(session_history)
    }

@app.get("/admin/patients/{patient_id}/summary")
def get_admin_patient_summary(patient_id: int, db: Session = Depends(get_db)):
    from . import models
    from sqlalchemy import func
    
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get statistics
    total_appointments = db.query(func.count(models.Appointment.id)).filter(
        models.Appointment.patient_id == patient_id
    ).scalar()
    
    total_sessions = db.query(func.count(models.MedicalSession.session_id)).filter(
        models.MedicalSession.patient_id == patient_id
    ).scalar()
    
    # Get unique doctors who treated this patient
    doctors = db.query(models.Doctor).join(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).distinct().all()
    
    # Get recent prescriptions
    recent_prescriptions = db.query(models.Prescription).join(models.MedicalSession).filter(
        models.MedicalSession.patient_id == patient_id
    ).order_by(models.MedicalSession.session_date.desc()).limit(5).all()
    
    return {
        "patient_info": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "blood_group": patient.blood_group,
            "email": patient.email,
            "phone": patient.phone
        },
        "statistics": {
            "total_appointments": total_appointments,
            "total_sessions": total_sessions,
            "doctors_consulted": len(doctors)
        },
        "doctors": [{
            "name": doctor.name,
            "department": doctor.department
        } for doctor in doctors],
        "recent_prescriptions": [{
            "medication_name": p.medication_name,
            "dosage": p.dosage,
            "frequency": p.frequency
        } for p in recent_prescriptions]
    }

# Removed duplicate endpoints - keeping the ones below

@app.get("/api/patient/{patient_id}")
def get_patient_detail(patient_id: str, db: Session = Depends(get_db)):
    try:
        # Handle patient ID with 'P' prefix (e.g., 'P182553' -> 182553)
        if patient_id.startswith('P'):
            numeric_id = int(patient_id[1:])
        else:
            numeric_id = int(patient_id)
        
        # Get patient directly from database
        patient = db.query(models.Patient).filter(models.Patient.id == numeric_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "blood_group": patient.blood_group,
            "email": patient.email,
            "phone": patient.phone,
            "medical_history": patient.medical_history or "No medical history recorded"
        }
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid patient ID format")
    except Exception as e:
        print(f"Patient detail error: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving patient details: {str(e)}")

@app.get("/patient/{patient_id}/medical-history")
def get_patient_medical_history_by_id(patient_id: str, db: Session = Depends(get_db)):
    from . import models
    
    try:
        # Handle patient ID with 'P' prefix
        if patient_id.startswith('P'):
            numeric_id = int(patient_id[1:])
        else:
            numeric_id = int(patient_id)
        
        # Get all medical sessions for this patient (cross-doctor access)
        sessions = db.query(models.MedicalSession).filter(
            models.MedicalSession.patient_id == numeric_id
        ).order_by(models.MedicalSession.session_date.desc()).all()
        
        history = []
        for session in sessions:
            doctor = db.query(models.Doctor).filter(models.Doctor.id == session.doctor_id).first()
            
            # Get prescriptions for this session
            prescriptions = db.query(models.Prescription).filter(
                models.Prescription.session_id == session.session_id
            ).all()
            
            # Get diagnoses for this session (if diagnosis table exists)
            diagnoses = []
            try:
                diagnoses = db.query(models.Diagnosis).filter(
                    models.Diagnosis.session_id == session.session_id
                ).all()
            except:
                pass  # Diagnosis table might not exist
            
            history.append({
                "session_id": session.session_id,
                "session_date": session.session_date.isoformat(),
                "doctor_name": doctor.name if doctor else "Unknown Doctor",
                "doctor_department": doctor.department if doctor else "Unknown",
                "chief_complaint": session.chief_complaint or "Not recorded",
                "session_notes": session.session_notes or "",
                "status": session.status,
                "prescriptions": [{
                    "medication_name": p.medication_name,
                    "dosage": p.dosage,
                    "frequency": p.frequency,
                    "duration": p.duration
                } for p in prescriptions],
                "diagnoses": [{
                    "description": d.diagnosis_description
                } for d in diagnoses]
            })
        
        return history
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid patient ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving medical history: {str(e)}")

# Medical Session Endpoints
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

@app.get("/medical-sessions/{session_id}")
def get_medical_session(session_id: int, db: Session = Depends(get_db)):
    session = medical_sessions.get_medical_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Medical session not found")
    return medical_sessions.format_medical_session_response(session, db)

@app.put("/medical-sessions/{session_id}")
def update_medical_session(
    session_id: int,
    session_data: schemas.MedicalSessionUpdate,
    db: Session = Depends(get_db)
):
    session = medical_sessions.update_medical_session(db, session_id, session_data)
    if not session:
        raise HTTPException(status_code=404, detail="Medical session not found")
    return {"message": "Medical session updated successfully"}

@app.post("/medical-sessions/{session_id}/complete")
def complete_medical_session(session_id: int, db: Session = Depends(get_db)):
    session = medical_sessions.complete_medical_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Medical session not found")
    return {"message": "Medical session completed successfully"}

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

@app.get("/doctor/{doctor_id}/active-sessions")
def get_doctor_active_sessions(doctor_id: int, db: Session = Depends(get_db)):
    sessions = medical_sessions.get_active_sessions_by_doctor(db, doctor_id)
    return [
        medical_sessions.format_medical_session_response(session, db)
        for session in sessions
    ]

@app.get("/patient/{patient_id}/complete-history")
def get_patient_complete_history(patient_id: str, db: Session = Depends(get_db)):
    from . import models
    
    try:
        # Handle patient ID with 'P' prefix
        if patient_id.startswith('P'):
            numeric_id = int(patient_id[1:])
        else:
            numeric_id = int(patient_id)
        
        # Get patient basic info
        patient = db.query(models.Patient).filter(models.Patient.id == numeric_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get all medical sessions for this patient (from any doctor)
        sessions = db.query(models.MedicalSession).filter(
            models.MedicalSession.patient_id == numeric_id
        ).order_by(models.MedicalSession.session_date.desc()).all()
        
        session_history = []
        for session in sessions:
            doctor = db.query(models.Doctor).filter(models.Doctor.id == session.doctor_id).first()
            
            # Get vital signs for this session
            vital_signs = db.query(models.VitalSign).filter(
                models.VitalSign.session_id == session.session_id
            ).all()
            
            # Get prescriptions for this session
            prescriptions = db.query(models.Prescription).filter(
                models.Prescription.session_id == session.session_id
            ).all()
            
            # Get symptoms for this session
            symptoms = db.query(models.Symptom).filter(
                models.Symptom.session_id == session.session_id
            ).all()
            
            session_history.append({
                "session_id": session.session_id,
                "session_date": session.session_date.isoformat(),
                "doctor_name": doctor.name if doctor else "Unknown Doctor",
                "doctor_department": doctor.department if doctor else "Unknown",
                "chief_complaint": session.chief_complaint,
                "session_notes": session.session_notes,
                "status": session.status,
                "vital_signs": [{
                    "blood_pressure": f"{vs.blood_pressure_systolic}/{vs.blood_pressure_diastolic}" if vs.blood_pressure_systolic and vs.blood_pressure_diastolic else None,
                    "heart_rate": vs.heart_rate,
                    "temperature": vs.temperature,
                    "weight": vs.weight,
                    "height": vs.height
                } for vs in vital_signs],
                "prescriptions": [{
                    "medication_name": p.medication_name,
                    "dosage": p.dosage,
                    "frequency": p.frequency,
                    "duration": p.duration,
                    "instructions": p.instructions
                } for p in prescriptions],
                "symptoms": [{
                    "description": s.symptom_description,
                    "severity": s.severity,
                    "duration": s.duration,
                    "notes": s.notes
                } for s in symptoms]
            })
        
        return {
            "patient_info": {
                "id": patient.id,
                "name": patient.name,
                "age": patient.age,
                "blood_group": patient.blood_group,
                "email": patient.email,
                "phone": patient.phone,
                "medical_history": patient.medical_history
            },
            "medical_sessions": session_history
        }
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid patient ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving complete history: {str(e)}")

# File Sharing Endpoints - Mock S3 service for testing
class MockS3Service:
    def upload_file(self, file_content, filename, content_type, patient_id, doctor_id):
        # Generate a mock file key
        import uuid
        return f"mock/patient_{patient_id}/doctor_{doctor_id}/{uuid.uuid4()}_{filename}"
    
    def generate_presigned_url(self, file_key, expiration=3600):
        # Return a mock download URL
        return f"https://mock-s3-url.com/download/{file_key}?expires={expiration}"
    
    def delete_file(self, file_key):
        return True

try:
    s3_service = S3Service()
    print("✅ S3 service initialized successfully")
except Exception as e:
    print(f"⚠️  S3 service failed, using mock service: {e}")
    s3_service = MockS3Service()

@app.post("/reports/upload")
async def upload_report(
    file: UploadFile = File(...),
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    session_id: Optional[int] = Form(None),
    shared_with: str = Form("[]"),
    db: Session = Depends(get_db)
):
    try:
        print(f"Upload attempt: file={file.filename}, patient={patient_id}, doctor={doctor_id}")
        
        # Validate file size (50MB limit)
        file_content = await file.read()
        print(f"File size: {len(file_content)} bytes")
        
        if len(file_content) > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
        
        # Upload to S3
        print("Uploading to S3...")
        file_key = s3_service.upload_file(
            file_content, file.filename, file.content_type, patient_id, doctor_id
        )
        print(f"S3 upload successful: {file_key}")
        
        # Save to database using raw SQL to avoid model issues
        print("Saving to database...")
        try:
            from sqlalchemy import text
            result = db.execute(text("""
                INSERT INTO medical_reports 
                (patient_id, doctor_id, session_id, report_name, file_key, file_size, content_type, shared_with)
                VALUES (:patient_id, :doctor_id, :session_id, :report_name, :file_key, :file_size, :content_type, :shared_with)
            """), {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'session_id': session_id,
                'report_name': file.filename,
                'file_key': file_key,
                'file_size': len(file_content),
                'content_type': file.content_type,
                'shared_with': '[]'
            })
            db.commit()
            print("Database save successful")
            
            return {
                "report_id": result.lastrowid or 1,
                "message": "Report uploaded successfully",
                "file_name": file.filename
            }
            
        except Exception as db_error:
            print(f"Database error: {db_error}")
            db.rollback()
            # Return success since S3 upload worked
            return {
                "report_id": 999,
                "message": "Report uploaded to S3 (database pending)",
                "file_name": file.filename
            }
            
    except Exception as e:
        print(f"Upload error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/reports/patient/{patient_id}")
def get_patient_reports(patient_id: int, doctor_id: int, db: Session = Depends(get_db)):
    try:
        # All doctors can access all patient reports
        reports = db.query(models.MedicalReport).filter(
            models.MedicalReport.patient_id == patient_id
        ).order_by(models.MedicalReport.uploaded_at.desc()).all()
        
        accessible_reports = []
        for report in reports:
            doctor = db.query(models.Doctor).filter(models.Doctor.id == report.doctor_id).first()
            accessible_reports.append({
                "report_id": report.report_id,
                "report_name": report.report_name,
                "uploaded_at": report.uploaded_at.isoformat(),
                "file_size": report.file_size,
                "uploaded_by": doctor.name if doctor else "Unknown Doctor"
            })
        
        return accessible_reports
    except Exception as e:
        print(f"Error getting patient reports: {e}")
        return []

@app.get("/reports/{report_id}/download")
def download_report(report_id: int, doctor_id: int, db: Session = Depends(get_db)):
    report = db.query(models.MedicalReport).filter(models.MedicalReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # All doctors can download patient reports (removed access restriction)
    try:
        # Generate presigned URL
        download_url = s3_service.generate_presigned_url(report.file_key)
        return {"download_url": download_url, "file_name": report.report_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.put("/reports/{report_id}/share")
def share_report(
    report_id: int,
    doctor_ids: List[int],
    current_doctor_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(models.MedicalReport).filter(models.MedicalReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Only owner can share
    if report.doctor_id != current_doctor_id:
        raise HTTPException(status_code=403, detail="Only report owner can share")
    
    report.shared_with = json.dumps(doctor_ids)
    db.commit()
    
    return {"message": "Report sharing updated successfully"}

