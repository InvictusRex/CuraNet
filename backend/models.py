from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Decimal, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# Enums for constrained fields
class GenderEnum(enum.Enum):
    M = "M"
    F = "F"
    O = "O"

class VisitTypeEnum(enum.Enum):
    Outpatient = "Outpatient"
    Inpatient = "Inpatient"
    Emergency = "Emergency"
    Follow_up = "Follow-up"

class PriorityLevelEnum(enum.Enum):
    Low = "Low"
    Normal = "Normal"
    High = "High"
    Critical = "Critical"

class AccessLevelEnum(enum.Enum):
    Read = "Read"
    Write = "Write"
    Full = "Full"

# Models
class Hospital(Base):
    __tablename__ = "hospitals"
    
    hospital_id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_name = Column(String(255), nullable=False)
    hospital_code = Column(String(20), unique=True, nullable=False)
    address = Column(String(500))
    phone = Column(String(20))
    email = Column(String(255))
    license_number = Column(String(100))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    departments = relationship("Department", back_populates="hospital")
    doctors = relationship("Doctor", back_populates="hospital")
    patient_visits = relationship("PatientVisit", back_populates="hospital")

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False)
    department_name = Column(String(255), nullable=False)
    department_code = Column(String(20), nullable=False)
    head_doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"))
    created_at = Column(DateTime, default=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    hospital = relationship("Hospital", back_populates="departments")
    doctors = relationship("Doctor", back_populates="department")

class Doctor(Base):
    __tablename__ = "doctors"
    
    doctor_id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    doctor_code = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    specialization = Column(String(255))
    license_number = Column(String(100), unique=True, nullable=False)
    years_of_experience = Column(Integer, default=0)
    qualification = Column(String(500))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    hospital = relationship("Hospital", back_populates="doctors")
    department = relationship("Department", back_populates="doctors")
    patient_visits = relationship("PatientVisit", back_populates="primary_doctor")

class Patient(Base):
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

class VitalSigns(Base):
    __tablename__ = "vital_signs"
    
    vital_id = Column(Integer, primary_key=True, autoincrement=True)
    visit_id = Column(Integer, ForeignKey("patient_visits.visit_id"), nullable=False)
    recorded_by_doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    recorded_at = Column(DateTime, default=func.current_timestamp())
    temperature = Column(Decimal(4, 1))
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    respiratory_rate = Column(Integer)
    oxygen_saturation = Column(Decimal(5, 2))
    weight_kg = Column(Decimal(5, 2))
    height_cm = Column(Decimal(5, 2))
    bmi = Column(Decimal(4, 1))
    notes = Column(String(500))