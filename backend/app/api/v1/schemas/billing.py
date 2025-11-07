"""Pydantic schemas for billing."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.billing_claim import ClaimStatus, ClaimType
from app.models.billing_payment import PaymentMethod, PaymentSource, PaymentStatus
from app.models.billing_transaction import AdjustmentReason, TransactionType


# ============================================================================
# Billing Claim Schemas
# ============================================================================


class BillingClaimBase(BaseModel):
    """Base schema for billing claims."""

    insurance_policy_id: UUID = Field(..., description="Insurance policy ID")
    provider_id: UUID = Field(..., description="Provider ID")
    appointment_id: Optional[UUID] = Field(None, description="Appointment ID")
    claim_type: ClaimType = Field(default=ClaimType.PROFESSIONAL, description="Claim type")
    service_date_from: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Service start date")
    service_date_to: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Service end date")
    total_charge: Decimal = Field(..., ge=0, le=999999.99, description="Total billed amount")
    diagnosis_codes: Optional[list[str]] = Field(None, description="ICD-10 diagnosis codes")
    procedure_codes: Optional[list[dict[str, Any]]] = Field(None, description="CPT/HCPCS procedure codes with details")
    place_of_service: Optional[str] = Field(None, max_length=2, description="Place of service code")
    notes: Optional[str] = Field(None, description="Internal notes")
    additional_info: Optional[dict[str, Any]] = Field(None, description="Additional structured data")


class BillingClaimCreate(BillingClaimBase):
    """Schema for creating a billing claim."""

    patient_id: UUID = Field(..., description="Patient ID")
    status: ClaimStatus = Field(default=ClaimStatus.DRAFT, description="Initial claim status")


class BillingClaimUpdate(BaseModel):
    """Schema for updating a billing claim."""

    insurance_policy_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    claim_type: Optional[ClaimType] = None
    status: Optional[ClaimStatus] = None
    service_date_from: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    service_date_to: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    total_charge: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    allowed_amount: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    paid_amount: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    patient_responsibility: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    adjustment_amount: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    diagnosis_codes: Optional[list[str]] = None
    procedure_codes: Optional[list[dict[str, Any]]] = None
    place_of_service: Optional[str] = Field(None, max_length=2)
    submission_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    submission_method: Optional[str] = Field(None, max_length=50)
    response_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    payment_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    denial_reason: Optional[str] = None
    denial_code: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    additional_info: Optional[dict[str, Any]] = None


class BillingClaim(BillingClaimBase):
    """Schema for billing claim response."""

    id: UUID
    patient_id: UUID
    practice_id: UUID
    claim_number: str
    external_claim_id: Optional[str] = None
    status: ClaimStatus
    allowed_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    patient_responsibility: Optional[Decimal] = None
    adjustment_amount: Optional[Decimal] = None
    submission_date: Optional[str] = None
    submission_method: Optional[str] = None
    response_date: Optional[str] = None
    payment_date: Optional[str] = None
    denial_reason: Optional[str] = None
    denial_code: Optional[str] = None
    created_at: str
    updated_at: str
    created_by: Optional[UUID] = None
    submitted_by: Optional[UUID] = None

    model_config = {'from_attributes': True}


class BillingClaimWithBalance(BillingClaim):
    """Claim with calculated balance."""

    outstanding_balance: Decimal
    payment_percentage: float
    is_fully_paid: bool


# ============================================================================
# Billing Payment Schemas
# ============================================================================


class BillingPaymentBase(BaseModel):
    """Base schema for billing payments."""

    payment_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date payment received")
    payment_amount: Decimal = Field(..., ge=0, le=999999.99, description="Payment amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    payment_source: PaymentSource = Field(..., description="Payment source")
    check_number: Optional[str] = Field(None, max_length=50, description="Check number")
    reference_number: Optional[str] = Field(None, max_length=100, description="Reference or transaction number")
    card_last_four: Optional[str] = Field(None, max_length=4, description="Last 4 digits of card")
    card_type: Optional[str] = Field(None, max_length=50, description="Card type")
    eob_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="EOB date")
    insurance_check_number: Optional[str] = Field(None, max_length=50, description="Insurance check number")
    applied_to_claim: Optional[Decimal] = Field(None, ge=0, le=999999.99, description="Amount applied to claim")
    applied_to_copay: Optional[Decimal] = Field(None, ge=0, le=999999.99, description="Amount applied to copay")
    applied_to_deductible: Optional[Decimal] = Field(None, ge=0, le=999999.99, description="Amount applied to deductible")
    applied_to_coinsurance: Optional[Decimal] = Field(None, ge=0, le=999999.99, description="Amount applied to coinsurance")
    notes: Optional[str] = Field(None, description="Payment notes")
    payment_details: Optional[dict[str, Any]] = Field(None, description="Additional payment details")


class BillingPaymentCreate(BillingPaymentBase):
    """Schema for creating a billing payment."""

    patient_id: UUID = Field(..., description="Patient ID")
    claim_id: Optional[UUID] = Field(None, description="Claim ID (optional)")
    status: PaymentStatus = Field(default=PaymentStatus.COMPLETED, description="Payment status")


class BillingPaymentUpdate(BaseModel):
    """Schema for updating a billing payment."""

    payment_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    payment_amount: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    payment_method: Optional[PaymentMethod] = None
    payment_source: Optional[PaymentSource] = None
    status: Optional[PaymentStatus] = None
    check_number: Optional[str] = Field(None, max_length=50)
    reference_number: Optional[str] = Field(None, max_length=100)
    card_last_four: Optional[str] = Field(None, max_length=4)
    card_type: Optional[str] = Field(None, max_length=50)
    eob_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    insurance_check_number: Optional[str] = Field(None, max_length=50)
    applied_to_claim: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    applied_to_copay: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    applied_to_deductible: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    applied_to_coinsurance: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    unapplied_amount: Optional[Decimal] = Field(None, ge=0, le=999999.99)
    posted_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    notes: Optional[str] = None
    payment_details: Optional[dict[str, Any]] = None


class BillingPayment(BillingPaymentBase):
    """Schema for billing payment response."""

    id: UUID
    patient_id: UUID
    claim_id: Optional[UUID] = None
    practice_id: UUID
    payment_number: str
    external_payment_id: Optional[str] = None
    status: PaymentStatus
    unapplied_amount: Optional[Decimal] = None
    refunded_amount: Optional[Decimal] = None
    refund_date: Optional[str] = None
    refund_reason: Optional[str] = None
    processed_by: Optional[UUID] = None
    posted_date: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


class BillingPaymentWithNet(BillingPayment):
    """Payment with calculated net amount."""

    net_payment: Decimal
    is_fully_refunded: bool


class RefundPaymentRequest(BaseModel):
    """Schema for refunding a payment."""

    refund_amount: Decimal = Field(..., ge=0, le=999999.99, description="Amount to refund")
    refund_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Refund date")
    refund_reason: str = Field(..., min_length=1, description="Reason for refund")


# ============================================================================
# Billing Transaction Schemas
# ============================================================================


class BillingTransactionBase(BaseModel):
    """Base schema for billing transactions."""

    transaction_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Transaction date")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    amount: Decimal = Field(..., description="Transaction amount")
    description: str = Field(..., max_length=500, description="Transaction description")
    adjustment_reason: Optional[AdjustmentReason] = Field(None, description="Adjustment reason if applicable")
    notes: Optional[str] = Field(None, description="Additional notes")
    reference_number: Optional[str] = Field(None, max_length=100, description="External reference number")


class BillingTransactionCreate(BillingTransactionBase):
    """Schema for creating a billing transaction."""

    patient_id: UUID = Field(..., description="Patient ID")
    claim_id: Optional[UUID] = Field(None, description="Claim ID")
    payment_id: Optional[UUID] = Field(None, description="Payment ID")
    provider_id: Optional[UUID] = Field(None, description="Provider ID")
    balance_after: Decimal = Field(..., description="Account balance after transaction")


class BillingTransaction(BillingTransactionBase):
    """Schema for billing transaction response."""

    id: UUID
    patient_id: UUID
    claim_id: Optional[UUID] = None
    payment_id: Optional[UUID] = None
    practice_id: UUID
    balance_after: Decimal
    provider_id: Optional[UUID] = None
    is_reversal: bool
    reversed_transaction_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}


# ============================================================================
# Combined/Summary Schemas
# ============================================================================


class PatientBillingBalance(BaseModel):
    """Patient billing balance summary."""

    patient_id: UUID
    total_charges: Decimal
    total_payments: Decimal
    total_adjustments: Decimal
    current_balance: Decimal
    insurance_pending: Decimal
    patient_responsibility: Decimal
    unapplied_credits: Decimal


class ClaimSummary(BaseModel):
    """Summary of claims for reporting."""

    total_claims: int
    total_billed: Decimal
    total_paid: Decimal
    total_pending: Decimal
    total_denied: Decimal
    by_status: dict[str, int]


class PaymentSummary(BaseModel):
    """Summary of payments for reporting."""

    total_payments: int
    total_amount: Decimal
    total_refunded: Decimal
    by_source: dict[str, Decimal]
    by_method: dict[str, Decimal]
