from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, PatientVisit, Patient, StatusCategory, Hospital, Doctor
from typing import List
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CuraNet Hospital Management API", version="1.0.0")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Kanban Board Endpoints
@app.get("/api/kanban-board")
def get_kanban_board(db: Session = Depends(get_db)):
    """Get current patient status for Kanban board"""
    query = db.query(
        StatusCategory.category_name,
        StatusCategory.color_code,
        StatusCategory.category_order
    ).join(PatientVisit).filter(
        PatientVisit.is_active == True,
        PatientVisit.discharge_date.is_(None)
    ).group_by(StatusCategory.category_id).order_by(StatusCategory.category_order)
    
    return query.all()

@app.get("/api/patients/active")
def get_active_patients(db: Session = Depends(get_db)):
    """Get all active patients with current status"""
    patients = db.query(
        PatientVisit.visit_id,
        PatientVisit.visit_number,
        Patient.patient_code,
        Patient.first_name,
        Patient.last_name,
        Patient.phone,
        StatusCategory.category_name.label("current_status"),
        StatusCategory.color_code,
        PatientVisit.priority_level,
        PatientVisit.admission_date,
        PatientVisit.chief_complaint,
        Hospital.hospital_name,
        Doctor.first_name.label("doctor_first_name"),
        Doctor.last_name.label("doctor_last_name")
    ).join(Patient).join(StatusCategory).join(Hospital).join(Doctor).filter(
        PatientVisit.is_active == True,
        PatientVisit.discharge_date.is_(None)
    ).all()
    
    return patients

@app.put("/api/visits/{visit_id}/status")
def update_patient_status(visit_id: int, new_status_id: int, doctor_id: int, reason: str = None, db: Session = Depends(get_db)):
    """Update patient status for Kanban board"""
    visit = db.query(PatientVisit).filter(PatientVisit.visit_id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    # Update status
    old_status_id = visit.current_status_id
    visit.current_status_id = new_status_id
    db.commit()
    
    return {"message": "Status updated successfully", "old_status": old_status_id, "new_status": new_status_id}

@app.get("/api/patients/search")
def search_patients(query: str, db: Session = Depends(get_db)):
    """Search patients across all hospitals"""
    patients = db.query(Patient).filter(
        (Patient.first_name.contains(query)) |
        (Patient.last_name.contains(query)) |
        (Patient.patient_code.contains(query)) |
        (Patient.phone.contains(query))
    ).limit(50).all()
    
    return patients

@app.get("/api/doctors/{doctor_id}/patients")
def get_doctor_patients(doctor_id: int, db: Session = Depends(get_db)):
    """Get current patients for a specific doctor"""
    patients = db.query(
        PatientVisit.visit_id,
        PatientVisit.visit_number,
        Patient.first_name,
        Patient.last_name,
        Patient.phone,
        StatusCategory.category_name.label("current_status"),
        StatusCategory.color_code,
        PatientVisit.priority_level,
        PatientVisit.chief_complaint,
        PatientVisit.admission_date
    ).join(Patient).join(StatusCategory).filter(
        PatientVisit.primary_doctor_id == doctor_id,
        PatientVisit.is_active == True,
        PatientVisit.discharge_date.is_(None)
    ).order_by(
        PatientVisit.priority_level.desc(),
        PatientVisit.admission_date
    ).all()
    
    return patients

@app.get("/api/hospitals")
def get_hospitals(db: Session = Depends(get_db)):
    """Get all hospitals"""
    return db.query(Hospital).filter(Hospital.is_active == True).all()

@app.get("/api/status-categories")
def get_status_categories(db: Session = Depends(get_db)):
    """Get all status categories for Kanban board"""
    return db.query(StatusCategory).filter(StatusCategory.is_active == True).order_by(StatusCategory.category_order).all()

@app.get("/")
def root():
    return {"message": "CuraNet Hospital Management API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)