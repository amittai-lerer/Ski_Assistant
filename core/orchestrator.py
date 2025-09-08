"""
SkiTrip Assistant - Main Orchestrator

This module provides the main coordination logic for the SkiTrip Assistant.
It serves as the entry point for processing user queries and managing the
conversation flow using OpenAI tool calling.

Key Responsibilities:
- Process user input through the LLM with tool calling
- Manage conversation context and history
- Coordinate between different components
- Handle errors gracefully

Author: SkiTrip Assistant Team
License: MIT
"""

import logging
from typing import Dict, Any, Optional

from core.reasoning import llm_with_tools
from core.memory import load_last_plan, get_plan_info

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


def get_existing_plan_info() -> Optional[str]:
    """
    Get information about any existing saved ski trip plan.

    Returns:
        String with plan information if a plan exists, None otherwise
    """
    try:
        existing_plan = load_last_plan()
        if existing_plan:
            plan_info = get_plan_info()
            if plan_info and plan_info != "No plan found":
                return plan_info
    except Exception as e:
        logger.warning(f"Could not load existing plan: {e}")

    return None
