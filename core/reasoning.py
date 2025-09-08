"""LLM reasoning and JSON validation for SkiTrip Assistant."""

import json
import logging
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, ValidationError
import openai
from config.settings import OPENAI_API_KEY, OPENAI_MODEL, LLM_TEMPERATURE, LLM_MAX_RETRIES, USE_REAL_OPENAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

T = TypeVar('T', bound=BaseModel)

async def llm_json(prompt: str, schema: Type[T], *, temperature: float = LLM_TEMPERATURE, max_retries: int = LLM_MAX_RETRIES) -> T:
    """Legacy function for backward compatibility - use llm_with_tools instead."""
    # For backward compatibility, return fake data
    return _get_fake_response(schema)

async def llm_with_tools(user_message: str, conversation_history: list = None) -> str:
    """Call LLM with tool calling capabilities for ski trip planning.

    Args:
        user_message: The user's message
        conversation_history: Previous conversation history

    Returns:
        Natural language response from LLM
    """
    if not USE_REAL_OPENAI:
        logger.info("Using fake LLM response (USE_REAL_OPENAI=False)")
        return _get_fake_conversation_response(user_message)

    # Define available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "find_resorts_geoapify",
                "description": "Find ski resorts near a location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City or area name. If not given, use lat/lon."},
                        "lat": {"type": "number", "description": "Latitude if already known."},
                        "lon": {"type": "number", "description": "Longitude if already known."},
                        "radius_km": {"type": "number", "minimum": 5, "maximum": 100, "default": 30},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 8}
                    }
                }
            }
        }
    ]

    # Build conversation messages
    messages = [
        {
            "role": "system",
            "content": """You are Ski Planner. You MUST use tools to fetch real data for ski-related queries.

TOOL USAGE RULES:
- ALWAYS call find_resorts_geoapify when user mentions: ski resorts, skiing, ski areas, alpine resorts, winter sports
- Use the tool for ANY location mentioned (cities, countries, regions, mountains)
- Do NOT ask for clarification if a location is mentioned - use the tool immediately
- If no location specified, ask for one, then use the tool

RESPONSE FORMAT:
After tool call: summarize results in 2-4 bullets with name, address, and website if available.
Example: "- Resort Name, City, Country - [website]"

ERROR HANDLING:
If tool fails or returns no results: provide helpful information about known ski destinations in that area.
For example: "While I couldn't find specific resorts, [Location] is known for [ski facts]. Consider nearby destinations like [nearby ski areas]."

FALLBACK KNOWLEDGE:
- Switzerland: Zermatt, St. Moritz, Verbier, Interlaken
- France: Chamonix, Val d'Isère, Courchevel
- USA: Lake Tahoe, Vail, Aspen, Park City
- Italy: Cortina d'Ampezzo, Val Gardena
- Austria: Innsbruck, Salzburg area

NEVER invent resort names or details. Only use data from tool results."""
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

async def _execute_tool(tool_name: str, args: dict) -> dict:
    """Execute a tool and return the results."""
    try:
        if tool_name == "find_resorts_geoapify":
            from apis.geoapify_resorts import find_resorts_geoapify
            result = await find_resorts_geoapify(**args)

            # If fallback is needed, enhance the response with helpful information
            if result.get("fallback") or not result.get("resorts"):
                city = args.get("city", "the area")
                fallback_info = get_fallback_ski_info(city)
                result["fallback_info"] = fallback_info

            return result

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {"error": f"Tool execution failed: {str(e)}"}

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
