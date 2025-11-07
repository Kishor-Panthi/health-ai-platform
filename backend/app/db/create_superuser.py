from __future__ import annotations

import asyncio

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.practice_service import PracticeService


async def run() -> None:
    async with AsyncSessionLocal() as session:
        practice_service = PracticeService(session)
        practice, admin = await practice_service.ensure_superuser(
            email=settings.first_superuser_email or 'admin@example.com',
            password=settings.first_superuser_password or 'ChangeMe123!',
            practice_name=settings.first_superuser_practice_name or 'Codex Health',
            practice_domain=settings.first_superuser_domain or 'codex.local',
        )
        print(f"Created superuser {admin.email} for practice {practice.name}")


if __name__ == '__main__':
    asyncio.run(run())