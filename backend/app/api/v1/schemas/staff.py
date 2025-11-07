"""Staff schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.staff import StaffRole


class StaffBase(BaseModel):
    """Base staff schema with common fields."""

    role: StaffRole = Field(..., description="Staff role within the practice")
    department: Optional[str] = Field(None, max_length=128)
    job_title: Optional[str] = Field(None, max_length=128)
    employee_id: Optional[str] = Field(None, max_length=64, description="Internal employee ID")
    hire_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="YYYY-MM-DD")
    termination_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="YYYY-MM-DD")
    phone_work: Optional[str] = Field(None, max_length=32)
    phone_mobile: Optional[str] = Field(None, max_length=32)
    email_work: Optional[str] = Field(None, max_length=255)
    extension: Optional[str] = Field(None, max_length=10)
    certifications: Optional[str] = Field(None, max_length=500, description="Comma-separated list")
    licenses: Optional[str] = Field(None, max_length=500, description="Comma-separated list")
    training_completed: Optional[str] = Field(None, max_length=500, description="Comma-separated list")
    work_schedule: Optional[str] = Field(None, max_length=500)
    is_full_time: bool = True
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=32)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True


class StaffCreate(StaffBase):
    """Schema for creating a staff member."""

    user_id: UUID = Field(..., description="User account ID to link staff profile to")


class StaffUpdate(BaseModel):
    """Schema for updating a staff member (all fields optional)."""

    role: Optional[StaffRole] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    employee_id: Optional[str] = None
    hire_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    termination_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    phone_work: Optional[str] = None
    phone_mobile: Optional[str] = None
    email_work: Optional[str] = None
    extension: Optional[str] = None
    certifications: Optional[str] = None
    licenses: Optional[str] = None
    training_completed: Optional[str] = None
    work_schedule: Optional[str] = None
    is_full_time: Optional[bool] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class StaffInDB(StaffBase):
    """Staff as stored in database."""

    id: UUID
    user_id: UUID
    practice_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Staff(StaffInDB):
    """Staff response schema."""

    pass


class StaffWithUser(Staff):
    """Staff with related user information."""

    from app.api.v1.schemas.user import User

    user: Optional[User] = None


class StaffListFilters(BaseModel):
    """Filters for staff list endpoint."""

    role: Optional[StaffRole] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    is_full_time: Optional[bool] = None
    search: Optional[str] = Field(None, description="Search by name, employee_id, job_title")
