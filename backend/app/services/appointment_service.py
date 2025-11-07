\"\"\"Appointment orchestration.\"\"\"

from __future__ import annotations

import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.base import BaseService


class AppointmentService(BaseService[Appointment]):
    def __init__(self, session: AsyncSession, practice_id: uuid.UUID):
        super().__init__(session, practice_id)

    async def list(self, page: int = 1, size: int = 20) -> tuple[list[Appointment], int]:
        stmt: Select[tuple[Appointment]] = self.scoped_query(Appointment, Appointment.is_deleted.is_(False))
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()
        stmt = stmt.order_by(Appointment.scheduled_start.desc()).offset((page - 1) * size).limit(size)
        rows = (await self.session.execute(stmt)).scalars().all()
        return rows, total

    async def create(self, payload: AppointmentCreate, *, actor_id: uuid.UUID | None = None) -> Appointment:
        appointment = Appointment(practice_id=self.practice_id, **payload.model_dump())
        self.session.add(appointment)
        await self.session.commit()
        await self.session.refresh(appointment)
        await self.audit.log(
            practice_id=self.practice_id,
            actor_id=actor_id,
            action='appointment.created',
            entity='Appointment',
            entity_id=appointment.id,
        )
        return appointment

    async def update(
        self,
        appointment_id: uuid.UUID,
        payload: AppointmentUpdate,
        *,
        actor_id: uuid.UUID | None = None,
    ) -> Appointment:
        result = await self.session.execute(
            self.scoped_query(Appointment, Appointment.id == appointment_id, Appointment.is_deleted.is_(False))
        )
        appointment = result.scalar_one_or_none()
        if appointment is None:
            raise LookupError('appointment_not_found')
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(appointment, field, value)
        await self.session.commit()
        await self.session.refresh(appointment)
        await self.audit.log(
            practice_id=self.practice_id,
            actor_id=actor_id,
            action='appointment.updated',
            entity='Appointment',
            entity_id=appointment.id,
        )
        return appointment