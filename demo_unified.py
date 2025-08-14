"""
Demo for the Unified Call Center AI Agent
This replaces demo_rag.py and shows the simplified architecture
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from unified_ai_agent import UnifiedCallCenterAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_unified_agent():
    """Demonstrate the unified agent capabilities"""
    
    print("🤖 Initializing Unified Call Center AI Agent...")
    
    try:
        # Initialize unified agent
        agent = UnifiedCallCenterAI()
        
        # Initialize knowledge base
        print("📚 Building knowledge base from customer service chats...")
        await agent.initialize_knowledge_base()
        
        print("✅ Unified agent initialized successfully!\n")
        
        # Demo 1: Analyze a conversation
        print("=" * 60)
        print("DEMO 1: Comprehensive Conversation Analysis")
        print("=" * 60)
        
        sample_conversation = {
            'conversation_id': 'unified_demo_001',
            'transcription': """
            Customer: Hi, I just got my bill and there's a $50 charge I don't recognize. My usual bill is around $75 but this month it's $125.
            Agent: Hello! I'm Sarah from customer service. I'd be happy to help you understand the charges on your bill.
            Customer: Thank you. Can you explain what this extra charge is for?
            Agent: Let me pull up your account. I can see the additional charge is for data overage. You used 2GB over your plan limit.
            Customer: Oh, I didn't realize I went over. How can I avoid this in the future?
            Agent: I can upgrade you to a larger data plan or set up usage alerts. Which would you prefer?
            Customer: The alerts sound good. Can you set that up?
            Agent: Absolutely! I've set up alerts at 75% and 90% of your data limit. You'll get text notifications.
            Customer: Perfect, thank you so much for your help!
            Agent: You're welcome! Is there anything else I can help you with today?
            Customer: No, that's everything. Thanks again!
            """,
            'customer_id': 'cust_demo_001'
        }
        
        print(f"🗣️  Analyzing conversation...")
        
        # Analyze with unified agent
        results = await agent.analyze_conversation(sample_conversation)
        
        print("📊 Analysis Results:")
        if 'summary' in results['analyses']:
            print(f"   📝 Summary: {results['analyses']['summary'][:150]}...")
        
        if 'sentiment' in results['analyses']:
            sentiment = results['analyses']['sentiment']
            print(f"   😊 Customer Sentiment: {sentiment.get('overall', 'N/A')}")
        
        if 'rag_insights' in results['analyses']:
            rag = results['analyses']['rag_insights']
            print(f"   🎯 Issue Category: {rag.get('issue_category', 'N/A')}")
            print(f"   🔍 Similar Cases: {len(rag.get('similar_conversations', []))}")
            print(f"   💡 Suggestions: {len(rag.get('resolution_suggestions', []))}")
        
        print()
        
        # Demo 2: Real-time agent assistance
        print("=" * 60)
        print("DEMO 2: Real-time Agent Assistance")
        print("=" * 60)
        
        customer_message = "I'm really frustrated! My internet has been down for 3 hours and I work from home. This is unacceptable!"
        
        print(f"🗣️  Customer says: {customer_message}\n")
        
        assistance = await agent.provide_agent_assistance(customer_message)
        
        print("🎯 Agent Assistance:")
        print(f"   ⚠️  Urgency Level: {assistance['urgency_level']}")
        print(f"   😊 Sentiment: {assistance['sentiment']['sentiment']}")
        print(f"   💬 Suggested Response: {assistance['enhanced_response'][:200]}...")
        
        print("\\n   📋 Recommended Actions:")
        for action in assistance['recommended_actions']:
            print(f"      - {action}")
        
        if assistance.get('rag_suggestions', {}).get('similar_cases'):
            print(f"\\n   🔍 Found {len(assistance['rag_suggestions']['similar_cases'])} similar cases")
        
        print()
        
        # Demo 3: Performance insights
        print("=" * 60)
        print("DEMO 3: Performance Analytics")
        print("=" * 60)
        
        insights = await agent.generate_performance_insights()
        
        print("📈 Performance Insights:")
        if 'summary' in insights:
            summary = insights['summary']
            print(f"   📊 Categories Analyzed: {summary.get('total_categories', 0)}")
            print(f"   ✅ Average Resolution Rate: {summary.get('avg_resolution_rate', 0):.2%}")
        
        if 'category_insights' in insights:
            print("\\n   📋 Category Breakdown:")
            for category, stats in list(insights['category_insights'].items())[:5]:
                rate = stats.get('resolution_rate', 0)
                cases = stats.get('total_cases', 0)
                print(f"      {category.title()}: {rate:.1%} resolution rate ({cases} cases)")
        
        if insights.get('recommendations'):
            print("\\n   💡 Recommendations:")
            for rec in insights['recommendations'][:3]:
                print(f"      - {rec['recommendation']}")
        
        print("\\n" + "=" * 60)
        print("🎉 Unified Agent Demo completed successfully!")
        print("=" * 60)
        
        # Show system capabilities
        print("\\n🚀 Unified Agent Capabilities:")
        capabilities = agent.capabilities
        for cap in capabilities:
            print(f"   ✅ {cap.replace('_', ' ').title()}")
        
        print(f"\\n🧠 ML Components: {'Available' if agent.ml_ready else 'Not Available'}")
        print(f"📚 Knowledge Base: {'Loaded' if agent.knowledge_base_loaded else 'Not Loaded'}")
        
        if agent.knowledge_base_loaded:
            total_patterns = sum(len(patterns) for patterns in agent.issue_patterns.values())
            total_templates = sum(len(templates) for templates in agent.resolution_templates.values())
            print(f"   📊 Issue Patterns: {total_patterns}")
            print(f"   🔧 Resolution Templates: {total_templates}")
            if agent.conversation_metadata:
                print(f"   💬 Indexed Conversations: {len(agent.conversation_metadata)}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

def show_architecture_comparison():
    """Show the architectural improvements"""
    
    print("\\n" + "=" * 80)
    print("ARCHITECTURE COMPARISON: Before vs After")
    print("=" * 80)
    
    print("\\n📦 BEFORE (Multiple Components):")
    print("   ├── aws_agent.py           (Main orchestrator)")
    print("   ├── bedrock_client.py      (Bedrock operations)")
    print("   ├── rag_handler.py         (RAG functionality)")
    print("   ├── s3_handler.py          (S3 operations)")
    print("   └── Multiple dependencies and duplicated code")
    
    print("\\n📦 AFTER (Unified Component):")
    print("   └── unified_ai_agent.py    (Everything in one optimized class)")
    print("       ├── AWS service integration")
    print("       ├── RAG capabilities")
    print("       ├── Conversation analysis")
    print("       ├── Agent assistance")
    print("       ├── Performance analytics")
    print("       └── Knowledge base management")
    
    print("\\n✨ BENEFITS:")
    print("   ✅ Reduced complexity - One class instead of multiple")
    print("   ✅ No duplicate AWS clients")
    print("   ✅ Streamlined dependencies")
    print("   ✅ Better error handling")
    print("   ✅ Consistent API")
    print("   ✅ Easier maintenance")
    print("   ✅ Optional ML components (graceful degradation)")
    
    print("\\n🔄 MIGRATION:")
    print("   • Replace: AWSCallCenterAgent → UnifiedCallCenterAI")
    print("   • All methods have similar signatures")
    print("   • Configuration remains the same")
    print("   • Knowledge base format compatible")

async def main():
    """Main demo function"""
    print("🚀 Unified Call Center AI - Simplified Architecture Demo")
    print("=" * 80)
    
    # Show architecture improvements
    show_architecture_comparison()
    
    # Ask user if they want to run the demo
    print("\\n" + "=" * 80)
    response = input("Would you like to run the unified agent demo? (y/n): ")
    if response.lower().startswith('y'):
        await demo_unified_agent()
    else:
        print("\\n📚 You can run the demo anytime with: python demo_unified.py")
        print("\\n💡 To use the unified agent in your code:")
        print("   from src.unified_ai_agent import UnifiedCallCenterAI")
        print("   agent = UnifiedCallCenterAI()")
        print("   await agent.initialize_knowledge_base()")
        print("   results = await agent.analyze_conversation(conversation_data)")

if __name__ == "__main__":
    asyncio.run(main())
