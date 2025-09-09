#!/usr/bin/env python3
"""
Debug tool call handling
"""

import asyncio
import json
from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from core.reasoning import llm_with_tools

async def debug_tool_calls():
    """Debug tool call handling step by step."""

    print("🔧 DEBUGGING TOOL CALL HANDLING")
    print("=" * 40)

    # Simple test message
    user_message = "Tell me about Aspen Mountain"

    try:
        # This should trigger the Wikipedia tool
        result = await llm_with_tools(user_message, [])

        print("✅ Tool execution completed")
        print(f"Result type: {type(result)}")
        print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")

    except Exception as e:
        print(f"❌ Exception during tool execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_tool_calls())
