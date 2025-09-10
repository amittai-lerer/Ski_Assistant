"""SkiTrip Assistant - A conversational CLI for planning ski vacations."""

"""CLI application module."""
# Empty init file - no imports needed here

"""Core business logic module."""

"""External API integrations."""

"""Data models and schemas."""

"""Deterministic ranking algorithms."""

"""User interface rendering."""

"""Configuration management."""

"""Test modules."""

"""Basic test script to verify the application works."""

#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import from the correct config module
from core.config import OPENAI_API_KEY, GEOAPIFY_API_KEY, RAPIDAPI_KEY
from core.reasoning import llm_with_tools

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
        result = await llm_with_tools("Tell me about Lake Tahoe ski resorts")
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

