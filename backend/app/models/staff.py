"""Staff model for non-provider staff members."""

from __future__ import annotations

import enum

from sqlalchemy import String, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class StaffRole(str, enum.Enum):
    """Staff roles within the practice."""

    RECEPTIONIST = 'receptionist'
    NURSE = 'nurse'
    MEDICAL_ASSISTANT = 'medical_assistant'
    BILLING_SPECIALIST = 'billing_specialist'
    PRACTICE_MANAGER = 'practice_manager'
    IT_SUPPORT = 'it_support'
    LABORATORY_TECHNICIAN = 'laboratory_technician'
    RADIOLOGY_TECHNICIAN = 'radiology_technician'
    PHARMACIST = 'pharmacist'
    OTHER = 'other'


class Staff(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """Non-provider staff member with specific roles and responsibilities."""

    __tablename__ = 'staff'

    # Link to User account
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )

    # Role and department
    role: Mapped[StaffRole] = mapped_column(
        Enum(StaffRole),
        nullable=False,
        default=StaffRole.OTHER
    )
    department: Mapped[str | None] = mapped_column(String(128))
    job_title: Mapped[str | None] = mapped_column(String(128))

    # Employment details
    employee_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        comment='Internal employee ID'
    )
    hire_date: Mapped[str | None] = mapped_column(String(10))  # YYYY-MM-DD as string
    termination_date: Mapped[str | None] = mapped_column(String(10))

    # Contact information
    phone_work: Mapped[str | None] = mapped_column(String(32))
    phone_mobile: Mapped[str | None] = mapped_column(String(32))
    email_work: Mapped[str | None] = mapped_column(String(255))
    extension: Mapped[str | None] = mapped_column(String(10))

    # Certifications and training
    certifications: Mapped[str | None] = mapped_column(
        String(500),
        comment='Comma-separated list of certifications'
    )
    licenses: Mapped[str | None] = mapped_column(
        String(500),
        comment='Comma-separated list of license numbers'
    )
    training_completed: Mapped[str | None] = mapped_column(
        String(500),
        comment='Comma-separated list of completed training'
    )

    # Work schedule
    work_schedule: Mapped[str | None] = mapped_column(
        String(500),
        comment='Description of work schedule'
    )
    is_full_time: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Emergency contact
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(32))
    emergency_contact_relationship: Mapped[str | None] = mapped_column(String(50))

    # Notes
    notes: Mapped[str | None] = mapped_column(String(1000))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    practice = relationship('Practice', back_populates='staff')
    user = relationship('User', back_populates='staff', foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<Staff(id={self.id}, role={self.role}, employee_id={self.employee_id})>"
