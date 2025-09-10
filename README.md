# SkiTrip Assistant

**Intelligent Conversational AI for Ski Trip Planning**

*Enterprise-Grade LLM Integration with Multi-API Orchestration*

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--green)](https://openai.com/)
[![APIs](https://img.shields.io/badge/APIs-4%20Integrated-orange)](apis/)

## 🎯 **OVERVIEW**

The SkiTrip Assistant is an intelligent conversational AI that helps users plan ski vacations through natural language interactions. It integrates multiple external APIs to provide accurate, real-time information about ski resorts, weather conditions, and trip planning.

### **Key Capabilities**
- ** Multi-turn Conversations**: Maintains context across interactions for natural dialogue

- **Intelligent Query Processing**: Handles resort information, trip planning, and weather queries

- **Real-time Data Integration**: Combines data from 4 external APIs (Geoapify, Open-Meteo, SkiAPI, Wikipedia)

- **Hallucination Prevention**: Multi-layer validation ensures factual responses

- **Fallback Mechanisms**: Automatic API switching when services are unavailable

## 🚀 **QUICK START**

### **Installation**
```bash
# Install Python dependencies
pip install -r requirements.txt

# For Streamlit web interface
pip install -r requirements-streamlit.txt
```

### **Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit with your real API keys
OPENAI_API_KEY=sk-your-actual-openai-key
GEOAPIFY_API_KEY=your-actual-geoapify-key
RAPIDAPI_KEY=your-actual-rapidapi-key
```

### **Run the Assistant**
```bash
# Terminal interface (Rich CLI)
python3 -m app.cli

# Web interface (Streamlit)
streamlit run app/streamlit_app.py

# Live demonstration
python3 demo_script.py
```

## 🏗️ **TECHNICAL ARCHITECTURE**

### **LLM Integration**
- **OpenAI GPT-4o-mini** with function calling capabilities
- **5-phase Chain-of-Thought** reasoning process
- **Multi-layer Hallucination Prevention** with evidence validation
- **Provider Abstraction** for LLM interchangeability

### **API Orchestration**
- **4 Production APIs**: Geoapify Places, Open-Meteo Weather, SkiAPI, Wikipedia
- **Intelligent Routing**: Context-aware API selection based on query type
- **Automatic Fallbacks**: Seamless service switching when APIs fail
- **Type-Safe Integration**: Pydantic models for all API interactions
- **Rate Limiting**: Sophisticated quota management with user notifications

### **Design Patterns**
- **Clean Architecture**: Strict separation of concerns across layers
- **Registry Pattern**: Centralized API tool management
- **Async/Await**: Concurrent API operations for performance
- **Environment Configuration**: Secure credential management

## 📁 **PROJECT STRUCTURE**

```
SkiTrip Assistant/
├── 📄 __init__.py                    # Package initialization
├── 📄 .env                          # Environment variables (gitignored)
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 pyproject.toml               # Project configuration
├── 📄 requirements.txt             # Python dependencies
├── 📄 requirements-streamlit.txt   # Streamlit dependencies
├── 📄 README.md                    # Project documentation
├── 📄 conversation_transcripts.md  # Assignment transcripts
├── 📄 demo_script.py              # Live demonstration
├── 📄 interview_presentation.md    # Interview preparation
│
├── 📁 apis/                        # External API Integrations
│   ├── 📄 geoapify_resorts.py      # Geoapify Places API
│   ├── 📄 weather_openmeteo.py     # Open-Meteo Weather API
│   ├── 📄 skiapi_resorts.py        # SkiAPI (RapidAPI)
│   └── 📄 wikipedia_resorts.py     # Wikipedia API
│
├── 📁 core/                        # Business Logic & Orchestration
│   ├── 📄 reasoning.py             # 5-Phase LLM Orchestrator
│   ├── 📄 prompts.py               # Advanced Prompt Engineering
│   ├── 📄 tools.py                 # API Tool Registry & Dispatcher
│   ├── 📄 config.py                # Environment Configuration
│   └── 📁 providers/               # LLM Provider Abstraction
│       └── 📄 llm.py               # OpenAI Provider Implementation
│
├── 📁 app/                         # User Interface Layer
│   ├── 📄 cli.py                   # Rich Terminal Interface
│   └── 📄 streamlit_app.py         # Web Chat Interface
│
└── 📁 utils/                       # Utility Functions
    ├── 📄 dates.py                 # Date Normalization Utilities
    └── 📄 errors.py                # Error Handling Helpers
```



### **Core Requirements**


| **Assistant Purpose** | 3+ query types (resort info, trip planning, weather) 
| **Context & Continuity** | Multi-turn conversations with conversation history 
| **Interaction Flow** | Natural, helpful, accurate responses 
| **Advanced Prompt Engineering** | 5-phase chain-of-thought reasoning 
| **External Data Integration** | 4 production APIs with intelligent routing 
| **Hallucination Management** | 3-layer validation system 

### **🔧 Technical Implementation**

- **Programming Language**: Python 3.8+ with comprehensive async/await
- **LLM Integration**: OpenAI GPT-4o-mini with function calling
- **User Interface**: Professional Rich CLI + Streamlit web interface
- **Error Handling**: Robust exception management with graceful degradation
- **Security**: Environment-based credential management

## 📚 **DEMONSTRATIONS & DOCUMENTATION**

- **[📄 Conversation Transcripts](conversation_transcripts.md)** - Complete interaction examples demonstrating assignment requirements
- **[📄 Demo Script](demo_script.py)** - Live functionality showcase with automated demonstrations

