#!/usr/bin/env python3
"""
Example queries showing how to use weather and snow condition APIs
in the SkiTrip Assistant.
"""

import asyncio
from core.reasoning import llm_with_tools

async def demonstrate_weather_queries():
    """Show example queries for weather and snow conditions."""

    print("❄️ SkiTrip Assistant - Weather Query Examples")
    print("=" * 50)

    # Example queries that trigger weather tools
    weather_queries = [
        "What's the snow forecast for Lake Tahoe this week?",
        "Snow conditions in Zermatt for skiing?",
        "Weather forecast for Austrian Alps resorts?",
        "Snowfall predictions for Chamonix?",
        "Will there be good skiing weather in Colorado next weekend?",
        "Current snow conditions at Aspen Mountain?"
    ]

    print("🔍 Example Weather & Snow Queries:")
    print("-" * 40)

    for i, query in enumerate(weather_queries, 1):
        print(f"{i}. \"{query}\"")

    print("\n" + "=" * 50)
    print("🚀 These queries will automatically:")
    print("1. Extract location from query (Lake Tahoe, Zermatt, etc.)")
    print("2. Call get_weather_forecast tool")
    print("3. Get coordinates using Geoapify geocoding")
    print("4. Fetch 7-day forecast from Open-Meteo API")
    print("5. Return snow conditions, temperature, wind data")
    print("6. Format as natural, ski-focused response")

    print("\n📊 Weather Data Available:")
    print("- Daily snowfall amounts (mm)")
    print("- Temperature ranges (max/min °C)")
    print("- Wind speeds (km/h)")
    print("- Precipitation data")
    print("- 7-day forecast horizon")

    print("\n🎿 Integration with Ski Assistant:")
    print("- Automatic tool calling when weather is mentioned")
    print("- Ski-relevant weather focus (not generic weather)")
    print("- Multi-step reasoning for weather analysis")
    print("- Fallback to general knowledge if APIs fail")

if __name__ == "__main__":
    asyncio.run(demonstrate_weather_queries())
