#!/usr/bin/env python3
"""
Test specific quota exceeded messages for SkiAPI
"""

import asyncio
from core.orchestrator import run

async def test_quota_messages():
    """Test that quota exceeded messages are clear and informative."""
    print("🎯 TESTING QUOTA EXCEEDED MESSAGES")
    print("=" * 50)

    query = "Tell me about Vail ski resort"

    print(f"Query: \"{query}\"")
    print("Expected: Clear message about daily limit, no hardcoded answers")
    print("-" * 50)

    result = await run(query, [])

    print(f"Response: {result}")

    # Check for key elements of good error messaging
    checks = {
        "mentions_daily_limit": "daily" in result.lower() or "limit" in result.lower(),
        "mentions_waiting": "wait" in result.lower() or "tomorrow" in result.lower() or "reset" in result.lower(),
        "mentions_upgrade": "upgrade" in result.lower() or "paid" in result.lower() or "plan" in result.lower(),
        "explains_situation": "request limit" in result.lower() or "quota" in result.lower(),
        "no_hardcoded_answers": "vail is" not in result.lower()[:50]  # Shouldn't start with hardcoded info
    }

    print("\n📋 MESSAGE QUALITY CHECK:")
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name.replace('_', ' ').title()}: {passed}")

    total_passed = sum(checks.values())
    print(f"\n📊 Score: {total_passed}/{len(checks)} checks passed")

    if total_passed >= 3:
        print("🎉 SUCCESS: Good error message quality!")
    else:
        print("⚠️  Could be improved")

if __name__ == "__main__":
    asyncio.run(test_quota_messages())
