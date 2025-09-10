# app/streamlit_app.py
import asyncio
import streamlit as st
from typing import List, Dict, Any

from core.reasoning import llm_with_tools

# Page configuration
st.set_page_config(
    page_title="SkiTrip Assistant",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history: List[Dict[str, str]] = []

def to_reasoning_format(hist: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Convert UI history to llm_with_tools expected format."""
    out = []
    for t in hist:
        row = {"user_input": t["user"]}
        if "assistant" in t:
            row["assistant_response"] = t["assistant"]
        out.append(row)
    return out

# Main title
st.title("🏂 SkiTrip Assistant")

# Sidebar
with st.sidebar:
    st.header("🎯 Quick Actions")

    if st.button("🔄 Start New Chat", use_container_width=True):
        st.session_state.history = []
        st.success("✨ Fresh start!")

    st.divider()

    st.header("💡 Quick Questions")
    quick_questions = [
        "Weather forecast?",
        "Best time to visit?",
        "Lift ticket costs?",
        "Beginner-friendly resorts?"
    ]

    for q in quick_questions:
        if st.button(q, key=f"quick_{q}", use_container_width=True):
            st.session_state.selected_question = q

    st.divider()

    st.header("📊 Statistics")
    total_messages = len(st.session_state.history)
    st.metric("Total Messages", total_messages)

    if total_messages > 0:
        user_messages = len([h for h in st.session_state.history if "user" in h])
        assistant_messages = len([h for h in st.session_state.history if "assistant" in h])
        st.metric("Your Messages", user_messages)
        st.metric("Assistant Replies", assistant_messages)

    st.divider()

   

# Handle selected question from sidebar
if "selected_question" in st.session_state and st.session_state.selected_question:
    selected_q = st.session_state.selected_question
    del st.session_state.selected_question
    st.session_state.user_input = selected_q

# Show conversation history
for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["user"])
    if "assistant" in turn:
        with st.chat_message("assistant"):
            st.write(turn["assistant"])


# Handle user input from buttons or text
user_input = None

# Check if user clicked a button
if "user_input" in st.session_state and st.session_state.user_input:
    user_input = st.session_state.user_input
    del st.session_state.user_input

# Text input form (always visible)
st.markdown("---")

with st.form("chat_form", clear_on_submit=True):
    text_input = st.text_input(
        "Type your question:",
        placeholder="Example: Tell me about skiing in Aspen...",
        key="text_input"
    )
    submitted = st.form_submit_button("🚀 Send Message", type="primary")

    if submitted and text_input.strip():
        user_input = text_input.strip()

# Process any user input
if user_input:
    # Add to history
    st.session_state.history.append({"user": user_input})

    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Planning your ski trip…"):
            try:
                conv = to_reasoning_format(st.session_state.history)
                reply = asyncio.run(llm_with_tools(user_input, conversation_history=conv))
                st.write(reply)
                st.session_state.history[-1]["assistant"] = reply
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.history[-1]["assistant"] = error_msg
