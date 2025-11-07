"""Billing claim model for insurance claims and billing."""

from __future__ import annotations

import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ClaimStatus(str, enum.Enum):
    """Claim status enumeration."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DENIED = "denied"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    APPEALED = "appealed"
    VOID = "void"


class ClaimType(str, enum.Enum):
    """Claim type enumeration."""

    PROFESSIONAL = "professional"  # CMS-1500
    INSTITUTIONAL = "institutional"  # UB-04
    DENTAL = "dental"
    PHARMACY = "pharmacy"


class BillingClaim(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """Insurance claim for billing."""

    __tablename__ = "billing_claims"

    # Patient and appointment references
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    appointment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        index=True,
    )

    # Insurance policy reference
    insurance_policy_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("insurance_policies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Provider reference
    provider_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Claim identification
    claim_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    external_claim_id: Mapped[str | None] = mapped_column(
        String(100), index=True, comment="Payer's claim ID"
    )
    claim_type: Mapped[ClaimType] = mapped_column(
        Enum(ClaimType), default=ClaimType.PROFESSIONAL, nullable=False
    )
    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus), default=ClaimStatus.DRAFT, nullable=False, index=True
    )

    # Service dates
    service_date_from: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True, comment="Service start date (YYYY-MM-DD)"
    )
    service_date_to: Mapped[str | None] = mapped_column(
        String(10), comment="Service end date (YYYY-MM-DD)"
    )

    # Financial information
    total_charge: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Total billed amount"
    )
    allowed_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Insurance allowed amount"
    )
    paid_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), comment="Amount paid by insurance"
    )
    patient_responsibility: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Amount patient owes"
    )
    adjustment_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), comment="Total adjustments"
    )

    # Diagnosis codes (up to 12 ICD-10 codes)
    diagnosis_codes: Mapped[list | None] = mapped_column(
        JSONB, comment="Array of ICD-10 diagnosis codes"
    )

    # Procedure/service codes (CPT/HCPCS codes)
    procedure_codes: Mapped[list | None] = mapped_column(
        JSONB,
        comment="Array of procedure objects with CPT/HCPCS codes, units, charges",
    )

    # Place of service
    place_of_service: Mapped[str | None] = mapped_column(
        String(2), comment="2-digit place of service code"
    )

    # Submission tracking
    submission_date: Mapped[str | None] = mapped_column(
        String(10), index=True, comment="Date claim was submitted"
    )
    submission_method: Mapped[str | None] = mapped_column(
        String(50), comment="EDI, paper, portal, etc."
    )

    # Response tracking
    response_date: Mapped[str | None] = mapped_column(
        String(10), comment="Date of payer response"
    )
    payment_date: Mapped[str | None] = mapped_column(
        String(10), comment="Date payment received"
    )

    # Denial/rejection information
    denial_reason: Mapped[str | None] = mapped_column(Text, comment="Reason for denial")
    denial_code: Mapped[str | None] = mapped_column(
        String(50), comment="Payer denial code"
    )

    # Additional information
    notes: Mapped[str | None] = mapped_column(Text, comment="Internal notes")
    additional_info: Mapped[dict | None] = mapped_column(
        JSONB, comment="Additional structured data"
    )

    # Audit fields
    created_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who created claim",
    )
    submitted_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who submitted claim",
    )

    # Relationships
    patient = relationship("Patient", back_populates="billing_claims")
    appointment = relationship("Appointment", back_populates="billing_claims")
    insurance_policy = relationship("InsurancePolicy", back_populates="billing_claims")
    provider = relationship("Provider", back_populates="billing_claims")
    payments = relationship(
        "BillingPayment", back_populates="claim", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "BillingTransaction", back_populates="claim", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<BillingClaim(claim_number={self.claim_number}, status={self.status}, total={self.total_charge})>"

    @property
    def outstanding_balance(self) -> Decimal:
        """Calculate outstanding balance (total - paid - adjustments)."""
        paid = self.paid_amount or Decimal("0.00")
        adjustments = self.adjustment_amount or Decimal("0.00")
        return self.total_charge - paid - adjustments

    @property
    def payment_percentage(self) -> float:
        """Calculate percentage of claim that has been paid."""
        if self.total_charge == 0:
            return 0.0
        paid = self.paid_amount or Decimal("0.00")
        return float((paid / self.total_charge) * 100)

    @property
    def is_fully_paid(self) -> bool:
        """Check if claim is fully paid."""
        return self.outstanding_balance <= Decimal("0.00")
