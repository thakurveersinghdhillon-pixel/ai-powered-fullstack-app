import uuid
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password, verify_password, hash_token, create_access_token
from app.models.user import User
from app.models.session import RefreshSession


@pytest.mark.asyncio
async def test_password_hashing_argon2id():
    raw_pwd = "MySecretSecurePassword123!"
    hashed = hash_password(raw_pwd)

    assert hashed != raw_pwd
    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_user_registration_success(async_client: AsyncClient):
    email = f"register_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "securepassword123"}

    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "password_hash" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(async_client: AsyncClient):
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "securepassword123"}

    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_login_success_and_cookie(async_client: AsyncClient):
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "password12345"

    reg_res = await async_client.post("/api/v1/auth/register", json={"email": email, "password": pwd})
    assert reg_res.status_code == 201

    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert login_res.status_code == 200

    data = login_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Check HttpOnly cookie
    assert settings.REFRESH_COOKIE_NAME in login_res.cookies


@pytest.mark.asyncio
async def test_user_login_invalid_credentials(async_client: AsyncClient):
    email = f"invalid_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "password12345"

    await async_client.post("/api/v1/auth/register", json={"email": email, "password": pwd})

    # Wrong password
    res1 = await async_client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})
    assert res1.status_code == 401
    assert "invalid email or password" in res1.json()["detail"].lower()

    # Non-existent email
    res2 = await async_client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": pwd})
    assert res2.status_code == 401
    assert "invalid email or password" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_login_disabled_account(async_client: AsyncClient, db_session):
    email = f"disabled_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "password12345"

    reg_res = await async_client.post("/api/v1/auth/register", json={"email": email, "password": pwd})
    user_id = uuid.UUID(reg_res.json()["id"])

    # Disable account in DB
    result = await db_session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.is_active = False
    await db_session.flush()

    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert login_res.status_code == 400
    assert "disabled" in login_res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_protected_me_endpoint(async_client: AsyncClient):
    email = f"me_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "password12345"

    await async_client.post("/api/v1/auth/register", json={"email": email, "password": pwd})
    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    token = login_res.json()["access_token"]

    # Valid token call
    me_res = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # Missing token call
    unauth_res = await async_client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 403 or unauth_res.status_code == 401

    # Malformed token call
    malformed_res = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid.jwt.string"}
    )
    assert malformed_res.status_code == 401


@pytest.mark.asyncio
async def test_access_token_expiry(async_client: AsyncClient, db_session):
    user = User(email=f"expired_{uuid.uuid4().hex[:8]}@example.com", password_hash=hash_password("pwd"))
    db_session.add(user)
    await db_session.flush()

    # Create expired JWT
    now = datetime.now(timezone.utc) - timedelta(minutes=30)
    expired_payload = {
        "sub": str(user.id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "access",
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    res = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_logout(async_client: AsyncClient):
    email = f"refresh_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "password12345"

    await async_client.post("/api/v1/auth/register", json={"email": email, "password": pwd})
    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    
    initial_access = login_res.json()["access_token"]
    initial_cookie = login_res.cookies.get(settings.REFRESH_COOKIE_NAME)
    assert initial_cookie is not None

    # Execute Refresh Token Rotation
    refresh_res = await async_client.post("/api/v1/auth/refresh")
    assert refresh_res.status_code == 200

    new_access = refresh_res.json()["access_token"]
    new_cookie = refresh_res.cookies.get(settings.REFRESH_COOKIE_NAME)

    assert new_access != initial_access
    assert new_cookie != initial_cookie

    # Attempt Replay Attack with Old Refresh Token Cookie -> Replay detected & rejected!
    async_client.cookies.set(settings.REFRESH_COOKIE_NAME, initial_cookie)
    replay_res = await async_client.post("/api/v1/auth/refresh")
    assert replay_res.status_code == 401

    # Log in again & execute Logout
    login_res2 = await async_client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    logout_res = await async_client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200

    # Verify refresh attempt after logout is rejected
    after_logout_res = await async_client.post("/api/v1/auth/refresh")
    assert after_logout_res.status_code == 401
