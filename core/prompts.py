"""Conversational prompts that make the LLM ask for relevant data."""

from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AbilityLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TripSlots(BaseModel):
    origin: Optional[str] = None
    region: Optional[str] = None
    start_date: date
    end_date: date
    ability: AbilityLevel
    preferences: Optional[List[str]] = None


class Resort(BaseModel):
    name: str
    latitude: float
    longitude: float
    source_id: str


class ForecastDay(BaseModel):
    date: date
    max_temp_c: float
    snowfall_mm: float
    source_id: str


class PlanStep(BaseModel):
    time: str
    activity: str
    location: str
    duration_minutes: int
    notes: Optional[str] = None
    source_id: str


class DayPlan(BaseModel):
    date: date
    resort: str
    weather_summary: str
    steps: List[PlanStep]
    total_ski_minutes: int
    source_id: str


class Itinerary(BaseModel):
    trip_slots: TripSlots
    ranked_resorts: List[Dict[str, Any]]
    daily_plans: List[DayPlan]
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"


class ConversationResponse(BaseModel):
    message: str
    action: str


def get_conversation_prompt(user_input: str, context: Dict[str, Any]) -> str:
    """Generate conversation prompt that makes LLM ask for relevant data with full conversation context."""

    # Build conversation history summary
    conversation_history = context.get('conversation_history', [])
    history_summary = ""
    if conversation_history:
        history_summary = "\nRecent conversation:\n"
        # Show last 3 exchanges to keep context manageable
        recent_exchanges = conversation_history[-3:]
        for i, exchange in enumerate(recent_exchanges, 1):
            history_summary += f"{i}. User: \"{exchange.get('user_input', '')}\"\n"
            if 'assistant_response' in exchange and exchange['assistant_response']:
                # Truncate long responses for context
                response = exchange['assistant_response'][:100]
                if len(exchange['assistant_response']) > 100:
                    response += "..."
                history_summary += f"   Assistant: {response}\n"

    has_plan = context.get('has_plan', False)
    plan_region = context.get('plan_region', 'None')
    interaction_count = context.get('interaction_count', 0)

    return f"""You are a friendly, conversational ski trip planning assistant. Have a natural back-and-forth discussion with the user about their ski trip.

CURRENT USER MESSAGE: "{user_input}"

CONVERSATION CONTEXT:
- This is exchange #{interaction_count + 1} in our conversation
- Has active plan: {has_plan}
- Current plan location: {plan_region}
{history_summary}

YOUR ROLE:
- Be conversational and friendly, like talking to a ski buddy
- Remember what we've discussed before from the conversation history
- Ask follow-up questions naturally to gather more details
- Reference previous parts of our conversation when relevant
- Help refine or modify existing plans when appropriate
- Be helpful about weather, resorts, and ski conditions

RESPONSE TYPES:
- "respond_only": For general chat, questions, or when gathering more info
- "create_plan": Only when you have enough details (region, dates, ability level) to create a plan
- "modify_plan": When user wants to change existing plan details
- "show_info": When user asks about current plan or wants to see details

Return ONLY JSON:
{{
  "message": "your natural, conversational response",
  "action": "respond_only|create_plan|modify_plan|show_info"
}}

EXAMPLES OF CONVERSATIONAL RESPONSES:

First-time user: "Hey, I want to go skiing"
→ {{"message": "Hey there! Skiing sounds awesome! Where are you thinking of going? Lake Tahoe, Colorado, or somewhere else? And when are you planning this trip?", "action": "respond_only"}}

User with existing plan: "What's the weather like?"
→ {{"message": "Great question! For your {plan_region} trip, let me check the current weather forecast and how it might affect your skiing.", "action": "show_info"}}

Ready to plan: "Lake Tahoe, December 20-22, intermediate level"
→ {{"message": "Perfect! Lake Tahoe in December is fantastic for intermediate skiers. I'll create a detailed 3-day itinerary with the best resorts and weather info.", "action": "create_plan"}}

Follow-up question: "Actually, make it 4 days instead"
→ {{"message": "No problem! I'll extend your Lake Tahoe trip by one day. Should I keep the same resorts or look for some variety?", "action": "modify_plan"}}

RESPOND TO: {user_input}"""


def get_slot_extract_prompt(user_input: str) -> str:
    """Extract trip parameters from conversation."""
    return f"""Extract trip parameters from this conversation: "{user_input}"

The user might have provided information across multiple messages. Extract what you can and make reasonable assumptions for missing data.

Return ONLY JSON:
{{
  "origin": "string or null",
  "region": "string or null", 
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "ability": "beginner|intermediate|advanced",
  "preferences": ["string"] or null
}}

Rules:
- If no dates given, use reasonable dates (e.g., next month)
- If no ability given, default to "intermediate"
- If no region given, return null (ask for clarification)

Examples:
"Lake Tahoe December 20-22 intermediate" → {{"origin": null, "region": "Lake Tahoe", "start_date": "2025-12-20", "end_date": "2025-12-22", "ability": "intermediate", "preferences": null}}

"Europe" → {{"origin": null, "region": "Europe", "start_date": "2025-01-15", "end_date": "2025-01-17", "ability": "intermediate", "preferences": null}}

Extract from: {user_input}"""


# --- Plan summary prompt (narrative → later used to shape itinerary text) -----

