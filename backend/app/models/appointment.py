"\"\"\"Appointment scheduling model.\""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELED = "canceled"
    NO_SHOW = "no_show"


class Appointment(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, SoftDeleteMixin, Base):
    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text())
    location: Mapped[str | None] = mapped_column(String(255))
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
    )

    practice = relationship("Practice", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("User", back_populates="appointments")
    billing_claims = relationship("BillingClaim", back_populates="appointment")
    clinical_notes = relationship("ClinicalNote", back_populates="appointment")
    documents = relationship("Document", back_populates="appointment")
