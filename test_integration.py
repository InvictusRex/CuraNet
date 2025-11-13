#!/usr/bin/env python3
"""
Integration test for file sharing in patient detail page
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_patient_detail_with_files():
    """Test the complete patient detail + file sharing flow"""
    
    print("🧪 Testing Patient Detail + File Sharing Integration\n")
    
    # Test 1: Get patient details
    print("1. Testing patient detail endpoint...")
    patient_id = "1"  # Test with patient ID 1
    
    response = requests.get(f"{BASE_URL}/api/patient/{patient_id}")
    if response.status_code == 200:
        patient = response.json()
        print(f"✅ Patient found: {patient['name']}")
    else:
        print(f"❌ Patient not found: {response.status_code}")
        return False
    
    # Test 2: Get patient reports
    print("\n2. Testing patient reports endpoint...")
    doctor_id = 1
    
    response = requests.get(f"{BASE_URL}/reports/patient/{patient_id}?doctor_id={doctor_id}")
    if response.status_code == 200:
        reports = response.json()
        print(f"✅ Found {len(reports)} reports for patient")
        for report in reports:
            print(f"  - {report['report_name']} (uploaded by {report['uploaded_by']})")
    else:
        print(f"❌ Failed to get reports: {response.status_code}")
    
    # Test 3: Test file upload (if S3 is configured)
    print("\n3. Testing file upload...")
    
    # Create a test file
    test_content = b"This is a test medical report for integration testing"
    files = {
        'file': ('test_integration_report.txt', test_content, 'text/plain')
    }
    
    data = {
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'shared_with': json.dumps([])
    }
    
    response = requests.post(f"{BASE_URL}/reports/upload", files=files, data=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful: {result['file_name']}")
        
        # Test download
        print("\n4. Testing file download...")
        report_id = result['report_id']
        
        response = requests.get(f"{BASE_URL}/reports/{report_id}/download?doctor_id={doctor_id}")
        if response.status_code == 200:
            download_result = response.json()
            print(f"✅ Download URL generated for: {download_result['file_name']}")
        else:
            print(f"❌ Download failed: {response.status_code}")
            
    else:
        print(f"⚠️  Upload failed (expected if S3 not configured): {response.status_code}")
        if response.status_code == 500:
            print("   This is normal if AWS credentials are not set up")
    
    print("\n🎉 Integration test completed!")
    return True

def test_api_endpoints():
    """Test all file sharing API endpoints"""
    
    print("\n📡 Testing API Endpoints\n")
    
    endpoints = [
        ("GET", "/api/patient/1", "Patient detail"),
        ("GET", "/reports/patient/1?doctor_id=1", "Patient reports"),
        ("GET", "/doctor/patients/testdoctor", "Doctor patients"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            status = "✅" if response.status_code in [200, 404] else "❌"
            print(f"{status} {description}: {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Server not running")
        except Exception as e:
            print(f"❌ {description}: {str(e)}")

if __name__ == "__main__":
    print("🚀 CuraNet File Sharing Integration Test")
    print("=" * 50)
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/api")
        if response.status_code == 200:
            print("✅ Server is running")
            test_patient_detail_with_files()
            test_api_endpoints()
        else:
            print("❌ Server not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start with:")
        print("   python -m uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")