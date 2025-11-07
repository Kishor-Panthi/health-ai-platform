\"\"\"Patient domain logic.\"\"\"

from __future__ import annotations

import uuid

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.services.base import BaseService


class PatientService(BaseService[Patient]):
    def __init__(self, session: AsyncSession, practice_id: uuid.UUID):
        super().__init__(session, practice_id)

    async def list(
        self,
        *,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Patient], int]:
        stmt: Select[tuple[Patient]] = self.scoped_query(Patient, Patient.is_deleted.is_(False))
        if search:
            like = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Patient.first_name).like(like),
                    func.lower(Patient.last_name).like(like),
                    func.lower(Patient.mrn).like(like),
                )
            )
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()
        stmt = stmt.order_by(Patient.created_at.desc()).offset((page - 1) * size).limit(size)
        rows = (await self.session.execute(stmt)).scalars().all()
        return rows, total

    async def create(self, payload: PatientCreate, *, actor_id: uuid.UUID | None = None) -> Patient:
        patient = Patient(practice_id=self.practice_id, **payload.model_dump())
        self.session.add(patient)
        await self.session.commit()
        await self.session.refresh(patient)
        await self.audit.log(
            practice_id=self.practice_id,
            actor_id=actor_id,
            action='patient.created',
            entity='Patient',
            entity_id=patient.id,
            payload={"mrn": patient.mrn},
        )
        return patient

    async def update(
        self,
        patient_id: uuid.UUID,
        payload: PatientUpdate,
        *,
        actor_id: uuid.UUID | None = None,
    ) -> Patient:
        result = await self.session.execute(
            self.scoped_query(Patient, Patient.id == patient_id, Patient.is_deleted.is_(False))
        )
        patient = result.scalar_one_or_none()
        if patient is None:
            raise LookupError('patient_not_found')
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(patient, field, value)
        await self.session.commit()
        await self.session.refresh(patient)
        await self.audit.log(
            practice_id=self.practice_id,
            actor_id=actor_id,
            action='patient.updated',
            entity='Patient',
            entity_id=patient.id,
        )
        return patient

    async def get(self, patient_id: uuid.UUID) -> Patient | None:
        result = await self.session.execute(
            self.scoped_query(Patient, Patient.id == patient_id, Patient.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()
