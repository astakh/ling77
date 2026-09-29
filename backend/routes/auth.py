from datetime import datetime, timedelta
import secrets

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database import get_db
from models import User, RefreshToken
from schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from auth import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, hash_refresh_token, decode_token,
    auth_rate_limiter, get_current_user
)
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user),
):
    """Get current user information"""
    logger.info(f"👤 Getting user info: {user.email}")
    return UserResponse(
        id=user.id,
        email=user.email,
        timezone=user.timezone,
        is_onboarded=user.is_onboarded,
        is_admin=user.is_admin,
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"📝 Register request received: {body.email}")
    # Rate limit
    client_ip = request.client.host if request.client else "unknown"
    if not auth_rate_limiter.is_allowed(f"register:{client_ip}"):
        raise HTTPException(status_code=429, detail="Too many requests")

    # Check existing user
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create user
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    family_id = secrets.token_hex(16)

    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        family_id=family_id,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(rt)
    await db.flush()

    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"🔑 Login request received: {body.email}")
    # Rate limit
    client_ip = request.client.host if request.client else "unknown"
    if not auth_rate_limiter.is_allowed(f"login:{client_ip}"):
        raise HTTPException(status_code=429, detail="Too many requests")

    # Find user
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    family_id = secrets.token_hex(16)

    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        family_id=family_id,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(rt)
    await db.flush()

    # Set refresh token as httpOnly cookie
    logger.info(f"🍪 Setting refresh token cookie for user {user.id}")
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # False для разработки (localhost), True для production (HTTPS)
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    logger.info("🔄 Refresh token request received")
    
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("❌ No refresh token in cookies")
        logger.info(f"   Available cookies: {list(request.cookies.keys())}")
        raise HTTPException(status_code=401, detail="No refresh token")
    
    logger.info(f"✅ Refresh token found (length: {len(refresh_token)})")

    token_hash = hash_refresh_token(refresh_token)
    logger.info(f"   Token hash: {token_hash[:20]}...")

    # Find token
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
        )
    )
    old_rt = result.scalar_one_or_none()

    if not old_rt:
        logger.error("❌ Invalid refresh token (not found in DB or already revoked)")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if old_rt.expires_at < datetime.utcnow():
        logger.error(f"❌ Refresh token expired at {old_rt.expires_at}")
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    logger.info(f"✅ Valid refresh token found for user {old_rt.user_id}")

    # Check for token reuse (potential theft)
    # If this token was already used, revoke entire family
    # (simplified — in production, track used tokens)

    # Revoke old token
    old_rt.is_revoked = True

    # Issue new tokens
    new_access_token = create_access_token(old_rt.user_id)
    new_refresh_token = create_refresh_token()

    new_rt = RefreshToken(
        user_id=old_rt.user_id,
        token_hash=hash_refresh_token(new_refresh_token),
        family_id=old_rt.family_id,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_rt)
    await db.flush()

    logger.info(f"🍪 Setting new refresh token cookie for user {old_rt.user_id}")
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # False для разработки (localhost), True для production (HTTPS)
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return TokenResponse(access_token=new_access_token)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        token_hash = hash_refresh_token(refresh_token)
        await db.execute(
            delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )

    response.delete_cookie("refresh_token")
    return {"status": "ok"}
