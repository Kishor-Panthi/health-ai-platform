"""Billing transaction model for financial ledger."""

from __future__ import annotations

import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PracticeScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class TransactionType(str, enum.Enum):
    """Transaction type enumeration."""

    CHARGE = "charge"
    PAYMENT = "payment"
    ADJUSTMENT = "adjustment"
    REFUND = "refund"
    WRITE_OFF = "write_off"
    TRANSFER = "transfer"
    REVERSAL = "reversal"


class AdjustmentReason(str, enum.Enum):
    """Adjustment reason enumeration."""

    CONTRACTUAL = "contractual"
    PROVIDER_DISCOUNT = "provider_discount"
    COURTESY = "courtesy"
    PROFESSIONAL_COURTESY = "professional_courtesy"
    HARDSHIP = "hardship"
    INSURANCE_WRITE_OFF = "insurance_write_off"
    BAD_DEBT = "bad_debt"
    COLLECTION_AGENCY = "collection_agency"
    OTHER = "other"


class BillingTransaction(UUIDPrimaryKeyMixin, PracticeScopedMixin, TimestampMixin, Base):
    """Financial transaction ledger for patient accounts."""

    __tablename__ = "billing_transactions"

    # Patient reference
    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Claim reference (optional)
    claim_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billing_claims.id", ondelete="SET NULL"),
        index=True,
    )

    # Payment reference (optional)
    payment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billing_payments.id", ondelete="SET NULL"),
        index=True,
    )

    # Transaction details
    transaction_date: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True, comment="Transaction date (YYYY-MM-DD)"
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False, index=True
    )

    # Amount (positive for charges, negative for payments/adjustments/refunds)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Transaction amount"
    )

    # Running balance after this transaction
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Account balance after transaction"
    )

    # Adjustment details (if applicable)
    adjustment_reason: Mapped[AdjustmentReason | None] = mapped_column(
        Enum(AdjustmentReason), comment="Reason for adjustment"
    )

    # Description and notes
    description: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Transaction description"
    )
    notes: Mapped[str | None] = mapped_column(Text, comment="Additional notes")

    # Reference information
    reference_number: Mapped[str | None] = mapped_column(
        String(100), comment="External reference number"
    )

    # Provider reference (for charges)
    provider_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="SET NULL"),
        comment="Provider associated with transaction",
    )

    # Reversal tracking
    is_reversal: Mapped[bool] = mapped_column(
        default=False, comment="Is this a reversal transaction"
    )
    reversed_transaction_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billing_transactions.id", ondelete="SET NULL"),
        comment="Original transaction being reversed",
    )

    # Audit
    created_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="User who created transaction",
    )

    # Relationships
    patient = relationship("Patient", back_populates="billing_transactions")
    claim = relationship("BillingClaim", back_populates="transactions")
    payment = relationship("BillingPayment")
    provider = relationship("Provider")
    reversed_transaction = relationship(
        "BillingTransaction", remote_side="BillingTransaction.id", uselist=False
    )

    def __repr__(self) -> str:
        return f"<BillingTransaction(type={self.transaction_type}, amount={self.amount}, date={self.transaction_date})>"

    @property
    def is_charge(self) -> bool:
        """Check if transaction is a charge."""
        return self.transaction_type == TransactionType.CHARGE

    @property
    def is_payment(self) -> bool:
        """Check if transaction is a payment."""
        return self.transaction_type == TransactionType.PAYMENT

    @property
    def is_adjustment(self) -> bool:
        """Check if transaction is an adjustment."""
        return self.transaction_type == TransactionType.ADJUSTMENT
