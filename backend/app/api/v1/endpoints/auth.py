"\"\"\"Authentication endpoints.\""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.security import create_token, decode_token
from app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    RegisterRequest,
    Token,
    TokenRefreshRequest,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_practice(
    payload: RegisterRequest,
    session: AsyncSession = Depends(deps.get_db),
) -> Token:
    service = AuthService(session)
    try:
        practice, user = await service.register(payload)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Practice already exists")
    tokens = service.issue_tokens(user=user)
    return Token(**tokens)


@router.post("/login", response_model=Token)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(deps.get_db),
) -> Token:
    service = AuthService(session)
    result = await service.authenticate(
        email=payload.email,
        password=payload.password,
        practice_domain=payload.practice_domain,
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    _, user = result
    tokens = service.issue_tokens(user=user)
    return Token(**tokens)


@router.post("/refresh", response_model=Token)
async def refresh_token(payload: TokenRefreshRequest) -> Token:
    token_payload = decode_token(payload.refresh_token)
    if token_payload is None or token_payload.type != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = token_payload.sub
    practice_id = token_payload.practice_id
    if user_id is None or practice_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    access_token = create_token(subject=user_id, practice_id=practice_id, token_type="access")
    refresh_token = create_token(subject=user_id, practice_id=practice_id, token_type="refresh")
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=AuthenticatedUser)
async def read_current_user(current_user=Depends(deps.get_current_user)) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=current_user.id,
        practice_id=current_user.practice_id,
        email=current_user.email,
        full_name=current_user.full_name,
    )
