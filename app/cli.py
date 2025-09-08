"""Conversational CLI for SkiTrip Assistant."""

import asyncio
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from core.orchestrator import run
from core.memory import load_last_plan, get_plan_info

console = Console()
logger = logging.getLogger(__name__)


def main():
    """Main entry point with full conversation context."""
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

    # Initialize conversation context
    conversation_context = {
        'conversation_history': [],
        'start_time': datetime.now().isoformat(),
        'interaction_count': 0
    }

    # Load any existing plan
    existing_plan = load_last_plan()
    if existing_plan:
        plan_info = get_plan_info()
        if plan_info and plan_info != "No plan found":
            console.print(f"\n[green]📋 {plan_info}[/green]")
            console.print("[dim]You can ask me to show it, modify it, or start a new one.[/dim]")

    while True:
        try:
            # Show conversation prompt with context
            prompt_text = "\n[bold blue]You[/bold blue]"
            if conversation_context['interaction_count'] > 0:
                prompt_text += f" [dim]({conversation_context['interaction_count']} exchanges)[/dim]"
            if existing_plan:
                prompt_text += " [dim](plan active)[/dim]"

            user_input = Prompt.ask(prompt_text)

            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                console.print("\n[green]Thanks for planning with me! Have an amazing ski trip! 🎿[/green]")
                if conversation_context['interaction_count'] > 0:
                    console.print(f"[dim]We had {conversation_context['interaction_count']} exchanges in this conversation.[/dim]")
                break

            if not user_input.strip():
                continue

            # Update conversation context
            conversation_context['interaction_count'] += 1
            conversation_context['last_input'] = user_input
            conversation_context['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'turn_number': conversation_context['interaction_count']
            })

            # Process with orchestrator (maintain full context)
            console.print("\n[bold magenta]Assistant:[/bold magenta] ", end="")
            result = asyncio.run(run(user_input, conversation_context))

            # Display result with better formatting
            if result and len(result.strip()) > 0:
                # If result contains a table or structured output, print as-is
                if '\n┏' in result or '\n┡' in result:
                    console.print(result)
                else:
                    console.print(result)
            else:
                console.print("[dim]I understood your request, but don't have a response ready. Could you rephrase?[/dim]")

            # Update context with assistant response
            conversation_context['conversation_history'][-1]['assistant_response'] = result

        except KeyboardInterrupt:
            console.print("\n[green]Conversation ended. Safe travels! 👋[/green]")
            break
        except Exception as e:
            console.print(f"\n[red]Oops! Something went wrong: {e}[/red]")
            console.print("[dim]Try rephrasing your request or start over.[/dim]")
            logger.error(f"Error in conversation loop: {e}")

            # Continue the conversation despite errors
            continue


if __name__ == "__main__":
    main()
