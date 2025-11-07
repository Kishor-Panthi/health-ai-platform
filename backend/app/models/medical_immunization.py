"""Medical immunization model for patient vaccination records."""

from __future__ import annotations

from sqlalchemy import String, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class MedicalImmunization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Patient immunization/vaccination record."""

    __tablename__ = 'medical_immunizations'

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Vaccine information
    vaccine_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Vaccine name (e.g., COVID-19, Influenza, MMR)'
    )
    cvx_code: Mapped[str | None] = mapped_column(
        String(10),
        comment='CVX (vaccine administered) code'
    )
    vaccine_manufacturer: Mapped[str | None] = mapped_column(
        String(100),
        comment='Vaccine manufacturer'
    )

    # Administration details
    administration_date: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment='Date vaccine was administered (YYYY-MM-DD)'
    )
    lot_number: Mapped[str | None] = mapped_column(
        String(100),
        comment='Vaccine lot number'
    )
    expiration_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Vaccine expiration date (YYYY-MM-DD)'
    )

    # Dosage information
    dosage: Mapped[str | None] = mapped_column(
        String(50),
        comment='Dosage amount (e.g., 0.5ml)'
    )
    dose_number: Mapped[int | None] = mapped_column(
        Integer,
        comment='Dose number in series (e.g., 1 for first dose, 2 for second)'
    )
    series_doses: Mapped[int | None] = mapped_column(
        Integer,
        comment='Total doses in series (e.g., 2 for two-dose series)'
    )

    # Administration location
    administered_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('providers.id', ondelete='SET NULL'),
        comment='Provider who administered vaccine'
    )
    administration_site: Mapped[str | None] = mapped_column(
        String(100),
        comment='Body site (e.g., left deltoid, right thigh)'
    )
    route: Mapped[str | None] = mapped_column(
        String(50),
        comment='Route of administration (e.g., intramuscular, subcutaneous)'
    )
    facility: Mapped[str | None] = mapped_column(
        String(255),
        comment='Facility where vaccine was administered'
    )

    # Clinical information
    indication: Mapped[str | None] = mapped_column(
        String(255),
        comment='Reason for vaccination'
    )
    funding_source: Mapped[str | None] = mapped_column(
        String(100),
        comment='Funding source (e.g., private, public, VFC)'
    )

    # Adverse reactions
    adverse_reaction: Mapped[str | None] = mapped_column(
        Text,
        comment='Any adverse reactions observed'
    )
    reaction_severity: Mapped[str | None] = mapped_column(
        String(50),
        comment='Severity of adverse reaction if any'
    )

    # Next dose
    next_dose_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date next dose is due (YYYY-MM-DD)'
    )

    # Additional notes
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment='Additional notes or special circumstances'
    )

    # Consent and documentation
    consent_obtained: Mapped[bool] = mapped_column(
        default=True,
        comment='Whether patient consent was obtained'
    )
    vis_provided: Mapped[bool] = mapped_column(
        default=False,
        comment='Whether Vaccine Information Statement was provided'
    )

    # Tracking
    recorded_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        comment='User who recorded this immunization'
    )

    # Relationships
    patient = relationship('Patient', back_populates='immunizations')
    administered_by_provider = relationship('Provider', foreign_keys=[administered_by])

    def __repr__(self) -> str:
        return f"<MedicalImmunization(patient_id={self.patient_id}, vaccine={self.vaccine_name}, date={self.administration_date})>"

    @property
    def is_series_complete(self) -> bool:
        """Check if vaccination series is complete."""
        if self.dose_number and self.series_doses:
            return self.dose_number >= self.series_doses
        return False

    @property
    def doses_remaining(self) -> int | None:
        """Calculate remaining doses in series."""
        if self.dose_number and self.series_doses:
            remaining = self.series_doses - self.dose_number
            return max(0, remaining)
        return None
