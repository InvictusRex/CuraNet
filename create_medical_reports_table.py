#!/usr/bin/env python3
"""
Create medical_reports table in the database
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from backend.database import engine, Base
from backend.models import MedicalReport

def create_medical_reports_table():
    """Create the medical_reports table"""
    try:
        print("Creating medical_reports table...")
        
        # Create only the MedicalReport table
        MedicalReport.__table__.create(engine, checkfirst=True)
        
        print("✅ medical_reports table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    success = create_medical_reports_table()
    if success:
        print("\n🎉 Database is ready for file sharing!")
    else:
        print("\n⚠️  Table creation failed. File sharing will use mock mode.")