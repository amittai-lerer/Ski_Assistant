#!/usr/bin/env python3
"""Basic test script to verify the application works."""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.orchestrator import run
from config.settings import OPENAI_API_KEY, FOURSQUARE_API_KEY

async def test_basic_flow():
    """Test the basic orchestration flow."""
    print("🧪 Testing SkiTrip Assistant...")
    
    # Check API keys
    print(f"OpenAI API Key: {'✅ Set' if OPENAI_API_KEY else '❌ Missing'}")
    print(f"Geoapify API Key: {'✅ Set' if GEOAPIFY_API_KEY else '❌ Missing'}")
    
    # Test with mock data
    ctx = {
        "region": "Lake Tahoe",
        "dates": "2025-12-20..2025-12-22",
        "ability": "intermediate"
    }
    
    try:
        print("\n🚀 Running orchestration...")
        result = await run("", ctx)
        print("✅ Success!")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_flow())
    sys.exit(0 if success else 1)
