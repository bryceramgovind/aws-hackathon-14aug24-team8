"""
Unified Call Center AI Agent with Integrated RAG
This replaces the need for separate aws_agent, bedrock_client, and rag_handler
"""

import os
import boto3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
from collections import defaultdict
import re
import yaml
from dotenv import load_dotenv
import pickle

# Try to import optional ML libraries
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries not available. Install with: pip install sentence-transformers faiss-cpu")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedCallCenterAI:
    """
    Unified Call Center AI Agent with integrated RAG, AWS services, and analytics
    This single class replaces aws_agent, rag_handler, and bedrock_client
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the unified AI system"""
        
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # AWS configuration
        self.region = os.getenv('AWS_REGION', self.config['aws']['region'])
        
        # Initialize AWS clients
        self._init_aws_clients()
        
        # Initialize ML components (if available)
        self.ml_ready = False
        if ML_AVAILABLE:
            self._init_ml_components()
        
        # Knowledge base storage
        self.conversation_index = None
        self.conversation_metadata = []
        self.issue_patterns = {}
        self.resolution_templates = {}
        self.agent_performance_data = {}
        self.knowledge_base_loaded = False
        
        # Agent settings
        self.agent_name = self.config['agent']['name']
        self.capabilities = self.config['agent']['capabilities']
        
        logger.info(f"Initialized {self.agent_name} with capabilities: {self.capabilities}")
    
    def _init_aws_clients(self):
        """Initialize all required AWS service clients"""
        try:
            # Core AWS clients
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
            self.s3_client = boto3.client('s3', region_name=self.region)
            self.comprehend_client = boto3.client('comprehend', region_name=self.region)
            
            # Optional clients (initialize only if needed)
            self.transcribe_client = None
            self.dynamodb_client = None
            
            logger.info("Successfully initialized AWS clients")
            
        except Exception as e:
            logger.error(f"Error initializing AWS clients: {e}")
            raise
    
    def _init_ml_components(self):
        """Initialize ML components if libraries are available"""
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.ml_ready = True
            logger.info("ML components initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize ML components: {e}")
            self.ml_ready = False
    
    # =============================================================================
    # CORE ANALYSIS METHODS
    # =============================================================================
    
    async def analyze_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive conversation analysis with RAG enhancement
        
        Args:
            conversation_data: Dictionary containing conversation information
                Required: 'transcription' or 'messages'
                Optional: 'call_id', 'customer_id', etc.
                
        Returns:
            Complete analysis results
        """
        try:
            results = {
                'conversation_id': conversation_data.get('call_id', conversation_data.get('conversation_id')),
                'timestamp': datetime.now().isoformat(),
                'analyses': {}
            }
            
            # Extract transcript from conversation data
            transcript = self._extract_transcript(conversation_data)
            if not transcript:
                return {'error': 'No transcript found in conversation data'}
            
            # Run parallel analyses
            tasks = []
            
            # Basic analyses
            if 'call_summarization' in self.capabilities:
                tasks.append(self._generate_summary(transcript))
            
            if 'sentiment_analysis' in self.capabilities:
                tasks.append(self._analyze_sentiment(transcript))
            
            if 'compliance_checking' in self.capabilities:
                tasks.append(self._check_compliance(transcript))
            
            # RAG-enhanced analyses (if knowledge base is loaded)
            if self.knowledge_base_loaded and self.ml_ready:
                tasks.append(self._get_rag_insights(transcript))
            
            # Execute all analyses concurrently
            if tasks:
                completed_analyses = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Merge results and handle exceptions
                for analysis in completed_analyses:
                    if isinstance(analysis, Exception):
                        logger.error(f"Analysis error: {analysis}")
                    else:
                        results['analyses'].update(analysis)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {e}")
            raise
    
    def _extract_transcript(self, conversation_data: Dict[str, Any]) -> str:
        """Extract transcript text from various conversation data formats"""
        
        # Direct transcription field
        if 'transcription' in conversation_data:
            return conversation_data['transcription']
        
        # Messages array format
        if 'messages' in conversation_data:
            messages = conversation_data['messages']
            transcript_parts = []
            
            for msg in messages:
                user_type = msg.get('user_type', msg.get('speaker', 'unknown'))
                text = msg.get('text', msg.get('message', ''))
                transcript_parts.append(f"{user_type.title()}: {text}")
            
            return "\n".join(transcript_parts)
        
        # Chat format (like your data)
        if 'chat_text' in conversation_data:
            return conversation_data['chat_text']
        
        return ""
    
    async def _generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Generate conversation summary using Bedrock"""
        try:
            prompt = f"""
            Analyze this customer service conversation and provide a structured summary:
            
            1. ISSUE: What was the customer's main problem or request?
            2. RESOLUTION: How was the issue addressed?
            3. OUTCOME: Was the issue resolved? Customer satisfaction level?
            4. FOLLOW-UP: Any required follow-up actions?
            5. KEY_POINTS: Important details or context
            
            Conversation:
            {transcript[:3000]}
            
            Summary:
            """
            
            response = await self._call_bedrock(prompt)
            
            return {
                'summary': response,
                'summary_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {'summary': None, 'error': str(e)}
    
    async def _analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Comprehensive sentiment analysis"""
        try:
            # Use AWS Comprehend for quick sentiment
            comprehend_result = {}
            try:
                comprehend_response = self.comprehend_client.detect_sentiment(
                    Text=transcript[:5000],  # Comprehend text limit
                    LanguageCode='en'
                )
                comprehend_result = {
                    'overall': comprehend_response['Sentiment'],
                    'confidence_scores': comprehend_response['SentimentScore']
                }
            except Exception as e:
                logger.warning(f"Comprehend sentiment analysis failed: {e}")
            
            # Enhanced sentiment analysis with Bedrock
            prompt = f"""
            Analyze the sentiment and emotional journey in this conversation:
            
            1. CUSTOMER_SENTIMENT: Overall customer emotional state
            2. SENTIMENT_PROGRESSION: How did emotions change during the call?
            3. AGENT_EMPATHY: How well did the agent handle customer emotions?
            4. EMOTIONAL_TRIGGERS: What caused emotional reactions?
            5. SATISFACTION_LEVEL: Likely customer satisfaction (1-10)
            
            Conversation:
            {transcript[:3000]}
            
            Sentiment Analysis:
            """
            
            bedrock_analysis = await self._call_bedrock(prompt)
            
            return {
                'sentiment': {
                    **comprehend_result,
                    'detailed_analysis': bedrock_analysis,
                    'analyzed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'sentiment': {'error': str(e)}}
    
    async def _check_compliance(self, transcript: str) -> Dict[str, Any]:
        """Check conversation for compliance issues"""
        try:
            prompt = f"""
            Review this customer service conversation for compliance and quality:
            
            Check for:
            1. GREETING: Proper professional greeting
            2. IDENTIFICATION: Agent identified themselves and company
            3. VERIFICATION: Customer identity verification (if applicable)
            4. INFORMATION_DISCLOSURE: Required disclosures made
            5. PROFESSIONALISM: Professional language and tone maintained
            6. RESOLUTION_PROCESS: Proper problem-solving approach
            7. CLOSING: Appropriate conversation closing
            8. VIOLATIONS: Any potential compliance issues
            
            Rate each area as: EXCELLENT / GOOD / NEEDS_IMPROVEMENT / POOR
            
            Conversation:
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
            return {'compliance': {'error': str(e)}}
    
    async def _get_rag_insights(self, transcript: str) -> Dict[str, Any]:
        """Get RAG-powered insights"""
        try:
            if not self.ml_ready:
                return {'rag_insights': {'error': 'ML components not available'}}
            
            # Find similar conversations
            similar_convs = self.find_similar_conversations(transcript)
            
            # Detect issue category
            issue_category = self._detect_issue_category(transcript)
            
            # Get resolution suggestions
            suggestions = self.get_resolution_suggestions(transcript, issue_category)
            
            # Get category insights
            category_insights = self.get_issue_insights(issue_category)
            
            return {
                'rag_insights': {
                    'similar_conversations': similar_convs,
                    'issue_category': issue_category,
                    'resolution_suggestions': suggestions,
                    'category_insights': category_insights,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG insights: {e}")
            return {'rag_insights': {'error': str(e)}}
    
    # =============================================================================
    # RAG SYSTEM METHODS
    # =============================================================================
    
    async def initialize_knowledge_base(self, chat_data_path: str = "data/customer_service_chats.json") -> None:
        """Initialize or load the knowledge base"""
        try:
            logger.info("Initializing knowledge base...")
            
            kb_path = self.config.get('rag', {}).get('knowledge_base_path', 'data/knowledge_base.pkl')
            
            if os.path.exists(kb_path):
                logger.info("Loading existing knowledge base...")
                self.load_knowledge_base(kb_path)
            else:
                logger.info("Building new knowledge base from chat data...")
                self.process_chat_data(chat_data_path)
                self.save_knowledge_base(kb_path)
            
            self.knowledge_base_loaded = True
            logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            raise
    
    def process_chat_data(self, chat_data_path: str) -> None:
        """Process chat data and build knowledge base"""
        if not self.ml_ready:
            logger.warning("ML components not available - skipping knowledge base building")
            return
        
        try:
            logger.info(f"Processing chat data from {chat_data_path}")
            
            with open(chat_data_path, 'r') as f:
                chat_data = json.load(f)
            
            # Group messages into conversations
            conversations = self._group_conversations(chat_data)
            
            # Extract patterns and templates
            self._extract_patterns(conversations)
            
            # Build vector index
            self._build_conversation_index(conversations)
            
            logger.info(f"Processed {len(conversations)} conversations")
            
        except Exception as e:
            logger.error(f"Error processing chat data: {e}")
            raise
    
    def _group_conversations(self, chat_data: List[Dict]) -> Dict[str, Dict]:
        """Group chat messages into complete conversations"""
        conversations = defaultdict(lambda: {
            'messages': [],
            'metadata': {},
            'customer_messages': [],
            'agent_messages': [],
            'resolved': False
        })
        
        for message in chat_data:
            contact_id = message['contact_id']
            conv = conversations[contact_id]
            
            # Add message
            conv['messages'].append({
                'text': message['chat_text'],
                'user_type': message['chat_user_type'],
                'timestamp': message['chat_time_shift']
            })
            
            # Separate by user type
            if message['chat_user_type'] == 'customer':
                conv['customer_messages'].append(message['chat_text'])
            else:
                conv['agent_messages'].append(message['chat_text'])
            
            # Store metadata
            if not conv['metadata']:
                conv['metadata'] = {
                    'contact_id': contact_id,
                    'start_date': message['start_date'],
                    'end_date': message['end_date'],
                    'phone_number': message['phone_number']
                }
        
        # Analyze each conversation
        for contact_id, conv in conversations.items():
            conv['resolved'] = self._detect_resolution(conv['messages'])
        
        return dict(conversations)
    
    def _detect_resolution(self, messages: List[Dict]) -> bool:
        """Detect if conversation was resolved"""
        if len(messages) < 2:
            return False
        
        last_messages = ' '.join([msg['text'].lower() for msg in messages[-3:]])
        
        resolution_indicators = [
            'thank you', 'thanks', 'resolved', 'fixed', 'sorted',
            'perfect', 'great', 'excellent', 'helped'
        ]
        
        return any(indicator in last_messages for indicator in resolution_indicators)
    
    def _extract_patterns(self, conversations: Dict[str, Dict]) -> None:
        """Extract issue patterns and resolution templates"""
        # Issue categorization patterns
        self.issue_patterns = defaultdict(list)
        self.resolution_templates = defaultdict(list)
        
        for contact_id, conv in conversations.items():
            if not conv['customer_messages']:
                continue
            
            # Categorize issue
            first_message = conv['customer_messages'][0].lower()
            category = self._detect_issue_category(first_message)
            
            self.issue_patterns[category].append({
                'contact_id': contact_id,
                'issue_text': first_message,
                'resolved': conv['resolved']
            })
            
            # Extract resolution templates for resolved conversations
            if conv['resolved'] and conv['agent_messages']:
                resolution_steps = [msg for msg in conv['agent_messages'] 
                                  if any(word in msg.lower() for word in 
                                        ['fixed', 'resolved', 'updated', 'processed'])]
                
                if resolution_steps:
                    self.resolution_templates[category].append({
                        'contact_id': contact_id,
                        'steps': resolution_steps
                    })
    
    def _detect_issue_category(self, text: str) -> str:
        """Detect issue category from text"""
        text_lower = text.lower()
        
        categories = {
            'billing': ['bill', 'charge', 'payment', 'cost', 'fee'],
            'technical': ['not working', 'broken', 'problem', 'error'],
            'account': ['account', 'login', 'password', 'access'],
            'service': ['cancel', 'upgrade', 'plan', 'change'],
            'roaming': ['roaming', 'overseas', 'international'],
            'data': ['data', 'internet', 'wifi', 'slow']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _build_conversation_index(self, conversations: Dict[str, Dict]) -> None:
        """Build FAISS vector index for semantic search"""
        if not self.ml_ready:
            return
        
        try:
            conversation_texts = []
            metadata = []
            
            for contact_id, conv in conversations.items():
                # Create summary text
                customer_text = ' '.join(conv['customer_messages'][:3])
                agent_text = ' '.join(conv['agent_messages'][:3])
                summary_text = f"Customer: {customer_text} Agent: {agent_text}"
                
                conversation_texts.append(summary_text)
                metadata.append({
                    'contact_id': contact_id,
                    'resolved': conv['resolved'],
                    'full_conversation': conv['messages']
                })
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(conversation_texts)
            
            # Build FAISS index
            dimension = embeddings.shape[1]
            self.conversation_index = faiss.IndexFlatIP(dimension)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)
            self.conversation_index.add(embeddings.astype('float32'))
            
            self.conversation_metadata = metadata
            
            logger.info(f"Built conversation index with {len(conversation_texts)} entries")
            
        except Exception as e:
            logger.error(f"Error building conversation index: {e}")
    
    def find_similar_conversations(self, query: str, top_k: int = 5) -> List[Dict]:
        """Find similar conversations using semantic search"""
        if not self.ml_ready or self.conversation_index is None:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.conversation_index.search(
                query_embedding.astype('float32'), top_k
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1:
                    result = self.conversation_metadata[idx].copy()
                    result['similarity_score'] = float(score)
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar conversations: {e}")
            return []
    
    def get_resolution_suggestions(self, issue_text: str, category: str = None) -> List[Dict]:
        """Get resolution suggestions based on similar cases"""
        try:
            suggestions = []
            
            # Get from resolution templates
            if category and category in self.resolution_templates:
                for template in self.resolution_templates[category][:2]:
                    suggestions.append({
                        'type': 'template',
                        'category': category,
                        'steps': template['steps']
                    })
            
            # Get from similar conversations
            similar_convs = self.find_similar_conversations(issue_text, top_k=3)
            for conv in similar_convs:
                if conv['resolved']:
                    agent_messages = [msg['text'] for msg in conv['full_conversation'] 
                                    if msg['user_type'] == 'agent']
                    if agent_messages:
                        suggestions.append({
                            'type': 'similar_case',
                            'similarity_score': conv['similarity_score'],
                            'agent_responses': agent_messages
                        })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting resolution suggestions: {e}")
            return []
    
    def get_issue_insights(self, category: str = None) -> Dict[str, Any]:
        """Get insights about issue patterns"""
        try:
            insights = {}
            
            patterns_to_analyze = {category: self.issue_patterns[category]} if category else self.issue_patterns
            
            for cat, patterns in patterns_to_analyze.items():
                if patterns:
                    total = len(patterns)
                    resolved = sum(1 for p in patterns if p['resolved'])
                    
                    insights[cat] = {
                        'total_cases': total,
                        'resolved_cases': resolved,
                        'resolution_rate': resolved / total if total > 0 else 0
                    }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting issue insights: {e}")
            return {}
    
    # =============================================================================
    # AGENT ASSISTANCE METHODS
    # =============================================================================
    
    async def provide_agent_assistance(self, 
                                     customer_message: str, 
                                     conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Provide real-time assistance to agents"""
        try:
            if not self.knowledge_base_loaded:
                await self.initialize_knowledge_base()
            
            # Analyze current message
            urgency = self._detect_urgency(customer_message)
            sentiment = await self._analyze_message_sentiment(customer_message)
            
            # Get RAG suggestions
            rag_suggestions = []
            if self.ml_ready:
                similar_cases = self.find_similar_conversations(customer_message)
                category = self._detect_issue_category(customer_message)
                resolution_suggestions = self.get_resolution_suggestions(customer_message, category)
                
                rag_suggestions = {
                    'similar_cases': similar_cases,
                    'category': category,
                    'suggestions': resolution_suggestions
                }
            
            # Generate enhanced response
            enhanced_response = await self._generate_agent_response(
                customer_message, conversation_history, rag_suggestions
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'customer_message': customer_message,
                'urgency_level': urgency,
                'sentiment': sentiment,
                'enhanced_response': enhanced_response,
                'rag_suggestions': rag_suggestions,
                'recommended_actions': self._get_recommended_actions(urgency, sentiment)
            }
            
        except Exception as e:
            logger.error(f"Error providing agent assistance: {e}")
            return {
                'error': str(e),
                'fallback_response': "I understand your concern. Let me help you with that."
            }
    
    def _detect_urgency(self, message: str) -> str:
        """Detect urgency level from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['emergency', 'urgent', 'asap', 'immediately']):
            return 'critical'
        elif any(word in message_lower for word in ['frustrated', 'angry', 'unacceptable']):
            return 'high'
        elif any(word in message_lower for word in ['problem', 'issue', 'concerned']):
            return 'medium'
        else:
            return 'low'
    
    async def _analyze_message_sentiment(self, message: str) -> Dict[str, Any]:
        """Quick sentiment analysis for a single message"""
        try:
            response = self.comprehend_client.detect_sentiment(
                Text=message[:1000],
                LanguageCode='en'
            )
            return {
                'sentiment': response['Sentiment'],
                'confidence': response['SentimentScore']
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {'sentiment': 'NEUTRAL', 'confidence': {}}
    
    async def _generate_agent_response(self, 
                                     customer_message: str, 
                                     history: List[Dict] = None,
                                     rag_suggestions: Dict = None) -> str:
        """Generate an enhanced agent response"""
        try:
            context = f"Customer message: {customer_message}\n"
            
            if history:
                context += f"Conversation history: {json.dumps(history[-3:])}\n"
            
            if rag_suggestions and rag_suggestions.get('suggestions'):
                context += f"Similar case solutions: {json.dumps(rag_suggestions['suggestions'][:2])}\n"
            
            prompt = f"""
            As a professional customer service agent, craft a helpful response to this customer.
            Be empathetic, solution-focused, and professional.
            
            Context:
            {context}
            
            Provide a clear, helpful response that:
            1. Acknowledges the customer's concern
            2. Offers a specific solution or next steps
            3. Maintains a professional and empathetic tone
            
            Agent Response:
            """
            
            return await self._call_bedrock(prompt, max_tokens=300)
            
        except Exception as e:
            logger.error(f"Error generating agent response: {e}")
            return "I understand your concern and I'm here to help. Let me look into this for you right away."
    
    def _get_recommended_actions(self, urgency: str, sentiment: Dict) -> List[str]:
        """Get recommended actions based on urgency and sentiment"""
        actions = []
        
        if urgency == 'critical':
            actions.append("Escalate to supervisor immediately")
        elif urgency == 'high':
            actions.append("Prioritize this customer")
        
        sentiment_level = sentiment.get('sentiment', 'NEUTRAL')
        if sentiment_level == 'NEGATIVE':
            actions.append("Use empathetic language")
            actions.append("Acknowledge frustration")
        
        if not actions:
            actions.append("Provide clear information")
        
        return actions
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    async def _call_bedrock(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call AWS Bedrock with standardized parameters"""
        try:
            request_body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens,
                "temperature": self.config['aws']['bedrock'].get('temperature', 0.7),
                "top_p": 0.9,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.config['aws']['bedrock']['model_id'],
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('completion', '').strip()
            
        except Exception as e:
            logger.error(f"Error calling Bedrock: {e}")
            raise
    
    def save_knowledge_base(self, file_path: str) -> None:
        """Save knowledge base to disk"""
        try:
            kb_data = {
                'issue_patterns': dict(self.issue_patterns),
                'resolution_templates': dict(self.resolution_templates),
                'conversation_metadata': self.conversation_metadata
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(kb_data, f)
            
            # Save FAISS index
            if self.conversation_index:
                index_path = file_path.replace('.pkl', '_index.faiss')
                faiss.write_index(self.conversation_index, index_path)
            
            logger.info(f"Saved knowledge base to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def load_knowledge_base(self, file_path: str) -> None:
        """Load knowledge base from disk"""
        try:
            with open(file_path, 'rb') as f:
                kb_data = pickle.load(f)
            
            self.issue_patterns = defaultdict(list, kb_data['issue_patterns'])
            self.resolution_templates = defaultdict(list, kb_data['resolution_templates'])
            self.conversation_metadata = kb_data['conversation_metadata']
            
            # Load FAISS index
            index_path = file_path.replace('.pkl', '_index.faiss')
            if os.path.exists(index_path) and self.ml_ready:
                self.conversation_index = faiss.read_index(index_path)
            
            logger.info(f"Loaded knowledge base from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
    
    # =============================================================================
    # PERFORMANCE AND ANALYTICS
    # =============================================================================
    
    async def generate_performance_insights(self) -> Dict[str, Any]:
        """Generate performance insights and recommendations"""
        try:
            insights = self.get_issue_insights()
            
            recommendations = []
            for category, stats in insights.items():
                if stats['resolution_rate'] < 0.8:
                    recommendations.append({
                        'category': category,
                        'issue': 'Low resolution rate',
                        'recommendation': f"Improve {category} resolution training"
                    })
            
            return {
                'generated_at': datetime.now().isoformat(),
                'category_insights': insights,
                'recommendations': recommendations,
                'summary': {
                    'total_categories': len(insights),
                    'avg_resolution_rate': sum(s['resolution_rate'] for s in insights.values()) / len(insights) if insights else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {'error': str(e)}
    
    async def batch_analyze_conversations(self, conversations: List[Dict]) -> List[Dict]:
        """Analyze multiple conversations efficiently"""
        try:
            logger.info(f"Batch analyzing {len(conversations)} conversations")
            
            tasks = [self.analyze_conversation(conv) for conv in conversations]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing conversation {i}: {result}")
                else:
                    successful_results.append(result)
            
            logger.info(f"Successfully analyzed {len(successful_results)} conversations")
            return successful_results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            raise
