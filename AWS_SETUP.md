# AWS S3 Setup for File Sharing

## 1. Create S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://curanet-medical-reports --region us-east-1
```

## 2. Create IAM User
1. Go to AWS Console → IAM → Users
2. Create user: `curanet-s3-user`
3. Attach policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetObjectVersion"
            ],
            "Resource": "arn:aws:s3:::curanet-medical-reports/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::curanet-medical-reports"
        }
    ]
}
```

## 3. Configure Environment Variables
Copy `.env.example` to `.env` and update:

```bash
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=curanet-medical-reports
```

## 4. Test Connection
Run the test script:
```bash
python test_s3.py
```