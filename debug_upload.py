#!/usr/bin/env python3
"""
Debug upload endpoint
"""
from fastapi import FastAPI, UploadFile, File, Form
import boto3
import os
from datetime import datetime
import uuid

app = FastAPI()

@app.post("/debug-upload")
async def debug_upload(
    file: UploadFile = File(...),
    patient_id: int = Form(...),
    doctor_id: int = Form(...)
):
    try:
        print(f"=== DEBUG UPLOAD START ===")
        print(f"File: {file.filename}")
        print(f"Content Type: {file.content_type}")
        print(f"Patient ID: {patient_id}")
        print(f"Doctor ID: {doctor_id}")
        
        # Read file
        file_content = await file.read()
        print(f"File size: {len(file_content)} bytes")
        
        # Check environment variables
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION')
        bucket_name = os.getenv('S3_BUCKET_NAME')
        
        print(f"AWS_ACCESS_KEY_ID: {aws_key[:10] if aws_key else 'NOT SET'}...")
        print(f"AWS_SECRET_ACCESS_KEY: {aws_secret[:10] if aws_secret else 'NOT SET'}...")
        print(f"AWS_REGION: {aws_region}")
        print(f"S3_BUCKET_NAME: {bucket_name}")
        
        if not aws_key or not aws_secret:
            return {"error": "AWS credentials not set in environment"}
        
        # Try S3 connection
        print("Creating S3 client...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region or 'eu-north-1'
        )
        
        # Test S3 connection
        print("Testing S3 connection...")
        buckets = s3_client.list_buckets()
        print(f"S3 connection successful. Found {len(buckets['Buckets'])} buckets")
        
        # Generate file key
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_key = f"debug/patient_{patient_id}/doctor_{doctor_id}/{timestamp}_{unique_id}_{file.filename}"
        print(f"File key: {file_key}")
        
        # Upload to S3
        print("Uploading to S3...")
        s3_client.put_object(
            Bucket=bucket_name or 'curanet-medical-reports',
            Key=file_key,
            Body=file_content,
            ContentType=file.content_type or 'application/octet-stream',
            ServerSideEncryption='AES256'
        )
        print("S3 upload successful!")
        
        print(f"=== DEBUG UPLOAD SUCCESS ===")
        return {
            "status": "success",
            "message": "Debug upload successful",
            "file_name": file.filename,
            "file_key": file_key,
            "file_size": len(file_content)
        }
        
    except Exception as e:
        print(f"=== DEBUG UPLOAD ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"=== END ERROR ===")
        
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)