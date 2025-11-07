"""Medical condition model for patient chronic conditions and diagnoses."""

from __future__ import annotations

import enum

from sqlalchemy import String, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ConditionStatus(str, enum.Enum):
    """Condition status."""

    ACTIVE = 'active'
    RESOLVED = 'resolved'
    IN_REMISSION = 'in_remission'
    CHRONIC = 'chronic'
    RECURRENT = 'recurrent'


class ConditionSeverity(str, enum.Enum):
    """Condition severity."""

    MILD = 'mild'
    MODERATE = 'moderate'
    SEVERE = 'severe'


class MedicalCondition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Patient medical condition or diagnosis record."""

    __tablename__ = 'medical_conditions'

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Condition information
    condition_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Condition or diagnosis name'
    )
    icd10_code: Mapped[str | None] = mapped_column(
        String(10),
        index=True,
        comment='ICD-10 diagnosis code'
    )
    snomed_code: Mapped[str | None] = mapped_column(
        String(20),
        comment='SNOMED CT code'
    )

    # Clinical details
    diagnosis_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date diagnosed (YYYY-MM-DD)'
    )
    onset_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date symptoms first appeared (YYYY-MM-DD)'
    )
    diagnosed_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('providers.id', ondelete='SET NULL'),
        comment='Diagnosing provider'
    )

    # Status and severity
    status: Mapped[ConditionStatus] = mapped_column(
        Enum(ConditionStatus),
        nullable=False,
        default=ConditionStatus.ACTIVE
    )
    severity: Mapped[ConditionSeverity | None] = mapped_column(
        Enum(ConditionSeverity),
        comment='Condition severity'
    )

    # Resolution
    resolved_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date condition was resolved (YYYY-MM-DD)'
    )

    # Clinical notes
    clinical_summary: Mapped[str | None] = mapped_column(
        Text,
        comment='Clinical summary or description'
    )
    treatment_plan: Mapped[str | None] = mapped_column(
        Text,
        comment='Treatment plan or management strategy'
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment='Additional notes or observations'
    )

    # Classification
    is_chronic: Mapped[bool] = mapped_column(
        default=False,
        comment='Whether this is a chronic condition'
    )
    is_primary: Mapped[bool] = mapped_column(
        default=False,
        comment='Whether this is a primary diagnosis'
    )

    # Tracking
    recorded_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        comment='User who recorded this condition'
    )
    last_reviewed_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date condition was last reviewed (YYYY-MM-DD)'
    )

    # Relationships
    patient = relationship('Patient', back_populates='conditions')
    diagnosed_by_provider = relationship('Provider', foreign_keys=[diagnosed_by])

    def __repr__(self) -> str:
        return f"<MedicalCondition(patient_id={self.patient_id}, condition={self.condition_name}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if condition is currently active."""
        return self.status in [ConditionStatus.ACTIVE, ConditionStatus.CHRONIC, ConditionStatus.RECURRENT]

    @property
    def display_code(self) -> str | None:
        """Get display code (ICD-10 preferred, SNOMED as fallback)."""
        return self.icd10_code or self.snomed_code
