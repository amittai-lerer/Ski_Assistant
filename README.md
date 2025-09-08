# SkiTrip Assistant

A conversational CLI assistant for planning ski vacations with weather and resort data integration.

## Overview

SkiTrip Assistant is a 3-day MVP that helps users plan short ski trips by:
- Integrating weather forecasts from Open-Meteo API
- Finding ski resorts through Foursquare Places API
- Ranking resorts by skiing conditions using deterministic algorithms
- Building detailed daily itineraries with activity suggestions
- Preventing hallucinations through multiple validation layers

## Key Features

### ✅ Assignment Requirements Met

- **Conversational Quality**: Natural language input with structured reasoning
- **Multi-turn Context**: Plan refinement and conversation memory
- **2+ External APIs**: Open-Meteo (weather) and Foursquare (resorts)
- **Hallucination Management**: Schema validation, source attribution, self-checking
- **Decision Logic**: Deterministic ranking based on snow, wind, and temperature

### 🛡️ Hallucination Prevention

- **Source Attribution**: Every claim includes source_id for verification
- **Schema Validation**: Pydantic models enforce data structure
- **Self-Checking**: LLM validates plans against evidence
- **Numeric Constraints**: Realistic limits on ski time and activity duration
- **API-Only Data**: No invented resort names, weather, or venue details

## Quick Start

### Installation

```bash
# Clone and setup
git clone <repository>
cd ski-assistant
make setup

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Environment Setup

```bash
# Copy environment template
cp config/.env.sample .env

# Edit .env with your API keys
OPENAI_API_KEY=sk-your-key-here
FOURSQUARE_API_KEY=fsq-your-key-here
```

### Usage Examples

```bash
# Plan a new trip
ski-assistant plan --region "Lake Tahoe" --dates 2025-12-20..2025-12-22 --ability intermediate

# Refine existing plan
ski-assistant refine --request "Add more après-ski activities"

# View plan info
ski-assistant info

# Clear saved plan
ski-assistant clear
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Input     │───▶│   Orchestrator   │───▶│   Rich Output   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Guardrails &    │
                    │  Validation      │
                    └──────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Open-Meteo API │◀───│  Data Fetching   │───▶│ Foursquare API  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Deterministic   │
                    │  Ranking &       │
                    │  Scoring         │
                    └──────────────────┘
```

### Data Flow

1. **Input Processing**: CLI parses flags or natural language
2. **Intent Extraction**: LLM extracts structured trip parameters
3. **Data Fetching**: Parallel API calls for resorts and weather
4. **Ranking**: Deterministic scoring based on skiing conditions
5. **Itinerary Building**: Daily schedules with activity suggestions
6. **Validation**: Multi-layer hallucination prevention
7. **Output**: Rich-formatted plan with source attribution

## Hallucination Controls

### Specific Checks Implemented

- **Source ID Verification**: Every external claim has provenance
- **Schema Validation**: Pydantic models prevent malformed data
- **Self-Check Prompt**: LLM identifies unsupported statements
- **Numeric Sanity**: Ski time ≤ 7.5h/day, realistic durations
- **Wind Thresholds**: Automatic wind-sheltered suggestions > 60 kph

### Example Validation

```python
# ✅ Valid: Has source_id
PlanStep(
    activity="Morning skiing",
    location="Heavenly Mountain Resort",
    source_id="fsq:venue_12345"
)

# ❌ Invalid: Missing source_id
PlanStep(
    activity="Morning skiing", 
    location="Heavenly Mountain Resort"
    # Missing source_id - validation fails
)
```

## Transcripts

Sample CLI sessions demonstrating different scenarios:

- [`transcripts/powder_day.md`](transcripts/powder_day.md) - High snowfall conditions
- [`transcripts/warm_spell.md`](transcripts/warm_spell.md) - Poor weather handling
- [`transcripts/beginner_group.md`](transcripts/beginner_group.md) - Family planning with refinement

## Testing

```bash
# Run all tests
make test

# Run specific test modules
python -m pytest tests/test_guardrails.py -v
python -m pytest tests/test_scorer.py -v
```

## Development

### Project Structure

```
ski-assistant/
├─ app/cli.py              # CLI entry point
├─ core/                   # Business logic
│  ├─ orchestrator.py      # Main coordination
│  ├─ prompts.py          # LLM prompts
│  ├─ reasoning.py        # LLM integration
│  ├─ guardrails.py       # Hallucination prevention
│  └─ memory.py           # Plan persistence
├─ apis/                   # External integrations
│  ├─ weather_openmeteo.py # Weather API
│  └─ places_foursquare.py # Resorts API
├─ models/schemas.py       # Data models
├─ ranking/scorer.py       # Deterministic ranking
├─ ui/renderers.py         # Rich output formatting
├─ config/                 # Configuration
│  ├─ settings.py         # Environment loading
│  └─ .env.sample         # Template
└─ tests/                  # Unit tests
```

### Key Design Decisions

- **Deterministic Ranking**: No LLM involvement in scoring decisions
- **Source Attribution**: Every external claim tracked with source_id
- **Mock Data**: Development mode uses fake data when APIs unavailable
- **Rich Output**: Beautiful terminal formatting with tables and colors
- **Multi-turn**: Plan persistence enables conversation refinement

## Future Work

- **Drive Times**: Integration with mapping APIs for travel planning
- **Lift Status**: Real-time lift and trail condition updates
- **Group Planning**: Multi-person trip coordination
- **Budget Integration**: Cost estimation and optimization
- **Advanced Weather**: Hourly forecasts and condition alerts

## License

MIT License - see LICENSE file for details.
```

