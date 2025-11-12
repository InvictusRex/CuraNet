# Medical File Sharing Setup Guide

## Overview
This implementation adds secure file sharing functionality to CuraNet HMS using AWS S3. Doctors can upload medical reports and share them with other doctors while maintaining patient privacy.

## Features
- ✅ Secure file upload to AWS S3
- ✅ File sharing between doctors
- ✅ Access control and permissions
- ✅ Download with presigned URLs
- ✅ File metadata tracking
- ✅ Modern UI with drag-and-drop

## Setup Instructions

### 1. AWS S3 Configuration
1. Create an AWS S3 bucket for medical reports
2. Set up IAM user with S3 permissions
3. Configure bucket policy for security

### 2. Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=curanet-medical-reports
```

### 3. Database Migration
Run the migration to create the medical_reports table:
```bash
alembic upgrade head
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## API Endpoints

### Upload Report
```
POST /reports/upload
Content-Type: multipart/form-data

Parameters:
- file: File to upload
- patient_id: Patient ID
- doctor_id: Doctor ID
- session_id: Medical session ID (optional)
- shared_with: JSON array of doctor IDs
```

### Get Patient Reports
```
GET /reports/patient/{patient_id}?doctor_id={doctor_id}
```

### Download Report
```
GET /reports/{report_id}/download?doctor_id={doctor_id}
```

### Share Report
```
PUT /reports/{report_id}/share
Content-Type: application/json

{
  "doctor_ids": [1, 2, 3],
  "current_doctor_id": 1
}
```

## Usage

### For Patients
1. Navigate to "Medical Reports" from the dashboard
2. View reports shared by doctors
3. Download reports as needed

### For Doctors
1. Upload reports during patient sessions
2. Share reports with other doctors
3. Access shared reports from colleagues
4. Download reports with secure URLs

## Security Features
- Server-side encryption (AES256)
- Presigned URLs with expiration
- Access control based on doctor permissions
- Secure file storage in S3

## File Support
- PDF documents
- Medical images (JPG, PNG)
- Word documents (DOC, DOCX)
- Maximum file size: Configurable

## Integration Points
- Patient Dashboard: Added "Medical Reports" menu item
- Doctor Dashboard: File upload/sharing functionality
- Medical Sessions: Attach reports to sessions
- Admin Panel: Report management (future enhancement)

## Next Steps
1. Set up AWS S3 bucket and IAM permissions
2. Configure environment variables
3. Run database migration
4. Test file upload/download functionality
5. Customize UI as needed

## Troubleshooting
- Check AWS credentials and permissions
- Verify S3 bucket exists and is accessible
- Ensure database migration completed successfully
- Check browser console for JavaScript errors