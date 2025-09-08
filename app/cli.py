"""
SkiTrip Assistant - Conversational CLI Interface

This module provides the main command-line interface for the SkiTrip Assistant,
a conversational AI that helps users plan ski vacations with real-time data
from external APIs.

Features:
- Natural language conversation about ski trips
- Integration with Geoapify API for resort information
- Intelligent fallback responses with ski destination knowledge
- Conversation history and context management
- Rich terminal output with colors and formatting

Usage:
    python -m app.cli
    # or
    python main.py (if created)

Author: SkiTrip Assistant Team
License: MIT
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from core.orchestrator import run
from core.memory import load_last_plan, get_plan_info

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Rich console for beautiful terminal output
console = Console()


def display_welcome_message() -> None:
    """
    Display the welcome message and usage instructions.

    This function shows the initial welcome panel with information about
    how to use the SkiTrip Assistant.
    """
    console.print(Panel(
        "🎿 Welcome to SkiTrip Assistant! 🎿\n\n"
        "Let's plan your perfect ski trip together!\n\n"
        "💬 You can:\n"
        "• Tell me about your ski trip ideas\n"
        "• Ask questions about your current plan\n"
        "• Modify or refine your itinerary\n"
        "• Get weather and resort information\n\n"
        "Try: 'I want to plan a ski trip to Lake Tahoe for 3 days'",
        title="SkiTrip Assistant",
        border_style="blue"
    ))


def initialize_conversation_context() -> Dict[str, Any]:
    """
    Initialize the conversation context dictionary.

    Returns:
        Dict containing conversation metadata and history
    """
    return {
        'conversation_history': [],
        'start_time': datetime.now().isoformat(),
        'interaction_count': 0
    }


def load_existing_plan() -> Optional[Any]:
    """
    Load any existing ski trip plan from memory.

    Returns:
        The loaded plan object if exists, None otherwise
    """
    return load_last_plan()


def display_existing_plan_info(plan_info: str) -> None:
    """
    Display information about an existing plan.

    Args:
        plan_info: String containing plan information to display
    """
    if plan_info and plan_info != "No plan found":
        console.print(f"\n[green]📋 {plan_info}[/green]")
        console.print("[dim]You can ask me to show it, modify it, or start a new one.[/dim]")


def create_conversation_prompt(context: Dict[str, Any], has_existing_plan: bool) -> str:
    """
    Create the conversation prompt with context information.

    Args:
        context: Conversation context dictionary
        has_existing_plan: Whether there's an existing plan loaded

    Returns:
        Formatted prompt string
    """
    prompt_text = "\n[bold blue]You[/bold blue]"

    if context['interaction_count'] > 0:
        prompt_text += f" [dim]({context['interaction_count']} exchanges)[/dim]"

    if has_existing_plan:
        prompt_text += " [dim](plan active)[/dim]"

    return prompt_text


def handle_user_input(user_input: str, context: Dict[str, Any]) -> bool:
    """
    Handle user input and determine if conversation should continue.

    Args:
        user_input: The user's input text
        context: Conversation context dictionary

    Returns:
        True if conversation should continue, False if should exit
    """
    if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
        console.print("\n[green]Thanks for planning with me! Have an amazing ski trip! 🎿[/green]")
        if context['interaction_count'] > 0:
            console.print(f"[dim]We had {context['interaction_count']} exchanges in this conversation.[/dim]")
        return False

    return True


def update_conversation_context(context: Dict[str, Any], user_input: str) -> None:
    """
    Update the conversation context with new user input.

    Args:
        context: Conversation context dictionary to update
        user_input: The user's input text
    """
    context['interaction_count'] += 1
    context['last_input'] = user_input
    context['conversation_history'].append({
        'timestamp': datetime.now().isoformat(),
        'user_input': user_input,
        'turn_number': context['interaction_count']
    })


async def process_assistant_response(user_input: str, context: Dict[str, Any]) -> str:
    """
    Process the user input through the orchestrator and get assistant response.

    Args:
        user_input: The user's input text
        context: Conversation context dictionary

    Returns:
        Assistant's response text
    """
    try:
        result = await run(user_input, context)
        return result if result else "[dim]I understood your request, but don't have a response ready. Could you rephrase?[/dim]"
    except Exception as e:
        logger.error(f"Error processing assistant response: {e}")
        return f"[red]Oops! Something went wrong: {e}[/red]\n[dim]Try rephrasing your request or start over.[/dim]"


def display_assistant_response(response: str) -> None:
    """
    Display the assistant's response with appropriate formatting.

    Args:
        response: The assistant's response text
    """
    console.print("\n[bold magenta]Assistant:[/bold magenta] ", end="")

    # Handle structured output (tables) differently
    if '\n┏' in response or '\n┡' in response:
        console.print(response)
    else:
        console.print(response)


def handle_conversation_error(error: Exception) -> None:
    """
    Handle errors that occur during the conversation loop.

    Args:
        error: The exception that occurred
    """
    console.print(f"\n[red]Oops! Something went wrong: {error}[/red]")
    console.print("[dim]Try rephrasing your request or start over.[/dim]")
    logger.error(f"Error in conversation loop: {error}")


def main() -> None:
    """
    Main entry point for the SkiTrip Assistant CLI.

    This function initializes the conversation interface, loads any existing plans,
    and runs the main conversation loop.
    """
    # Display welcome message
    display_welcome_message()

    # Initialize conversation context
    conversation_context = initialize_conversation_context()

    # Load any existing plan
    existing_plan = load_existing_plan()
    if existing_plan:
        plan_info = get_plan_info()
        display_existing_plan_info(plan_info)

    # Main conversation loop
    while True:
        try:
            # Create and display conversation prompt
            prompt_text = create_conversation_prompt(conversation_context, bool(existing_plan))
            user_input = Prompt.ask(prompt_text)

            # Handle exit commands
            if not handle_user_input(user_input, conversation_context):
                break

            # Skip empty input
            if not user_input.strip():
                continue

            # Update conversation context
            update_conversation_context(conversation_context, user_input)

            # Process user input and get response
            response = asyncio.run(process_assistant_response(user_input, conversation_context))

            # Display response
            display_assistant_response(response)

            # Update context with assistant response
            conversation_context['conversation_history'][-1]['assistant_response'] = response

        except KeyboardInterrupt:
            console.print("\n[green]Conversation ended. Safe travels! 👋[/green]")
            break
        except Exception as e:
            handle_conversation_error(e)
            continue


if __name__ == "__main__":
    main()
