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
from .rag_handler import CallCenterRAG
from .s3_handler import S3CallCenterHandler
from .bedrock_client import BedrockCallAnalyzer

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
        
        # Initialize RAG system
        self.rag_system = CallCenterRAG(self.config)
        
        # Initialize S3 handler
        bucket_name = self.config['aws']['s3'].get('bucket_name', 'call-center-data')
        self.s3_handler = S3CallCenterHandler(bucket_name, self.region)
        
        # Initialize specialized Bedrock client
        self.bedrock_analyzer = BedrockCallAnalyzer(self.region)
        
        # Agent settings
        self.agent_name = self.config['agent']['name']
        self.capabilities = self.config['agent']['capabilities']
        
        # Knowledge base loaded flag
        self.knowledge_base_loaded = False
        
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
    
    async def initialize_knowledge_base(self, chat_data_path: str = "data/customer_service_chats.json") -> None:
        """
        Initialize the RAG knowledge base with chat data
        
        Args:
            chat_data_path: Path to the customer service chat data
        """
        try:
            logger.info("Initializing knowledge base...")
            
            # Check if knowledge base already exists
            kb_path = "data/knowledge_base.pkl"
            if os.path.exists(kb_path):
                logger.info("Loading existing knowledge base...")
                self.rag_system.load_knowledge_base(kb_path)
            else:
                logger.info("Building new knowledge base from chat data...")
                self.rag_system.process_chat_data(chat_data_path)
                self.rag_system.save_knowledge_base(kb_path)
            
            self.knowledge_base_loaded = True
            logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            raise
    
    async def analyze_call_with_rag(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced call analysis using RAG system
        
        Args:
            call_data: Dictionary containing call information
            
        Returns:
            Enhanced analysis results with RAG insights
        """
        try:
            if not self.knowledge_base_loaded:
                await self.initialize_knowledge_base()
            
            # Start with basic analysis
            results = await self.analyze_call(call_data)
            
            # Add RAG-enhanced insights
            if 'transcription' in call_data:
                transcript = call_data['transcription']
                
                # Find similar conversations
                similar_convs = self.rag_system.find_similar_conversations(transcript)
                
                # Get resolution suggestions
                issue_category = self._detect_issue_category(transcript)
                suggestions = self.rag_system.get_resolution_suggestions(transcript, issue_category)
                
                # Get issue insights
                insights = self.rag_system.get_issue_insights(issue_category)
                
                # Add RAG results
                results['rag_insights'] = {
                    'similar_conversations': similar_convs,
                    'resolution_suggestions': suggestions,
                    'issue_category': issue_category,
                    'category_insights': insights,
                    'generated_at': datetime.now().isoformat()
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing call with RAG: {e}")
            # Fallback to basic analysis
            return await self.analyze_call(call_data)
    
    def _detect_issue_category(self, transcript: str) -> str:
        """
        Detect the issue category from transcript
        
        Args:
            transcript: Call transcript
            
        Returns:
            Detected issue category
        """
        transcript_lower = transcript.lower()
        
        categories = {
            'billing': ['bill', 'charge', 'payment', 'cost', 'price', 'fee', 'invoice'],
            'technical': ['not working', 'broken', 'issue', 'problem', 'error', 'bug', 'fault'],
            'account': ['account', 'login', 'password', 'access', 'profile', 'credentials'],
            'service': ['cancel', 'upgrade', 'downgrade', 'change', 'plan', 'service'],
            'roaming': ['roaming', 'overseas', 'international', 'abroad', 'travel'],
            'data': ['data', 'internet', 'wifi', 'connection', 'slow', 'speed']
        }
        
        for category, keywords in categories.items():
            if any(keyword in transcript_lower for keyword in keywords):
                return category
        
        return 'other'
    
    async def provide_agent_assistance(self, 
                                     customer_message: str, 
                                     conversation_history: List[Dict],
                                     agent_id: str = None) -> Dict[str, Any]:
        """
        Provide real-time assistance to agents using RAG
        
        Args:
            customer_message: Current customer message
            conversation_history: Previous conversation messages
            agent_id: Optional agent identifier
            
        Returns:
            Agent assistance with suggestions and insights
        """
        try:
            if not self.knowledge_base_loaded:
                await self.initialize_knowledge_base()
            
            # Get RAG-enhanced response suggestions
            assistance = await self.rag_system.enhance_agent_response(
                customer_message, conversation_history
            )
            
            # Add sentiment analysis
            sentiment_analysis = await self._analyze_message_sentiment(customer_message)
            
            # Add urgency detection
            urgency_level = self._detect_urgency(customer_message)
            
            # Compile assistance package
            result = {
                'agent_id': agent_id,
                'timestamp': datetime.now().isoformat(),
                'customer_message': customer_message,
                'enhanced_response': assistance['enhanced_response'],
                'similar_cases': assistance['similar_cases'],
                'resolution_suggestions': assistance['suggestions'],
                'confidence_score': assistance['confidence_score'],
                'sentiment_analysis': sentiment_analysis,
                'urgency_level': urgency_level,
                'recommended_actions': self._generate_recommended_actions(
                    customer_message, sentiment_analysis, urgency_level
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error providing agent assistance: {e}")
            return {
                'error': str(e),
                'fallback_response': "I understand your concern. Let me help you with that right away."
            }
    
    async def _analyze_message_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment of a single message"""
        try:
            response = self.comprehend_client.detect_sentiment(
                Text=message[:5000],
                LanguageCode='en'
            )
            
            return {
                'sentiment': response['Sentiment'],
                'confidence_scores': response['SentimentScore']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message sentiment: {e}")
            return {'sentiment': 'NEUTRAL', 'confidence_scores': {}}
    
    def _detect_urgency(self, message: str) -> str:
        """
        Detect urgency level from message content
        
        Args:
            message: Customer message
            
        Returns:
            Urgency level: 'low', 'medium', 'high', 'critical'
        """
        message_lower = message.lower()
        
        critical_indicators = ['emergency', 'urgent', 'asap', 'immediately', 'critical', 'escalate']
        high_indicators = ['frustrated', 'angry', 'unacceptable', 'terrible', 'awful', 'horrible']
        medium_indicators = ['disappointed', 'concerned', 'worried', 'problem', 'issue']
        
        if any(indicator in message_lower for indicator in critical_indicators):
            return 'critical'
        elif any(indicator in message_lower for indicator in high_indicators):
            return 'high'
        elif any(indicator in message_lower for indicator in medium_indicators):
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommended_actions(self, 
                                    message: str, 
                                    sentiment: Dict[str, Any], 
                                    urgency: str) -> List[str]:
        """Generate recommended actions based on message analysis"""
        actions = []
        
        # Urgency-based actions
        if urgency == 'critical':
            actions.append("Escalate to supervisor immediately")
            actions.append("Prioritize this customer in queue")
        elif urgency == 'high':
            actions.append("Provide immediate attention")
            actions.append("Consider offering compensation if applicable")
        
        # Sentiment-based actions
        sentiment_level = sentiment.get('sentiment', 'NEUTRAL')
        if sentiment_level == 'NEGATIVE':
            actions.append("Use empathetic language")
            actions.append("Acknowledge customer frustration")
            actions.append("Focus on solution-oriented responses")
        elif sentiment_level == 'POSITIVE':
            actions.append("Maintain positive momentum")
            actions.append("Thank customer for their patience")
        
        # Default professional actions
        if not actions:
            actions.append("Provide clear and helpful information")
            actions.append("Confirm understanding of the issue")
        
        return actions
    
    async def generate_performance_insights(self, agent_id: str = None, time_period: str = "7d") -> Dict[str, Any]:
        """
        Generate performance insights for agents
        
        Args:
            agent_id: Optional specific agent ID
            time_period: Time period for analysis (7d, 30d, etc.)
            
        Returns:
            Performance insights and recommendations
        """
        try:
            if not self.knowledge_base_loaded:
                await self.initialize_knowledge_base()
            
            # Get issue insights from RAG system
            overall_insights = self.rag_system.get_issue_insights()
            
            # Generate recommendations
            recommendations = []
            
            for category, stats in overall_insights.items():
                resolution_rate = stats['resolution_rate']
                avg_duration = stats['avg_duration_seconds']
                
                if resolution_rate < 0.8:
                    recommendations.append({
                        'category': category,
                        'issue': 'Low resolution rate',
                        'recommendation': f"Focus on improving {category} issue resolution training",
                        'priority': 'high' if resolution_rate < 0.6 else 'medium'
                    })
                
                if avg_duration > 600:  # 10 minutes
                    recommendations.append({
                        'category': category,
                        'issue': 'Long resolution time',
                        'recommendation': f"Develop faster resolution procedures for {category} issues",
                        'priority': 'medium'
                    })
            
            result = {
                'agent_id': agent_id,
                'time_period': time_period,
                'generated_at': datetime.now().isoformat(),
                'category_insights': overall_insights,
                'recommendations': recommendations,
                'overall_metrics': {
                    'total_categories': len(overall_insights),
                    'avg_resolution_rate': sum(s['resolution_rate'] for s in overall_insights.values()) / len(overall_insights),
                    'categories_needing_attention': len([r for r in recommendations if r['priority'] == 'high'])
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating performance insights: {e}")
            return {'error': str(e)}
    
    async def batch_process_conversations(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple conversations in batch for efficiency
        
        Args:
            conversations: List of conversation data
            
        Returns:
            List of analysis results
        """
        try:
            logger.info(f"Processing {len(conversations)} conversations in batch")
            
            # Process conversations concurrently
            tasks = []
            for conv in conversations:
                tasks.append(self.analyze_call_with_rag(conv))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing conversation {i}: {result}")
                else:
                    processed_results.append(result)
            
            logger.info(f"Successfully processed {len(processed_results)} conversations")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
    
    