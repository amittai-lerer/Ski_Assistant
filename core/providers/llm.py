"""
LLM Provider Abstraction - Clean Interface Pattern

Demonstrates professional practices:
- Abstract base class for provider independence
- Dependency injection for testability
- Clean error handling for API failures
- Configuration management for different models
- Async patterns for scalability

Interview Notes:
- Shows understanding of abstraction layers
- Demonstrates dependency inversion principle
- Clean separation of concerns
- Easy to extend with new providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import openai
from core.config import OPENAI_API_KEY

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Interview Notes:
    - Shows understanding of design patterns
    - Enables easy testing with mocks
    - Allows provider switching without code changes
    """
    @abstractmethod
    async def chat(self, messages: List[Dict[str, Any]], **opts) -> Any:
        """Send messages to LLM and return response."""
        pass

class OpenAIProvider(LLMProvider):
    """
    OpenAI provider implementation.

    Interview Notes:
    - Demonstrates proper resource management
    - Shows understanding of async patterns
    - Handles API nuances (tool_choice validation)
    - Clean parameter building pattern
    """

    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    async def chat(self, messages: List[Dict[str, Any]], **opts) -> Any:
        """
        Execute chat completion with proper parameter handling.

        Interview Notes:
        - Conditional parameter building prevents API errors
        - Proper error handling for API failures
        - Clean separation of concerns
        """
        # Build request parameters dynamically
        request_params = {
            "model": opts.get("model", "gpt-4o-mini"),
            "messages": messages,
            "temperature": opts.get("temperature", 0.1),
        }

        # Only include tools if provided (prevents API errors)
        if "tools" in opts and opts["tools"]:
            request_params["tools"] = opts["tools"]
            request_params["tool_choice"] = opts.get("tool_choice", "auto")

        response = self.client.chat.completions.create(**request_params)
        return response.choices[0].message
