# 🎿 SkiTrip Assistant

*A conversational AI assistant for planning ski vacations with real-time resort data*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)

## ✨ Overview

SkiTrip Assistant is an intelligent conversational CLI tool that helps users discover ski resorts and plan amazing ski vacations. Built with cutting-edge AI technology, it combines:

- 🤖 **OpenAI GPT-4o-mini** for natural language understanding
- 🏔️ **Geoapify Places API** for real-time resort data
- 🎯 **Tool calling** for structured API interactions
- 🛡️ **Hallucination prevention** through source attribution
- 💬 **Conversational interface** with rich terminal output

## 🚀 Key Features

### ✅ Core Capabilities
- **Natural Conversations**: Chat naturally about ski trips and resorts
- **Real Data Integration**: Fetches live resort information from Geoapify
- **Smart Fallbacks**: Provides expert knowledge when APIs are unavailable
- **Multi-turn Context**: Remembers conversation history
- **Beautiful Output**: Rich terminal formatting with colors and emojis

### 🛡️ Reliability Features
- **Source Attribution**: Every recommendation includes data source
- **Error Handling**: Graceful degradation with helpful alternatives
- **API Validation**: Robust error handling for external services
- **Fallback Knowledge**: Expert ski destination recommendations

### 🎯 Assignment Compliance
- ✅ **Conversational Quality**: Natural language processing with GPT-4
- ✅ **External API Integration**: **2 APIs** - Geoapify (resorts) + Open-Meteo (weather)
- ✅ **Tool Calling**: OpenAI function calling for structured interactions
- ✅ **Hallucination Management**: Source attribution and validation
- ✅ **Real Data**: Live data from both APIs, no invented information

## 🏁 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Geoapify API key (free tier available)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ski-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Environment Setup

Create a `.env` file in the project root:

```bash
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
GEOAPIFY_API_KEY=your-geoapify-api-key-here

# Optional Configuration
OPEN_METEO_BASE=https://api.open-meteo.com/v1/forecast
TIMEOUT_S=15
ENV=development
```

### Get API Keys

