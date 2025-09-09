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

from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from typing import Type, TypeVar, Optional, Dict, Any, List, Callable, Awaitable

import openai
from pydantic import BaseModel, Field, ValidationError

from config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_RETRIES,
    USE_REAL_OPENAI
)

# Configure logging
logger = logging.getLogger(__name__)

# Suppress httpx HTTP request logs to keep output clean
logging.getLogger("httpx").setLevel(logging.WARNING)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Type variable for generic Pydantic models
T = TypeVar('T', bound=BaseModel)




# --- Multi-Step Reasoning with Chain-of-Thought ---

def _build_chain_of_thought_instruction() -> str:
    """Build a structured chain-of-thought prompt for ski planning decisions."""
    return (
        "CHAIN-OF-THOUGHT REASONING - Follow these steps systematically:\n\n"
        "STEP 1: UNDERSTAND THE QUERY\n"
        "- Identify the user's core intent (planning, information, weather, etc.)\n"
        "- Extract explicit parameters (dates, locations, ability level)\n"
        "- Note any missing information that needs clarification\n\n"
        "STEP 2: CONTEXT ANALYSIS\n"
        "- Review conversation history for prior preferences/discussions\n"
        "- Check if this relates to an existing trip plan\n"
        "- Consider seasonal factors (current month, weather patterns)\n\n"
        "STEP 3: TOOL SELECTION & EXECUTION\n"
        "- Choose appropriate tools based on query type:\n"
        "  * Resort info: Wikipedia (primary) → SkiAPI (secondary)\n"
        "  * Location search: Geoapify Places API\n"
        "  * Weather: Open-Meteo (ski-relevant only)\n"
        "- Execute tools in logical sequence (primary first, fallback second)\n\n"
        "STEP 4: INFORMATION SYNTHESIS\n"
        "- Combine data from multiple sources when available\n"
        "- Cross-reference facts for consistency\n"
        "- Identify any gaps or conflicting information\n\n"
        "STEP 5: RESPONSE FORMULATION\n"
        "- Structure response logically (facts → recommendations → next steps)\n"
        "- Ensure all claims are supported by tool data\n"
        "- Include clarifying questions for missing information\n"
        "- Maintain ski-focused, helpful tone\n\n"
        "REASONING TRACE:\n"
        "- Document each step briefly in your thinking\n"
        "- Show your logic for tool selection and data interpretation\n"
        "- Explain any assumptions or fallbacks used\n\n"
        "FINAL OUTPUT:\n"
        "- Provide natural, conversational response\n"
        "- Base all facts on tool results\n"
        "- Ask one clear question if more info needed"
    )

def _build_evidence_only_system_instruction() -> str:
    return (
        "EVIDENCE-ONLY MODE:\n"
        "- You must answer ONLY using the tool messages in this conversation.\n"
        "- If evidence is insufficient, ask ONE concise ski-relevant question.\n"
        "- Stay ski-focused, friendly, concise; no speculation.\n"
        "- Include specific resort names and dates only if present in the tool evidence.\n"
        "- If you use any external facts from tools, mention their source_id briefly at the end."
    )

