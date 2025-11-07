"\"\"\"Shared FastAPI dependencies.\""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import TokenPayload, decode_token
from app.models.practice import Practice
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db(session: AsyncSession = Depends(get_async_session)) -> AsyncSession:
    return session


async def _get_token_payload(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    payload = decode_token(token)
    if payload is None or payload.type != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


async def get_current_user(
    payload: TokenPayload = Depends(_get_token_payload),
    session: AsyncSession = Depends(get_db),
) -> User:
    user_id = uuid.UUID(payload.sub)
    stmt = select(User).where(User.id == user_id, User.is_active.is_(True))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if payload.practice_id and str(user.practice_id) != payload.practice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant mismatch")
    return user


async def get_current_practice(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Practice:
    stmt = select(Practice).where(Practice.id == user.practice_id)
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()
    if practice is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Practice missing")
    return practice


class PaginationParams:
    def __init__(self, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
        self.page = page
        self.size = size
