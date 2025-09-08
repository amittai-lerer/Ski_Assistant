"""
SkiTrip Assistant - LLM Reasoning and Tool Integration

This module handles the core intelligence of the SkiTrip Assistant by:
- Integrating with OpenAI's GPT models using function/tool calling
- Processing user queries about ski trips and resorts
- Coordinating with external APIs (Geoapify) to fetch real data
- Providing intelligent fallback responses when APIs are unavailable
- Maintaining conversation context and history

The system uses OpenAI's tool calling feature to enable the LLM to:
1. Understand when users ask about ski resorts/locations
2. Call the appropriate tools (find_resorts_geoapify) with correct parameters
3. Process API responses and provide natural language summaries
4. Fall back to expert knowledge when APIs don't return results

Key Features:
- Tool-based LLM integration with OpenAI
- Real-time resort data from Geoapify API
- Intelligent fallback responses with ski destination knowledge
- Conversation context management
- Error handling and graceful degradation

Author: SkiTrip Assistant Team
License: MIT
"""

import json
import logging
from datetime import date, timedelta
from typing import Type, TypeVar, Optional, Dict, Any, List

import openai
from pydantic import BaseModel

from config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_RETRIES,
    USE_REAL_OPENAI
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Type variable for generic Pydantic models
T = TypeVar('T', bound=BaseModel)

async def llm_json(prompt: str, schema: Type[T], *, temperature: float = LLM_TEMPERATURE, max_retries: int = LLM_MAX_RETRIES) -> T:
    """
    Legacy function for backward compatibility.

    This function is kept for compatibility with older code that expects
    JSON schema validation. New code should use llm_with_tools() instead.

    Args:
        prompt: The prompt to send to the LLM
        schema: Pydantic schema for response validation
        temperature: Sampling temperature for response generation
        max_retries: Maximum number of API retry attempts

    Returns:
        Validated Pydantic model instance
    """
    logger.warning("Using deprecated llm_json() function - consider using llm_with_tools() instead")
    return _get_fake_response(schema)


