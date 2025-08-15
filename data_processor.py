import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def load_and_process_chat_data(file_path):
    """Load and process chat data into analytics format"""
    
    # Load raw chat data
    with open(file_path, 'r') as f:
        raw_data = json.load(f)
    
    # Convert to DataFrame
    df = pd.DataFrame(raw_data)
    
    # Process conversations by contact_id
    conversations = []
    topics_list = ['Billing', 'Technical Support', 'Roaming', 'Account Management', 'Cancellation', 
                   'Service Issues', 'Data Usage', 'Payment', 'International Plans', 'Device Support']
    
    agents = ['Jessica', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Lisa', 'Robert', 'Anna', 'Tom']
    
    for contact_id in df['contact_id'].unique():
        conv_data = df[df['contact_id'] == contact_id].copy()
        conv_data = conv_data.sort_values('message_number')
        
        # Extract conversation details
        start_time = pd.to_datetime(conv_data['start_date'].iloc[0])
        end_time = pd.to_datetime(conv_data['end_date'].iloc[0])
        duration = (end_time - start_time).total_seconds() / 60
        
        # Get messages
        customer_messages = conv_data[conv_data['chat_user_type'] == 'customer']['chat_text'].tolist()
        agent_messages = conv_data[conv_data['chat_user_type'] == 'agent']['chat_text'].tolist()
        
        # Simulate analytics (in real scenario, these would come from AI models)
        full_conversation = ' '.join(customer_messages + agent_messages).lower()
        
        # Determine primary topic based on keywords
        primary_topic = 'General'
        for topic in topics_list:
            keywords = {
                'Billing': ['bill', 'charge', 'payment', 'cost', 'invoice'],
                'Technical Support': ['technical', 'not working', 'problem', 'issue', 'broken'],
                'Roaming': ['roaming', 'travel', 'international', 'overseas'],
                'Account Management': ['account', 'profile', 'password', 'login'],
                'Cancellation': ['cancel', 'close', 'terminate', 'end service'],
                'Service Issues': ['service', 'network', 'signal', 'coverage'],
                'Data Usage': ['data', 'internet', 'usage', 'limit'],
                'Payment': ['payment', 'pay', 'credit card', 'bank'],
                'International Plans': ['international', 'global', 'worldwide'],
                'Device Support': ['phone', 'device', 'mobile', 'smartphone']
            }
            
            if any(keyword in full_conversation for keyword in keywords.get(topic, [])):
                primary_topic = topic
                break
        
        # Generate simulated analytics
        # Sentiment: -1 to 1 (based on conversation tone)
        sentiment_indicators = ['thank', 'great', 'good', 'excellent', 'satisfied']
        negative_indicators = ['frustrated', 'angry', 'terrible', 'worst', 'cancel']
        
        sentiment_score = 0.0
        for indicator in sentiment_indicators:
            if indicator in full_conversation:
                sentiment_score += 0.3
        for indicator in negative_indicators:
            if indicator in full_conversation:
                sentiment_score -= 0.4
        
        sentiment_score = max(-1.0, min(1.0, sentiment_score + random.uniform(-0.2, 0.2)))
        
        # Empathy score (0 to 1) - based on agent responses
        empathy_score = random.uniform(0.6, 1.0) if len(agent_messages) > 0 else 0.5
        
        # Outcome determination
        resolution_keywords = ['resolved', 'solved', 'fixed', 'helped', 'thank you']
        escalation_keywords = ['manager', 'supervisor', 'escalate', 'complaint']
        
        if any(keyword in full_conversation for keyword in escalation_keywords):
            outcome = 'escalated'
        elif any(keyword in full_conversation for keyword in resolution_keywords) or sentiment_score > 0.3:
            outcome = 'successful'
        else:
            outcome = 'unsuccessful'
        
        # Create conversation record
        conversation = {
            'conversation_id': contact_id,
            'contact_id': contact_id,
            'start_date': start_time,
            'end_date': end_time,
            'duration_minutes': duration,
            'agent_id': f"agent_{hash(contact_id) % 10}",
            'agent_name': agents[hash(contact_id) % len(agents)],
            'customer_id': conv_data['chat_user_id'].iloc[0],
            'outcome': outcome,
            'outcome_confidence': random.uniform(0.7, 0.95),
            'primary_topic': primary_topic,
            'secondary_topics': random.sample([t for t in topics_list if t != primary_topic], 
                                            random.randint(0, 2)),
            'sentiment_score': sentiment_score,
            'empathy_score': empathy_score,
            'message_count': len(conv_data),
            'resolution_time_minutes': duration
        }
        
        conversations.append(conversation)
    
    return pd.DataFrame(conversations)

def generate_daily_aggregations(conversations_df):
    """Generate daily aggregation data"""
    daily_data = []
    
    # Group by date
    conversations_df['date'] = conversations_df['start_date'].dt.date
    
    for date in conversations_df['date'].unique():
        daily_convs = conversations_df[conversations_df['date'] == date]
        
        daily_record = {
            'date': date,
            'total_conversations': len(daily_convs),
            'successful_conversations': len(daily_convs[daily_convs['outcome'] == 'successful']),
            'avg_sentiment': daily_convs['sentiment_score'].mean(),
            'avg_empathy': daily_convs['empathy_score'].mean(),
            'top_topics': daily_convs['primary_topic'].value_counts().head(3).index.tolist(),
            'avg_duration': daily_convs['duration_minutes'].mean()
        }
        
        daily_data.append(daily_record)
    
    return pd.DataFrame(daily_data)

if __name__ == "__main__":
    # Process the data
    conversations_df = load_and_process_chat_data('data/customer_service_chats.json')
    daily_df = generate_daily_aggregations(conversations_df)
    
    # Save processed data
    conversations_df.to_csv('data/processed_conversations.csv', index=False)
    daily_df.to_csv('data/daily_aggregations.csv', index=False)
    
    print(f"Processed {len(conversations_df)} conversations")
    print(f"Generated {len(daily_df)} daily aggregation records")