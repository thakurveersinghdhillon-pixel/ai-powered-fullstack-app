import json
from typing import AsyncGenerator, List, Optional, Type, Dict, Any
from pydantic import BaseModel
import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.types import LLMMessage, LLMChunk, LLMResult
from app.services.llm.exceptions import (
    LLMProviderError,
    LLMAuthenticationError,
    LLMInvalidRequestError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMConnectionError,
    LLMStructuredOutputError,
)
from app.services.llm.retry import execute_with_retry


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider integration using official AsyncOpenAI SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model or settings.LLM_MODEL
        self._client: Optional[AsyncOpenAI] = None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self.model_name

    def _get_client(self) -> AsyncOpenAI:
        if not self.api_key:
            raise LLMAuthenticationError(
                "OpenAI API key is not configured in environment settings",
                provider=self.provider_name,
            )
        if not self._client:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
        return self._client

    def _handle_exception(self, exc: Exception) -> LLMProviderError:
        """Normalizes OpenAI SDK exceptions to custom LLMProviderError hierarchy."""
        if isinstance(exc, openai.AuthenticationError):
            return LLMAuthenticationError(str(exc), provider=self.provider_name)
        elif isinstance(exc, openai.RateLimitError):
            return LLMRateLimitError(str(exc), provider=self.provider_name)
        elif isinstance(exc, openai.APITimeoutError):
            return LLMTimeoutError(str(exc), provider=self.provider_name)
        elif isinstance(exc, openai.APIConnectionError):
            return LLMConnectionError(str(exc), provider=self.provider_name)
        elif isinstance(exc, openai.BadRequestError):
            return LLMInvalidRequestError(str(exc), provider=self.provider_name)
        elif isinstance(exc, LLMProviderError):
            return exc
        return LLMProviderError(f"OpenAI error: {str(exc)}", is_retryable=False, provider=self.provider_name)

    def _format_messages(
        self, messages: List[LLMMessage], system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            formatted.append({"role": msg.role, "content": msg.content})
        return formatted

    async def generate_response(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        model: Optional[str] = None,
    ) -> LLMResult:
        client = self._get_client()
        target_model = model or self.model_name
        formatted_msgs = self._format_messages(messages, system_prompt)

        kwargs: Dict[str, Any] = {
            "model": target_model,
            "messages": formatted_msgs,
        }

        if response_format is not None:
            kwargs["response_format"] = {"type": "json_object"}

        async def _call():
            try:
                response = await client.chat.completions.create(**kwargs)
                return response
            except Exception as e:
                raise self._handle_exception(e)

        response = await execute_with_retry(_call)
        choice = response.choices[0]
        raw_content = choice.message.content or ""

        parsed_json = None
        if response_format is not None:
            try:
                parsed_dict = json.loads(raw_content)
                validated_model = response_format.model_validate(parsed_dict)
                parsed_json = validated_model.model_dump()
            except Exception as json_err:
                raise LLMStructuredOutputError(
                    f"Structured JSON output validation failed: {str(json_err)}",
                    provider=self.provider_name,
                )

        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        return LLMResult(
            content=raw_content,
            structured_output=parsed_json,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=target_model,
            provider=self.provider_name,
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[LLMChunk, None]:
        client = self._get_client()
        target_model = model or self.model_name
        formatted_msgs = self._format_messages(messages, system_prompt)

        kwargs: Dict[str, Any] = {
            "model": target_model,
            "messages": formatted_msgs,
            "stream": True,
            "stream_options": {"include_usage": True},
        }

        if response_format is not None:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            stream = await client.chat.completions.create(**kwargs)
            accumulated_content = ""

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        accumulated_content += delta
                        yield LLMChunk(content=delta, is_done=False)

                if hasattr(chunk, "usage") and chunk.usage:
                    u = chunk.usage
                    usage_dict = {
                        "prompt_tokens": u.prompt_tokens,
                        "completion_tokens": u.completion_tokens,
                        "total_tokens": u.total_tokens,
                    }
                    parsed_json = None
                    if response_format is not None and accumulated_content:
                        try:
                            parsed_dict = json.loads(accumulated_content)
                            validated_model = response_format.model_validate(parsed_dict)
                            parsed_json = validated_model.model_dump()
                        except Exception:
                            pass

                    yield LLMChunk(
                        content="",
                        is_done=True,
                        usage=usage_dict,
                        structured_output=parsed_json,
                    )

        except Exception as e:
            norm_err = self._handle_exception(e)
            yield LLMChunk(content="", is_done=True, error=norm_err.message)
