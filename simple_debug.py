#!/usr/bin/env python3
"""
Simple debug test
"""
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test environment variables
print("=== ENVIRONMENT VARIABLES ===")
aws_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
bucket_name = os.getenv('S3_BUCKET_NAME')

print(f"AWS_ACCESS_KEY_ID: {aws_key[:10] if aws_key else 'NOT SET'}...")
print(f"AWS_SECRET_ACCESS_KEY: {aws_secret[:10] if aws_secret else 'NOT SET'}...")
print(f"AWS_REGION: {aws_region}")
print(f"S3_BUCKET_NAME: {bucket_name}")

if not aws_key or not aws_secret:
    print("ERROR: AWS credentials not set!")
    exit(1)

# Test S3 connection
print("\n=== S3 CONNECTION TEST ===")
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name=aws_region or 'eu-north-1'
    )
    
    buckets = s3_client.list_buckets()
    print(f"SUCCESS: Found {len(buckets['Buckets'])} buckets")
    
    # Test upload
    print("\n=== UPLOAD TEST ===")
    test_content = b"Debug test file content"
    file_key = "debug/test_file.txt"
    
    s3_client.put_object(
        Bucket=bucket_name or 'curanet-medical-reports',
        Key=file_key,
        Body=test_content,
        ContentType='text/plain',
        ServerSideEncryption='AES256'
    )
    print(f"SUCCESS: Uploaded {file_key}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()