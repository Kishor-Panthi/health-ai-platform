"""API endpoints for billing, claims, and payments."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.billing import (
    BillingClaim,
    BillingClaimCreate,
    BillingClaimUpdate,
    BillingClaimWithBalance,
    BillingPayment,
    BillingPaymentCreate,
    BillingPaymentUpdate,
    BillingPaymentWithNet,
    BillingTransaction,
    PatientBillingBalance,
    RefundPaymentRequest,
)
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.models.billing_claim import ClaimStatus
from app.models.billing_payment import PaymentSource
from app.models.billing_transaction import TransactionType
from app.models.user import User
from app.services.billing_service import BillingService
from app.services.patient_service import PatientService

router = APIRouter()


async def verify_patient_access(
    patient_id: UUID,
    current_user: User,
    db: AsyncSession,
) -> None:
    """Verify current user has access to patient."""
    patient_service = PatientService(db, current_user.practice_id)
    patient = await patient_service.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")


# ============================================================================
# Claims Endpoints
# ============================================================================


@router.get("/patients/{patient_id}/claims", response_model=PaginatedResponse[BillingClaim])
async def list_patient_claims(
    patient_id: UUID,
    status: Optional[ClaimStatus] = None,
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all claims for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    claims, total = await service.list_claims(
        patient_id=patient_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    return PaginatedResponse(
        items=claims,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post("/patients/{patient_id}/claims", response_model=BillingClaim, status_code=status.HTTP_201_CREATED)
async def create_claim(
    patient_id: UUID,
    claim_in: BillingClaimCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new billing claim."""
    await verify_patient_access(patient_id, current_user, db)

    if claim_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")

    service = BillingService(db, current_user.practice_id)
    claim = await service.create_claim(claim_in, created_by=current_user.id)
    await db.commit()
    return claim


@router.get("/claims/{claim_id}", response_model=BillingClaimWithBalance)
async def get_claim(
    claim_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific claim by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    claim = await service.get_claim_by_id(claim_id, patient_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Add computed fields
    return BillingClaimWithBalance(
        **claim.__dict__,
        outstanding_balance=claim.outstanding_balance,
        payment_percentage=claim.payment_percentage,
        is_fully_paid=claim.is_fully_paid,
    )


@router.patch("/claims/{claim_id}", response_model=BillingClaim)
async def update_claim(
    claim_id: UUID,
    claim_in: BillingClaimUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a claim."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    claim = await service.update_claim(claim_id, patient_id, claim_in)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    await db.commit()
    return claim


@router.post("/claims/{claim_id}/submit", response_model=BillingClaim)
async def submit_claim(
    claim_id: UUID,
    patient_id: UUID = Query(...),
    submission_method: str = Query(..., max_length=50),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Submit a claim."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    try:
        claim = await service.submit_claim(
            claim_id,
            patient_id,
            submission_method,
            submitted_by=current_user.id,
        )
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")

        await db.commit()
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/claims/{claim_id}/status", response_model=BillingClaim)
async def update_claim_status(
    claim_id: UUID,
    patient_id: UUID = Query(...),
    new_status: ClaimStatus = Query(...),
    denial_reason: Optional[str] = Query(None),
    denial_code: Optional[str] = Query(None, max_length=50),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update claim status."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    claim = await service.update_claim_status(
        claim_id,
        patient_id,
        new_status,
        denial_reason,
        denial_code,
    )
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    await db.commit()
    return claim


@router.delete("/claims/{claim_id}", response_model=SuccessResponse)
async def delete_claim(
    claim_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a claim (drafts only)."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    try:
        deleted = await service.delete_claim(claim_id, patient_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Claim not found")

        await db.commit()
        return SuccessResponse(message="Claim deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Payments Endpoints
# ============================================================================


@router.get("/patients/{patient_id}/payments", response_model=PaginatedResponse[BillingPayment])
async def list_patient_payments(
    patient_id: UUID,
    payment_source: Optional[PaymentSource] = None,
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all payments for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    payments, total = await service.list_payments(
        patient_id=patient_id,
        payment_source=payment_source,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    return PaginatedResponse(
        items=payments,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post("/patients/{patient_id}/payments", response_model=BillingPayment, status_code=status.HTTP_201_CREATED)
async def create_payment(
    patient_id: UUID,
    payment_in: BillingPaymentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new payment."""
    await verify_patient_access(patient_id, current_user, db)

    if payment_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")

    service = BillingService(db, current_user.practice_id)
    payment = await service.create_payment(payment_in, processed_by=current_user.id)
    await db.commit()
    return payment


@router.get("/payments/{payment_id}", response_model=BillingPaymentWithNet)
async def get_payment(
    payment_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific payment by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    payment = await service.get_payment_by_id(payment_id, patient_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return BillingPaymentWithNet(
        **payment.__dict__,
        net_payment=payment.net_payment,
        is_fully_refunded=payment.is_fully_refunded,
    )


@router.patch("/payments/{payment_id}", response_model=BillingPayment)
async def update_payment(
    payment_id: UUID,
    payment_in: BillingPaymentUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a payment."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    payment = await service.update_payment(payment_id, patient_id, payment_in)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    await db.commit()
    return payment


@router.post("/payments/{payment_id}/refund", response_model=BillingPayment)
async def refund_payment(
    payment_id: UUID,
    refund_request: RefundPaymentRequest,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Refund a payment."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    try:
        payment = await service.refund_payment(
            payment_id,
            patient_id,
            refund_request.refund_amount,
            refund_request.refund_reason,
            processed_by=current_user.id,
        )
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        await db.commit()
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Transactions and Balance Endpoints
# ============================================================================


@router.get("/patients/{patient_id}/transactions", response_model=list[BillingTransaction])
async def list_patient_transactions(
    patient_id: UUID,
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    transaction_type: Optional[TransactionType] = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get transaction history for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    transactions = await service.get_patient_transactions(
        patient_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        limit=limit,
    )
    return transactions


@router.get("/patients/{patient_id}/balance", response_model=PatientBillingBalance)
async def get_patient_balance(
    patient_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get comprehensive billing balance for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = BillingService(db, current_user.practice_id)
    balance = await service.get_patient_balance(patient_id)
    return balance
