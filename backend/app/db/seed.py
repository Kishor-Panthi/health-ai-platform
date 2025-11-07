from __future__ import annotations

import asyncio
from datetime import date

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.schemas.patient import PatientCreate
from app.services.patient_service import PatientService
from app.services.practice_service import PracticeService


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        practice_service = PracticeService(session)
        practice, admin = await practice_service.ensure_superuser(
            email=settings.first_superuser_email or 'admin@example.com',
            password=settings.first_superuser_password or 'ChangeMe123!',
            practice_name=settings.first_superuser_practice_name or 'Codex Health',
            practice_domain=settings.first_superuser_domain or 'codex.local',
        )
        patient_service = PatientService(session, practice.id)
        await patient_service.create(
            PatientCreate(
                first_name='Demo',
                last_name='Patient',
                mrn='MRN-1001',
                dob=date(1990, 1, 1),
                email='patient@example.com',
                phone='555-0101',
            )
        )


if __name__ == '__main__':
    asyncio.run(seed())