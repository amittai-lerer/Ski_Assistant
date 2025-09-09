#!/usr/bin/env python3
"""
Final test to verify SkiAPI is working with the ski assistant
"""

import asyncio
import os
from dotenv import load_dotenv
from core.orchestrator import run

load_dotenv()

async def test_ski_assistant_with_skiapi():
    """Test the ski assistant with SkiAPI integration."""
    print("🎿 FINAL SKI ASSISTANT TEST WITH SKIAPI")
    print("=" * 60)

    # Check if RAPIDAPI_KEY is set
    rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
    if not rapidapi_key or rapidapi_key == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not set in .env file!")
        print("Please add your RapidAPI key first.")
        return

    print("✅ RAPIDAPI_KEY found")
    print("🧪 Testing ski assistant with SkiAPI integration...")
    print()

    test_queries = [
        "Tell me about Vail ski resort",
        "What are the details for Aspen Mountain?",
        "Give me information about Whistler Blackcomb",
        "What's the snow report for Park City?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Testing: '{query}'")
        print("-" * 50)

        try:
            result = await run(query, {})
            # Check if it used SkiAPI or fallback
            if "SkiAPI HTTP error" in result:
                print("❌ SkiAPI failed - check your key/subscription")
                print(f"Response: {result[:100]}...")
            else:
                print("✅ Working! Response received")
                print(f"Response: {result[:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("🎉 Test complete!")
    print("If you see ✅ Working messages, SkiAPI is integrated successfully!")

if __name__ == "__main__":
    asyncio.run(test_ski_assistant_with_skiapi())