import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test S3 connection
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    # Test bucket access
    response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
    print(f"✅ Successfully connected to S3 bucket: {bucket_name}")
    
except Exception as e:
    print(f"❌ S3 connection failed: {str(e)}")
    print("Check your AWS credentials and bucket name in .env file")