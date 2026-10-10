from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.models.session import RefreshSession
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registers a new user account with normalized email and Argon2id hashed password."""
    normalized_email = payload.email.strip().lower()

    # Check for existing email
    result = await db.execute(select(User).where(User.email == normalized_email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    # Hash password securely
    hashed_pwd = hash_password(payload.password)
    user = User(
        email=normalized_email,
        password_hash=hashed_pwd,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticates user, issues JWT access token, and sets HttpOnly refresh cookie."""
    normalized_email = payload.email.strip().lower()

    result = await db.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    # Generic credential verification error to prevent account enumeration
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is disabled",
        )

    # Generate tokens
    access_token = create_access_token(user.id)
    raw_refresh, token_hash, expires_at = create_refresh_token(user.id)

    # Store refresh session in database
    session = RefreshSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(session)
    await db.flush()

    # Set secure HttpOnly cookie
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=raw_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path=settings.COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Refreshes access token and rotates refresh token using HttpOnly cookie.
    Detects replay attacks and revokes invalid sessions.
    """
    raw_refresh = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not raw_refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    # Decode refresh JWT envelope
    payload = decode_jwt_token(raw_refresh, expected_type="refresh")
    token_h = hash_token(raw_refresh)

    # Find matching refresh session
    result = await db.execute(
        select(RefreshSession).where(RefreshSession.token_hash == token_h)
    )
    session = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    # Replay or invalid session handling
    if not session or session.revoked_at is not None or session.expires_at <= now:
        if session and session.revoked_at is not None:
            # Token reuse/replay detected: revoke ALL active sessions for security!
            await db.execute(
                update(RefreshSession)
                .where(RefreshSession.user_id == session.user_id)
                .values(revoked_at=now)
            )
        response.delete_cookie(key=settings.REFRESH_COOKIE_NAME, path=settings.COOKIE_PATH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh session",
        )

    # Revoke old session (Rotation)
    session.revoked_at = now

    # Issue new access token and rotated refresh token
    new_access_token = create_access_token(session.user_id)
    new_raw_refresh, new_token_hash, new_expires_at = create_refresh_token(session.user_id)

    new_session = RefreshSession(
        user_id=session.user_id,
        token_hash=new_token_hash,
        expires_at=new_expires_at,
    )
    db.add(new_session)
    await db.flush()

    # Update HttpOnly cookie
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=new_raw_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path=settings.COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return TokenResponse(access_token=new_access_token)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Revokes active refresh session and clears the HttpOnly cookie."""
    raw_refresh = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if raw_refresh:
        token_h = hash_token(raw_refresh)
        result = await db.execute(
            select(RefreshSession).where(RefreshSession.token_hash == token_h)
        )
        session = result.scalar_one_or_none()
        if session and session.revoked_at is None:
            session.revoked_at = datetime.now(timezone.utc)
            await db.flush()

    response.delete_cookie(key=settings.REFRESH_COOKIE_NAME, path=settings.COOKIE_PATH)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile data of the currently authenticated user."""
    return current_user
