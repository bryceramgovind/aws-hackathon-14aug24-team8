"""
Test script to verify AWS setup
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def test_aws_connection():
    """Test AWS CLI configuration"""
    try:
        # Test S3
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        print("✅ S3 Connection: Success")
        print(f"   Found {len(response['Buckets'])} buckets")
        
        # Test Bedrock
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock.list_foundation_models()
        print("✅ Bedrock Connection: Success")
        print(f"   Found {len(models['modelSummaries'])} models")
        
        # Test IAM permissions
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS Identity:")
        print(f"   Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_aws_connection()