"""Authentication and authorization helpers."""

from __future__ import annotations

from typing import Tuple
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token, verify_password
from app.models.practice import Practice
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.practice_service import PracticeService


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.practice_service = PracticeService(session)

    async def authenticate(
        self,
        *,
        email: str,
        password: str,
        practice_domain: str,
    ) -> tuple[Practice, User] | None:
        practice = await self.practice_service.get_by_domain(practice_domain)
        if practice is None:
            return None
        stmt = select(User).where(User.practice_id == practice.id, User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return practice, user

    async def register(self, payload: RegisterRequest) -> tuple[Practice, User]:
        return await self.practice_service.create_with_admin(
            name=payload.practice_name,
            domain=payload.practice_domain,
            admin_email=payload.email,
            admin_full_name=payload.full_name,
            password=payload.password,
        )

    def issue_tokens(self, *, user: User) -> dict[str, str]:
        access_token = create_token(subject=user.id, practice_id=user.practice_id, token_type="access")
        refresh_token = create_token(subject=user.id, practice_id=user.practice_id, token_type="refresh")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
