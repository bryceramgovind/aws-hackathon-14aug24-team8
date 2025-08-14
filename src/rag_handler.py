"""
RAG (Retrieval Augmented Generation) Handler for Call Center Analytics
"""

import boto3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional, Any, Tuple
import logging
from botocore.exceptions import ClientError
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
from collections import defaultdict
import re
from sentence_transformers import SentenceTransformer
import faiss
import pickle

logger = logging.getLogger(__name__)

class CallCenterRAG:
    """
    RAG system specifically designed for call center data
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RAG system
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.region = config['aws']['region']
        
        # Initialize AWS clients
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Knowledge base storage
        self.conversation_index = None
        self.conversation_metadata = []
        self.issue_patterns = {}
        self.resolution_templates = {}
        self.agent_performance_data = {}
        
        logger.info("Initialized CallCenterRAG system")
    
    def process_chat_data(self, chat_data_path: str) -> None:
        """
        Process customer service chat data and build knowledge base
        
        Args:
            chat_data_path: Path to the chat data JSON file
        """
        try:
            logger.info(f"Processing chat data from {chat_data_path}")
            
            # Load chat data
            with open(chat_data_path, 'r') as f:
                chat_data = json.load(f)
            
            # Group messages by contact_id to form complete conversations
            conversations = self._group_conversations(chat_data)
            
            # Extract knowledge components
            self._extract_issue_patterns(conversations)
            self._extract_resolution_templates(conversations)
            self._analyze_agent_performance(conversations)
            
            # Build vector index for semantic search
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
            'duration': 0,
            'resolution_achieved': False
        })
        
        for message in chat_data:
            contact_id = message['contact_id']
            conv = conversations[contact_id]
            
            # Add message
            conv['messages'].append({
                'text': message['chat_text'],
                'user_type': message['chat_user_type'],
                'timestamp': message['chat_time_shift'],
                'message_number': message['message_number']
            })
            
            # Separate customer and agent messages
            if message['chat_user_type'] == 'customer':
                conv['customer_messages'].append(message['chat_text'])
            else:
                conv['agent_messages'].append(message['chat_text'])
            
            # Update metadata
            if not conv['metadata']:
                conv['metadata'] = {
                    'contact_id': contact_id,
                    'start_date': message['start_date'],
                    'end_date': message['end_date'],
                    'phone_number': message['phone_number']
                }
                
                # Calculate duration
                start = datetime.fromisoformat(message['start_date'].replace('+10:00', ''))
                end = datetime.fromisoformat(message['end_date'].replace('+10:00', ''))
                conv['duration'] = (end - start).total_seconds()
        
        # Analyze resolution status
        for contact_id, conv in conversations.items():
            conv['resolution_achieved'] = self._detect_resolution(conv['messages'])
        
        return dict(conversations)
    
    def _detect_resolution(self, messages: List[Dict]) -> bool:
        """Detect if the conversation was resolved"""
        resolution_indicators = [
            'resolved', 'fixed', 'sorted', 'done', 'complete',
            'thank you', 'thanks', 'perfect', 'great', 'excellent'
        ]
        
        # Look at the last few messages
        last_messages = ' '.join([msg['text'].lower() for msg in messages[-3:]])
        
        return any(indicator in last_messages for indicator in resolution_indicators)
    
    def _extract_issue_patterns(self, conversations: Dict[str, Dict]) -> None:
        """Extract common issue patterns and categorize them"""
        issue_categories = {
            'billing': ['bill', 'charge', 'payment', 'cost', 'price', 'fee'],
            'technical': ['not working', 'broken', 'issue', 'problem', 'error', 'bug'],
            'account': ['account', 'login', 'password', 'access', 'profile'],
            'service': ['cancel', 'upgrade', 'downgrade', 'change', 'plan'],
            'roaming': ['roaming', 'overseas', 'international', 'abroad'],
            'data': ['data', 'internet', 'wifi', 'connection', 'slow']
        }
        
        self.issue_patterns = defaultdict(list)
        
        for contact_id, conv in conversations.items():
            # Get the first customer message (usually contains the main issue)
            if conv['customer_messages']:
                first_message = conv['customer_messages'][0].lower()
                
                # Categorize the issue
                for category, keywords in issue_categories.items():
                    if any(keyword in first_message for keyword in keywords):
                        self.issue_patterns[category].append({
                            'contact_id': contact_id,
                            'issue_text': first_message,
                            'resolved': conv['resolution_achieved'],
                            'duration': conv['duration']
                        })
                        break
                else:
                    # Uncategorized issues
                    self.issue_patterns['other'].append({
                        'contact_id': contact_id,
                        'issue_text': first_message,
                        'resolved': conv['resolution_achieved'],
                        'duration': conv['duration']
                    })
    
    def _extract_resolution_templates(self, conversations: Dict[str, Dict]) -> None:
        """Extract successful resolution templates"""
        self.resolution_templates = defaultdict(list)
        
        for contact_id, conv in conversations.items():
            if conv['resolution_achieved'] and conv['agent_messages']:
                # Find the issue category
                issue_category = 'other'
                if conv['customer_messages']:
                    first_message = conv['customer_messages'][0].lower()
                    for category, keywords in {
                        'billing': ['bill', 'charge', 'payment'],
                        'technical': ['not working', 'broken', 'issue'],
                        'account': ['account', 'login', 'password'],
                        'service': ['cancel', 'upgrade', 'plan']
                    }.items():
                        if any(keyword in first_message for keyword in keywords):
                            issue_category = category
                            break
                
                # Extract resolution steps from agent messages
                resolution_steps = []
                for msg in conv['agent_messages']:
                    if any(indicator in msg.lower() for indicator in 
                          ['let me', 'i will', 'i can', 'processed', 'updated', 'fixed']):
                        resolution_steps.append(msg)
                
                if resolution_steps:
                    self.resolution_templates[issue_category].append({
                        'contact_id': contact_id,
                        'steps': resolution_steps,
                        'duration': conv['duration']
                    })
    
    def _analyze_agent_performance(self, conversations: Dict[str, Dict]) -> None:
        """Analyze agent performance patterns"""
        agent_stats = defaultdict(lambda: {
            'total_conversations': 0,
            'resolved_conversations': 0,
            'avg_resolution_time': 0,
            'common_phrases': [],
            'resolution_rate': 0
        })
        
        # Extract agent performance data
        for contact_id, conv in conversations.items():
            if conv['agent_messages']:
                # Simplified agent identification (would need more sophisticated matching)
                agent_id = 'agent_general'  # Placeholder
                
                stats = agent_stats[agent_id]
                stats['total_conversations'] += 1
                
                if conv['resolution_achieved']:
                    stats['resolved_conversations'] += 1
                    stats['avg_resolution_time'] = (
                        (stats['avg_resolution_time'] * (stats['resolved_conversations'] - 1) + 
                         conv['duration']) / stats['resolved_conversations']
                    )
        
        # Calculate resolution rates
        for agent_id, stats in agent_stats.items():
            if stats['total_conversations'] > 0:
                stats['resolution_rate'] = stats['resolved_conversations'] / stats['total_conversations']
        
        self.agent_performance_data = dict(agent_stats)
    
    def _build_conversation_index(self, conversations: Dict[str, Dict]) -> None:
        """Build FAISS vector index for semantic search"""
        try:
            conversation_texts = []
            metadata = []
            
            for contact_id, conv in conversations.items():
                # Create a summary text for each conversation
                summary_text = f"Customer: {' '.join(conv['customer_messages'][:3])} " \
                              f"Agent: {' '.join(conv['agent_messages'][:3])}"
                
                conversation_texts.append(summary_text)
                metadata.append({
                    'contact_id': contact_id,
                    'resolved': conv['resolution_achieved'],
                    'duration': conv['duration'],
                    'full_conversation': conv['messages']
                })
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(conversation_texts)
            
            # Build FAISS index
            dimension = embeddings.shape[1]
            self.conversation_index = faiss.IndexFlatIP(dimension)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.conversation_index.add(embeddings.astype('float32'))
            
            self.conversation_metadata = metadata
            
            logger.info(f"Built conversation index with {len(conversation_texts)} entries")
            
        except Exception as e:
            logger.error(f"Error building conversation index: {e}")
            raise
    
    def find_similar_conversations(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find similar conversations using semantic search
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar conversations with metadata
        """
        try:
            if self.conversation_index is None:
                logger.warning("Conversation index not built. Call process_chat_data first.")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.conversation_index.search(
                query_embedding.astype('float32'), top_k
            )
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1:  # Valid result
                    result = self.conversation_metadata[idx].copy()
                    result['similarity_score'] = float(score)
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar conversations: {e}")
            return []
    
    def get_resolution_suggestions(self, issue_text: str, issue_category: str = None) -> List[Dict]:
        """
        Get resolution suggestions based on similar past issues
        
        Args:
            issue_text: Description of the current issue
            issue_category: Optional category hint
            
        Returns:
            List of resolution suggestions
        """
        try:
            # Find similar conversations
            similar_convs = self.find_similar_conversations(issue_text, top_k=10)
            
            # Filter for resolved conversations
            resolved_convs = [conv for conv in similar_convs if conv['resolved']]
            
            suggestions = []
            
            # Get resolution templates if category is known
            if issue_category and issue_category in self.resolution_templates:
                templates = self.resolution_templates[issue_category][:3]
                for template in templates:
                    suggestions.append({
                        'type': 'template',
                        'steps': template['steps'],
                        'avg_duration': template['duration'],
                        'source': 'resolution_templates'
                    })
            
            # Add suggestions from similar resolved conversations
            for conv in resolved_convs[:3]:
                agent_messages = [msg['text'] for msg in conv['full_conversation'] 
                               if msg['user_type'] == 'agent']
                
                if agent_messages:
                    suggestions.append({
                        'type': 'similar_case',
                        'agent_responses': agent_messages,
                        'duration': conv['duration'],
                        'similarity_score': conv['similarity_score'],
                        'source': 'similar_conversations'
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting resolution suggestions: {e}")
            return []
    
    def get_issue_insights(self, issue_category: str = None) -> Dict[str, Any]:
        """
        Get insights about issue patterns and resolution rates
        
        Args:
            issue_category: Optional category to focus on
            
        Returns:
            Dictionary with insights
        """
        try:
            insights = {}
            
            if issue_category and issue_category in self.issue_patterns:
                patterns = self.issue_patterns[issue_category]
                
                total_issues = len(patterns)
                resolved_issues = sum(1 for p in patterns if p['resolved'])
                avg_duration = np.mean([p['duration'] for p in patterns])
                
                insights[issue_category] = {
                    'total_cases': total_issues,
                    'resolved_cases': resolved_issues,
                    'resolution_rate': resolved_issues / total_issues if total_issues > 0 else 0,
                    'avg_duration_seconds': avg_duration,
                    'common_phrases': self._extract_common_phrases([p['issue_text'] for p in patterns])
                }
            else:
                # Overall insights
                for category, patterns in self.issue_patterns.items():
                    total_issues = len(patterns)
                    resolved_issues = sum(1 for p in patterns if p['resolved'])
                    avg_duration = np.mean([p['duration'] for p in patterns]) if patterns else 0
                    
                    insights[category] = {
                        'total_cases': total_issues,
                        'resolved_cases': resolved_issues,
                        'resolution_rate': resolved_issues / total_issues if total_issues > 0 else 0,
                        'avg_duration_seconds': avg_duration
                    }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting issue insights: {e}")
            return {}
    
    def _extract_common_phrases(self, texts: List[str], top_k: int = 10) -> List[str]:
        """Extract common phrases from a list of texts"""
        # Simple phrase extraction - could be enhanced with NLP
        word_freq = defaultdict(int)
        
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_freq[word] += 1
        
        # Return top words
        return sorted(word_freq.keys(), key=word_freq.get, reverse=True)[:top_k]
    
    async def enhance_agent_response(self, 
                                   customer_message: str, 
                                   conversation_history: List[Dict],
                                   agent_draft: str = None) -> Dict[str, Any]:
        """
        Enhance agent response using RAG and historical data
        
        Args:
            customer_message: Current customer message
            conversation_history: Previous conversation messages
            agent_draft: Optional draft response from agent
            
        Returns:
            Enhanced response with suggestions and context
        """
        try:
            # Find similar conversations
            similar_convs = self.find_similar_conversations(customer_message, top_k=5)
            
            # Get resolution suggestions
            suggestions = self.get_resolution_suggestions(customer_message)
            
            # Prepare context for Bedrock
            context = {
                'customer_message': customer_message,
                'conversation_history': conversation_history,
                'similar_cases': similar_convs[:3],
                'resolution_suggestions': suggestions[:2],
                'agent_draft': agent_draft
            }
            
            # Generate enhanced response using Bedrock
            enhanced_response = await self._generate_enhanced_response(context)
            
            return {
                'enhanced_response': enhanced_response,
                'similar_cases': similar_convs,
                'suggestions': suggestions,
                'confidence_score': self._calculate_confidence(similar_convs)
            }
            
        except Exception as e:
            logger.error(f"Error enhancing agent response: {e}")
            return {
                'enhanced_response': agent_draft or "I'll help you with that.",
                'similar_cases': [],
                'suggestions': [],
                'confidence_score': 0.0
            }
    
    async def _generate_enhanced_response(self, context: Dict[str, Any]) -> str:
        """Generate enhanced response using Bedrock"""
        try:
            prompt = f"""
You are an expert customer service agent. Based on the following context, provide an enhanced response to the customer.

Customer Message: {context['customer_message']}

Conversation History:
{json.dumps(context['conversation_history'], indent=2)}

Similar Resolved Cases:
{json.dumps(context['similar_cases'], indent=2)}

Resolution Suggestions:
{json.dumps(context['resolution_suggestions'], indent=2)}

Current Agent Draft: {context.get('agent_draft', 'None')}

Provide an empathetic, professional, and solution-focused response that:
1. Acknowledges the customer's concern
2. Uses insights from similar resolved cases
3. Provides clear next steps
4. Maintains a helpful tone

Enhanced Response:
"""

            request_body = {
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.7,
                "top_p": 0.9
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
            logger.error(f"Error generating enhanced response: {e}")
            return context.get('agent_draft', "I'll help you with that right away.")
    
    def _calculate_confidence(self, similar_cases: List[Dict]) -> float:
        """Calculate confidence score based on similar cases"""
        if not similar_cases:
            return 0.0
        
        # Base confidence on similarity scores and resolution status
        total_score = 0.0
        weight_sum = 0.0
        
        for case in similar_cases:
            similarity = case.get('similarity_score', 0.0)
            resolved_bonus = 0.2 if case.get('resolved', False) else 0.0
            
            score = similarity + resolved_bonus
            weight = similarity  # Weight by similarity
            
            total_score += score * weight
            weight_sum += weight
        
        return total_score / weight_sum if weight_sum > 0 else 0.0
    
    def save_knowledge_base(self, file_path: str) -> None:
        """Save the knowledge base to disk"""
        try:
            knowledge_base = {
                'issue_patterns': dict(self.issue_patterns),
                'resolution_templates': dict(self.resolution_templates),
                'agent_performance_data': self.agent_performance_data,
                'conversation_metadata': self.conversation_metadata
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(knowledge_base, f)
            
            # Save FAISS index separately
            if self.conversation_index:
                index_path = file_path.replace('.pkl', '_index.faiss')
                faiss.write_index(self.conversation_index, index_path)
            
            logger.info(f"Saved knowledge base to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            raise
    
    def load_knowledge_base(self, file_path: str) -> None:
        """Load the knowledge base from disk"""
        try:
            with open(file_path, 'rb') as f:
                knowledge_base = pickle.load(f)
            
            self.issue_patterns = defaultdict(list, knowledge_base['issue_patterns'])
            self.resolution_templates = defaultdict(list, knowledge_base['resolution_templates'])
            self.agent_performance_data = knowledge_base['agent_performance_data']
            self.conversation_metadata = knowledge_base['conversation_metadata']
            
            # Load FAISS index
            index_path = file_path.replace('.pkl', '_index.faiss')
            if os.path.exists(index_path):
                self.conversation_index = faiss.read_index(index_path)
            
            logger.info(f"Loaded knowledge base from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            raise