def _build_verify_instruction(message: str) -> str:
    # We run this as a short follow-up completion to prune any unsupported claims
    return (
        "VERIFY THE PREVIOUS ASSISTANT DRAFT.\n"
        "Return ONLY the corrected final message (no JSON, no preface).\n"
        "Rules:\n"
        "- Remove/soften any statement not supported by tool messages above.\n"
        "- Keep ski-friendly tone. If info is missing, ask ONE clarifying ski question.\n"
        f"- Start from this draft:\n{message}"
    )




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
        },
        {
            "type": "function",
            "function": {
                "name": "get_ski_resort_details",
                "description": "Get detailed information about a specific ski resort using SkiAPI database including location, basic details, and resort information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resort_name": {
                            "type": "string",
                            "description": "Name of the ski resort to get details for"
                        },
                        "country": {
                            "type": "string",
                            "description": "Country code (e.g., 'US', 'CA', 'FR') to help narrow down the search"
                        },
                        "include_snow_report": {
                            "type": "boolean",
                            "description": "Whether to include current snow conditions and report (may not be available)",
                            "default": False
                        }
                    },
                    "required": ["resort_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_wikipedia_resort_info",
                "description": "Get comprehensive information about a ski resort from Wikipedia including history, location, and key facts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resort_name": {
                            "type": "string",
                            "description": "Name of the ski resort to look up on Wikipedia"
                        },
                        "country": {
                            "type": "string",
                            "description": "Optional country context to help with the search"
                        }
                    },
                    "required": ["resort_name"]
                }
            }
        }
    ]

    # Build conversation messages with system prompt
    messages = [
        {
            "role": "system",
            "content": """You are SkiTrip Assistant, a specialized ski vacation planning expert. You ONLY help with ski-related topics and winter sports planning.

SKI CONTEXT ONLY:
- You ONLY answer questions about skiing, snow sports, winter vacations, and ski resorts
- If someone asks about weather in non-ski areas, redirect to ski destinations
- If someone asks about generic activities, redirect to ski-specific activities
- NEVER give generic weather info unless it's ski-relevant (snow conditions, temperatures for skiing)

TOOL USAGE RULES:
- ALWAYS call find_resorts_geoapify when users ask about ski resorts, skiing, or winter sports locations
- ONLY call get_weather_forecast for SKI-RELEVANT weather (snow conditions, ski temperatures, avalanche risks)
- ALWAYS call get_wikipedia_resort_info FIRST when users ask about ANY ski resort information - it's our primary source for resort details, history, and background
- Use get_ski_resort_details as a SECONDARY option when users specifically need operational data (lifts, trails, snow reports) that Wikipedia might not have
- Use tools immediately when ANY ski location is mentioned
- Do NOT use tools for non-ski locations or generic weather requests
- Wikipedia is our MAIN tool for resort information - use it proactively, not just as fallback

CLARIFYING QUESTIONS:
- If location unclear for skiing: "Which ski resort or region are you interested in?"
- If activity unclear: "Are you looking for downhill skiing, cross-country skiing, or snowboarding?"
- If specific resort details: "Which ski resort would you like detailed information about?"
- If no ski context: "I'd love to help with your ski trip planning! What ski destination interests you?"
- If weather request: "For skiing, are you asking about snow conditions, temperatures, or avalanche risks?"
- If resort info needed: "Would you like details about a specific resort including lift counts, trails, or snow conditions?"

RESPONSE RULES:
- Keep ALL responses focused on skiing and winter sports
- If no ski context in query: Ask clarifying ski-related questions
- No generic answers - redirect everything to ski context
- Be enthusiastic about skiing but stay focused
- If you don't have specific data: Ask for ski-specific clarification

API ERROR HANDLING:
- Since Wikipedia is our PRIMARY tool, first check if it works
- When Wikipedia fails or has no info: Try SkiAPI as secondary option
- When Wikipedia returns 'no_wikipedia_info': Ask for clarification about the resort name
- When SkiAPI has errors (quota, auth, subscription): Give short notice about API limitations
- For other API errors: Provide what information we can get
- Keep error messages brief and user-friendly
- Always try to provide some information rather than complete failure

SKI-RELEVANT WEATHER ONLY:
- Snow depth and quality
- Temperature for ski conditions
- Wind conditions affecting skiing
- Avalanche risks
- NEVER generic weather unless ski-related

REDIRECT NON-SKI QUERIES:
- "For skiing, I'd recommend checking [ski destination] instead"
- "That area isn't known for skiing. Consider [ski area] for great snow conditions"
- "Let me help you find ski resorts! What type of skiing interests you?"

KNOWLEDGE BASE:
Switzerland: Zermatt, St. Moritz, Verbier, Interlaken
France: Chamonix, Val d'Isère, Courchevel, Les Trois Vallées
USA: Lake Tahoe, Vail, Aspen, Park City, Jackson Hole
Italy: Cortina d'Ampezzo, Val Gardena, Sestriere
Austria: Innsbruck, Zell am See, Kaprun, Salzburg

API INTEGRATION:
- PRIMARY: Use Wikipedia FIRST for ALL resort information, history, background, and general details
- SECONDARY: Use SkiAPI when users specifically need operational data (lifts, trails, snow reports)
- Use Geoapify for finding nearby ski resorts and locations
- Use Open-Meteo for ski-relevant weather forecasts
- Wikipedia is the main information source - call it directly and proactively"""
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
            logger.info(f"LLM made {len(message.tool_calls)} tool calls")

            # First add the assistant message with tool calls
            messages.append(message)

            # Handle all tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_call_id = tool_call.id

                logger.info(f"Processing tool call: {tool_name} (ID: {tool_call_id})")

                # Execute the tool
                try:
                    tool_result = await _execute_tool(tool_name, tool_args)
                    logger.info(f"Tool execution result: {tool_result}")
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    tool_result = {"error": "tool_execution_failed", "message": str(e)}

                # Add tool result to conversation (must come after assistant message)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(tool_result, default=str)
                }
                messages.append(tool_message)
                logger.info(f"Added tool response for {tool_name}")

            # Get final response from LLM with Multi-Step Chain-of-Thought
            # Step 1: Chain-of-Thought Analysis
            messages.append({
                "role": "system",
                "content": _build_chain_of_thought_instruction()
            })

            # Step 2: Execute Chain-of-Thought reasoning
            try:
                cot_response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    temperature=0.3  # Slightly higher for creative reasoning
                )
                cot_result = cot_response.choices[0].message.content or ""

                # Step 3: Add CoT result to conversation for evidence-only synthesis
                messages.append({
                    "role": "assistant",
                    "content": cot_result
                })

                # Step 4: Force evidence-only synthesis BEFORE the final reply
                messages.append({
                    "role": "system",
                    "content": _build_evidence_only_system_instruction()
                })

                # Step 5: Synthesis (evidence-only)
                synthesis = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    temperature=0.0  # strict: reduce drift/hallucination
                )
                draft = synthesis.choices[0].message.content or ""

                # Step 6: Verification pass (hallucination pruning)
                verify_messages = messages + [
                    {"role": "assistant", "content": draft},
                    {"role": "system", "content": _build_verify_instruction(draft)},
                ]
                verified = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=verify_messages,
                    temperature=0.0
                )
                return verified.choices[0].message.content

            except Exception as e:
                logger.error(f"Chain-of-Thought LLM response failed: {e}")
                return f"Sorry, I encountered an issue processing the results. {str(e)}"



        # No tool call needed, return direct response
        return message.content

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "I'm sorry, I'm having trouble processing your request right now. Could you try again?"

