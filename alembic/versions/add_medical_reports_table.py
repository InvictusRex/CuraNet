"""Add medical reports table

Revision ID: add_medical_reports
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_medical_reports'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create medical_reports table
    op.create_table('medical_reports',
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('file_key', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('shared_with', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['medical_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('report_id')
    )
    op.create_index(op.f('ix_medical_reports_report_id'), 'medical_reports', ['report_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_medical_reports_report_id'), table_name='medical_reports')
    op.drop_table('medical_reports')