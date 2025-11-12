from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum

class BaseUser(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    def verify_password(self, password: str) -> bool:
        return self.password == password

class Patient(BaseUser):
    __tablename__ = "patients"
    
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_code = Column(String(20), unique=True, nullable=False)
    national_id = Column(String(50), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(String(500))
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    blood_group = Column(String(5))
    allergies = Column(Text)
    chronic_conditions = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    patient_visits = relationship("PatientVisit", back_populates="patient")

class StatusCategory(Base):
    __tablename__ = "status_categories"
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    category_order = Column(Integer, nullable=False)
    color_code = Column(String(7))
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    patient_visits = relationship("PatientVisit", back_populates="current_status")

class PatientVisit(Base):
    __tablename__ = "patient_visits"
    
    visit_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    primary_doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    visit_number = Column(String(50), unique=True, nullable=False)
    visit_type = Column(Enum(VisitTypeEnum), nullable=False)
    admission_date = Column(DateTime, nullable=False)
    discharge_date = Column(DateTime)
    current_status_id = Column(Integer, ForeignKey("status_categories.category_id"), nullable=False)
    chief_complaint = Column(Text)
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    notes = Column(Text)
    priority_level = Column(Enum(PriorityLevelEnum), default=PriorityLevelEnum.Normal)
    estimated_duration_hours = Column(Integer)
    total_cost = Column(Decimal(10, 2), default=0)
    insurance_info = Column(String(500))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="patient_visits")
    hospital = relationship("Hospital", back_populates="patient_visits")
    primary_doctor = relationship("Doctor", back_populates="patient_visits")
    current_status = relationship("StatusCategory", back_populates="patient_visits")

# Enum classes for medical session management
class SessionStatus(enum.Enum):
    active = "active"
    completed = "completed"
    paused = "paused"

class SeverityLevel(enum.Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"

class DiagnosisType(enum.Enum):
    primary = "primary"
    secondary = "secondary"
    differential = "differential"

class ConfidenceLevel(enum.Enum):
    confirmed = "confirmed"
    probable = "probable"
    possible = "possible"

class TreatmentStatus(enum.Enum):
    active = "active"
    completed = "completed"
    discontinued = "discontinued"

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="pending")

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    medical_sessions = relationship("MedicalSession", back_populates="appointment")

class MedicalSession(Base):
    __tablename__ = "medical_sessions"
    session_id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    session_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(SessionStatus), default=SessionStatus.active)
    chief_complaint = Column(Text)
    session_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="medical_sessions")
    patient = relationship("Patient")
    doctor = relationship("Doctor")
    prescriptions = relationship("Prescription", back_populates="session")
    symptoms = relationship("Symptom", back_populates="session")
    diagnoses = relationship("Diagnosis", back_populates="session")
    vital_signs = relationship("VitalSign", back_populates="session")
    treatment_plans = relationship("TreatmentPlan", back_populates="session")

class Prescription(Base):
    __tablename__ = "prescriptions"
    prescription_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("medical_sessions.session_id"), nullable=False)
    medication_name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration = Column(String(100), nullable=False)
    instructions = Column(Text)
    prescribed_date = Column(DateTime, default=datetime.utcnow)

    session = relationship("MedicalSession", back_populates="prescriptions")

class Symptom(Base):
    __tablename__ = "symptoms"
    symptom_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("medical_sessions.session_id"), nullable=False)
    symptom_description = Column(Text, nullable=False)
    severity = Column(Enum(SeverityLevel), nullable=False)
    duration = Column(String(100))
    notes = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("MedicalSession", back_populates="symptoms")

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    diagnosis_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("medical_sessions.session_id"), nullable=False)
    diagnosis_code = Column(String(20))
    diagnosis_description = Column(Text, nullable=False)
    diagnosis_type = Column(Enum(DiagnosisType), default=DiagnosisType.primary)
    confidence_level = Column(Enum(ConfidenceLevel), default=ConfidenceLevel.probable)
    notes = Column(Text)
    diagnosed_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("MedicalSession", back_populates="diagnoses")

class VitalSign(Base):
    __tablename__ = "vital_signs"
    vital_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("medical_sessions.session_id"), nullable=False)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    temperature = Column(DECIMAL(4, 2))
    respiratory_rate = Column(Integer)
    oxygen_saturation = Column(Integer)
    weight = Column(DECIMAL(5, 2))
    height = Column(DECIMAL(5, 2))
    recorded_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("MedicalSession", back_populates="vital_signs")

class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"
    plan_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("medical_sessions.session_id"), nullable=False)
    treatment_description = Column(Text, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum(TreatmentStatus), default=TreatmentStatus.active)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("MedicalSession", back_populates="treatment_plans")

class MedicalReport(Base):
    __tablename__ = "medical_reports"
    report_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("medical_sessions.session_id"), nullable=True)
    report_name = Column(String(255), nullable=False)
    file_key = Column(String(500), nullable=False)  # S3 object key
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    shared_with = Column(Text)  # JSON array of doctor IDs who can access
    
    patient = relationship("Patient")
    doctor = relationship("Doctor")
    session = relationship("MedicalSession")