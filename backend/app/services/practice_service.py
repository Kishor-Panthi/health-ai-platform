"""Practice service helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.practice import Practice
from app.models.user import User, UserRole


class PracticeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_domain(self, domain: str) -> Practice | None:
        result = await self.session.execute(
            select(Practice).where(Practice.domain == domain)
        )
        return result.scalar_one_or_none()

    async def create_with_admin(
        self,
        *,
        name: str,
        domain: str,
        admin_email: str,
        admin_full_name: str,
        password: str,
        timezone: str = "UTC",
    ) -> tuple[Practice, User]:
        practice = Practice(
            name=name,
            domain=domain,
            timezone=timezone,
        )
        self.session.add(practice)
        await self.session.flush()

        user = User(
            practice_id=practice.id,
            email=admin_email,
            full_name=admin_full_name,
            role=UserRole.ADMIN,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(practice)
        await self.session.refresh(user)
        return practice, user

    async def ensure_superuser(
        self,
        *,
        email: str,
        password: str,
        practice_name: str,
        practice_domain: str,
    ) -> tuple[Practice, User]:
        practice = await self.get_by_domain(practice_domain)
        if practice is None:
            practice, user = await self.create_with_admin(
                name=practice_name,
                domain=practice_domain,
                admin_email=email,
                admin_full_name="System Admin",
                password=password,
            )
            return practice, user

        result = await self.session.execute(
            select(User).where(User.email == email, User.practice_id == practice.id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                practice_id=practice.id,
                email=email,
                full_name="System Admin",
                hashed_password=get_password_hash(password),
                role=UserRole.ADMIN,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return practice, user
