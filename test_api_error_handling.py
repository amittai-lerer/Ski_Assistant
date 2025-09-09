#!/usr/bin/env python3
"""
Test API Error Handling for SkiAPI

Tests the improved error messages for rate limits and other API issues.
"""

import asyncio
import os
from core.orchestrator import run

async def test_api_error_handling():
    """Test various API error scenarios."""
    print("🧪 TESTING API ERROR HANDLING")
    print("=" * 50)

    # Test queries that should trigger SkiAPI and potentially hit rate limits
    test_queries = [
        "Tell me about Vail ski resort",
        "What are the details for Aspen Mountain?",
        "Give me information about Whistler Blackcomb",
        "Show me details for 49 Degrees North resort"
    ]

    print("Testing SkiAPI error handling...")
    print("Note: If you've exceeded your daily limit, you'll see informative error messages")
    print()

    for i, query in enumerate(test_queries, 1):
        print(f"{i}. \"{query}\"")
        print("-" * 40)

        try:
            result = await run(query, [])
            print(f"Response: {result[:200]}..." if len(result) > 200 else f"Response: {result}")

            # Check for specific error indicators
            if "quota_exceeded" in result or "daily request limit" in result.lower():
                print("✅ SUCCESS: Clear quota exceeded message!")
            elif "api_quota_exceeded" in result:
                print("✅ SUCCESS: API quota error properly handled!")
            elif "authentication failed" in result.lower():
                print("✅ SUCCESS: Auth error properly handled!")
            elif "subscription required" in result.lower():
                print("✅ SUCCESS: Subscription error properly handled!")
            elif "SkiAPI" in result and ("error" in result or "HTTP" in result):
                print("🔍 SkiAPI error detected - checking message quality...")

        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("🎯 ERROR HANDLING TEST COMPLETE")
    print("Expected results:")
    print("• If quota exceeded: Clear message about daily limits")
    print("• If auth failed: Clear message about RAPIDAPI_KEY")
    print("• If subscription: Clear message about subscription needed")
    print("• No hardcoded answers - only informative error messages")

if __name__ == "__main__":
    asyncio.run(test_api_error_handling())
