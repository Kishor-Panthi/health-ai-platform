"""Provider model for healthcare providers (doctors, nurses, etc)."""

from __future__ import annotations

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Provider(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """Healthcare provider extending User with medical credentials."""

    __tablename__ = 'providers'

    # Link to User account
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )

    # Professional credentials
    npi: Mapped[str | None] = mapped_column(
        String(10),
        unique=True,
        index=True,
        comment='National Provider Identifier'
    )
    license_number: Mapped[str | None] = mapped_column(String(64))
    license_state: Mapped[str | None] = mapped_column(String(2))
    dea_number: Mapped[str | None] = mapped_column(
        String(9),
        comment='DEA registration number for prescribing'
    )

    # Professional details
    title: Mapped[str | None] = mapped_column(
        String(50),
        comment='Dr., MD, DO, NP, PA, RN, etc.'
    )
    specialty: Mapped[str | None] = mapped_column(String(128))
    sub_specialty: Mapped[str | None] = mapped_column(String(128))
    department: Mapped[str | None] = mapped_column(String(128))

    # Practice information
    accepting_new_patients: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    years_of_experience: Mapped[int | None] = mapped_column()
    education: Mapped[str | None] = mapped_column(String(500))
    board_certifications: Mapped[str | None] = mapped_column(String(500))

    # Contact preferences
    phone_direct: Mapped[str | None] = mapped_column(String(32))
    email_work: Mapped[str | None] = mapped_column(String(255))
    pager: Mapped[str | None] = mapped_column(String(32))

    # Bio and notes
    bio: Mapped[str | None] = mapped_column(String(2000))
    languages_spoken: Mapped[str | None] = mapped_column(
        String(255),
        comment='Comma-separated list of languages'
    )
    notes: Mapped[str | None] = mapped_column(String(1000))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    practice = relationship('Practice', back_populates='providers')
    user = relationship('User', back_populates='provider', foreign_keys=[user_id])
    schedules = relationship('ProviderSchedule', back_populates='provider', cascade='all, delete-orphan')
    appointments = relationship('Appointment', back_populates='provider')
    billing_claims = relationship('BillingClaim', back_populates='provider')
    clinical_notes = relationship('ClinicalNote', foreign_keys='ClinicalNote.provider_id', back_populates='provider')

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, npi={self.npi}, specialty={self.specialty})>"
