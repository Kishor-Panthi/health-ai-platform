"""Medical allergy model for patient allergy tracking."""

from __future__ import annotations

import enum

from sqlalchemy import String, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AllergySeverity(str, enum.Enum):
    """Allergy severity levels."""

    MILD = 'mild'
    MODERATE = 'moderate'
    SEVERE = 'severe'
    LIFE_THREATENING = 'life_threatening'


class AllergyStatus(str, enum.Enum):
    """Allergy status."""

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    RESOLVED = 'resolved'


class MedicalAllergy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Patient allergy record."""

    __tablename__ = 'medical_allergies'

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Allergen information
    allergen: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Allergen name (e.g., Penicillin, Peanuts, Latex)'
    )
    allergen_type: Mapped[str | None] = mapped_column(
        String(50),
        comment='Type: medication, food, environmental, other'
    )

    # Reaction details
    reaction: Mapped[str | None] = mapped_column(
        String(500),
        comment='Description of allergic reaction'
    )
    severity: Mapped[AllergySeverity] = mapped_column(
        Enum(AllergySeverity),
        nullable=False,
        default=AllergySeverity.MODERATE
    )

    # Clinical information
    onset_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date allergy first observed (YYYY-MM-DD)'
    )
    diagnosed_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date formally diagnosed (YYYY-MM-DD)'
    )
    status: Mapped[AllergyStatus] = mapped_column(
        Enum(AllergyStatus),
        nullable=False,
        default=AllergyStatus.ACTIVE
    )

    # Additional details
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment='Additional notes, context, or special instructions'
    )
    recorded_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        comment='User who recorded this allergy'
    )

    # Relationships
    patient = relationship('Patient', back_populates='allergies')

    def __repr__(self) -> str:
        return f"<MedicalAllergy(patient_id={self.patient_id}, allergen={self.allergen}, severity={self.severity})>"

    @property
    def is_active(self) -> bool:
        """Check if allergy is currently active."""
        return self.status == AllergyStatus.ACTIVE

    @property
    def is_critical(self) -> bool:
        """Check if allergy is severe or life-threatening."""
        return self.severity in [AllergySeverity.SEVERE, AllergySeverity.LIFE_THREATENING]
