"\"\"\"Pydantic schemas for patients.\""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.patient import PatientStatus


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    dob: date | None = None
    gender: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    primary_provider_id: uuid.UUID | None = None


class PatientCreate(PatientBase):
    mrn: str = Field(..., min_length=3)
    ssn: str | None = None


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    dob: date | None = None
    gender: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    status: PatientStatus | None = None
    primary_provider_id: uuid.UUID | None = None


class PatientInDBBase(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    practice_id: uuid.UUID
    mrn: str
    status: PatientStatus


class PatientResponse(PatientInDBBase):
    pass
