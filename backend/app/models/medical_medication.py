"""Medical medication model for patient medication tracking."""

from __future__ import annotations

import enum

from sqlalchemy import String, Enum, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class MedicationStatus(str, enum.Enum):
    """Medication status."""

    ACTIVE = 'active'
    DISCONTINUED = 'discontinued'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'


class MedicationRoute(str, enum.Enum):
    """Medication administration route."""

    ORAL = 'oral'
    SUBLINGUAL = 'sublingual'
    INTRAVENOUS = 'intravenous'
    INTRAMUSCULAR = 'intramuscular'
    SUBCUTANEOUS = 'subcutaneous'
    TOPICAL = 'topical'
    INHALED = 'inhaled'
    NASAL = 'nasal'
    OPHTHALMIC = 'ophthalmic'
    OTIC = 'otic'
    RECTAL = 'rectal'
    TRANSDERMAL = 'transdermal'
    OTHER = 'other'


class MedicalMedication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Patient medication record."""

    __tablename__ = 'medical_medications'

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Medication information
    medication_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Generic or brand name'
    )
    generic_name: Mapped[str | None] = mapped_column(
        String(255),
        comment='Generic/chemical name'
    )
    brand_name: Mapped[str | None] = mapped_column(
        String(255),
        comment='Brand/trade name'
    )

    # Dosage information
    dosage: Mapped[str | None] = mapped_column(
        String(100),
        comment='Dosage amount (e.g., 10mg, 5ml)'
    )
    dosage_form: Mapped[str | None] = mapped_column(
        String(50),
        comment='Form: tablet, capsule, liquid, injection, etc.'
    )
    route: Mapped[MedicationRoute | None] = mapped_column(
        Enum(MedicationRoute),
        comment='Administration route'
    )

    # Frequency and timing
    frequency: Mapped[str | None] = mapped_column(
        String(100),
        comment='Frequency (e.g., twice daily, every 6 hours, as needed)'
    )
    instructions: Mapped[str | None] = mapped_column(
        String(500),
        comment='Special instructions (e.g., take with food)'
    )

    # Duration
    start_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Start date (YYYY-MM-DD)'
    )
    end_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='End date or discontinuation date (YYYY-MM-DD)'
    )
    duration_days: Mapped[int | None] = mapped_column(
        Integer,
        comment='Prescribed duration in days'
    )

    # Prescription details
    prescribed_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('providers.id', ondelete='SET NULL'),
        comment='Prescribing provider'
    )
    prescription_number: Mapped[str | None] = mapped_column(
        String(100),
        comment='Prescription or Rx number'
    )
    refills_remaining: Mapped[int | None] = mapped_column(
        Integer,
        comment='Number of refills remaining'
    )

    # Status and reason
    status: Mapped[MedicationStatus] = mapped_column(
        Enum(MedicationStatus),
        nullable=False,
        default=MedicationStatus.ACTIVE
    )
    discontinuation_reason: Mapped[str | None] = mapped_column(
        String(500),
        comment='Reason for discontinuation if applicable'
    )

    # Additional information
    indication: Mapped[str | None] = mapped_column(
        String(255),
        comment='Reason for medication (condition being treated)'
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment='Additional notes, side effects, or observations'
    )

    # Tracking
    recorded_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        comment='User who recorded this medication'
    )

    # Relationships
    patient = relationship('Patient', back_populates='medications')
    prescribed_by_provider = relationship('Provider', foreign_keys=[prescribed_by])

    def __repr__(self) -> str:
        return f"<MedicalMedication(patient_id={self.patient_id}, medication={self.medication_name}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if medication is currently active."""
        return self.status == MedicationStatus.ACTIVE

    @property
    def display_name(self) -> str:
        """Get display name (brand if available, otherwise generic)."""
        return self.brand_name or self.medication_name
