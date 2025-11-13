#!/usr/bin/env python3
"""
Test script for file sharing functionality
"""
import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PATIENT_ID = 1
TEST_DOCTOR_ID = 1

def test_file_upload():
    """Test file upload functionality"""
    # Create a test file
    test_file_content = b"This is a test medical report content"
    
    files = {
        'file': ('test_report.txt', test_file_content, 'text/plain')
    }
    
    data = {
        'patient_id': TEST_PATIENT_ID,
        'doctor_id': TEST_DOCTOR_ID,
        'shared_with': json.dumps([2, 3])  # Share with doctors 2 and 3
    }
    
    response = requests.post(f"{BASE_URL}/reports/upload", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful: {result}")
        return result['report_id']
    else:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return None

def test_get_reports(patient_id, doctor_id):
    """Test getting patient reports"""
    response = requests.get(f"{BASE_URL}/reports/patient/{patient_id}?doctor_id={doctor_id}")
    
    if response.status_code == 200:
        reports = response.json()
        print(f"✅ Found {len(reports)} reports")
        for report in reports:
            print(f"  - {report['report_name']} (ID: {report['report_id']})")
        return reports
    else:
        print(f"❌ Get reports failed: {response.status_code} - {response.text}")
        return []

def test_download_report(report_id, doctor_id):
    """Test downloading a report"""
    response = requests.get(f"{BASE_URL}/reports/{report_id}/download?doctor_id={doctor_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Download URL generated: {result['file_name']}")
        return result['download_url']
    else:
        print(f"❌ Download failed: {response.status_code} - {response.text}")
        return None

def main():
    print("🧪 Testing File Sharing Functionality\n")
    
    # Test 1: Upload a file
    print("1. Testing file upload...")
    report_id = test_file_upload()
    
    if not report_id:
        print("❌ Cannot continue tests without successful upload")
        return
    
    print()
    
    # Test 2: Get patient reports
    print("2. Testing get patient reports...")
    reports = test_get_reports(TEST_PATIENT_ID, TEST_DOCTOR_ID)
    print()
    
    # Test 3: Download report
    print("3. Testing report download...")
    download_url = test_download_report(report_id, TEST_DOCTOR_ID)
    print()
    
    if download_url:
        print("🎉 All tests passed! File sharing is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your configuration.")

if __name__ == "__main__":
    main()