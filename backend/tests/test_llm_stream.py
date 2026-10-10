import json
import uuid
import pytest
from pydantic import BaseModel
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.llm import (
    LLMMessage,
    MockLLMProvider,
    OpenAIProvider,
    LLMAuthenticationError,
    LLMRateLimitError,
)
from app.services.llm.retry import execute_with_retry


class TargetSchema(BaseModel):
    summary: str
    confidence: float
    status: str


@pytest.mark.asyncio
async def test_mock_llm_provider_generation():
    provider = MockLLMProvider(mock_response="Hello world testing mock provider")
    messages = [LLMMessage(role="user", content="Hi")]

    # Non-streaming
    result = await provider.generate_response(messages)
    assert result.content == "Hello world testing mock provider"
    assert result.total_tokens > 0
    assert result.provider == "mock"

    # Streaming
    chunks = []
    async for chunk in provider.generate_stream(messages):
        chunks.append(chunk)

    assert len(chunks) > 1
    text = "".join([c.content for c in chunks if c.content])
    assert text == "Hello world testing mock provider"
    assert chunks[-1].is_done is True


@pytest.mark.asyncio
async def test_mock_llm_structured_output():
    provider = MockLLMProvider()
    messages = [LLMMessage(role="user", content="Return structured data")]

    result = await provider.generate_response(messages, response_format=TargetSchema)
    assert result.structured_output is not None
    assert result.structured_output["confidence"] == 0.99
    assert result.structured_output["summary"] == "Mock summary"


@pytest.mark.asyncio
async def test_sse_streaming_endpoint(async_client: AsyncClient, db_session):
    user = User(email=f"stream_user_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="SSE Streaming Chat")
    db_session.add(conv)
    await db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    stream_res = await async_client.post(
        f"/api/v1/conversations/{conv.id}/messages/stream",
        json={"content": "Tell me a story about space exploration"},
        headers=headers,
    )
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]

    lines = stream_res.text.strip().split("\n\n")
    events = [l for l in lines if l]

    assert len(events) >= 3  # start, token(s), metadata, done

    # Verify start event
    assert "event: start" in events[0]
    start_data = json.loads(events[0].split("data: ")[1])
    assert start_data["conversation_id"] == str(conv.id)
    assert "user_message_id" in start_data

    # Verify done event at end
    done_event = events[-1]
    assert "event: done" in done_event
    done_data = json.loads(done_event.split("data: ")[1])
    assert done_data["status"] == "completed"

    # Verify user message and assistant message persisted in DB
    msg_query = (
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
    )
    msg_res = await db_session.execute(msg_query)
    saved_msgs = msg_res.scalars().all()
    assert len(saved_msgs) == 2
    assert saved_msgs[0].role == "user"
    assert saved_msgs[0].content == "Tell me a story about space exploration"
    assert saved_msgs[1].role == "assistant"


@pytest.mark.asyncio
async def test_sse_streaming_ownership_isolation(async_client: AsyncClient, db_session):
    user_a = User(email=f"usera_stream_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    user_b = User(email=f"userb_stream_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    conv_a = Conversation(user_id=user_a.id, title="User A Private Chat")
    db_session.add(conv_a)
    await db_session.flush()

    token_b = create_access_token(user_b.id)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts to stream to User A conversation -> 404
    res = await async_client.post(
        f"/api/v1/conversations/{conv_a.id}/messages/stream",
        json={"content": "Unauthorized stream request"},
        headers=headers_b,
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_llm_retry_and_non_retryable_exceptions():
    attempts = 0

    async def transient_failing_func():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise LLMRateLimitError("429 Rate Limit Exceeded")
        return "Success"

    res = await execute_with_retry(transient_failing_func, max_retries=3, base_delay=0.01)
    assert res == "Success"
    assert attempts == 2

    auth_attempts = 0

    async def auth_failing_func():
        nonlocal auth_attempts
        auth_attempts += 1
        raise LLMAuthenticationError("401 Invalid API Key")

    with pytest.raises(LLMAuthenticationError):
        await execute_with_retry(auth_failing_func, max_retries=3, base_delay=0.01)

    assert auth_attempts == 1


@pytest.mark.asyncio
async def test_openai_provider_missing_key_protection():
    provider = OpenAIProvider(api_key=None)
    messages = [LLMMessage(role="user", content="Hi")]

    with pytest.raises(LLMAuthenticationError) as exc_info:
        await provider.generate_response(messages)

    assert "API key is not configured" in str(exc_info.value)
