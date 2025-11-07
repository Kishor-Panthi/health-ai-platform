"""Provider schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProviderBase(BaseModel):
    """Base provider schema with common fields."""

    npi: Optional[str] = Field(None, min_length=10, max_length=10, description="National Provider Identifier")
    license_number: Optional[str] = Field(None, max_length=64)
    license_state: Optional[str] = Field(None, min_length=2, max_length=2, description="Two-letter state code")
    dea_number: Optional[str] = Field(None, max_length=9, description="DEA registration number")
    title: Optional[str] = Field(None, max_length=50, description="Dr., MD, DO, NP, PA, etc.")
    specialty: Optional[str] = Field(None, max_length=128)
    sub_specialty: Optional[str] = Field(None, max_length=128)
    department: Optional[str] = Field(None, max_length=128)
    accepting_new_patients: bool = True
    years_of_experience: Optional[int] = Field(None, ge=0, le=100)
    education: Optional[str] = Field(None, max_length=500)
    board_certifications: Optional[str] = Field(None, max_length=500)
    phone_direct: Optional[str] = Field(None, max_length=32)
    email_work: Optional[str] = Field(None, max_length=255)
    pager: Optional[str] = Field(None, max_length=32)
    bio: Optional[str] = Field(None, max_length=2000)
    languages_spoken: Optional[str] = Field(None, max_length=255, description="Comma-separated list")
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True

    @field_validator('license_state')
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        """Validate state code is uppercase."""
        if v:
            return v.upper()
        return v

    @field_validator('npi')
    @classmethod
    def validate_npi(cls, v: Optional[str]) -> Optional[str]:
        """Validate NPI is numeric."""
        if v and not v.isdigit():
            raise ValueError('NPI must contain only digits')
        return v


class ProviderCreate(ProviderBase):
    """Schema for creating a provider."""

    user_id: UUID = Field(..., description="User account ID to link provider profile to")


class ProviderUpdate(BaseModel):
    """Schema for updating a provider (all fields optional)."""

    npi: Optional[str] = Field(None, min_length=10, max_length=10)
    license_number: Optional[str] = None
    license_state: Optional[str] = Field(None, min_length=2, max_length=2)
    dea_number: Optional[str] = None
    title: Optional[str] = None
    specialty: Optional[str] = None
    sub_specialty: Optional[str] = None
    department: Optional[str] = None
    accepting_new_patients: Optional[bool] = None
    years_of_experience: Optional[int] = Field(None, ge=0, le=100)
    education: Optional[str] = None
    board_certifications: Optional[str] = None
    phone_direct: Optional[str] = None
    email_work: Optional[str] = None
    pager: Optional[str] = None
    bio: Optional[str] = None
    languages_spoken: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ProviderInDB(ProviderBase):
    """Provider as stored in database."""

    id: UUID
    user_id: UUID
    practice_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Provider(ProviderInDB):
    """Provider response schema."""

    pass


class ProviderWithUser(Provider):
    """Provider with related user information."""

    from app.api.v1.schemas.user import User

    user: Optional[User] = None


class ProviderWithSchedules(Provider):
    """Provider with schedule information."""

    from app.api.v1.schemas.provider_schedule import ProviderSchedule

    schedules: list[ProviderSchedule] = []


class ProviderListFilters(BaseModel):
    """Filters for provider list endpoint."""

    specialty: Optional[str] = None
    department: Optional[str] = None
    accepting_new_patients: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = Field(None, description="Search by name, NPI, specialty")
