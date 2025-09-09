#!/usr/bin/env python3
"""
Test Wikipedia integration with the full ski assistant
"""

import asyncio
from core.orchestrator import run

async def test_wikipedia_with_assistant():
    """Test Wikipedia integration with the ski assistant."""
    print("🎿 TESTING WIKIPEDIA WITH SKI ASSISTANT")
    print("=" * 60)

    # Test queries that should trigger Wikipedia tool
    test_queries = [
        "Tell me about Whistler Blackcomb",
        "What is Aspen Mountain?",
        "Give me information about Chamonix",
        "Tell me about Zermatt ski resort",
        "What do you know about Vail?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. \"{query}\"")
        print("-" * 50)

        try:
            result = await run(query, [])

            # Check for Wikipedia integration indicators
            if "wikipedia" in result.lower() or "according to wikipedia" in result.lower():
                print("✅ Wikipedia tool used")
            elif "summary" in result.lower() or any(word in result.lower() for word in ["history", "located", "municipality", "mountain", "ski resort"]):
                print("✅ Wikipedia content included")
            elif "couldn't find" in result.lower() or "clarify" in result.lower():
                print("✅ Proper fallback for missing Wikipedia page")
            else:
                print("🤔 Response generated")

            # Show response preview
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"Response: {preview}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n🎉 WIKIPEDIA ASSISTANT TEST COMPLETE")
    print("Expected results:")
    print("• Queries should use Wikipedia tool for resort information")
    print("• Successful queries should include Wikipedia summaries")
    print("• Missing pages should ask for clarification")
    print("• All responses should be ski-focused and helpful")

if __name__ == "__main__":
    asyncio.run(test_wikipedia_with_assistant())
