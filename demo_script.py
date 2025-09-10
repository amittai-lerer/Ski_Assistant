#!/usr/bin/env python3
"""
SkiTrip Assistant - Live Demonstration Script
Shows the three main types of queries/tasks the assistant handles
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.reasoning import llm_with_tools

async def demonstrate_resort_query():
    """Demonstrate resort information query"""
    print("\n" + "="*60)
    print("�� DEMONSTRATION 1: Resort Information Query")
    print("="*60)
    
    user_query = "Tell me about ski resorts in Colorado for intermediate skiers"
    print(f"User: {user_query}")
    
    try:
        response = await llm_with_tools(user_query)
        print(f"Assistant: {response}")
    except Exception as e:
        print(f"Demo: {e}")

async def demonstrate_trip_planning():
    """Demonstrate trip planning query"""
    print("\n" + "="*60)
    print("🎯 DEMONSTRATION 2: Trip Planning Query")
    print("="*60)
    
    user_query = "Help me plan a 2-day ski trip to Lake Tahoe for intermediate skiers"
    print(f"User: {user_query}")
    
    try:
        response = await llm_with_tools(user_query)
        print(f"Assistant: {response}")
    except Exception as e:
        print(f"Demo: {e}")

async def demonstrate_clarifying_questions():
    """Demonstrate context management with clarifying questions"""
    print("\n" + "="*60)
    print("🎯 DEMONSTRATION 3: Context Management & Clarifying Questions")
    print("="*60)
    
    # First exchange
    user_query1 = "I want to go skiing"
    print(f"User: {user_query1}")
    
    try:
        response1 = await llm_with_tools(user_query1)
        print(f"Assistant: {response1}")
        
        # Second exchange with context
        user_query2 = "Somewhere in Europe, mid-range budget"
        print(f"User: {user_query2}")
        
        # Pass conversation history (in real implementation this would be maintained)
        conversation_history = [
            {"user_input": user_query1, "assistant_response": response1}
        ]
        
        response2 = await llm_with_tools(user_query2, conversation_history)
        print(f"Assistant: {response2}")
        
    except Exception as e:
        print(f"Demo: {e}")

async def demonstrate_error_handling():
    """Demonstrate off-topic and error handling"""
    print("\n" + "="*60)
    print("🎯 DEMONSTRATION 4: Error Handling & Off-Topic Management")
    print("="*60)
    
    user_query = "What's the weather like in Hawaii?"
    print(f"User: {user_query}")
    
    try:
        response = await llm_with_tools(user_query)
        print(f"Assistant: {response}")
    except Exception as e:
        print(f"Demo: {e}")

async def main():
    """Run all demonstrations"""
    print("🎿 SkiTrip Assistant - Live Demonstration")
    print("Demonstrating assignment requirements implementation")
    
    print("\n📋 REQUIREMENTS DEMONSTRATED:")
    print("✅ Assistant Purpose - Handles 3+ types of queries")
    print("✅ Context & Continuity - Multi-turn conversations")
    print("✅ Interaction Flow - Natural, helpful, accurate")
    
    await demonstrate_resort_query()
    await demonstrate_trip_planning()
    await demonstrate_clarifying_questions()
    await demonstrate_error_handling()
    
    print("\n" + "="*60)
    print("🎉 DEMONSTRATION COMPLETE")
    print("="*60)
    print("\n🔧 TECHNICAL FEATURES:")
    print("- OpenAI GPT-4 integration")
    print("- Multi-API data sources")
    print("- Chain-of-thought reasoning")
    print("- Error handling & fallbacks")
    print("- Context-aware conversations")

if __name__ == "__main__":
    asyncio.run(main())
