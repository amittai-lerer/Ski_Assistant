"""Simple conversational orchestrator for SkiTrip Assistant."""

import logging
from datetime import date, timedelta
from typing import Dict, List, Any, Optional

from models.schemas import TripSlots, Itinerary, DayPlan, PlanStep, AbilityLevel, ConversationResponse
from core.reasoning import llm_with_tools
from core.guardrails import verify_and_prune
from core.memory import save_last_plan, load_last_plan, get_plan_info
from apis.weather_openmeteo import get_forecast
from apis.places_foursquare import search_resorts
from ranking.scorer import rank_resorts
from ui.renderers import render_plan, render_conversation

logger = logging.getLogger(__name__)

async def run(user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Main conversational entry point using tool calling.

    Args:
        user_input: What the user said
        context: Optional context from previous interactions

    Returns:
        Assistant's response
    """
    try:
        # Get conversation context
        conversation_history = context.get('conversation_history', []) if context else []

        # Use LLM with tool calling for natural conversation
        response = await llm_with_tools(user_input, conversation_history)

        # Return the natural language response
        return response

    except Exception as e:
        logger.error(f"Error in run: {e}")
        return "Sorry, I had trouble with that. Could you try rephrasing?"

async def _handle_planning(slots: TripSlots, conversation_history: List[str]) -> str:
    """Handle trip planning request."""
    try:
        # Validate we have enough info
        if not slots.region or not slots.start_date or not slots.end_date or not slots.ability:
            missing = []
            if not slots.region: missing.append("region")
            if not slots.start_date: missing.append("start_date") 
            if not slots.end_date: missing.append("end_date")
            if not slots.ability: missing.append("ability")
            
            return render_conversation(
                f"I'd love to help plan your ski trip! I need a bit more information: {', '.join(missing)}. Could you tell me more about these?",
                needs_info=True,
                missing_fields=missing
            )
        
        # Get resorts
        resorts = await search_resorts(slots.region)
        if not resorts:
            return render_conversation(f"I couldn't find any ski resorts in {slots.region}. Could you try a different region?")
        
        # Get weather for each resort
        weather_data = {}
        for resort in resorts:
            try:
                forecast = await get_forecast(resort.latitude, resort.longitude, slots.start_date, slots.end_date)
                weather_data[resort.name] = forecast
            except Exception as e:
                logger.warning(f"Could not get weather for {resort.name}: {e}")
        
        # Rank resorts
        ranked_resorts = rank_resorts(resorts, weather_data)
        
        # Build itinerary
        itinerary = _build_itinerary(slots, ranked_resorts, weather_data)

        # Build evidence for verification
        evidence = {
            'resorts': resorts,
            'weather_data': weather_data,
            'ranked_resorts': ranked_resorts
        }

        # Verify and prune
        verified_itinerary = verify_and_prune(itinerary, evidence)
        
        # Save plan
        save_last_plan(verified_itinerary)
        
        # Render response
        return render_plan(verified_itinerary)
        
    except Exception as e:
        logger.error(f"Error in planning: {e}")
        return "Sorry, I had trouble planning your trip. Could you try again?"

async def _handle_refinement(user_input: str, last_plan: Itinerary, conversation_history: List[str]) -> str:
    """Handle plan refinement request."""
    try:
        # For now, just return the current plan
        # In a full implementation, you'd use the LLM to modify the plan
        return render_plan(last_plan)
    except Exception as e:
        logger.error(f"Error in refinement: {e}")
        return "Sorry, I had trouble refining your plan. Could you try again?"

async def _handle_clear(conversation_history: List[str]) -> str:
    """Handle clear request."""
    try:
        # Clear the last plan
        save_last_plan(None)
        return render_conversation("I've cleared your last plan. Ready to help with a new one!")
    except Exception as e:
        logger.error(f"Error in clear: {e}")
        return "Sorry, I had trouble clearing your plan. Could you try again?"

def _build_itinerary(slots: TripSlots, resorts: List, weather_data: Dict) -> Itinerary:
    """Build a basic itinerary."""
    # This is a simplified version - in reality you'd use the LLM to build a detailed itinerary
    days = []
    current_date = slots.start_date
    
    while current_date <= slots.end_date:
        # Get the best resort for this day
        best_resort = resorts[0] if resorts else None
        weather = weather_data.get(best_resort.name, []) if best_resort else []
        
        # Create a simple day plan
        day_plan = DayPlan(
            date=current_date,
            morning=PlanStep(
                time="9:00 AM",
                activity="Skiing",
                description=f"Morning skiing at {best_resort.name}",
                source_id="assistant"
            ),
            lunch=PlanStep(
                time="12:00 PM", 
                activity="Lunch",
                description=f"Lunch at {best_resort.name} lodge",
                source_id="assistant"
            ),
            afternoon=PlanStep(
                time="2:00 PM",
                activity="Skiing", 
                description=f"Afternoon skiing at {best_resort.name}",
                source_id="assistant"
            ),
            weather=weather[0] if weather else None,
            resort=best_resort
        )
        
        days.append(day_plan)
        current_date += timedelta(days=1)
    
    return Itinerary(
        region=slots.region,
        start_date=slots.start_date,
        end_date=slots.end_date,
        ability=slots.ability,
        days=days,
        source_id="assistant"
    )
