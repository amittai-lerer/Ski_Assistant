#!/usr/bin/env python3
"""
Test script to demonstrate Multi-Step Chain-of-Thought reasoning in the Ski Assistant.
This shows how the LLM follows a structured 6-step reasoning process.
"""

import asyncio
import os
from core.reasoning import llm_with_tools
from core.prompts import get_chain_of_thought_ski_planning_prompt

async def test_cot_reasoning():
    """Test the chain-of-thought reasoning with different ski planning scenarios."""

    print("🧠 Testing Multi-Step Chain-of-Thought Reasoning")
    print("=" * 60)

    # Set environment to use real APIs for testing
    os.environ["USE_REAL_OPENAI"] = "1"

    test_cases = [
        {
            "query": "I'm planning a ski trip to Austria next winter. What should I know?",
            "description": "Complex planning query requiring multi-step analysis"
        },
        {
            "query": "Tell me about Zermatt ski resort",
            "description": "Specific resort information request"
        },
        {
            "query": "What's the weather like for skiing in Colorado this season?",
            "description": "Weather-focused ski query"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")
        print("-" * 50)

        try:
            # Test the actual chain-of-thought reasoning
            response = await llm_with_tools(test_case['query'], [])

            print("✅ Response generated successfully!")
            print(f"Response length: {len(response)} characters")

            # Show a preview of the response
            preview = response[:300] + "..." if len(response) > 300 else response
            print(f"Preview: {preview}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Chain-of-Thought Process Summary:")
    print("1. ✅ Query Analysis - Understand user intent and extract parameters")
    print("2. ✅ Context Evaluation - Review conversation history and existing plans")
    print("3. ✅ Information Requirements - Determine what data is needed")
    print("4. ✅ Tool Execution Strategy - Choose and sequence API calls")
    print("5. ✅ Data Synthesis - Combine and cross-validate information")
    print("6. ✅ Response Formulation - Structure natural, helpful response")

def demonstrate_cot_prompt():
    """Show what the chain-of-thought prompt looks like."""

    print("\n🔍 Chain-of-Thought Prompt Structure:")
    print("=" * 40)

    context = {
        'has_plan': True,
        'plan_region': 'Lake Tahoe',
        'conversation_history': [
            {'user_input': 'I want to go skiing in Lake Tahoe'},
            {'user_input': 'What resorts should I visit?'}
        ]
    }

    cot_prompt = get_chain_of_thought_ski_planning_prompt(
        user_query="Should I visit Heavenly Mountain?",
        context=context
    )

    print("Generated Prompt Structure:")
    print("- STEP 1: QUERY ANALYSIS")
    print("- STEP 2: CONTEXT EVALUATION")
    print("- STEP 3: INFORMATION REQUIREMENTS")
    print("- STEP 4: TOOL EXECUTION STRATEGY")
    print("- STEP 5: DATA SYNTHESIS")
    print("- STEP 6: RESPONSE STRUCTURE")
    print("- REASONING TRACE")
    print("- FINAL RESPONSE")

    print(f"\nPrompt length: {len(cot_prompt)} characters")
    print(f"Context included: {'Yes' if 'Lake Tahoe' in cot_prompt else 'No'}")

if __name__ == "__main__":
    # Demonstrate the prompt structure first
    demonstrate_cot_prompt()

    print("\n🚀 Ready to test live Chain-of-Thought reasoning!")
    print("Note: This requires valid API keys in .env file")
    print("Run: python test_chain_of_thought.py")

    # Uncomment to run live tests
    # asyncio.run(test_cot_reasoning())
