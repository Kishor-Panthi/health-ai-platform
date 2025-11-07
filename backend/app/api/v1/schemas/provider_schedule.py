"""Provider schedule schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.provider_schedule import DayOfWeek


class ProviderScheduleBase(BaseModel):
    """Base provider schedule schema."""

    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time = Field(..., description="Schedule start time")
    end_time: time = Field(..., description="Schedule end time")
    location: Optional[str] = Field(None, max_length=255, description="Office location or room number")
    is_available: bool = Field(True, description="Whether accepting appointments")
    slot_duration_minutes: int = Field(30, ge=5, le=480, description="Appointment slot duration")
    max_patients_per_slot: int = Field(1, ge=1, le=10, description="Max patients per slot")
    lunch_break_start: Optional[time] = Field(None, description="Lunch break start time")
    lunch_break_end: Optional[time] = Field(None, description="Lunch break end time")
    notes: Optional[str] = Field(None, max_length=500)
    effective_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Start date YYYY-MM-DD")
    expiration_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="End date YYYY-MM-DD")

    @field_validator('end_time')
    @classmethod
    def validate_end_after_start(cls, v: time, info) -> time:
        """Ensure end_time is after start_time."""
        if 'start_time' in info.data:
            start_time = info.data['start_time']
            if v <= start_time:
                raise ValueError('end_time must be after start_time')
        return v

    @field_validator('lunch_break_end')
    @classmethod
    def validate_lunch_break(cls, v: Optional[time], info) -> Optional[time]:
        """Ensure lunch break is within schedule and properly ordered."""
        if v is None:
            return v

        if 'lunch_break_start' not in info.data or info.data['lunch_break_start'] is None:
            raise ValueError('lunch_break_start required when lunch_break_end is set')

        lunch_start = info.data['lunch_break_start']
        if v <= lunch_start:
            raise ValueError('lunch_break_end must be after lunch_break_start')

        if 'start_time' in info.data and 'end_time' in info.data:
            start_time = info.data['start_time']
            end_time = info.data['end_time']
            if lunch_start < start_time or v > end_time:
                raise ValueError('lunch break must be within schedule hours')

        return v


class ProviderScheduleCreate(ProviderScheduleBase):
    """Schema for creating a provider schedule."""

    provider_id: UUID = Field(..., description="Provider ID")


class ProviderScheduleUpdate(BaseModel):
    """Schema for updating a provider schedule (all fields optional)."""

    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    is_available: Optional[bool] = None
    slot_duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    max_patients_per_slot: Optional[int] = Field(None, ge=1, le=10)
    lunch_break_start: Optional[time] = None
    lunch_break_end: Optional[time] = None
    notes: Optional[str] = None
    effective_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    expiration_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')


class ProviderScheduleInDB(ProviderScheduleBase):
    """Provider schedule as stored in database."""

    id: UUID
    provider_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProviderSchedule(ProviderScheduleInDB):
    """Provider schedule response schema."""

    pass


class ProviderScheduleWithProvider(ProviderSchedule):
    """Schedule with provider information."""

    from app.api.v1.schemas.provider import Provider

    provider: Optional[Provider] = None


class ProviderScheduleListFilters(BaseModel):
    """Filters for provider schedule list endpoint."""

    provider_id: Optional[UUID] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    is_available: Optional[bool] = None


class DayScheduleSummary(BaseModel):
    """Summary of provider schedules for a specific day."""

    day_of_week: int
    day_name: str
    schedules: list[ProviderSchedule] = []
    total_available_hours: float
    total_appointment_slots: int


class WeekScheduleSummary(BaseModel):
    """Summary of provider schedules for entire week."""

    provider_id: UUID
    days: list[DayScheduleSummary] = []
    total_weekly_hours: float
    total_weekly_slots: int
