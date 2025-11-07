"""Billing payment model for tracking payments."""

from __future__ import annotations

import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration."""

    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    ACH = "ach"
    WIRE_TRANSFER = "wire_transfer"
    INSURANCE = "insurance"
    OTHER = "other"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"


class PaymentSource(str, enum.Enum):
    """Payment source enumeration."""

    PATIENT = "patient"
    INSURANCE_PRIMARY = "insurance_primary"
    INSURANCE_SECONDARY = "insurance_secondary"
    INSURANCE_TERTIARY = "insurance_tertiary"
    THIRD_PARTY = "third_party"


class BillingPayment(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """Payment record for claims and patient balances."""

    __tablename__ = "billing_payments"

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Claim reference (optional - payment may not be tied to specific claim)
    claim_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billing_claims.id", ondelete="SET NULL"),
        index=True,
    )

    # Payment identification
    payment_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    external_payment_id: Mapped[str | None] = mapped_column(
        String(100), index=True, comment="External transaction/confirmation ID"
    )

    # Payment details
    payment_date: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True, comment="Date payment received"
    )
    payment_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Payment amount"
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False
    )
    payment_source: Mapped[PaymentSource] = mapped_column(
        Enum(PaymentSource), nullable=False, index=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.COMPLETED, nullable=False, index=True
    )

    # Check/transaction details
    check_number: Mapped[str | None] = mapped_column(String(50), comment="Check number")
    reference_number: Mapped[str | None] = mapped_column(
        String(100), comment="Reference or transaction number"
    )

    # Card details (last 4 digits only for security)
    card_last_four: Mapped[str | None] = mapped_column(
        String(4), comment="Last 4 digits of card"
    )
    card_type: Mapped[str | None] = mapped_column(
        String(50), comment="Visa, Mastercard, etc."
    )

    # Insurance EOB details
    eob_date: Mapped[str | None] = mapped_column(
        String(10), comment="Explanation of Benefits date"
    )
    insurance_check_number: Mapped[str | None] = mapped_column(
        String(50), comment="Insurance check number"
    )

    # Applied amounts
    applied_to_claim: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Amount applied to specific claim"
    )
    applied_to_copay: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Amount applied to copay"
    )
    applied_to_deductible: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Amount applied to deductible"
    )
    applied_to_coinsurance: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Amount applied to coinsurance"
    )
    unapplied_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), comment="Unapplied credit"
    )

    # Refund tracking
    refunded_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), comment="Amount refunded"
    )
    refund_date: Mapped[str | None] = mapped_column(
        String(10), comment="Date of refund"
    )
    refund_reason: Mapped[str | None] = mapped_column(Text, comment="Reason for refund")

    # Processing information
    processed_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who processed payment",
    )
    posted_date: Mapped[str | None] = mapped_column(
        String(10), comment="Date payment was posted to account"
    )

    # Additional information
    notes: Mapped[str | None] = mapped_column(Text, comment="Payment notes")
    payment_details: Mapped[dict | None] = mapped_column(
        JSONB, comment="Additional payment details"
    )

    # Relationships
    patient = relationship("Patient", back_populates="billing_payments")
    claim = relationship("BillingClaim", back_populates="payments")

    def __repr__(self) -> str:
        return f"<BillingPayment(payment_number={self.payment_number}, amount={self.payment_amount}, source={self.payment_source})>"

    @property
    def net_payment(self) -> Decimal:
        """Calculate net payment after refunds."""
        refunded = self.refunded_amount or Decimal("0.00")
        return self.payment_amount - refunded

    @property
    def is_fully_refunded(self) -> bool:
        """Check if payment is fully refunded."""
        return self.refunded_amount == self.payment_amount