# ---- Drop-in replacement for _execute_tool() plus helpers ----

# ---------- Common helpers ----------

def _ok(payload: Dict[str, Any], **extras) -> Dict[str, Any]:
    """Standard success envelope; keeps backwards-compatible keys."""
    out = {"ok": True, **payload}
    out.update(extras)
    return out

def _err(code: str, message: str, **extras) -> Dict[str, Any]:
    """Standard error envelope; keeps backwards-compatible keys."""
    out = {"ok": False, "error": code, "message": message}
    out.update(extras)
    return out

def _normalize_date_range(start_str: str, end_str: str) -> Dict[str, Any]:
    """Parse/normalize dates; if past or reversed, nudge to a sane 7-day window."""
    try:
        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)
    except Exception as e:
        raise ValueError(f"Invalid date format (YYYY-MM-DD required): {e}")

    today = date.today()
    if start < today:
        start = today
    if end < start:
        end = start + timedelta(days=6)
    return {"start": start, "end": end}

# ---------- Args models (validation) ----------

class FindResortsArgs(BaseModel):
    city: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius_km: int = Field(50, ge=5, le=100)
    limit: int = Field(8, ge=1, le=20)

class GetWeatherForecastArgs(BaseModel):
    city: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

class GetSkiResortDetailsArgs(BaseModel):
    resort_name: str
    country: Optional[str] = ""
    include_snow_report: bool = False

class GetWikipediaResortInfoArgs(BaseModel):
    resort_name: str
    country: Optional[str] = ""

# ---------- Tool handlers (one per tool) ----------

async def _handle_find_resorts_geoapify(args: FindResortsArgs) -> Dict[str, Any]:
    from apis.geoapify_resorts import find_resorts_geoapify
    result = await find_resorts_geoapify(**args.model_dump())
    logger.info(f"Geoapify API call completed for city: {args.city}")

    needs_fallback = (
        result.get("fallback")
        or not result.get("resorts")
        or result.get("error")
    )
    if needs_fallback:
        city = args.city or "the area"
        try:
            fallback_info = get_fallback_ski_info(city)
            result["fallback_info"] = fallback_info
            logger.info(f"Added fallback information for {city}")
        except Exception as e:
            logger.warning(f"Fallback info failed for {city}: {e}")
    return result  # keep your original shape

