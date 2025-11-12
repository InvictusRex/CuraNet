"""add_medical_session_tables

Revision ID: b6c664048e91
Revises: 
Create Date: 2025-01-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b6c664048e91'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create medical_sessions table
    op.create_table('medical_sessions',
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('session_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('active', 'completed', 'paused', name='sessionstatus'), nullable=True),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('session_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index(op.f('ix_medical_sessions_session_id'), 'medical_sessions', ['session_id'], unique=False)

    # Create prescriptions table
    op.create_table('prescriptions',
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('medication_name', sa.String(length=200), nullable=False),
        sa.Column('dosage', sa.String(length=100), nullable=False),
        sa.Column('frequency', sa.String(length=100), nullable=False),
        sa.Column('duration', sa.String(length=100), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('prescribed_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['medical_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('prescription_id')
    )
    op.create_index(op.f('ix_prescriptions_prescription_id'), 'prescriptions', ['prescription_id'], unique=False)

    # Create symptoms table
    op.create_table('symptoms',
        sa.Column('symptom_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('symptom_description', sa.Text(), nullable=False),
        sa.Column('severity', sa.Enum('mild', 'moderate', 'severe', name='severitylevel'), nullable=False),
        sa.Column('duration', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['medical_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('symptom_id')
    )
    op.create_index(op.f('ix_symptoms_symptom_id'), 'symptoms', ['symptom_id'], unique=False)

    # Create diagnoses table
    op.create_table('diagnoses',
        sa.Column('diagnosis_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('diagnosis_code', sa.String(length=20), nullable=True),
        sa.Column('diagnosis_description', sa.Text(), nullable=False),
        sa.Column('diagnosis_type', sa.Enum('primary', 'secondary', 'differential', name='diagnosistype'), nullable=True),
        sa.Column('confidence_level', sa.Enum('confirmed', 'probable', 'possible', name='confidencelevel'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('diagnosed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['medical_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('diagnosis_id')
    )
    op.create_index(op.f('ix_diagnoses_diagnosis_id'), 'diagnoses', ['diagnosis_id'], unique=False)

    # Create vital_signs table
    op.create_table('vital_signs',
        sa.Column('vital_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('blood_pressure_systolic', sa.Integer(), nullable=True),
        sa.Column('blood_pressure_diastolic', sa.Integer(), nullable=True),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('temperature', sa.DECIMAL(precision=4, scale=2), nullable=True),
        sa.Column('respiratory_rate', sa.Integer(), nullable=True),
        sa.Column('oxygen_saturation', sa.Integer(), nullable=True),
        sa.Column('weight', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('height', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['medical_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('vital_id')
    )
    op.create_index(op.f('ix_vital_signs_vital_id'), 'vital_signs', ['vital_id'], unique=False)

    # Create treatment_plans table
    op.create_table('treatment_plans',
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('treatment_description', sa.Text(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('active', 'completed', 'discontinued', name='treatmentstatus'), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=True),
        sa.Column('follow_up_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['medical_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('plan_id')
    )
    op.create_index(op.f('ix_treatment_plans_plan_id'), 'treatment_plans', ['plan_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_treatment_plans_plan_id'), table_name='treatment_plans')
    op.drop_table('treatment_plans')
    op.drop_index(op.f('ix_vital_signs_vital_id'), table_name='vital_signs')
    op.drop_table('vital_signs')
    op.drop_index(op.f('ix_diagnoses_diagnosis_id'), table_name='diagnoses')
    op.drop_table('diagnoses')
    op.drop_index(op.f('ix_symptoms_symptom_id'), table_name='symptoms')
    op.drop_table('symptoms')
    op.drop_index(op.f('ix_prescriptions_prescription_id'), table_name='prescriptions')
    op.drop_table('prescriptions')
    op.drop_index(op.f('ix_medical_sessions_session_id'), table_name='medical_sessions')
    op.drop_table('medical_sessions')