def get_plan_summary_prompt(*args, context: str | None = None, **kwargs) -> str:
    """
    Build a prompt that asks the LLM to write a concise day-by-day ski plan summary
    as plain text (the app will structure it later). Keep it short and actionable.
    """
    ctx = (context or "").strip()
    return f"""
You are a ski-trip planner. Write a concise day-by-day plan in 3–6 sentences total,
prioritizing good snow, morning conditions, and wind safety. Use short sentences.

Context (resort, forecast, ability, dates, notes):
{ctx}

Constraints:
- Be practical (arrive early, lunch window, lifts that suit ability).
- Mention wind or storm impacts if relevant.
- No JSON, no code fences, no markdown. Plain sentences only.
""".strip()





def get_self_check_prompt(*args, text: str | None = None, **kwargs) -> str:
    """
    Build a JSON-only self-check prompt used to detect unsafe content
    or hallucinations and produce a corrected draft.
    """
    body = (text or "").strip()
    return f"""
You are a critical reviewer for a ski-trip planning assistant. Analyze the draft below.
Return ONLY a single JSON object with this schema (no extra text, no code fences):

{{
  "is_safe": boolean,                 // false if harmful/illegal or disallowed content
  "has_hallucination": boolean,       // true if claims are unsupported by given inputs/sources
  "reasons": [string],                // concise bullet reasons (1–5 items)
  "fixed_text": string                // the draft with unsafe/unsupported parts removed or corrected
}}

Guidelines:
- Consider ski-safety constraints (wind closures, avalanche control, terrain difficulty).
- Prefer removal over speculation. If unsure, say so in "reasons" and neutralize the claim.
- Keep "fixed_text" short, actionable, and safe. If nothing to change, echo the original draft.

Draft to review:
{body}
""".strip()




def get_chain_of_thought_ski_planning_prompt(*, user_query: str, context: Dict[str, Any]) -> str:
    """
    Build a chain-of-thought prompt specifically for ski planning decisions.
    This implements structured multi-step reasoning for ski trip planning.
    """
    has_existing_plan = context.get('has_plan', False)
    plan_region = context.get('plan_region', 'None')
    conversation_history = context.get('conversation_history', [])

    # Build context summary
    context_summary = f"""
EXISTING CONTEXT:
- Current Plan: {'Yes' if has_existing_plan else 'No'}
- Plan Location: {plan_region}
- Conversation Turns: {len(conversation_history)}
"""

    if conversation_history:
        recent_exchanges = conversation_history[-2:]  # Last 2 exchanges
        context_summary += "\nRECENT CONVERSATION:"
        for i, exchange in enumerate(recent_exchanges, 1):
            user_msg = exchange.get('user_input', '')[:50]
            context_summary += f"\n{i}. User: {user_msg}..."

    return f"""
CHAIN-OF-THOUGHT SKI PLANNING REASONING

USER QUERY: "{user_query}"

{context_summary}

FOLLOW THIS STRUCTURED REASONING PROCESS:

STEP 1: QUERY ANALYSIS
- What is the user asking for? (information, planning, weather, comparison, etc.)
- What ski-specific parameters are mentioned? (location, dates, ability, preferences)
- Is this a new query or related to existing conversation?

STEP 2: CONTEXT EVALUATION
- Review existing plan details if any
- Consider seasonal factors (current time of year affects recommendations)
- Check for user preferences from conversation history

STEP 3: INFORMATION REQUIREMENTS
- What data do I need to answer this query?
- Which tools should I call and in what order?
- Are there any gaps that require clarification?

STEP 4: TOOL EXECUTION STRATEGY
- Primary tools: Wikipedia for resort info, Geoapify for location search
- Secondary tools: SkiAPI for detailed resort data, Open-Meteo for weather
- Fallback sequence: If primary fails, try secondary; if both fail, ask for clarification

STEP 5: DATA SYNTHESIS
- Combine information from multiple sources
- Cross-validate facts for consistency
- Identify key insights and recommendations

STEP 6: RESPONSE STRUCTURE
- Start with direct answer to the query
- Provide supporting facts from tools
- Include practical recommendations
- End with one clear follow-up question if more info needed

REASONING TRACE:
- Document your thought process at each step
- Explain tool selection rationale
- Note any assumptions made

FINAL RESPONSE:
- Keep ski-focused and enthusiastic
- Base all facts on tool results
- Be conversational and helpful

THINK STEP BY STEP, then provide your final response.
""".strip()

def get_chat_router_prompt(*, history: str, user_text: str) -> str:
    return f"""
You are a conversational ski-trip assistant. Decide what the user wants and ask for any missing info.

Return ONLY a JSON object:
{{
  "intent": "plan_trip" | "refine_plan" | "smalltalk" | "help",
  "slots": {{
    "origin": string|null,
    "region": string|null,
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "ability": "beginner"|"intermediate"|"advanced",
    "preferences": [string]|null
  }} | null,
  "missing": ["region"|"start_date"|"end_date"|"ability"|"origin"|"preferences"],
  "ask": string|null
}}

Rules:
- If user wants a plan, intent="plan_trip". Extract as many fields as possible.
- If anything important is missing, put those keys in "missing" and craft ONE concise friendly follow-up question in "ask".
- Dates MUST be YYYY-MM-DD. Ability MUST be beginner|intermediate|advanced.
- If casual chat, use "smalltalk". If asking how to use, use "help".
- Output ONLY JSON — no extra text.

Conversation so far:
{history}

Latest user message:
{user_text}
""".strip()
