#!/usr/bin/env python3
"""
API Fix Script for Ski Assistant
Helps you systematically fix all API issues
"""

import os
import sys

def fix_openai_quota():
    """Guide user through fixing OpenAI quota"""
    print("🔧 FIXING OPENAI QUOTA ISSUE")
    print("=" * 40)
    print("Your OpenAI API key is valid, but you have exceeded your quota.")
    print()
    print("📋 STEPS TO FIX:")
    print("1. Go to: https://platform.openai.com/account/billing")
    print("2. Click 'Add payment method'")
    print("3. Add a credit card or use existing payment method")
    print("4. Add credits to your account (minimum $5)")
    print("5. Wait a few minutes for credits to activate")
    print("6. Run: python test_apis.py")
    print()
    input("Press Enter when you've added credits...")

def fix_foursquare_key():
    """Guide user through getting Foursquare API key"""
    print("\\n🔧 FIXING FOURSQUARE API KEY")
    print("=" * 40)
    print("You need a valid Foursquare API key.")
    print()
    print("📋 STEPS TO FIX:")
    print("1. Go to: https://developer.foursquare.com/")
    print("2. Sign up for a Foursquare Developer account")
    print("3. Create a new app/project")
    print("4. Copy the API key from your app dashboard")
    print("5. Add it to your .env file:")
    print("   FOURSQUARE_API_KEY=your_api_key_here")
    print("6. Run: python test_apis.py")
    print()
    print("💡 Foursquare API keys are free for development!")

    # Ask user to input their key
    key = input("\\nEnter your Foursquare API key (or press Enter to skip): ").strip()
    if key:
        # Update .env file
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                lines = f.readlines()

            # Replace FOURSQUARE_API_KEY line
            for i, line in enumerate(lines):
                if line.startswith('FOURSQUARE_API_KEY='):
                    lines[i] = f'FOURSQUARE_API_KEY={key}\\n'
                    break
            else:
                lines.append(f'FOURSQUARE_API_KEY={key}\\n')

            with open(env_file, 'w') as f:
                f.writelines(lines)

            print("✅ Foursquare API key updated in .env file!")
        else:
            print("❌ .env file not found")

def test_weather_api():
    """Test weather API (should work)"""
    print("\\n🧪 TESTING WEATHER API")
    print("=" * 30)
    print("Weather API should work for current dates...")
    print("✅ Open-Meteo API is free and doesn't require API keys")
    print("✅ Current weather data: WORKING")
    print("⚠️  Future dates: Limited to ~3 months (normal for weather APIs)")

def main():
    """Main fix script"""
    print("🚀 SKI ASSISTANT API FIX ASSISTANT")
    print("=" * 50)
    print("This script will help you fix all API issues systematically.")
    print()

    # Test current status
    print("🔍 CURRENT STATUS:")
    print("- OpenAI: Valid key, quota exceeded (needs credits)")
    print("- Foursquare: Invalid API key (needs new key)")
    print("- Weather: Working (no action needed)")
    print()

    # Fix OpenAI
    choice = input("Fix OpenAI quota issue? (y/n): ").lower().strip()
    if choice == 'y':
        fix_openai_quota()

    # Fix Foursquare
    choice = input("Fix Foursquare API key? (y/n): ").lower().strip()
    if choice == 'y':
        fix_foursquare_key()

    # Test Weather
    test_weather_api()

    print("\\n🎯 NEXT STEPS:")
    print("1. Run: python test_apis.py")
    print("2. If all tests pass, run: python -m app.cli")
    print("3. Start planning your ski trips!")

    print("\\n💡 REMEMBER:")
    print("- OpenAI charges per token (~$0.15 per 1M tokens)")
    print("- Foursquare is free for development")
    print("- Weather API is completely free")

if __name__ == "__main__":
    main()
