#!/usr/bin/env python3
"""
Demo of SkiAPI Integration with SkiTrip Assistant.

This script demonstrates how the SkiAPI integrates with the LLM
to provide detailed ski resort information.
"""

import asyncio
import os
from core.orchestrator import run

async def demo_skiapi_with_llm():
    """Demo the SkiAPI integration with the LLM."""
    print("🎿 SkiTrip Assistant - SkiAPI Integration Demo")
    print("=" * 60)

    # Check if RAPIDAPI_KEY is available
    rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
    if not rapidapi_key:
        print("❌ RAPIDAPI_KEY not found in environment variables")
        print("Please add your RapidAPI key to the .env file:")
        print("RAPIDAPI_KEY=your_rapidapi_key_here")
        print("\nThen subscribe to SkiAPI at: https://rapidapi.com/skapi/api/ski-api")
        return

    print("✅ RAPIDAPI_KEY found")

    # Demo scenarios
    test_scenarios = [
        "Tell me about Vail ski resort",
        "What are the details for Aspen Mountain?",
        "Give me information about Whistler Blackcomb",
        "What's the snow report for Park City?"
    ]

    print("\n🧪 Testing SkiAPI integration with LLM...")
    print("Note: These queries will attempt to use the SkiAPI tool")
    print("If you haven't subscribed to SkiAPI yet, they'll use fallback info")
    print()

    for i, query in enumerate(test_scenarios, 1):
        print(f"🔹 Query {i}: \"{query}\"")
        print("-" * 40)

        try:
            result = await run(query, {})
            # Clean up result for display
            result = result.replace('\n', ' ').strip()
            if len(result) > 200:
                result = result[:200] + '...'
            print(f"Assistant: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("🎉 Demo completed!")
    print("\n📋 What this demonstrates:")
    print("✅ SkiAPI tool integration with OpenAI")
    print("✅ Fallback responses when API unavailable")
    print("✅ Ski-focused conversation handling")
    print("✅ Detailed resort information retrieval")

    print("\n🚀 To enable full SkiAPI functionality:")
    print("1. Go to: https://rapidapi.com/skapi/api/ski-api")
    print("2. Subscribe to a plan (free or paid)")
    print("3. Run this demo again to see real SkiAPI data!")

if __name__ == "__main__":
    asyncio.run(demo_skiapi_with_llm())
