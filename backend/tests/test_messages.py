import uuid
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from app.core.security import create_access_token
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message


@pytest.mark.asyncio
async def test_create_and_list_messages(async_client: AsyncClient, db_session):
    user = User(email=f"msg_user_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Message Test Conversation")
    db_session.add(conv)
    await db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Post message with structured output
    msg_payload = {
        "role": "user",
        "content": "Analyze the financial report",
        "structured_output": {"target_year": 2026, "type": "pdf"},
    }
    post_res = await async_client.post(
        f"/api/v1/conversations/{conv.id}/messages",
        json=msg_payload,
        headers=headers,
    )
    assert post_res.status_code == 201
    post_data = post_res.json()
    assert post_data["role"] == "user"
    assert post_data["content"] == "Analyze the financial report"
    assert post_data["structured_output"]["target_year"] == 2026
    msg_id = post_data["id"]

    # List messages
    list_res = await async_client.get(
        f"/api/v1/conversations/{conv.id}/messages",
        headers=headers,
    )
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["id"] == msg_id

    # Get single message
    get_res = await async_client.get(
        f"/api/v1/conversations/{conv.id}/messages/{msg_id}",
        headers=headers,
    )
    assert get_res.status_code == 200
    assert get_res.json()["content"] == "Analyze the financial report"


@pytest.mark.asyncio
async def test_reject_client_assistant_or_system_message(async_client: AsyncClient, db_session):
    user = User(email=f"reject_role_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Role Test")
    db_session.add(conv)
    await db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Attempting to client-submit role='assistant' -> 422
    res_assistant = await async_client.post(
        f"/api/v1/conversations/{conv.id}/messages",
        json={"role": "assistant", "content": "Fake AI response"},
        headers=headers,
    )
    assert res_assistant.status_code == 422

    # Attempting to client-submit role='system' -> 422
    res_system = await async_client.post(
        f"/api/v1/conversations/{conv.id}/messages",
        json={"role": "system", "content": "Fake system prompt"},
        headers=headers,
    )
    assert res_system.status_code == 422


@pytest.mark.asyncio
async def test_message_conversation_ownership_isolation(async_client: AsyncClient, db_session):
    user_a = User(email=f"usera_msg_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    user_b = User(email=f"userb_msg_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    conv_a = Conversation(user_id=user_a.id, title="User A Private Chat")
    db_session.add(conv_a)
    await db_session.flush()

    token_b = create_access_token(user_b.id)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts to post message to User A conversation -> 404
    post_res = await async_client.post(
        f"/api/v1/conversations/{conv_a.id}/messages",
        json={"role": "user", "content": "Unauthorized message"},
        headers=headers_b,
    )
    assert post_res.status_code == 404

    # User B attempts to read messages from User A conversation -> 404
    list_res = await async_client.get(
        f"/api/v1/conversations/{conv_a.id}/messages",
        headers=headers_b,
    )
    assert list_res.status_code == 404


@pytest.mark.asyncio
async def test_message_pagination_and_chronological_order(async_client: AsyncClient, db_session):
    user = User(email=f"chrono_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Chronological Conv")
    db_session.add(conv)
    await db_session.flush()

    base_time = datetime.now(timezone.utc)
    for i in range(5):
        msg = Message(
            conversation_id=conv.id,
            role="user",
            content=f"Message index {i}",
            created_at=base_time + timedelta(seconds=i),
        )
        db_session.add(msg)
    await db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch with limit=2, offset=0
    list_res = await async_client.get(
        f"/api/v1/conversations/{conv.id}/messages?limit=2&offset=0",
        headers=headers,
    )
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["items"][0]["content"] == "Message index 0"
    assert data["items"][1]["content"] == "Message index 1"
