"""
Demo script for the enhanced RAG-powered Call Center AI Agent
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from aws_agent import AWSCallCenterAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_rag_capabilities():
    """Demonstrate RAG capabilities of the Call Center AI Agent"""
    
    print("🤖 Initializing Enhanced Call Center AI Agent with RAG...")
    
    try:
        # Initialize agent
        agent = AWSCallCenterAgent()
        
        # Initialize knowledge base
        print("📚 Building knowledge base from customer service chats...")
        await agent.initialize_knowledge_base()
        
        print("✅ Knowledge base initialized successfully!\n")
        
        # Demo 1: Analyze a sample call with RAG
        print("=" * 60)
        print("DEMO 1: Enhanced Call Analysis with RAG")
        print("=" * 60)
        
        sample_call = {
            'call_id': 'demo_001',
            'transcription': "Hi, I just got my bill and there's a $50 charge I don't recognize. My usual bill is around $75 but this month it's $125. Can someone help me understand what's going on?",
            'customer_id': 'cust_12345',
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"🗣️  Customer says: {sample_call['transcription']}\n")
        
        # Analyze with RAG
        results = await agent.analyze_call_with_rag(sample_call)
        
        print("📊 Analysis Results:")
        print(f"   • Issue Category: {results['rag_insights']['issue_category']}")
        print(f"   • Similar Cases Found: {len(results['rag_insights']['similar_conversations'])}")
        print(f"   • Resolution Suggestions: {len(results['rag_insights']['resolution_suggestions'])}")
        
        if results['rag_insights']['similar_conversations']:
            print(f"   • Top Similar Case Confidence: {results['rag_insights']['similar_conversations'][0]['similarity_score']:.3f}")
        
        print(f"   • Summary: {results['analyses'].get('summary', 'N/A')[:100]}...")
        print(f"   • Sentiment: {results['analyses'].get('sentiment', {}).get('overall', 'N/A')}\n")
        
        # Demo 2: Real-time agent assistance
        print("=" * 60)
        print("DEMO 2: Real-time Agent Assistance")
        print("=" * 60)
        
        conversation_history = [
            {'text': "Hi, I need help with my account", 'user_type': 'customer', 'timestamp': 0},
            {'text': "Hello! I'm here to help. What seems to be the issue?", 'user_type': 'agent', 'timestamp': 30}
        ]
        
        customer_message = "I can't access my online account. I keep getting an error message saying my password is incorrect, but I'm sure it's right."
        
        print(f"🗣️  Customer says: {customer_message}\n")
        
        assistance = await agent.provide_agent_assistance(
            customer_message, 
            conversation_history, 
            agent_id="agent_demo"
        )
        
        print("🎯 Agent Assistance:")
        print(f"   • Urgency Level: {assistance['urgency_level']}")
        print(f"   • Sentiment: {assistance['sentiment_analysis']['sentiment']}")
        print(f"   • Confidence Score: {assistance['confidence_score']:.3f}")
        print(f"   • Suggested Response: {assistance['enhanced_response'][:150]}...")
        
        print("\\n   📋 Recommended Actions:")
        for action in assistance['recommended_actions']:
            print(f"      - {action}")
        
        print(f"\\n   💡 Similar Cases: {len(assistance['similar_cases'])} found")
        print(f"   🔧 Resolution Suggestions: {len(assistance['resolution_suggestions'])} available\\n")
        
        # Demo 3: Performance insights
        print("=" * 60)
        print("DEMO 3: Performance Analytics")
        print("=" * 60)
        
        insights = await agent.generate_performance_insights()
        
        print("📈 Performance Insights:")
        print(f"   • Categories Analyzed: {insights['overall_metrics']['total_categories']}")
        print(f"   • Average Resolution Rate: {insights['overall_metrics']['avg_resolution_rate']:.2%}")
        print(f"   • Categories Needing Attention: {insights['overall_metrics']['categories_needing_attention']}")
        
        print("\\n   📊 Category Breakdown:")
        for category, stats in list(insights['category_insights'].items())[:5]:
            print(f"      {category.title()}: {stats['resolution_rate']:.1%} resolution rate, {stats['total_cases']} cases")
        
        if insights['recommendations']:
            print("\\n   ⚠️  Recommendations:")
            for rec in insights['recommendations'][:3]:
                print(f"      [{rec['priority'].upper()}] {rec['recommendation']}")
        
        print("\\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("=" * 60)
        
        # Show knowledge base stats
        print("\\n📚 Knowledge Base Statistics:")
        total_patterns = sum(len(patterns) for patterns in agent.rag_system.issue_patterns.values())
        total_templates = sum(len(templates) for templates in agent.rag_system.resolution_templates.values())
        
        print(f"   • Issue Patterns: {total_patterns}")
        print(f"   • Resolution Templates: {total_templates}")
        print(f"   • Conversation Index: {len(agent.rag_system.conversation_metadata)} entries")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

def demo_query_examples():
    """Show example queries that the RAG system can handle"""
    
    print("\\n" + "=" * 60)
    print("RAG SYSTEM CAPABILITIES")
    print("=" * 60)
    
    examples = [
        {
            "scenario": "Customer asks about billing charges",
            "query": "There's a charge on my bill I don't understand",
            "rag_helps": "Finds similar billing disputes and their resolutions"
        },
        {
            "scenario": "Technical support request",
            "query": "My internet isn't working properly",
            "rag_helps": "Retrieves successful troubleshooting steps from past cases"
        },
        {
            "scenario": "Account access issues",
            "query": "I can't log into my account",
            "rag_helps": "Provides account recovery procedures that worked before"
        },
        {
            "scenario": "Service cancellation",
            "query": "I want to cancel my service",
            "rag_helps": "Shows retention strategies and proper cancellation steps"
        },
        {
            "scenario": "Roaming charges complaint",
            "query": "I got huge roaming charges while traveling",
            "rag_helps": "Finds similar cases and resolution options"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['scenario']}")
        print(f"   Customer: \"{example['query']}\"")
        print(f"   RAG Helps: {example['rag_helps']}\\n")

async def main():
    """Main demo function"""
    print("🚀 Enhanced Call Center AI with RAG - Demo")
    print("=" * 60)
    
    # Show capabilities overview
    demo_query_examples()
    
    # Run interactive demo
    response = input("\\nWould you like to run the interactive demo? (y/n): ")
    if response.lower().startswith('y'):
        await demo_rag_capabilities()
    else:
        print("Demo skipped. You can run it anytime by answering 'y' above.")

if __name__ == "__main__":
    asyncio.run(main())
