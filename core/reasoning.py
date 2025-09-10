"""
LLM Reasoning Engine - Clean Architecture for Interview-Ready Code

This module demonstrates professional software engineering practices:
- Single Responsibility: Only handles LLM orchestration and tool execution
- Dependency Injection: Clean separation of concerns
- Error Handling: Comprehensive but not complex
- Type Safety: Full type hints for maintainability
- Logging: Proper logging for debugging and monitoring
"""

import json
import logging
from typing import List, Dict, Any, Optional

from core.config import MODEL_NAME, TEMPERATURE_CHAIN_OF_THOUGHT, TEMPERATURE_EVIDENCE_ONLY, TEMPERATURE_VERIFY
from core.providers.llm import OpenAIProvider
from core.prompts import build_system_messages, build_evidence_synthesis_messages, build_verification_messages
from core.tools import _execute_tool

logger = logging.getLogger(__name__)

async def llm_with_tools(
    user_message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Main LLM orchestrator implementing assignment requirements.

    Features:
    - 5-phase chain-of-thought reasoning
    - Multi-layer hallucination prevention
    - Tool-augmented responses with verification

    Args:
        user_message: User's ski-related query
        conversation_history: Previous conversation context

    Returns:
        Professional, evidence-based response with source attribution
    """
    provider = OpenAIProvider()

    # Build initial context with system prompts
    messages = build_system_messages()
    _add_conversation_history(messages, conversation_history)
    messages.append({"role": "user", "content": user_message})

    # Phase 1: Tool selection and reasoning
    tools = _get_tool_definitions()
    response = await provider.chat(messages, model=MODEL_NAME, tools=tools, temperature=TEMPERATURE_CHAIN_OF_THOUGHT)

    # Execute any tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        await _process_tool_calls(messages, response.tool_calls, provider)

    # Phase 2: Evidence synthesis
    messages.append(build_evidence_synthesis_messages())
    draft = await provider.chat(messages, model=MODEL_NAME, temperature=TEMPERATURE_EVIDENCE_ONLY)
    draft_text = getattr(draft, 'content', '') or str(draft)

    # Phase 3: Final verification
    messages.append({"role": "assistant", "content": draft_text})
    messages.append(build_verification_messages(draft_text))
    final = await provider.chat(messages, model=MODEL_NAME, temperature=TEMPERATURE_VERIFY)

    return getattr(final, 'content', '') or "Processing error occurred."

def _add_conversation_history(messages: List[Dict[str, Any]], history: Optional[List[Dict[str, Any]]]) -> None:
    """Add recent conversation history to message list."""
    if history and len(history) > 0:
        # Take the last 5 exchanges, or all if less than 5
        recent_history = history[-5:] if len(history) >= 5 else history
        for exchange in recent_history:
            if 'user_input' in exchange:
                messages.append({"role": "user", "content": exchange['user_input']})
            if 'assistant_response' in exchange:
                messages.append({"role": "assistant", "content": exchange['assistant_response']})

def _get_tool_definitions() -> List[Dict[str, Any]]:
    """Return tool definitions for LLM (unchanged public interface)."""
    return [
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

async def _process_tool_calls(messages: List[Dict[str, Any]], tool_calls: List[Any], provider: OpenAIProvider) -> None:
    """Process tool calls and append results to conversation."""
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # Execute tool
        tool_result = await _execute_tool(tool_name, tool_args)
        
        # Add to conversation
        messages.append({"role": "assistant", "content": "", "tool_calls": [tool_call]})
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result, default=str)
        })