1. **OpenAI API Key**: Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **Geoapify API Key**: Visit [geoapify.com](https://www.geoapify.com/) (3000 free requests/day)

### Run the Assistant

```bash
# Start the interactive assistant
python -m app.cli

# Or use the alternative entry point
python main.py
```

## 💬 Usage Examples

### Interactive Conversations

```
🎿 Welcome to SkiTrip Assistant! 🎿

You: Find ski resorts near Chamonix

Assistant: While I couldn't find specific resorts in Chamonix, it's legendary for its challenging slopes and stunning Mont Blanc views. Consider exploring nearby areas such as Val d'Isère, Courchevel, and Les Trois Vallées for excellent skiing opportunities.

You: Tell me about Lake Tahoe

Assistant: Lake Tahoe has fantastic skiing! It has excellent snow conditions and diverse terrain. Heavenly Mountain Resort is a highlight with stunning lake views. Other popular areas include Northstar California Resort, Kirkwood Mountain Resort, and Squaw Valley Alpine Meadows.

You: What about Switzerland?

Assistant: Switzerland is world-famous for skiing! Consider these top destinations: Zermatt (Matterhorn views), St. Moritz (luxury skiing), Verbier (off-piste paradise), and Interlaken (gateway to the Jungfrau region).
```

### Programmatic Usage

```python
from core.orchestrator import run
import asyncio

async def plan_trip():
    result = await run("Find ski resorts near Zermatt", {})
    print(result)

asyncio.run(plan_trip())
```

## 🏗️ Architecture

### System Design

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   CLI Interface  │───▶│   Rich Output   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Orchestrator    │
                    │  (Coordinates)   │
                    └──────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenAI GPT    │◀───│  Tool Calling    │───▶│ Geoapify API   │
│   (Reasoning)   │    │   (Dispatcher)   │    │  (Resorts)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Fallback       │
                    │   Knowledge      │
                    └──────────────────┘
```

### Core Components

- **`app/cli.py`**: Main conversational interface with rich terminal output
- **`core/reasoning.py`**: OpenAI integration with tool calling capabilities
- **`core/orchestrator.py`**: Coordinates between components
- **`apis/geoapify_resorts.py`**: Geoapify Places API integration
- **`core/memory.py`**: Conversation history and plan persistence

### Data Flow

1. **User Input** → CLI interface parses and formats
2. **Intent Recognition** → LLM analyzes query for ski-related intent
3. **Tool Calling** → LLM calls `find_resorts_geoapify` with location
4. **API Execution** → Geoapify API returns resort data
5. **Response Generation** → LLM summarizes results naturally
6. **Fallback Handling** → Expert knowledge if APIs unavailable

## 🧪 Testing

### Run All Tests
```bash
# Run the test suite
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_guardrails.py -v
```

### Manual Testing
```bash
# Test Geoapify integration
python test_geoapify.py

# Test with real data
python test_with_real_data.py
```

### API Testing
```bash
# Test OpenAI integration
python -c "from core.reasoning import llm_with_tools; import asyncio; print(asyncio.run(llm_with_tools('Hello')))"

# Test Geoapify API
python -c "from apis.geoapify_resorts import find_resorts_geoapify; import asyncio; print(asyncio.run(find_resorts_geoapify(city='Zermatt')))"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | ✅ |
| `GEOAPIFY_API_KEY` | Geoapify API key for resort data | ✅ |
| `OPEN_METEO_BASE` | Open-Meteo API base URL | ❌ |
| `TIMEOUT_S` | API request timeout in seconds | ❌ |
| `ENV` | Environment (development/production) | ❌ |

### Advanced Settings

Edit `config/settings.py` to modify:
- Model selection (`OPENAI_MODEL`)
- Temperature settings (`LLM_TEMPERATURE`)
- Retry logic (`LLM_MAX_RETRIES`)
- Logging levels

## 📁 Project Structure

```
ski-assistant/
├── app/
│   └── cli.py                 # Main CLI interface
├── core/
│   ├── reasoning.py           # OpenAI tool calling & LLM integration
│   ├── orchestrator.py        # Main coordination logic
│   ├── memory.py              # Conversation persistence
│   └── prompts.py             # System prompts and templates
├── apis/
│   ├── geoapify_resorts.py    # Geoapify Places API integration
│   └── weather_openmeteo.py   # Weather API (future use)
├── models/
│   └── schemas.py             # Pydantic data models
├── config/
│   └── settings.py            # Environment configuration
├── ranking/
│   └── scorer.py              # Resort ranking algorithms
├── ui/
│   └── renderers.py           # Output formatting
├── tests/
│   ├── test_guardrails.py     # Validation tests
│   └── test_scorer.py         # Ranking tests
├── transcripts/               # Sample conversations
├── main.py                    # Alternative entry point
├── pyproject.toml             # Project configuration
├── requirements.txt           # Dependencies
├── .env                       # Environment variables (gitignored)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🎯 Key Technologies

- **Python 3.8+**: Core language
- **OpenAI GPT-4o-mini**: Conversational AI and tool calling
- **Geoapify Places API**: Real-time resort and activity data
- **Rich**: Beautiful terminal output formatting
- **Pydantic**: Data validation and serialization
- **httpx**: Modern async HTTP client
- **python-dotenv**: Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and tool calling capabilities
- **Geoapify** for comprehensive places and resort data
- **Rich** library for beautiful terminal interfaces
- **Pydantic** for robust data validation

---

## 🆕 Latest Features & Enhancements

### 🧠 Advanced LLM Integration
- **Tool Calling**: OpenAI function calling for seamless API interactions
- **Multi-API Orchestration**: Coordinates 4 different APIs simultaneously
- **Intelligent Query Routing**: Automatically selects optimal APIs for user queries

### 🔄 Robust Error Handling & Fallbacks
- **Rate Limit Management**: Short, informative notices for API quota exceeded
- **Automatic Wikipedia Fallback**: Seamless transition when SkiAPI is rate-limited
- **Graceful Degradation**: Continues providing value despite API limitations
- **User-Friendly Messages**: Clear, actionable error communications

### 📚 Wikipedia Integration
- **Comprehensive Resort Coverage**: Background info for major ski destinations
- **Fallback Support**: Automatic activation when SkiAPI is unavailable
- **Rich Historical Content**: Geographical, historical, and operational details
- **Smart Name Resolution**: Handles alternative resort name spellings

### 🎿 Enhanced Ski Information System
- **Multi-Source Intelligence**: Combines data from 4 complementary APIs
- **Real-time Weather**: Current conditions optimized for skiing
- **Detailed Resort Database**: Comprehensive info via SkiAPI with Wikipedia backup
- **Location Intelligence**: Precise coordinates and regional context

### 🛠️ Complete API Stack
- **🤖 OpenAI GPT-4**: Intelligent conversation and tool orchestration
- **🏔️ Geoapify Places API**: Resort discovery and location intelligence
- **🌤️ Open-Meteo Weather API**: Ski-optimized weather forecasting
- **📖 Wikipedia API**: Comprehensive resort background information
- **🎿 SkiAPI (RapidAPI)**: Detailed resort database with automatic fallback

## 🧪 Enhanced Testing Suite

### Comprehensive API Testing
```bash
# Test all 4 APIs integration
python test_all_apis.py

# Test Wikipedia fallback functionality
python test_wikipedia_integration.py

# Test error handling scenarios
python test_error_fallback.py

# Validate RapidAPI key setup
python test_rapidapi_key.py
```

### Error Handling Examples
- **Rate Limited**: "Using Wikipedia info (SkiAPI rate limit exceeded)"
- **Auth Failed**: "SkiAPI authentication failed. Please check your RAPIDAPI_KEY"
- **Wikipedia Success**: Automatic detailed resort information from Wikipedia

## 🔧 Environment Configuration

Create a `.env` file with all required API keys:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_key_here
GEOAPIFY_API_KEY=your_geoapify_key_here
RAPIDAPI_KEY=your_rapidapi_key_here

# Optional Configuration
ENV=dev
DEBUG=1
USE_REAL_OPENAI=1
USE_REAL_OPEN_METEO=1
```

---

**Ready to experience the most advanced ski planning assistant?** 🎿❄️

```bash
python -m app.cli
# Advanced AI-powered ski trip planning with comprehensive resort intelligence!
```
```

