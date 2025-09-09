#!/usr/bin/env python3
"""
Test Wikipedia integration for ski resort information
"""

import asyncio
from apis.wikipedia_resorts import get_resort_wikipedia_summary, search_wikipedia_resort_info

async def test_wikipedia_api():
    """Test Wikipedia API integration."""
    print("🧪 TESTING WIKIPEDIA INTEGRATION")
    print("=" * 50)

    # Test with a well-known ski resort
    test_resorts = [
        "Vail",
        "Aspen Mountain",
        "Whistler Blackcomb",
        "Chamonix",
        "Zermatt"
    ]

    for resort in test_resorts:
        print(f"\n🏔️ Testing: {resort}")
        print("-" * 30)

        try:
            result = await search_wikipedia_resort_info(resort, "")

            if result.get("success"):
                print("✅ SUCCESS: Found Wikipedia page")
                print(f"Title: {result.get('wikipedia_title', 'N/A')}")
                summary = result.get('summary', '')
                if summary:
                    # Show first 200 characters of summary
                    preview = summary[:200] + "..." if len(summary) > 200 else summary
                    print(f"Summary: {preview}")
                else:
                    print("Summary: (empty)")
                print(f"URL: {result.get('page_url', 'N/A')}")

            elif result.get("error") == "no_wikipedia_page":
                print("❌ No Wikipedia page found")
                print(f"Message: {result.get('message', 'N/A')}")

            else:
                print("❌ Error occurred")
                print(f"Error: {result.get('error', 'unknown')}")
                print(f"Message: {result.get('message', 'N/A')}")

        except Exception as e:
            print(f"❌ Exception: {e}")

    print("\n🎯 WIKIPEDIA INTEGRATION TEST COMPLETE")
    print("Expected: At least some resorts should have Wikipedia pages")

if __name__ == "__main__":
    asyncio.run(test_wikipedia_api())
