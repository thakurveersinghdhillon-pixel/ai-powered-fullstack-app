from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional, Type
from pydantic import BaseModel
from app.services.llm.types import LLMMessage, LLMChunk, LLMResult


class BaseLLMProvider(ABC):
    """Abstract interface for LLM provider implementations (OpenAI, Gemini, Anthropic, Mock)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name (e.g. 'openai', 'mock')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Returns the default model identifier."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        model: Optional[str] = None,
    ) -> LLMResult:
        """Generates a complete non-streaming AI response."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[LLMChunk, None]:
        """Streams AI tokens as an AsyncGenerator yielding LLMChunk objects."""
        pass
