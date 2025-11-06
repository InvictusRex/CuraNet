from sqlalchemy.orm import Session
from ..models import Patient, Appointment, Doctor
from ..schemas import PatientResponse
from typing import Optional, Dict, Any
from datetime import datetime

def get_patient_detail(db: Session, patient_id: int) -> Optional[Dict[Any, Any]]:
    """
    Get comprehensive patient details including appointments, medical history, etc.
    """
    try:
        # Get patient basic info
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        
        if not patient:
            return None
        
        # Get patient's appointments with doctor details
        appointments = db.query(Appointment, Doctor).join(
            Doctor, Appointment.doctor_id == Doctor.id
        ).filter(Appointment.patient_id == patient_id).all()
        
        # Format appointments for response
        visit_history = []
        for appointment, doctor in appointments:
            visit_history.append({
                "date": appointment.appointment_time.strftime("%Y-%m-%d") if appointment.appointment_time else "N/A",
                "doctor": doctor.name,
                "department": doctor.department,
                "diagnosis": "General consultation",  # This would come from a diagnosis table in a real system
                "status": appointment.status
            })
        
        # Create comprehensive patient data
        patient_detail = {
            "id": patient.id,
            "patient_id": f"P{patient.id:03d}",
            "name": patient.name,
            "age": patient.age,
            "blood_group": patient.blood_group,
            "phone": patient.phone,
            "email": patient.email,
            "medical_history": patient.medical_history,
            "gender": "Not specified",  # Add this field to Patient model in future
            "emergency_contact": "+1 (555) 123-4567",  # Add this field to Patient model in future
            "address": "123 Main St, City, State 12345",  # Add this field to Patient model in future
            "registration_date": "2023-01-15",  # Add this field to Patient model in future
            "visits": visit_history,
            "prescriptions": [
                # Mock prescription data - in a real system, this would come from a prescriptions table
                {
                    "date": "2024-01-15",
                    "medication": "Lisinopril 10mg",
                    "dosage": "Once daily",
                    "duration": "30 days",
                    "prescribed_by": "Dr. Smith"
                }
            ] if visit_history else [],
            "lab_reports": [
                # Mock lab report data - in a real system, this would come from a lab_reports table
                {
                    "date": "2024-01-15",
                    "test_name": "Complete Blood Count",
                    "result": "Normal",
                    "reference_range": "4.5-11.0 x10³/μL",
                    "status": "normal"
                }
            ] if visit_history else [],
            "documents": [
                # Mock document data - in a real system, this would come from a documents table
                {
                    "id": "doc1",
                    "name": "Blood Test Results",
                    "date": "2024-01-15"
                }
            ] if visit_history else []
        }
        
        return patient_detail
        
    except Exception as e:
        print(f"Error getting patient detail: {e}")
        return None

def get_patient_basic_info(db: Session, patient_id: int) -> Optional[PatientResponse]:
    """
    Get basic patient information
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        
        if not patient:
            return None
            
        return PatientResponse(
            id=patient.id,
            name=patient.name,
            phone=patient.phone,
            email=patient.email,
            age=patient.age,
            blood_group=patient.blood_group,
            medical_history=patient.medical_history
        )
        
    except Exception as e:
        print(f"Error getting patient basic info: {e}")
        return None