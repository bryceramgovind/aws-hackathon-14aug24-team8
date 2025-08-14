"""
Specialized Bedrock client for call center use cases
"""

import boto3
import json
import logging
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class BedrockCallAnalyzer:
    """
    Specialized class for call center analytics using Bedrock
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=region_name
        )
        self.bedrock = boto3.client(
            'bedrock',
            region_name=region_name
        )
        
    def list_available_models(self) -> List[Dict]:
        """List all available Bedrock models"""
        try:
            response = self.bedrock.list_foundation_models()
            models = []
            
            for model in response['modelSummaries']:
                models.append({
                    'modelId': model['modelId'],
                    'modelName': model['modelName'],
                    'provider': model['providerName'],
                    'inputModalities': model.get('inputModalities', []),
                    'outputModalities': model.get('outputModalities', [])
                })
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def generate_coaching_insights(self, 
                                       transcript: str,
                                       agent_name: str) -> Dict[str, Any]:
        """Generate coaching insights for agents"""
        
        prompt = f"""
        As an expert call center coach, analyze this call handled by {agent_name}.
        
        Provide specific coaching feedback on:
        1. Communication skills (clarity, pace, tone)
        2. Problem-solving approach
        3. Customer empathy and rapport building
        4. Product knowledge demonstration
        5. Opportunities for improvement
        6. Things done well
        
        Call Transcript:
        {transcript[:4000]}
        
        Coaching Feedback:
        """
        
        try:
            response = self._invoke_claude(prompt)
            
            return {
                'agent_name': agent_name,
                'coaching_insights': response,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating coaching insights: {e}")
            return {'error': str(e)}
    
    async def extract_customer_intent(self, transcript: str) -> Dict[str, Any]:
        """Extract customer intent and needs from call"""
        
        prompt = f"""
        Analyze this customer service call and extract:
        
        1. Primary customer intent/reason for calling
        2. Underlying needs or concerns
        3. Customer's emotional state
        4. Urgency level (low/medium/high)
        5. Product/service mentioned
        6. Suggested follow-up actions
        
        Transcript:
        {transcript[:4000]}
        
        Analysis:
        """
        
        try:
            response = self._invoke_claude(prompt)
            
            return {
                'intent_analysis': response,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting customer intent: {e}")
            return {'error': str(e)}
    
    def _invoke_claude(self, prompt: str, max_tokens: int = 4096) -> str:
        """Invoke Claude model through Bedrock"""
        
        body = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop_sequences": ["\n\nHuman:"]
        }
        
        response = self.bedrock_runtime.invoke_model(
            modelId='anthropic.claude-v2',
            body=json.dumps(body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body.get('completion', '').strip()