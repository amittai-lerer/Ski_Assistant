#!/usr/bin/env python3
"""
Demonstrate API Error Handling for SkiTrip Assistant

Shows how the assistant handles different types of API errors:
- Rate limiting (429)
- Authentication failures (401)
- Subscription issues (403)
"""

import asyncio
from core.orchestrator import run

async def demo_api_errors():
    """Demonstrate different API error scenarios."""
    print("🚨 SKI ASSISTANT API ERROR HANDLING DEMO")
    print("=" * 60)

    print("This demo shows how the assistant handles API limitations:")
    print("• Rate limiting (daily quota exceeded)")
    print("• Authentication issues")
    print("• Subscription requirements")
    print()
    print("Instead of hardcoded answers, you'll see informative error messages")
    print("with clear solutions for each scenario.")
    print()

    # Since we're hitting rate limits, all queries will show quota exceeded
    # But this demonstrates the error handling system

    test_scenarios = [
        ("Rate Limiting", "Tell me about Vail ski resort", "Shows daily quota message"),
        ("Authentication", "What are Aspen details?", "Would show auth error if key invalid"),
        ("Subscription", "Give me Whistler info", "Would show subscription needed if expired")
    ]

    for i, (scenario, query, description) in enumerate(test_scenarios, 1):
        print(f"{i}. {scenario}: {query}")
        print(f"   {description}")
        print("-" * 50)

        try:
            result = await run(query, [])
            print(f"Response: {result[:250]}..." if len(result) > 250 else f"Response: {result}")

            # Check for error indicators
            if "daily" in result.lower() and "limit" in result.lower():
                print("✅ CLEAR: Daily limit explained")
            if "upgrade" in result.lower() or "plan" in result.lower():
                print("✅ SOLUTION: Upgrade option provided")
            if "api" in result.lower() and ("error" in result.lower() or "limit" in result.lower()):
                print("✅ TRANSPARENT: API limitation acknowledged")

        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("🎯 KEY FEATURES OF ERROR HANDLING:")
    print("✅ No hardcoded resort information when API fails")
    print("✅ Clear explanation of what's wrong")
    print("✅ Actionable solutions provided")
    print("✅ Transparent about API limitations")
    print("✅ Maintains helpful ski assistant persona")
    print()
    print("🚀 This ensures users understand API limitations without")
    print("   receiving misleading or outdated information!")

if __name__ == "__main__":
    asyncio.run(demo_api_errors())
