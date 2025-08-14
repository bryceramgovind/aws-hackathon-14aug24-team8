"""
Main entry point for the Call Center AI Agent
"""

import asyncio
import logging
from datetime import datetime, timedelta
from src.aws_agent import AWSCallCenterAgent
from src.bedrock_client import BedrockCallAnalyzer
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to demonstrate the AI agent"""
    
    # Initialize the agent
    agent = AWSCallCenterAgent()
    bedrock_analyzer = BedrockCallAnalyzer()
    
    # Example 1: Analyze a sample call
    sample_call_data = {
        'call_id': 'CALL-12345',
        'agent_name': 'John Doe',
        'customer_id': 'CUST-67890',
        'transcription': """
        Agent: Thank you for calling TechSupport. My name is John. How can I help you today?
        Customer: Hi John. I'm having issues with my internet connection. It's been very slow for the past week.
        Agent: I'm sorry to hear you're experiencing slow internet speeds. Let me help you with that. 
        Can you tell me which plan you're currently on?
        Customer: I have the 100 Mbps plan, but I'm only getting about 10 Mbps.
        Agent: That's definitely not right. Let me run some diagnostics on your connection...
        """
    }
    
    # Analyze the call
    logger.info("Analyzing sample call...")
    analysis_results = await agent.analyze_call(sample_call_data)
    
    # Pretty print results
    print("\n=== Call Analysis Results ===")
    print(json.dumps(analysis_results, indent=2))
    
    # Generate coaching insights
    logger.info("Generating coaching insights...")
    coaching = await bedrock_analyzer.generate_coaching_insights(
        sample_call_data['transcription'],
        sample_call_data['agent_name']
    )
    
    print("\n=== Coaching Insights ===")
    print(json.dumps(coaching, indent=2))
    
    # Extract customer intent
    logger.info("Extracting customer intent...")
    intent = await bedrock_analyzer.extract_customer_intent(
        sample_call_data['transcription']
    )
    
    print("\n=== Customer Intent Analysis ===")
    print(json.dumps(intent, indent=2))

if __name__ == "__main__":
    asyncio.run(main())