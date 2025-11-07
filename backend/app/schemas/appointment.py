"\"\"\"Appointment schemas.\""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    patient_id: uuid.UUID
    provider_id: uuid.UUID | None = None
    reason: str | None = None
    notes: str | None = None
    location: str | None = None
    scheduled_start: datetime
    scheduled_end: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    provider_id: uuid.UUID | None = None
    reason: str | None = None
    notes: str | None = None
    location: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    status: AppointmentStatus | None = None


class AppointmentInDBBase(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    practice_id: uuid.UUID


class AppointmentResponse(AppointmentInDBBase):
    pass
