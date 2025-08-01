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

def get_sto_file_from_s3(identifier):
    """
    Get .sto file from S3 bucket ebi-rnacentral/dev/alignments/
    
    Args:
        identifier (str): The identifier for the Stockholm file
        
    Returns:
        str: Content of the Stockholm file
        
    Raises:
        Exception: If file retrieval fails
    """
    bucket_name = 'ebi-rnacentral'
    object_key = f'{os.getenv("ENVIRONMENT")}/alignments/{identifier.lower()}.sto'
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to retrieve {object_key} from S3: {str(e)}")
