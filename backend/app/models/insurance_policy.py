"""Insurance policy model for patient insurance coverage."""

from __future__ import annotations

import enum

from sqlalchemy import String, Enum, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, PracticeScopedMixin


class PolicyType(str, enum.Enum):
    """Insurance policy type."""

    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    TERTIARY = 'tertiary'


class PolicyStatus(str, enum.Enum):
    """Insurance policy status."""

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING = 'pending'
    TERMINATED = 'terminated'


class InsurancePolicy(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """Patient insurance policy information."""

    __tablename__ = 'insurance_policies'

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Policy identification
    policy_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment='Insurance policy number'
    )
    group_number: Mapped[str | None] = mapped_column(
        String(100),
        comment='Group number'
    )
    plan_name: Mapped[str | None] = mapped_column(
        String(255),
        comment='Plan or product name'
    )

    # Insurance company
    insurance_company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment='Insurance company/payer name'
    )
    payer_id: Mapped[str | None] = mapped_column(
        String(50),
        comment='Electronic payer ID for claims submission'
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        comment='Insurance company phone number'
    )
    website: Mapped[str | None] = mapped_column(
        String(255),
        comment='Insurance company website'
    )

    # Subscriber information
    subscriber_id: Mapped[str | None] = mapped_column(
        String(100),
        comment='Subscriber/member ID'
    )
    subscriber_name: Mapped[str | None] = mapped_column(
        String(255),
        comment='Name of subscriber (if different from patient)'
    )
    subscriber_relationship: Mapped[str | None] = mapped_column(
        String(50),
        comment='Relationship to patient: self, spouse, child, other'
    )
    subscriber_dob: Mapped[str | None] = mapped_column(
        String(10),
        comment='Subscriber date of birth (YYYY-MM-DD)'
    )
    subscriber_ssn: Mapped[str | None] = mapped_column(
        String(255),
        comment='Subscriber SSN (encrypted)'
    )

    # Policy type and status
    policy_type: Mapped[PolicyType] = mapped_column(
        Enum(PolicyType),
        nullable=False,
        default=PolicyType.PRIMARY
    )
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus),
        nullable=False,
        default=PolicyStatus.ACTIVE
    )

    # Coverage dates
    effective_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Policy effective date (YYYY-MM-DD)'
    )
    termination_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Policy termination date (YYYY-MM-DD)'
    )

    # Financial information
    copay: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment='Standard copay amount'
    )
    deductible: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment='Annual deductible amount'
    )
    deductible_met: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment='Amount of deductible met to date'
    )
    out_of_pocket_max: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment='Out-of-pocket maximum'
    )
    coinsurance_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment='Coinsurance percentage (e.g., 20 for 20%)'
    )

    # Verification
    verification_status: Mapped[str | None] = mapped_column(
        String(50),
        comment='Verification status: verified, pending, expired, failed'
    )
    verified_date: Mapped[str | None] = mapped_column(
        String(10),
        comment='Date insurance was last verified (YYYY-MM-DD)'
    )
    verified_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        comment='User who verified the insurance'
    )

    # Authorization
    requires_authorization: Mapped[bool] = mapped_column(
        default=False,
        comment='Whether pre-authorization is required'
    )
    authorization_phone: Mapped[str | None] = mapped_column(
        String(20),
        comment='Phone number for authorization requests'
    )

    # Additional information
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment='Additional notes or special instructions'
    )

    # Image storage
    card_front_image_url: Mapped[str | None] = mapped_column(
        String(500),
        comment='URL to front of insurance card image'
    )
    card_back_image_url: Mapped[str | None] = mapped_column(
        String(500),
        comment='URL to back of insurance card image'
    )

    # Relationships
    practice = relationship('Practice')
    patient = relationship('Patient', back_populates='insurance_policies')
    verifications = relationship('InsuranceVerification', back_populates='policy', cascade='all, delete-orphan')
    billing_claims = relationship('BillingClaim', back_populates='insurance_policy')

    def __repr__(self) -> str:
        return f"<InsurancePolicy(patient_id={self.patient_id}, company={self.insurance_company}, policy_number={self.policy_number})>"

    @property
    def is_active(self) -> bool:
        """Check if policy is currently active."""
        return self.status == PolicyStatus.ACTIVE

    @property
    def is_primary(self) -> bool:
        """Check if this is the primary insurance."""
        return self.policy_type == PolicyType.PRIMARY

    @property
    def is_verified(self) -> bool:
        """Check if insurance is verified."""
        return self.verification_status == 'verified'

    @property
    def deductible_remaining(self) -> Decimal | None:
        """Calculate remaining deductible."""
        if self.deductible and self.deductible_met:
            remaining = self.deductible - self.deductible_met
            return max(Decimal('0'), remaining)
        return self.deductible
