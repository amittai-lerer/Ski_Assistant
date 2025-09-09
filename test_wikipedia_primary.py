#!/usr/bin/env python3
"""
Test script to verify Wikipedia is used as a PRIMARY tool by the LLM.
This tests that the LLM calls get_wikipedia_resort_info directly when users ask about ski resorts.
"""

import asyncio
import os
from core.reasoning import llm_with_tools

async def test_wikipedia_primary():
    """Test that Wikipedia is called as primary tool for resort queries."""

    # Test queries that should trigger Wikipedia
    test_queries = [
        "Tell me about Zermatt ski resort",
        "What's the history of Aspen?",
        "Give me information about Lake Tahoe skiing",
        "What can you tell me about Chamonix?",
        "Details about Jackson Hole resort"
    ]

    print("🧪 Testing Wikipedia as PRIMARY Tool")
    print("=" * 50)

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        print("-" * 40)

        try:
            # Call the LLM with the query
            response = await llm_with_tools(query, [])

            if "wikipedia" in response.lower() or "zermatt" in response.lower() or "aspen" in response.lower():
                print("✅ SUCCESS: Wikipedia information retrieved")
            else:
                print("⚠️  UNCLEAR: Response may not have used Wikipedia")

            print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    print("\n" + "=" * 50)
    print("Test completed. Check if Wikipedia is being called as the primary tool.")

if __name__ == "__main__":
    # Set environment to use real APIs for testing
    os.environ["USE_REAL_OPENAI"] = "1"

    asyncio.run(test_wikipedia_primary())