async def _handle_get_weather_forecast(args: GetWeatherForecastArgs) -> Dict[str, Any]:
    from apis.weather_openmeteo import get_forecast
    from apis.geoapify_resorts import _geocode

    # Validate/normalize dates
    try:
        rng = _normalize_date_range(args.start_date, args.end_date)
        start, end = rng["start"], rng["end"]
    except ValueError as e:
        return _err("invalid_dates", str(e))

    # Geocode
    try:
        coords = await _geocode(args.city)
    except Exception as e:
        logger.error(f"Geocoding failed for {args.city}: {e}")
        return _err("geocode_failed", f"Could not find coordinates for city: {args.city}")
    if not coords:
        return _err("geocode_not_found", f"Could not find coordinates for city: {args.city}")

    lat, lon, location_name = coords

    # Forecast
    try:
        forecast = await get_forecast(lat, lon, start, end)
    except Exception as e:
        logger.error(f"Weather API error for {location_name}: {e}")
        return _err("weather_api_error", f"Weather service unavailable: {e}", location=args.city)

    if not forecast:
        logger.warning(f"No weather data available for {args.city}")
        return _err("no_weather_data", f"No weather data available for {args.city}", location=args.city)

    # Convert to JSON-serializable dicts (keep your old keys for compatibility)
    forecast_data = []
    for d in forecast:
        forecast_data.append({
            "date": d.date.isoformat(),
            "temperature_max": getattr(d, "temperature_2m_max", None),
            "temperature_min": getattr(d, "temperature_2m_min", None),
            "precipitation": getattr(d, "precipitation_sum", None),
            "snowfall": getattr(d, "snowfall_sum", None),
            "wind_speed": getattr(d, "wind_speed_10m_max", None),
        })

    return _ok(
        {"location": location_name, "forecast": forecast_data, "days": len(forecast_data)}
    )

async def _handle_get_ski_resort_details(args: GetSkiResortDetailsArgs) -> Dict[str, Any]:
    from apis.skiapi_resorts import get_ski_resort_details

    try:
        result = await get_ski_resort_details(
            resort_name=args.resort_name,
            country=args.country or "",
            include_snow_report=args.include_snow_report,
        )
        logger.info(f"SkiAPI call completed for resort: {args.resort_name}")
    except Exception as e:
        logger.error(f"SkiAPI call failed for {args.resort_name}: {e}")
        return _err("skiapi_call_failed", f"SkiAPI unavailable: {e}", resort_requested=args.resort_name)

    # Handle SkiAPI errors & Wikipedia fallback
    error_type = result.get("error")
    if error_type in {"rate_limit_exceeded", "authentication_failed", "subscription_required", "http_429", "http_401", "http_403"}:
        logger.info(f"SkiAPI error ({error_type}), attempting Wikipedia fallback for {args.resort_name}")
        return await _wikipedia_fallback_from_skiapi(args.resort_name, args.country or "", error_type)

    if result.get("fallback") or result.get("error"):
        # other SkiAPI issues → try Wikipedia augment
        augmented = await _try_attach_wikipedia(result, args.resort_name, args.country or "")
        if augmented:
            return augmented
        return _err("api_unavailable", "SkiAPI temporarily unavailable. Please try again later.",
                    resort_requested=args.resort_name, api_status="unavailable")

    return result  # keep original shape if good

