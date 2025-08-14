"""
AWS Bedrock AI Agent for Call Center Analytics
"""

import os
import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging (continued)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AWSCallCenterAgent:
    """
    AI Agent for Call Center Analytics using AWS Services
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the AI Agent with AWS services"""
        
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Initialize AWS clients
        self.region = os.getenv('AWS_REGION', self.config['aws']['region'])
        
        # Initialize AWS services
        self._init_aws_clients()
        
        # Agent settings
        self.agent_name = self.config['agent']['name']
        self.capabilities = self.config['agent']['capabilities']
        
        logger.info(f"Initialized {self.agent_name} with capabilities: {self.capabilities}")
    
    def _init_aws_clients(self):
        """Initialize AWS service clients"""
        try:
            # S3 Client
            self.s3_client = boto3.client('s3', region_name=self.region)
            
            # Bedrock Client
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=self.region
            )
            
            # Transcribe Client
            self.transcribe_client = boto3.client(
                'transcribe',
                region_name=self.region
            )
            
            # Comprehend Client
            self.comprehend_client = boto3.client(
                'comprehend',
                region_name=self.region
            )
            
            # DynamoDB Client
            self.dynamodb_client = boto3.client(
                'dynamodb',
                region_name=self.region
            )
            
            logger.info("Successfully initialized all AWS clients")
            
        except Exception as e:
            logger.error(f"Error initializing AWS clients: {e}")
            raise
    
    async def analyze_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a call using multiple AI capabilities
        
        Args:
            call_data: Dictionary containing call information
            
        Returns:
            Analysis results
        """
        try:
            results = {
                'call_id': call_data.get('call_id'),
                'timestamp': datetime.now().isoformat(),
                'analyses': {}
            }
            
            # Run analyses concurrently
            tasks = []
            
            if 'transcription' in call_data:
                if 'call_summarization' in self.capabilities:
                    tasks.append(self._summarize_call(call_data['transcription']))
                
                if 'sentiment_analysis' in self.capabilities:
                    tasks.append(self._analyze_sentiment(call_data['transcription']))
                
                if 'compliance_checking' in self.capabilities:
                    tasks.append(self._check_compliance(call_data['transcription']))
            
            # Wait for all tasks to complete
            if tasks:
                completed_analyses = await asyncio.gather(*tasks)
                
                # Merge results
                for analysis in completed_analyses:
                    results['analyses'].update(analysis)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing call: {e}")
            raise
    
    async def _summarize_call(self, transcript: str) -> Dict[str, Any]:
        """Generate call summary using Bedrock"""
        try:
            prompt = f"""
            Summarize the following customer service call transcript.
            Include:
            1. Main issue/reason for call
            2. Steps taken to resolve
            3. Outcome/resolution
            4. Any follow-up actions needed
            
            Transcript:
            {transcript}
            
            Summary:
            """
            
            response = await self._call_bedrock(prompt)
            
            return {
                'summary': response,
                'summary_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error summarizing call: {e}")
            return {'summary': None, 'error': str(e)}
    
    async def _analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentiment using Comprehend and Bedrock"""
        try:
            # Use Comprehend for basic sentiment
            comprehend_response = self.comprehend_client.detect_sentiment(
                Text=transcript[:5000],  # Comprehend has text limit
                LanguageCode='en'
            )
            
            # Use Bedrock for detailed analysis
            prompt = f"""
            Analyze the emotional journey of this customer service call.
            Identify:
            1. Overall customer sentiment (positive/negative/neutral)
            2. Sentiment changes throughout the call
            3. Key emotional triggers
            4. Agent empathy level
            
            Transcript:
            {transcript[:3000]}
            
            Analysis:
            """
            
            bedrock_analysis = await self._call_bedrock(prompt)
            
            return {
                'sentiment': {
                    'overall': comprehend_response['Sentiment'],
                    'scores': comprehend_response['SentimentScore'],
                    'detailed_analysis': bedrock_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'sentiment': None, 'error': str(e)}
    
    async def _check_compliance(self, transcript: str) -> Dict[str, Any]:
        """Check for compliance issues"""
        try:
            prompt = f"""
            Review this call transcript for compliance issues.
            Check for:
            1. Proper greeting and closing
            2. Verification of customer identity
            3. Disclosure of required information
            4. Any potential compliance violations
            5. Use of prohibited language
            
            Transcript:
            {transcript[:3000]}
            
            Compliance Review:
            """
            
            compliance_review = await self._call_bedrock(prompt)
            
            return {
                'compliance': {
                    'review': compliance_review,
                    'checked_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            return {'compliance': None, 'error': str(e)}
    
    async def _call_bedrock(self, prompt: str) -> str:
        """Make a call to AWS Bedrock"""
        try:
            # Prepare the request
            request_body = {
                "prompt": prompt,
                "max_tokens_to_sample": self.config['aws']['bedrock']['max_tokens'],
                "temperature": self.config['aws']['bedrock']['temperature'],
                "top_p": 0.9,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.config['aws']['bedrock']['model_id'],
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body.get('completion', '').strip()
            
        except Exception as e:
            logger.error(f"Error calling Bedrock: {e}")
            raise
    
    def process_call_recording(self, s3_key: str) -> Dict[str, Any]:
        """Process a call recording from S3"""
        try:
            # Start transcription job
            job_name = f"call-transcription-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={
                    'MediaFileUri': f"s3://{self.config['aws']['s3']['bucket']}/{s3_key}"
                },
                MediaFormat='mp3',  # Adjust based on your audio format
                LanguageCode='en-US',
                Settings={
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': 2
                }
            )
            
            # Wait for transcription to complete
            while True:
                status = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(5)
            
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                # Get transcript
                transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                transcript_response = requests.get(transcript_uri)
                transcript_data = transcript_response.json()
                
                return {
                    'status': 'success',
                    'transcript': transcript_data['results']['transcripts'][0]['transcript'],
                    'job_name': job_name
                }
            else:
                return {
                    'status': 'failed',
                    'error': 'Transcription job failed'
                }
                
        except Exception as e:
            logger.error(f"Error processing call recording: {e}")
            return {'status': 'error', 'error': str(e)}