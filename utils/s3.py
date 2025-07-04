
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('S3_HOST'),
    aws_access_key_id=os.getenv('S3_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET')
)

def list_buckets():
    response = s3_client.list_buckets()
    for bucket in response['Buckets']:
        print(bucket['Name'])

def list_objects(bucket_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        print(obj['Key'])