async def _handle_get_wikipedia_resort_info(args: GetWikipediaResortInfoArgs) -> Dict[str, Any]:
    from apis.wikipedia_resorts import search_wikipedia_resort_info

    try:
        wiki = await search_wikipedia_resort_info(args.resort_name, args.country or "")
    except Exception as e:
        logger.error(f"Wikipedia search failed for {args.resort_name}: {e}")
        return _err("wikipedia_error", f"Wikipedia service unavailable: {e}", resort_requested=args.resort_name)

    if wiki.get("success"):
        return _ok({
            "wikipedia_info": wiki,
            "resort_name": wiki.get("resort_name"),
            "summary": wiki.get("summary"),
            "page_url": wiki.get("page_url"),
            "source": "wikipedia",
        })
    if wiki.get("error") == "no_wikipedia_page":
        return _err(
            "no_wikipedia_info",
            f"I couldn't find a Wikipedia page for '{args.resort_name}'. Could you clarify the resort name or provide more details?",
            resort_requested=args.resort_name,
            suggestion="Try exact resort name or check alternative spelling."
        )
    return _err(
        "wikipedia_error",
        f"Sorry, I encountered an issue while fetching information about {args.resort_name}. {wiki.get('message', 'Please try again later.')}",
        resort_requested=args.resort_name
    )

# ---------- Fallback helpers ----------

async def _wikipedia_fallback_from_skiapi(resort_name: str, country: str, error_type: str) -> Dict[str, Any]:
    """Hard fallback to Wikipedia when SkiAPI quotas/auth block us."""
    try:
        from apis.wikipedia_resorts import search_wikipedia_resort_info
        wiki = await search_wikipedia_resort_info(resort_name, country)
        if wiki.get("success"):
            return {
                "wikipedia_fallback": True,
                "api_status": f"skiapi_{error_type}",
                "resort_name": wiki.get("resort_name"),
                "summary": wiki.get("summary"),
                "page_url": wiki.get("page_url"),
                "source": "wikipedia_fallback",
                "message": f"Using Wikipedia info (SkiAPI {error_type.replace('_', ' ')})"
            }
        return _err("all_apis_failed",
                    f"Sorry, both SkiAPI and Wikipedia are unavailable. {wiki.get('message', 'Please try again later.')}",
                    resort_requested=resort_name, api_status="all_failed")
    except Exception as e:
        logger.error(f"Wikipedia fallback failed for {resort_name}: {e}")
        return _err("api_unavailable",
                    "SkiAPI unavailable and Wikipedia fallback failed. Please try again later.",
                    resort_requested=resort_name, api_status=error_type)

async def _try_attach_wikipedia(skiapi_result: Dict[str, Any], resort_name: str, country: str) -> Optional[Dict[str, Any]]:
    """Soft fallback: attach Wikipedia details to SkiAPI result if possible."""
    try:
        from apis.wikipedia_resorts import search_wikipedia_resort_info
        wiki = await search_wikipedia_resort_info(resort_name, country)
        if wiki.get("success"):
            skiapi_result["wikipedia_fallback"] = True
            skiapi_result["api_status"] = "skiapi_error_wikipedia_fallback"
            skiapi_result["wikipedia_info"] = wiki
            return skiapi_result
    except Exception as e:
        logger.error(f"Wikipedia soft-fallback failed for {resort_name}: {e}")
    return None

# ---------- Public dispatcher (unchanged signature) ----------

async def _execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool function based on LLM tool-calls.
    Returns dicts compatible with your existing outputs.
    """
    # Map tool names to (ArgsModel, handler)
    registry: Dict[str, tuple[type[BaseModel], Callable[[BaseModel], Awaitable[Dict[str, Any]]]]] = {
        "find_resorts_geoapify": (FindResortsArgs, _handle_find_resorts_geoapify),
        "get_weather_forecast": (GetWeatherForecastArgs, _handle_get_weather_forecast),
        "get_ski_resort_details": (GetSkiResortDetailsArgs, _handle_get_ski_resort_details),
        "get_wikipedia_resort_info": (GetWikipediaResortInfoArgs, _handle_get_wikipedia_resort_info),
    }

    if tool_name not in registry:
        msg = f"Unknown tool requested: {tool_name}"
        logger.warning(msg)
        return _err("unknown_tool", msg)

    ArgsModel, handler = registry[tool_name]

    try:
        args = ArgsModel(**(tool_args or {}))
    except ValidationError as ve:
        logger.warning(f"Validation error for {tool_name}: {ve}")
        return _err("invalid_arguments", f"Invalid arguments for {tool_name}: {ve}")

    try:
        return await handler(args)
    except Exception as e:
        logger.error(f"Tool execution failed for {tool_name}: {e}")
        return _err("tool_execution_failed", f"{tool_name} failed: {e}", fallback=True)








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
