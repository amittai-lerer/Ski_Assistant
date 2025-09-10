# SkiTrip Assistant - Streamlit UI

A beautiful, production-ready web interface for your SkiTrip Assistant built with Streamlit.

## 🚀 Quick Start

### Option 1: Simple Launcher (Recommended)
```bash
python run_streamlit.py
```

### Option 2: Direct Streamlit Command
```bash
streamlit run app/streamlit_app.py
```

## 📋 Prerequisites

1. Install dependencies:
```bash
pip install -r requirements-streamlit.txt
```

2. Ensure your environment variables are set up (same as CLI version):
   - `OPENAI_API_KEY`
   - `GEOAPIFY_API_KEY`
   - `OPEN_METEO_API_KEY`
   - `RAPIDAPI_KEY` (optional, for SkiAPI)

## 🎯 Features

### ✨ Core Features
- **Real-time Chat**: Natural conversation flow with your SkiTrip Assistant
- **Persistent Sessions**: Conversation history maintained across page refreshes
- **Error Handling**: Graceful error messages with automatic recovery
- **Loading States**: Visual feedback during processing

### 🎨 User Interface
- **Warm & Clean Design**: Friendly chat interface with welcoming vibes
- **Responsive Layout**: Works beautifully on all devices
- **Message History**: Clean conversation view
- **Loading States**: Friendly "thinking" indicators
- **Example Questions**: One-click starters for inspiration
- **Prominent Text Input**: Natural question entry for all users
- **Flexible Interaction**: Choose between examples or type freely

### ⚙️ Simple Controls
- **Start New Chat**: Fresh conversation anytime
- **Clean Sidebar**: Focused on essential functions
- **Natural Input**: Free-form question entry

## 🛠️ Architecture

### Integration
- **Seamless Backend**: Uses existing `core.reasoning.llm_with_tools()` function
- **No Changes Required**: Backend logic remains untouched
- **Format Conversion**: Automatically converts between UI and backend data formats

### Conversation Flow
1. User types message
2. Message added to session history
3. History converted to backend format
4. Async call to `llm_with_tools()`
5. Response added to history and displayed
6. UI updates automatically

## 🔧 Technical Details

### Session Management
- **State Persistence**: Uses `st.session_state` for conversation history
- **Format Conversion**: Converts between UI dicts and backend expectations
- **Thread Safety**: Proper async handling with `asyncio.run()`

### Error Handling
- **Graceful Degradation**: User-friendly error messages
- **Logging**: Detailed error logging for debugging
- **Recovery**: Automatic error recovery where possible

### Performance
- **Minimal Overhead**: Lightweight wrapper around existing logic
- **Async Processing**: Non-blocking AI calls
- **Efficient Rendering**: Optimized Streamlit components

## 💬 Question Features

### **Welcome Experience**
New users see a clean, focused welcome with clear guidance:

- **Centered welcome message** inviting natural questions
- **Sidebar reference** for question inspiration
- **Prominent text input** for immediate interaction

### **Sidebar Examples**
6 friendly example questions available in the sidebar:

- 🏔️ **Tell me about skiing in Zermatt**
- 🌨️ **What's the snow forecast for Aspen?**
- 🎿 **Best beginner-friendly ski resorts**
- 🏠 **Luxury ski lodges in the Alps**
- ⛷️ **Compare Whistler vs Banff**
- 🎪 **Family ski resorts with activities**

### **Free-Form Input**
Always available: Type any natural question in the prominent text box for personalized responses!

## 🎯 Use Cases

Perfect for:
- **Demo Presentations**: Showcase your AI assistant's capabilities
- **User Testing**: Gather feedback on conversation quality
- **Development**: Debug and iterate on responses
- **Production**: Deploy as a web service
- **New Users**: Easy onboarding with example questions

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements-streamlit.txt
```

**API key errors:**
- Ensure `.env` file exists with required API keys
- Check API key validity and quotas

**Streamlit not starting:**
```bash
# Try specifying the Python path explicitly
python -m streamlit run app/streamlit_app.py
```

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📱 Mobile Support

The interface is fully responsive and works well on:
- 📱 Mobile phones
- 📟 Tablets
- 💻 Desktop computers
- 🖥️ Large screens

## 🔒 Security

- **Environment Variables**: API keys stored securely
- **Input Validation**: Basic input sanitization
- **Error Masking**: Sensitive information not exposed in errors

---

**Ready to chat with your SkiTrip Assistant!** ❄️🏂