async def llm_with_tools(user_message: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Main LLM interface with tool calling capabilities for ski trip planning.

    This function integrates with OpenAI's tool calling feature to enable the LLM
    to interact with external APIs (Geoapify) to fetch real ski resort data.
    When users ask about ski resorts, the LLM can call the find_resorts_geoapify
    tool to get actual data instead of making assumptions.

    Args:
        user_message: The current user message/query
        conversation_history: List of previous conversation exchanges for context

    Returns:
        Natural language response from the LLM, potentially including tool results

    Raises:
        Exception: If LLM API call fails after retries
    """
    if not USE_REAL_OPENAI:
        logger.info("Using fake LLM response (USE_REAL_OPENAI=False)")
        return _get_fake_conversation_response(user_message)

    # Define available tools for the LLM
    tools = [
        {
            "type": "function",
            "function": {
                "name": "find_resorts_geoapify",
                "description": "Search for ski resorts and winter sports facilities near a location using Geoapify API.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Name of city, town, or region to search for ski resorts"
                        },
                        "lat": {
                            "type": "number",
                            "description": "Latitude coordinate (optional, will be geocoded from city if not provided)"
                        },
                        "lon": {
                            "type": "number",
                            "description": "Longitude coordinate (optional, will be geocoded from city if not provided)"
                        },
                        "radius_km": {
                            "type": "integer",
                            "description": "Search radius in kilometers",
                            "minimum": 5,
                            "maximum": 100,
                            "default": 50
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 8
                        }
                    },
                    "required": ["city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a specific location using Open-Meteo API.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Name of city or location to get weather for"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date for forecast in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date for forecast in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["city", "start_date", "end_date"]
                }
            }
        }
    ]

    # Build conversation messages with system prompt
    messages = [
        {
            "role": "system",
            "content": """You are SkiTrip Assistant, an expert ski vacation planner. You help users find ski resorts and plan amazing ski trips.

TOOL USAGE RULES:
- ALWAYS call find_resorts_geoapify when users ask about ski resorts, skiing, winter sports, or alpine activities
- ALWAYS call get_weather_forecast when users ask about weather, snow conditions, temperature, or forecasts
- Use the tools immediately when ANY location is mentioned (cities, countries, regions, mountains)
- Do NOT ask for clarification - use the appropriate tool right away with the location provided
- If no location specified, ask for one, then use the tool
- For weather requests, also ask for date range if not specified

RESPONSE GUIDELINES:
- After tool calls: Summarize results naturally in 2-4 bullet points
- Include resort names, locations, and websites when available
- Keep responses conversational and helpful
- Be enthusiastic about skiing and winter sports

FALLBACK BEHAVIOR:
When APIs don't return results or fail:
- Provide expert knowledge about famous ski destinations
- Suggest well-known resorts in the requested area
- Maintain helpful, informative tone

EXAMPLE RESPONSE:
"Here are some great ski resorts near [Location]:
- Resort Name - [Location], [Country] - [website]
- Another Resort - [Location], [Country]"

KNOWLEDGE BASE:
Switzerland: Zermatt, St. Moritz, Verbier, Interlaken
France: Chamonix, Val d'Isère, Courchevel, Les Trois Vallées
USA: Lake Tahoe, Vail, Aspen, Park City, Jackson Hole
Italy: Cortina d'Ampezzo, Val Gardena, Sestriere
Austria: Innsbruck, Zell am See, Kaprun, Salzburg

Always prioritize real data from tools over general knowledge."""
        }
    ]

    # Add conversation history
    if conversation_history:
        for exchange in conversation_history[-5:]:  # Keep last 5 exchanges
            if 'user_input' in exchange:
                messages.append({"role": "user", "content": exchange['user_input']})
            if 'assistant_response' in exchange:
                messages.append({"role": "assistant", "content": exchange['assistant_response']})

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    try:
        # Make the API call with tools
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )

        message = response.choices[0].message

        # Check if LLM wants to call a tool
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Execute the tool
            tool_result = await _execute_tool(tool_name, tool_args)

            # Add tool result to conversation and get final response
            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

            # Get final response from LLM
            final_response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7
            )

            return final_response.choices[0].message.content

        # No tool call needed, return direct response
        return message.content

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "I'm sorry, I'm having trouble processing your request right now. Could you try again?"

async def _execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool function with the provided arguments.

    This function acts as a dispatcher for tool calls from the LLM. It handles
    the execution of external API calls and provides fallback behavior when
    APIs are unavailable or return no results.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments to pass to the tool function

    Returns:
        Dictionary containing tool execution results, potentially enhanced
        with fallback information if the primary API call fails or returns
        no results.

    Raises:
        Exception: Re-raised after logging if tool execution fails
    """
    try:
        if tool_name == "find_resorts_geoapify":
            # Import the Geoapify resorts API module
            from apis.geoapify_resorts import find_resorts_geoapify

            # Execute the tool with provided arguments
            result = await find_resorts_geoapify(**tool_args)
            logger.info(f"Geoapify API call completed for city: {tool_args.get('city', 'unknown')}")

            # Check if we need to provide fallback information
            needs_fallback = (
                result.get("fallback") or
                not result.get("resorts") or
                result.get("error")
            )

            if needs_fallback:
                city = tool_args.get("city", "the area")
                fallback_info = get_fallback_ski_info(city)
                result["fallback_info"] = fallback_info
                logger.info(f"Added fallback information for {city}")

            return result

        elif tool_name == "get_weather_forecast":
            # Import the weather API module
            from apis.weather_openmeteo import get_forecast
            from apis.geoapify_resorts import _geocode

            # Parse the arguments
            city = tool_args.get("city")
            start_date_str = tool_args.get("start_date")
            end_date_str = tool_args.get("end_date")

            if not city or not start_date_str or not end_date_str:
                return {"error": "Missing required parameters: city, start_date, end_date"}

            try:
                # Parse dates
                start_date = date.fromisoformat(start_date_str)
                end_date = date.fromisoformat(end_date_str)

                # Validate dates are not in the past
                today = date.today()
                if start_date < today:
                    # If dates are in the past, use next week instead
                    start_date = today
                    end_date = today + timedelta(days=6)  # Next 7 days
                    logger.info(f"Dates were in past, adjusted to: {start_date} to {end_date}")

                # Ensure end_date is not before start_date
                if end_date < start_date:
                    end_date = start_date + timedelta(days=6)

                # Geocode the city to get coordinates
                coords = await _geocode(city)
                if not coords:
                    return {"error": f"Could not find coordinates for city: {city}"}

                lat, lon, location_name = coords

                # Get weather forecast
                forecast = await get_forecast(lat, lon, start_date, end_date)

                if forecast:
                    logger.info(f"Weather forecast retrieved for {location_name} ({len(forecast)} days)")
                    # Convert forecast objects to dictionaries for JSON serialization
                    forecast_data = []
                    for day_forecast in forecast:
                        forecast_data.append({
                            "date": day_forecast.date.isoformat(),
                            "temperature_max": day_forecast.temperature_2m_max,
                            "temperature_min": day_forecast.temperature_2m_min,
                            "precipitation": day_forecast.precipitation_sum,
                            "snowfall": day_forecast.snowfall_sum,
                            "wind_speed": day_forecast.wind_speed_10m_max
                        })

                    return {
                        "location": location_name,
                        "forecast": forecast_data,
                        "days": len(forecast_data)
                    }
                else:
                    logger.warning(f"No weather data available for {city}")
                    return {"error": f"No weather data available for {city}", "location": city}

            except ValueError as e:
                return {"error": f"Invalid date format: {e}"}
            except Exception as e:
                logger.error(f"Weather API error: {e}")
                return {"error": f"Weather service unavailable: {str(e)}"}

        else:
            # Unknown tool requested
            error_msg = f"Unknown tool requested: {tool_name}"
            logger.warning(error_msg)
            return {"error": error_msg}

    except Exception as e:
        # Log the error and return a structured error response
        logger.error(f"Tool execution failed for {tool_name}: {e}")
        return {"error": f"Tool execution failed: {str(e)}", "fallback": True}

def get_fallback_ski_info(location: str) -> str:
    """Provide helpful fallback information for ski destinations."""
    location_lower = location.lower()

    # Switzerland
    if "switzerland" in location_lower or "swiss" in location_lower:
        return "Switzerland is world-famous for skiing! Consider these top destinations: Zermatt (Matterhorn views), St. Moritz (luxury skiing), Verbier (off-piste paradise), and Interlaken (gateway to Jungfrau region)."

    # France
    if "france" in location_lower or "chamonix" in location_lower:
        return "France has incredible skiing! Chamonix is legendary for its challenging slopes and Mont Blanc views. Other great areas include Val d'Isère, Courchevel, and Les Trois Vallées."

    # USA
    if "usa" in location_lower or "united states" in location_lower or "america" in location_lower:
        if "tahoe" in location_lower:
            return "Lake Tahoe is fantastic for skiing! It has excellent snow conditions and diverse terrain. Heavenly Mountain is a highlight with stunning lake views."
        return "The USA has amazing ski destinations! Consider Lake Tahoe (California/Nevada), Vail (Colorado), Aspen (Colorado), or Park City (Utah)."

    # Italy
    if "italy" in location_lower:
        return "Italy offers spectacular skiing! Try Cortina d'Ampezzo (Dolomites), Val Gardena, or Sestriere. The Italian Alps provide diverse terrain and amazing food."

    # Austria
    if "austria" in location_lower:
        return "Austria is ski paradise! Innsbruck is a great base, and the Salzburg area has fantastic resorts like Zell am See and Kaprun."

    # General fallback
    return f"{location} is in a great skiing region! Many world-class resorts are nearby. Popular destinations include the Alps, Rockies, and Sierra Nevada mountains."

def _get_fake_conversation_response(user_message: str) -> str:
    """Return a fake conversation response for development."""
    if "hello" in user_message.lower() or "hi" in user_message.lower():
        return "Hello! I'm your ski trip planning assistant. I'd love to help you plan an amazing ski vacation!"
    elif "lake tahoe" in user_message.lower():
        return "Lake Tahoe is fantastic for skiing! Do you have specific dates in mind and what's your ability level?"
    elif "france" in user_message.lower():
        return "France has incredible skiing in the Alps! Places like Chamonix, Val d'Isère, and Courchevel are world-class resorts."
    else:
        return "That sounds like a great ski trip idea! Where are you thinking of going and when?"

def validate_response(response: str, schema: Type[T]) -> T:
    """Validate a response string against a schema.

    Args:
        response: The response string to validate
        schema: Pydantic model to validate against

    Returns:
        Validated response object

    Raises:
        ValueError: If validation fails
    """
    try:
        data = json.loads(response)
        return schema(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Response validation failed: {e}")


def _get_fake_response(schema: Type[T]) -> T:
    """Generate fake responses for development and testing.

    This function provides deterministic fake data that matches
    the expected schema, allowing the application to run without
    actual LLM integration during development.

    Args:
        schema: The Pydantic model class to generate data for

    Returns:
        Fake model instance with realistic test data
    """
    from models.schemas import TripSlots, ConversationResponse, AbilityLevel
    from datetime import date

    if schema == TripSlots:
        return TripSlots(
            origin=None,
            region="Lake Tahoe",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
            ability=AbilityLevel.INTERMEDIATE,
            preferences=[]
        )

    if schema == ConversationResponse:
        return ConversationResponse(
            response="Perfect! I'll create a detailed ski trip plan for Lake Tahoe from December 20-22 for intermediate skiers. Let me gather the best resorts and weather data for you!",
            needs_info=False,
            missing_fields=[],
            action="plan",
            slots=TripSlots(
                origin=None,
                region="Lake Tahoe",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 22),
                ability=AbilityLevel.INTERMEDIATE,
                preferences=[]
            )
        )

    # Add more fake responses as needed for other schemas
    raise ValueError(f"No fake response available for schema: {schema}")
