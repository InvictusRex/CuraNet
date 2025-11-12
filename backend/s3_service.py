import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import uuid

class S3Service:
    def __init__(self):
        # Get AWS credentials from environment or use defaults
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID', 'your_access_key_here')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'your_secret_key_here')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'curanet-medical-reports')
    
    def upload_file(self, file_content, file_name, content_type, patient_id, doctor_id):
        """Upload file to S3 and return the file key"""
        try:
            # Generate unique file key
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            file_key = f"reports/patient_{patient_id}/doctor_{doctor_id}/{timestamp}_{unique_id}_{file_name}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                ServerSideEncryption='AES256'
            )
            
            return file_key
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def generate_presigned_url(self, file_key, expiration=3600):
        """Generate a presigned URL for file download"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def delete_file(self, file_key):
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")