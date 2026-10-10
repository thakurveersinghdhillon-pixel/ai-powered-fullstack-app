import uuid
import pytest
from httpx import AsyncClient
from app.core.security import create_access_token
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message


@pytest.mark.asyncio
async def test_create_and_get_conversation(async_client: AsyncClient, db_session):
    user = User(email=f"user_conv_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create conversation
    create_res = await async_client.post(
        "/api/v1/conversations",
        json={"title": "Python Architecture Discussion"},
        headers=headers,
    )
    assert create_res.status_code == 201
    conv_data = create_res.json()
    assert conv_data["title"] == "Python Architecture Discussion"
    assert conv_data["user_id"] == str(user.id)
    conv_id = conv_data["id"]

    # Get single conversation
    get_res = await async_client.get(
        f"/api/v1/conversations/{conv_id}",
        headers=headers,
    )
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Python Architecture Discussion"


@pytest.mark.asyncio
async def test_list_conversations_pagination_and_isolation(async_client: AsyncClient, db_session):
    user_a = User(email=f"usera_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    user_b = User(email=f"userb_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    token_a = create_access_token(user_a.id)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    for i in range(3):
        conv = Conversation(user_id=user_a.id, title=f"User A Chat {i+1}")
        db_session.add(conv)

    conv_b = Conversation(user_id=user_b.id, title="User B Secret Chat")
    db_session.add(conv_b)
    await db_session.flush()

    list_res = await async_client.get(
        "/api/v1/conversations?limit=2&offset=0",
        headers=headers_a,
    )
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert "User B Secret Chat" not in [c["title"] for c in data["items"]]


@pytest.mark.asyncio
async def test_user_cannot_access_or_modify_other_user_conversation(async_client: AsyncClient, db_session):
    user_a = User(email=f"user_a_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    user_b = User(email=f"user_b_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    conv_a = Conversation(user_id=user_a.id, title="User A Private Conv")
    db_session.add(conv_a)
    await db_session.flush()

    token_b = create_access_token(user_b.id)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    get_res = await async_client.get(
        f"/api/v1/conversations/{conv_a.id}",
        headers=headers_b,
    )
    assert get_res.status_code == 404

    patch_res = await async_client.patch(
        f"/api/v1/conversations/{conv_a.id}",
        json={"title": "Hacked Title"},
        headers=headers_b,
    )
    assert patch_res.status_code == 404

    del_res = await async_client.delete(
        f"/api/v1/conversations/{conv_a.id}",
        headers=headers_b,
    )
    assert del_res.status_code == 404


@pytest.mark.asyncio
async def test_update_and_delete_conversation_with_message_cascade(async_client: AsyncClient, db_session):
    user = User(email=f"user_del_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Old Title")
    db_session.add(conv)
    await db_session.flush()

    msg = Message(conversation_id=conv.id, role="user", content="Hello world")
    db_session.add(msg)
    await db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    update_res = await async_client.patch(
        f"/api/v1/conversations/{conv.id}",
        json={"title": "New Updated Title"},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "New Updated Title"

    delete_res = await async_client.delete(
        f"/api/v1/conversations/{conv.id}",
        headers=headers,
    )
    assert delete_res.status_code == 204

    get_res = await async_client.get(
        f"/api/v1/conversations/{conv.id}",
        headers=headers,
    )
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_and_empty_title_validation(async_client: AsyncClient, db_session):
    unauth_res = await async_client.get("/api/v1/conversations")
    assert unauth_res.status_code in (401, 403)

    user = User(email=f"empty_title_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(user.id)
    invalid_res = await async_client.post(
        "/api/v1/conversations",
        json={"title": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert invalid_res.status_code == 422
