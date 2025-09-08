"""UI rendering for SkiTrip Assistant."""

from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from models.schemas import Itinerary, ConversationResponse

console = Console()

def render_conversation(response: str, needs_info: bool = False, missing_fields: List[str] = None) -> str:
    """Render a conversational response."""
    if needs_info and missing_fields:
        text = Text(response, style="yellow")
        text.append(f"\n\nI still need: {', '.join(missing_fields)}", style="dim")
    else:
        text = Text(response, style="green")
    
    panel = Panel(text, title="Assistant", border_style="blue")
    console.print(panel)
    return response

def render_plan(itinerary: Itinerary) -> str:
    """Render a ski trip plan."""
    # Create a simple table
    table = Table(title=f"Ski Trip to {itinerary.region}")
    table.add_column("Date", style="cyan")
    table.add_column("Morning", style="green")
    table.add_column("Lunch", style="yellow")
    table.add_column("Afternoon", style="green")
    
    for day in itinerary.days:
        table.add_row(
            str(day.date),
            day.morning.activity,
            day.lunch.activity,
            day.afternoon.activity
        )
    
    console.print(table)
    return f"Here's your ski trip plan for {itinerary.region}!"


