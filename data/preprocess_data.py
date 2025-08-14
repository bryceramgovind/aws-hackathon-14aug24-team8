"""
Data preprocessing utilities for customer service chat data
"""

import json
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import re
import os

logger = logging.getLogger(__name__)

class ChatDataPreprocessor:
    """
    Preprocessor for customer service chat data to optimize for RAG
    """
    
    def __init__(self):
        self.processed_conversations = {}
        self.conversation_summaries = []
        self.issue_categories = {}
        
    def load_and_preprocess(self, data_path: str) -> Dict[str, Any]:
        """
        Load and preprocess chat data
        
        Args:
            data_path: Path to the JSON data file
            
        Returns:
            Preprocessed data dictionary
        """
        try:
            logger.info(f"Loading chat data from {data_path}")
            
            with open(data_path, 'r') as f:
                raw_data = json.load(f)
            
            logger.info(f"Loaded {len(raw_data)} chat messages")
            
            # Group by conversations
            conversations = self._group_by_conversation(raw_data)
            
            # Clean and structure conversations
            cleaned_conversations = self._clean_conversations(conversations)
            
            # Generate conversation summaries
            summaries = self._generate_summaries(cleaned_conversations)
            
            # Categorize issues
            categories = self._categorize_issues(cleaned_conversations)
            
            # Extract temporal patterns
            temporal_patterns = self._analyze_temporal_patterns(cleaned_conversations)
            
            result = {
                'conversations': cleaned_conversations,
                'summaries': summaries,
                'categories': categories,
                'temporal_patterns': temporal_patterns,
                'statistics': self._generate_statistics(cleaned_conversations)
            }
            
            logger.info(f"Preprocessed {len(cleaned_conversations)} conversations")
            return result
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            raise
    
    def _group_by_conversation(self, raw_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Group messages by contact_id"""
        conversations = defaultdict(list)
        
        for message in raw_data:
            contact_id = message['contact_id']
            conversations[contact_id].append(message)
        
        # Sort messages by message_number
        for contact_id in conversations:
            conversations[contact_id].sort(key=lambda x: x['message_number'])
        
        return dict(conversations)
    
    def _clean_conversations(self, conversations: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Clean and structure conversations"""
        cleaned = {}
        
        for contact_id, messages in conversations.items():
            if not messages:
                continue
            
            # Basic conversation metadata
            first_msg = messages[0]
            last_msg = messages[-1]
            
            conversation = {
                'contact_id': contact_id,
                'start_time': first_msg['start_date'],
                'end_time': first_msg['end_date'],
                'phone_number': first_msg['phone_number'],
                'total_messages': len(messages),
                'messages': [],
                'customer_messages': [],
                'agent_messages': [],
                'message_count': {'customer': 0, 'agent': 0},
                'duration_seconds': 0,
                'turns': 0  # Number of back-and-forth exchanges
            }
            
            # Process individual messages
            customer_turns = 0
            agent_turns = 0
            last_speaker = None
            
            for msg in messages:
                cleaned_msg = {
                    'text': self._clean_text(msg['chat_text']),
                    'user_type': msg['chat_user_type'],
                    'timestamp_offset': msg['chat_time_shift'],
                    'message_number': msg['message_number'],
                    'user_id': msg['chat_user_id']
                }
                
                conversation['messages'].append(cleaned_msg)
                
                # Separate by user type
                if msg['chat_user_type'] == 'customer':
                    conversation['customer_messages'].append(cleaned_msg['text'])
                    conversation['message_count']['customer'] += 1
                    if last_speaker != 'customer':
                        customer_turns += 1
                        last_speaker = 'customer'
                else:
                    conversation['agent_messages'].append(cleaned_msg['text'])
                    conversation['message_count']['agent'] += 1
                    if last_speaker != 'agent':
                        agent_turns += 1
                        last_speaker = 'agent'
            
            # Calculate conversation metrics
            conversation['turns'] = max(customer_turns, agent_turns)
            if messages:
                conversation['duration_seconds'] = messages[-1]['chat_time_shift']
            
            # Determine resolution status
            conversation['appears_resolved'] = self._detect_resolution(conversation['messages'])
            
            # Extract key phrases
            conversation['key_phrases'] = self._extract_key_phrases(conversation)
            
            cleaned[contact_id] = conversation
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Clean individual message text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common typos/abbreviations (optional)
        text = text.replace(' ur ', ' your ')
        text = text.replace(' u ', ' you ')
        text = text.replace(' cant ', ' cannot ')
        text = text.replace(' wont ', ' will not ')
        
        return text
    
    def _detect_resolution(self, messages: List[Dict]) -> bool:
        """Detect if conversation appears to be resolved"""
        if len(messages) < 2:
            return False
        
        # Look at last few messages for resolution indicators
        last_messages = ' '.join([msg['text'].lower() for msg in messages[-3:]])
        
        positive_indicators = [
            'thank you', 'thanks', 'perfect', 'great', 'excellent',
            'resolved', 'fixed', 'sorted', 'done', 'complete',
            'helped', 'appreciate', 'wonderful', 'fantastic'
        ]
        
        negative_indicators = [
            'still not working', 'not resolved', 'still have the problem',
            'not fixed', 'disappointed', 'frustrated', 'angry'
        ]
        
        positive_score = sum(1 for indicator in positive_indicators if indicator in last_messages)
        negative_score = sum(1 for indicator in negative_indicators if indicator in last_messages)
        
        return positive_score > negative_score
    
    def _extract_key_phrases(self, conversation: Dict) -> List[str]:
        """Extract key phrases from conversation"""
        all_text = ' '.join(conversation['customer_messages'] + conversation['agent_messages'])
        
        # Simple keyword extraction (could be enhanced with NLP)
        common_keywords = [
            'bill', 'billing', 'charge', 'payment', 'account', 'service',
            'internet', 'connection', 'roaming', 'data', 'plan', 'upgrade',
            'cancel', 'problem', 'issue', 'not working', 'broken', 'error'
        ]
        
        found_keywords = []
        text_lower = all_text.lower()
        
        for keyword in common_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _generate_summaries(self, conversations: Dict[str, Dict]) -> List[Dict]:
        """Generate conversation summaries"""
        summaries = []
        
        for contact_id, conv in conversations.items():
            # Create a structured summary
            summary = {
                'contact_id': contact_id,
                'issue_summary': self._extract_issue_summary(conv),
                'resolution_summary': self._extract_resolution_summary(conv),
                'customer_sentiment': self._estimate_sentiment(conv['customer_messages']),
                'conversation_flow': self._analyze_conversation_flow(conv),
                'key_metrics': {
                    'total_messages': conv['total_messages'],
                    'duration_seconds': conv['duration_seconds'],
                    'turns': conv['turns'],
                    'resolved': conv['appears_resolved']
                }
            }
            
            summaries.append(summary)
        
        return summaries
    
    def _extract_issue_summary(self, conversation: Dict) -> str:
        """Extract what the customer's main issue was"""
        if not conversation['customer_messages']:
            return "No customer messages found"
        
        # Usually the first customer message contains the main issue
        first_message = conversation['customer_messages'][0]
        
        # Truncate if too long
        if len(first_message) > 200:
            return first_message[:200] + "..."
        
        return first_message
    
    def _extract_resolution_summary(self, conversation: Dict) -> str:
        """Extract how the issue was resolved"""
        if not conversation['agent_messages']:
            return "No agent responses found"
        
        # Look for resolution-indicating messages
        resolution_keywords = ['resolved', 'fixed', 'processed', 'updated', 'completed']
        
        for msg in reversed(conversation['agent_messages']):
            msg_lower = msg.lower()
            if any(keyword in msg_lower for keyword in resolution_keywords):
                if len(msg) > 200:
                    return msg[:200] + "..."
                return msg
        
        # If no specific resolution found, return last agent message
        if conversation['agent_messages']:
            last_msg = conversation['agent_messages'][-1]
            if len(last_msg) > 200:
                return last_msg[:200] + "..."
            return last_msg
        
        return "No resolution information available"
    
    def _estimate_sentiment(self, customer_messages: List[str]) -> str:
        """Estimate customer sentiment (simplified)"""
        if not customer_messages:
            return "neutral"
        
        all_text = ' '.join(customer_messages).lower()
        
        positive_words = ['thank', 'great', 'perfect', 'excellent', 'good', 'happy', 'satisfied']
        negative_words = ['angry', 'frustrated', 'terrible', 'awful', 'horrible', 'unacceptable', 'disappointed']
        
        positive_count = sum(1 for word in positive_words if word in all_text)
        negative_count = sum(1 for word in negative_words if word in all_text)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    def _analyze_conversation_flow(self, conversation: Dict) -> Dict[str, Any]:
        """Analyze the flow of conversation"""
        messages = conversation['messages']
        
        if len(messages) < 2:
            return {'pattern': 'insufficient_data'}
        
        # Analyze pattern
        user_types = [msg['user_type'] for msg in messages]
        
        # Check for balanced exchange
        customer_count = user_types.count('customer')
        agent_count = user_types.count('agent')
        
        flow_analysis = {
            'message_balance': abs(customer_count - agent_count),
            'starts_with': user_types[0],
            'ends_with': user_types[-1],
            'alternating_pattern': self._check_alternating_pattern(user_types),
            'avg_response_time': self._calculate_avg_response_time(messages)
        }
        
        return flow_analysis
    
    def _check_alternating_pattern(self, user_types: List[str]) -> bool:
        """Check if conversation follows an alternating pattern"""
        if len(user_types) < 4:
            return False
        
        alternating_count = 0
        for i in range(1, len(user_types)):
            if user_types[i] != user_types[i-1]:
                alternating_count += 1
        
        # Consider alternating if >70% of transitions are alternating
        return (alternating_count / (len(user_types) - 1)) > 0.7
    
    def _calculate_avg_response_time(self, messages: List[Dict]) -> float:
        """Calculate average response time between messages"""
        if len(messages) < 2:
            return 0.0
        
        response_times = []
        for i in range(1, len(messages)):
            time_diff = messages[i]['timestamp_offset'] - messages[i-1]['timestamp_offset']
            response_times.append(time_diff)
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _categorize_issues(self, conversations: Dict[str, Dict]) -> Dict[str, List[str]]:
        """Categorize conversations by issue type"""
        categories = {
            'billing': [],
            'technical': [],
            'account': [],
            'service_changes': [],
            'roaming': [],
            'data_usage': [],
            'complaints': [],
            'general_inquiry': []
        }
        
        category_keywords = {
            'billing': ['bill', 'charge', 'payment', 'cost', 'price', 'fee', 'invoice'],
            'technical': ['not working', 'broken', 'issue', 'problem', 'error', 'bug', 'fault', 'connection'],
            'account': ['account', 'login', 'password', 'access', 'profile', 'credentials'],
            'service_changes': ['cancel', 'upgrade', 'downgrade', 'change', 'plan', 'switch'],
            'roaming': ['roaming', 'overseas', 'international', 'abroad', 'travel'],
            'data_usage': ['data', 'internet', 'wifi', 'slow', 'speed'],
            'complaints': ['complain', 'frustrated', 'angry', 'unacceptable', 'terrible'],
            'general_inquiry': ['question', 'information', 'help', 'assistance']
        }
        
        for contact_id, conv in conversations.items():
            # Analyze customer messages for categorization
            customer_text = ' '.join(conv['customer_messages']).lower()
            
            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in customer_text for keyword in keywords):
                    categories[category].append(contact_id)
                    categorized = True
                    break
            
            if not categorized:
                categories['general_inquiry'].append(contact_id)
        
        return categories
    
    def _analyze_temporal_patterns(self, conversations: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in the data"""
        timestamps = []
        durations = []
        
        for conv in conversations.values():
            try:
                # Parse timestamp
                dt = datetime.fromisoformat(conv['start_time'].replace('+10:00', ''))
                timestamps.append(dt)
                durations.append(conv['duration_seconds'])
            except:
                continue
        
        if not timestamps:
            return {}
        
        # Analyze patterns
        df = pd.DataFrame({
            'timestamp': timestamps,
            'duration': durations
        })
        
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        patterns = {
            'busiest_hours': df.groupby('hour').size().to_dict(),
            'busiest_days': df.groupby('day_of_week').size().to_dict(),
            'monthly_distribution': df.groupby('month').size().to_dict(),
            'avg_duration_by_hour': df.groupby('hour')['duration'].mean().to_dict(),
            'total_conversations': len(df),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            }
        }
        
        return patterns
    
    def _generate_statistics(self, conversations: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate overall statistics"""
        if not conversations:
            return {}
        
        total_convs = len(conversations)
        resolved_convs = sum(1 for conv in conversations.values() if conv['appears_resolved'])
        
        durations = [conv['duration_seconds'] for conv in conversations.values()]
        message_counts = [conv['total_messages'] for conv in conversations.values()]
        
        stats = {
            'total_conversations': total_convs,
            'resolved_conversations': resolved_convs,
            'resolution_rate': resolved_convs / total_convs if total_convs > 0 else 0,
            'avg_duration_seconds': sum(durations) / len(durations) if durations else 0,
            'avg_messages_per_conversation': sum(message_counts) / len(message_counts) if message_counts else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'min_messages': min(message_counts) if message_counts else 0,
            'max_messages': max(message_counts) if message_counts else 0
        }
        
        return stats
    
    def save_processed_data(self, processed_data: Dict[str, Any], output_path: str):
        """Save processed data to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(processed_data, f, indent=2, default=str)
            
            logger.info(f"Saved processed data to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            raise

def main():
    """Main preprocessing function"""
    preprocessor = ChatDataPreprocessor()
    
    # Process the data
    processed_data = preprocessor.load_and_preprocess('data/customer_service_chats.json')
    
    # Save processed data
    preprocessor.save_processed_data(processed_data, 'data/processed_conversations.json')
    
    # Print summary statistics
    stats = processed_data['statistics']
    print("\\n" + "="*50)
    print("DATA PREPROCESSING SUMMARY")
    print("="*50)
    print(f"Total Conversations: {stats['total_conversations']}")
    print(f"Resolution Rate: {stats['resolution_rate']:.2%}")
    print(f"Average Duration: {stats['avg_duration_seconds']:.1f} seconds")
    print(f"Average Messages per Conversation: {stats['avg_messages_per_conversation']:.1f}")
    
    print("\\nCategory Distribution:")
    for category, contact_ids in processed_data['categories'].items():
        print(f"  {category.replace('_', ' ').title()}: {len(contact_ids)} conversations")
    
    print("\\nTemporal Patterns:")
    patterns = processed_data['temporal_patterns']
    if 'busiest_hours' in patterns:
        busiest_hour = max(patterns['busiest_hours'], key=patterns['busiest_hours'].get)
        print(f"  Busiest Hour: {busiest_hour}:00 ({patterns['busiest_hours'][busiest_hour]} conversations)")
    
    print("\\n✅ Preprocessing complete!")

if __name__ == "__main__":
    main()
