import uuid
import pytest
from httpx import AsyncClient
from app.core.security import create_access_token
from app.models.user import User
from app.models.template import PromptTemplate


@pytest.mark.asyncio
async def test_template_crud_and_versioning(async_client: AsyncClient, db_session):
    user = User(email=f"tmpl_user_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "name": "Article Summarizer",
        "description": "Summarizes articles into key points",
        "template_content": "Summarize the text in {{tone}} tone: {{text}}",
        "version": 1,
    }
    create_res = await async_client.post(
        "/api/v1/templates",
        json=create_payload,
        headers=headers,
    )
    assert create_res.status_code == 201
    tmpl_data = create_res.json()
    assert tmpl_data["name"] == "Article Summarizer"
    assert tmpl_data["version"] == 1
    tmpl_id = tmpl_data["id"]

    get_res = await async_client.get(
        f"/api/v1/templates/{tmpl_id}",
        headers=headers,
    )
    assert get_res.status_code == 200
    assert get_res.json()["template_content"] == "Summarize the text in {{tone}} tone: {{text}}"

    patch_res = await async_client.patch(
        f"/api/v1/templates/{tmpl_id}",
        json={"template_content": "Updated prompt: {{text}}"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["version"] == 2
    assert patch_res.json()["template_content"] == "Updated prompt: {{text}}"

    del_res = await async_client.delete(
        f"/api/v1/templates/{tmpl_id}",
        headers=headers,
    )
    assert del_res.status_code == 204

    get_del_res = await async_client.get(
        f"/api/v1/templates/{tmpl_id}",
        headers=headers,
    )
    assert get_del_res.status_code == 404


@pytest.mark.asyncio
async def test_template_ownership_isolation(async_client: AsyncClient, db_session):
    user_a = User(email=f"usera_tmpl_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    user_b = User(email=f"userb_tmpl_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    tmpl_a = PromptTemplate(
        user_id=user_a.id,
        name="User A Code Reviewer",
        template_content="Review code: {{code}}",
    )
    db_session.add(tmpl_a)
    await db_session.flush()

    token_b = create_access_token(user_b.id)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    list_res = await async_client.get("/api/v1/templates", headers=headers_b)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 0

    get_res = await async_client.get(f"/api/v1/templates/{tmpl_a.id}", headers=headers_b)
    assert get_res.status_code == 404

    patch_res = await async_client.patch(
        f"/api/v1/templates/{tmpl_a.id}",
        json={"name": "Hacked Template"},
        headers=headers_b,
    )
    assert patch_res.status_code == 404

    del_res = await async_client.delete(f"/api/v1/templates/{tmpl_a.id}", headers=headers_b)
    assert del_res.status_code == 404


@pytest.mark.asyncio
async def test_template_unauthenticated_and_not_found(async_client: AsyncClient, db_session):
    unauth_res = await async_client.get("/api/v1/templates")
    assert unauth_res.status_code in (401, 403)

    user = User(email=f"tmpl_notfound_{uuid.uuid4().hex[:8]}@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(user.id)
    fake_id = uuid.uuid4()
    not_found_res = await async_client.get(
        f"/api/v1/templates/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert not_found_res.status_code == 404
