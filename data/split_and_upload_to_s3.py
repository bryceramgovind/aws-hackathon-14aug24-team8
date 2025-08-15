#!/usr/bin/env python3
"""
Script to split customer service chats by contact_id and upload each conversation to S3.
Each contact_id becomes a separate JSON file uploaded to a specified S3 folder.
"""

import json
import boto3
import os
from collections import defaultdict
from botocore.exceptions import ClientError, NoCredentialsError
import tempfile
from datetime import datetime
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_customer_service_chats(file_path):
    """Load the customer service chats from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} messages from {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise

def group_by_contact_id(chat_data):
    """Group chat messages by contact_id."""
    grouped_chats = defaultdict(list)
    
    for message in chat_data:
        contact_id = message.get('contact_id')
        if contact_id:
            grouped_chats[contact_id].append(message)
    
    # Sort messages within each contact by message_number
    for contact_id in grouped_chats:
        grouped_chats[contact_id].sort(key=lambda x: x.get('message_number', 0))
    
    logger.info(f"Grouped messages into {len(grouped_chats)} conversations")
    return dict(grouped_chats)

def create_s3_client():
    """Create and return an S3 client."""
    try:
        # Try to create S3 client - will use default credentials
        s3_client = boto3.client('s3')
        # Test the credentials by listing buckets
        s3_client.list_buckets()
        logger.info("Successfully connected to AWS S3")
        return s3_client
    except NoCredentialsError:
        logger.error("No AWS credentials found. Please configure your credentials using 'aws configure' or environment variables.")
        raise
    except ClientError as e:
        logger.error(f"Error connecting to AWS S3: {e}")
        raise

def upload_conversation_to_s3(s3_client, bucket_name, s3_folder, contact_id, conversation_data):
    """Upload a single conversation to S3."""
    try:
        # Create filename with contact_id
        filename = f"{contact_id}.json"
        s3_key = f"{s3_folder.rstrip('/')}/{filename}" if s3_folder else filename
        
        # Create conversation metadata
        # conversation_metadata = {
        #     "contact_id": contact_id,
        #     "total_messages": len(conversation_data),
        #     "start_date": conversation_data[0].get('start_date') if conversation_data else None,
        #     "end_date": conversation_data[0].get('end_date') if conversation_data else None,
        #     "phone_number": conversation_data[0].get('phone_number') if conversation_data else None,
        #     "messages": conversation_data
        # }
        
        # Convert to JSON
        json_content = json.dumps(conversation_data, indent=2, ensure_ascii=False)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json_content.encode('utf-8'),
            ContentType='application/json',
            Metadata={
                'contact-id': contact_id,
                'message-count': str(len(conversation_data)),
                'upload-timestamp': datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Uploaded conversation {contact_id} to s3://{bucket_name}/{s3_key}")
        return True
        
    except ClientError as e:
        logger.error(f"Error uploading conversation {contact_id} to S3: {e}")
        return False

def validate_bucket_exists(s3_client, bucket_name):
    """Check if the S3 bucket exists and is accessible."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' is accessible")
        return True
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            logger.error(f"Bucket '{bucket_name}' does not exist")
        elif error_code == 403:
            logger.error(f"Access denied to bucket '{bucket_name}'")
        else:
            logger.error(f"Error accessing bucket '{bucket_name}': {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Split customer service chats by contact_id and upload to S3')
    parser.add_argument('--input-file', '-i', 
                       default='customer_service_chats.json',
                       help='Input JSON file with customer service chats')
    parser.add_argument('--bucket', '-b', 
                       required=True,
                       help='S3 bucket name')
    parser.add_argument('--folder', '-f', 
                       default='customer-conversations',
                       help='S3 folder path (default: customer-conversations)')
    parser.add_argument('--dry-run', '-d', 
                       action='store_true',
                       help='Perform a dry run without uploading to S3')
    parser.add_argument('--max-conversations', '-m', 
                       type=int,
                       help='Maximum number of conversations to process (for testing)')
    
    args = parser.parse_args()
    
    logger.info("Starting customer service chat splitting and upload process")
    
    # Load the chat data
    try:
        chat_data = load_customer_service_chats(args.input_file)
    except Exception as e:
        logger.error(f"Failed to load chat data: {e}")
        return 1
    
    # Group by contact_id
    grouped_conversations = group_by_contact_id(chat_data)
    
    if args.max_conversations:
        # Limit for testing
        limited_conversations = dict(list(grouped_conversations.items())[:args.max_conversations])
        grouped_conversations = limited_conversations
        logger.info(f"Limited to {len(grouped_conversations)} conversations for testing")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be uploaded to S3")
        for contact_id, messages in grouped_conversations.items():
            logger.info(f"Would upload conversation {contact_id} with {len(messages)} messages")
        logger.info(f"Total conversations that would be uploaded: {len(grouped_conversations)}")
        return 0
    
    # Create S3 client
    try:
        s3_client = create_s3_client()
    except Exception as e:
        logger.error(f"Failed to create S3 client: {e}")
        return 1
    
    # Validate bucket exists
    if not validate_bucket_exists(s3_client, args.bucket):
        return 1
    
    # Upload each conversation
    successful_uploads = 0
    failed_uploads = 0
    
    logger.info(f"Starting upload of {len(grouped_conversations)} conversations to s3://{args.bucket}/{args.folder}")
    
    for contact_id, conversation_messages in grouped_conversations.items():
        success = upload_conversation_to_s3(
            s3_client, 
            args.bucket, 
            args.folder, 
            contact_id, 
            conversation_messages
        )
        
        if success:
            successful_uploads += 1
        else:
            failed_uploads += 1
    
    logger.info(f"Upload complete! Successful: {successful_uploads}, Failed: {failed_uploads}")
    
    if failed_uploads > 0:
        logger.warning(f"{failed_uploads} uploads failed. Check the logs above for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
