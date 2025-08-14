"""
S3 Handler for Call Center Data Management
"""

import boto3
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional, Any, Union
import logging
from botocore.exceptions import ClientError
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import mimetypes
import tempfile
from pathlib import Path
import threading
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

class S3CallCenterHandler:
    """
    Comprehensive S3 handler for call center data operations
    """
    
    def __init__(self, 
                 bucket_name: str,
                 region_name: str = 'us-east-1',
                 max_workers: int = 10):
        """
        Initialize S3 handler
        
        Args:
            bucket_name: Name of the S3 bucket
            region_name: AWS region
            max_workers: Maximum number of threads for concurrent operations
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.max_workers = max_workers
        
        # Initialize S3 clients
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.s3_resource = boto3.resource('s3', region_name=region_name)
        self.bucket = self.s3_resource.Bucket(bucket_name)
        
        # Thread lock for concurrent operations
        self.lock = threading.Lock()
        
        # Verify bucket exists
        self._verify_bucket()
        
        logger.info(f"Initialized S3 handler for bucket: {bucket_name}")
    
    def _verify_bucket(self):
        """Verify that the bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Bucket {self.bucket_name} does not exist")
                raise ValueError(f"Bucket {self.bucket_name} does not exist")
            else:
                logger.error(f"Error accessing bucket: {e}")
                raise

    def upload_transcript(self,
                         call_id: str,
                         transcript: Union[str, Dict],
                         format: str = 'json') -> Dict[str, Any]:
        """
        Upload call transcript to S3
        
        Args:
            call_id: Call identifier
            transcript: Transcript data (string or dict)
            format: Output format ('json', 'txt', or 'vtt')
            
        Returns:
            Upload details
        """
        try:
            timestamp = datetime.now().strftime('%Y/%m/%d')
            
            if format == 'json':
                if isinstance(transcript, str):
                    content = json.dumps({'transcript': transcript}, indent=2)
                else:
                    content = json.dumps(transcript, indent=2)
                s3_key = f"transcripts/{timestamp}/{call_id}_transcript.json"
                content_type = 'application/json'
                
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType=content_type,
                Metadata={
                    'call-id': call_id,
                    'upload-timestamp': datetime.now().isoformat(),
                    'format': format
                },
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Uploaded transcript for {call_id} to {s3_key}")
            
            return {
                'success': True,
                'call_id': call_id,
                's3_key': s3_key,
                'format': format,
                'size_bytes': len(content.encode('utf-8')),
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading transcript: {e}")
            return {
                'success': False,
                'error': str(e),
                'call_id': call_id
            }
    
    def upload_analytics_results(self,
                                call_id: str,
                                analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload analytics results to S3
        
        Args:
            call_id: Call identifier
            analytics_data: Analytics results dictionary
            
        Returns:
            Upload details
        """
        try:
            timestamp = datetime.now().strftime('%Y/%m/%d')
            s3_key = f"analytics/{timestamp}/{call_id}_enrich.json"
            
            # Add metadata to analytics
            analytics_data['_metadata'] = {
                'call_id': call_id,
                'processed_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(analytics_data, indent=2),
                ContentType='application/json',
                Metadata={
                    'call-id': call_id,
                    'analytics-timestamp': datetime.now().isoformat()
                },
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Uploaded analytics for {call_id} to {s3_key}")
            
            return {
                'success': True,
                'call_id': call_id,
                's3_key': s3_key,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading analytics: {e}")
            return {
                'success': False,
                'error': str(e),
                'call_id': call_id
            }
    
    def get_call_data(self, call_id: str) -> Dict[str, Any]:
        """
        Retrieve all data for a specific call
        
        Args:
            call_id: Call identifier
            
        Returns:
            Dictionary with all call data
        """
        try:
            call_data = {
                'call_id': call_id,
                'recording': None,
                'transcript': None,
                'analytics': None
            }
            
            # Search for files related to this call
            prefixes = [
                'call-recordings/',
                'transcripts/',
                'analytics/'
            ]
            
            for prefix in prefixes:
                paginator = self.s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                
                for page in pages:
                    if 'Contents' not in page:
                        continue
                    
                    for obj in page['Contents']:
                        if call_id in obj['Key']:
                            if 'call-recordings' in obj['Key']:
                                call_data['recording'] = {
                                    'key': obj['Key'],
                                    'size': obj['Size'],
                                    'last_modified': obj['LastModified']
                                }
                            elif 'transcripts' in obj['Key']:
                                # Download transcript
                                response = self.s3_client.get_object(
                                    Bucket=self.bucket_name,
                                    Key=obj['Key']
                                )
                                content = response['Body'].read().decode('utf-8')
                                
                                if obj['Key'].endswith('.json'):
                                    call_data['transcript'] = json.loads(content)
                                else:
                                    call_data['transcript'] = content
                                    
                            elif 'analytics' in obj['Key']:
                                # Download analytics
                                response = self.s3_client.get_object(
                                    Bucket=self.bucket_name,
                                    Key=obj['Key']
                                )
                                call_data['analytics'] = json.loads(
                                    response['Body'].read().decode('utf-8')
                                )
            
            return call_data
            
        except Exception as e:
            logger.error(f"Error retrieving call data: {e}")
            raise
    
    def generate_presigned_url(self,
                             s3_key: str,
                             expiration: int = 3600) -> str:
        """
        Generate a presigned URL for temporary access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for {s3_key}")
            return url
            
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def create_batch_upload_manifest(self,
                                   file_list: List[Dict[str, str]]) -> str:
        """
        Create a manifest for batch uploads
        
        Args:
            file_list: List of dicts with 'local_path' and 'call_id'
            
        Returns:
            Path to manifest file
        """
        try:
            manifest = []
            
            for file_info in file_list:
                manifest.append({
                    'local_path': file_info['local_path'],
                    'call_id': file_info['call_id'],
                    's3_key': f"call-recordings/{datetime.now().strftime('%Y/%m/%d')}/{file_info['call_id']}{Path(file_info['local_path']).suffix}"
                })
            
            # Save manifest
            manifest_path = os.path.join(tempfile.gettempdir(), 'upload_manifest.json')
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Created batch upload manifest with {len(manifest)} files")
            return manifest_path
            
        except Exception as e:
            logger.error(f"Error creating manifest: {e}")
            raise
    
 
    def delete_call_data(self, call_id: str) -> Dict[str, Any]:
        """
        Delete all data for a specific call
        
        Args:
            call_id: Call identifier
            
        Returns:
            Deletion summary
        """
        try:
            deleted_objects = []
            
            # Find all objects with this call_id
            prefixes = ['call-recordings/', 'transcripts/', 'analytics/']
            
            for prefix in prefixes:
                paginator = self.s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                
                for page in pages:
                    if 'Contents' not in page:
                        continue
                    
                    for obj in page['Contents']:
                        if call_id in obj['Key']:
                            # Delete object
                            self.s3_client.delete_object(
                                Bucket=self.bucket_name,
                                Key=obj['Key']
                            )
                            deleted_objects.append(obj['Key'])
                            logger.info(f"Deleted {obj['Key']}")
            
            return {
                'success': True,
                'call_id': call_id,
                'deleted_count': len(deleted_objects),
                'deleted_objects': deleted_objects
            }
            
        except Exception as e:
            logger.error(f"Error deleting call data: {e}")
            return {
                'success': False,
                'error': str(e),
                'call_id': call_id
            }