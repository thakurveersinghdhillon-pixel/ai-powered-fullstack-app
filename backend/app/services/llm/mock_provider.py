import asyncio
import json
from typing import AsyncGenerator, List, Optional, Type
from pydantic import BaseModel

from app.services.llm.base import BaseLLMProvider
from app.services.llm.types import LLMMessage, LLMChunk, LLMResult
from app.services.llm.exceptions import LLMStructuredOutputError


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for deterministic offline testing and verification."""

    def __init__(self, mock_response: str = "This is a mocked AI assistant response for testing.", delay_ms: float = 10):
        self.mock_response = mock_response
        self.delay_ms = delay_ms

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-gpt-4"

    async def generate_response(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        model: Optional[str] = None,
    ) -> LLMResult:
        await asyncio.sleep(self.delay_ms / 1000.0)
        
        parsed_json = None
        content = self.mock_response

        if response_format is not None:
            # Generate valid JSON for model format if requested
            dummy_json = {"summary": "Mock summary", "confidence": 0.99, "status": "ok"}
            try:
                validated = response_format.model_validate(dummy_json)
                parsed_json = validated.model_dump()
                content = json.dumps(parsed_json)
            except Exception as e:
                raise LLMStructuredOutputError(f"Mock structured JSON validation failed: {str(e)}")

        return LLMResult(
            content=content,
            structured_output=parsed_json,
            prompt_tokens=15,
            completion_tokens=25,
            total_tokens=40,
            model=model or self.default_model,
            provider=self.provider_name,
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[LLMChunk, None]:
        content_to_stream = self.mock_response
        parsed_json = None

        if response_format is not None:
            dummy_json = {"summary": "Mock summary", "confidence": 0.99, "status": "ok"}
            try:
                validated = response_format.model_validate(dummy_json)
                parsed_json = validated.model_dump()
                content_to_stream = json.dumps(parsed_json)
            except Exception as e:
                yield LLMChunk(content="", is_done=True, error=f"Structured output error: {str(e)}")
                return

        # Tokenize content into words for streaming simulation
        words = content_to_stream.split(" ")
        for idx, word in enumerate(words):
            token_chunk = word if idx == len(words) - 1 else word + " "
            yield LLMChunk(content=token_chunk, is_done=False)
            await asyncio.sleep(self.delay_ms / 1000.0)

        # Final metadata chunk
        yield LLMChunk(
            content="",
            is_done=True,
            usage={"prompt_tokens": 15, "completion_tokens": len(words), "total_tokens": 15 + len(words)},
            structured_output=parsed_json,
        )
