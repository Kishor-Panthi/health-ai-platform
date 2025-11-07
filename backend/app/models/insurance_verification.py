"""Insurance verification model for tracking insurance verification activities."""

from __future__ import annotations

import enum

from sqlalchemy import String, Enum, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class VerificationStatus(str, enum.Enum):
    """Insurance verification status."""

    VERIFIED = 'verified'
    PENDING = 'pending'
    FAILED = 'failed'
    EXPIRED = 'expired'
    NEEDS_UPDATE = 'needs_update'


class VerificationMethod(str, enum.Enum):
    """Method used for verification."""

    PHONE = 'phone'
    ONLINE_PORTAL = 'online_portal'
    FAX = 'fax'
    EMAIL = 'email'
    ELECTRONIC = 'electronic'
    OTHER = 'other'


class InsuranceVerification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Insurance verification record."""

    __tablename__ = 'insurance_verifications'

    # Policy reference
    policy_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('insurance_policies.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Verification details
    verification_date: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment='Date verification was performed (YYYY-MM-DD)'
    )
    verification_time: Mapped[str | None] = mapped_column(
        String(8),
        comment='Time verification was performed (HH:MM:SS)'
    )
    verified_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='User who performed verification'
    )

    # Verification method and status
    method: Mapped[VerificationMethod] = mapped_column(
        Enum(VerificationMethod),
        nullable=False,
        default=VerificationMethod.PHONE
    )
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus),
        nullable=False,
        default=VerificationStatus.PENDING
    )

    # Contact information
    contact_name: Mapped[str | None] = mapped_column(
        String(255),
        comment='Name of insurance rep contacted'
    )
    contact_phone: Mapped[str | None] = mapped_column(
        String(20),
        comment='Phone number used for verification'
    )
    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        comment='Verification reference or confirmation number'
    )

    # Coverage details verified
    coverage_active: Mapped[bool | None] = mapped_column(
        comment='Whether coverage is active'
    )
    effective_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Coverage effective date confirmed (YYYY-MM-DD)'
    )
    termination_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Coverage termination date if applicable (YYYY-MM-DD)'
    )

    # Benefits verified
    benefits_verified: Mapped[dict | None] = mapped_column(
        JSONB,
        comment='JSON object containing verified benefits details'
    )

    # Specific service verification (optional)
    service_type: Mapped[str | None] = mapped_column(
        String(100),
        comment='Type of service being verified (e.g., office visit, surgery)'
    )
    service_cpt_code: Mapped[str | None] = mapped_column(
        String(10),
        comment='CPT code for service being verified'
    )
    service_authorized: Mapped[bool | None] = mapped_column(
        comment='Whether service is authorized/covered'
    )
    authorization_required: Mapped[bool | None] = mapped_column(
        comment='Whether pre-authorization is required'
    )
    authorization_number: Mapped[str | None] = mapped_column(
        String(100),
        comment='Authorization number if obtained'
    )

    # Financial information verified
    copay_amount: Mapped[str | None] = mapped_column(
        String(50),
        comment='Copay amount confirmed'
    )
    deductible_amount: Mapped[str | None] = mapped_column(
        String(50),
        comment='Deductible amount confirmed'
    )
    deductible_met: Mapped[str | None] = mapped_column(
        String(50),
        comment='Amount of deductible met'
    )
    out_of_pocket_max: Mapped[str | None] = mapped_column(
        String(50),
        comment='Out-of-pocket maximum confirmed'
    )
    coinsurance: Mapped[str | None] = mapped_column(
        String(50),
        comment='Coinsurance percentage confirmed'
    )

    # Notes and additional details
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment='Detailed notes from verification call/process'
    )
    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        comment='Reason for verification failure if applicable'
    )

    # Next verification
    next_verification_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date next verification is recommended (YYYY-MM-DD)'
    )

    # Relationships
    policy = relationship('InsurancePolicy', back_populates='verifications')
    verified_by_user = relationship('User', foreign_keys=[verified_by])

    def __repr__(self) -> str:
        return f"<InsuranceVerification(policy_id={self.policy_id}, date={self.verification_date}, status={self.status})>"

    @property
    def is_successful(self) -> bool:
        """Check if verification was successful."""
        return self.status == VerificationStatus.VERIFIED

    @property
    def is_current(self) -> bool:
        """Check if verification is current (verified and not expired)."""
        return self.status == VerificationStatus.VERIFIED
