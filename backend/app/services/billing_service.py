"""Service for managing billing, claims, and payments."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.billing import (
    BillingClaimCreate,
    BillingClaimUpdate,
    BillingPaymentCreate,
    BillingPaymentUpdate,
    BillingTransactionCreate,
    PatientBillingBalance,
)
from app.models.billing_claim import BillingClaim, ClaimStatus
from app.models.billing_payment import BillingPayment, PaymentSource, PaymentStatus
from app.models.billing_transaction import BillingTransaction, TransactionType


class BillingService:
    """Service for billing operations."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ========================================================================
    # Claims Management
    # ========================================================================

    async def list_claims(
        self,
        patient_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        status: Optional[ClaimStatus] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BillingClaim], int]:
        """List claims with filtering."""
        query = select(BillingClaim).where(BillingClaim.practice_id == self.practice_id)

        if patient_id:
            query = query.where(BillingClaim.patient_id == patient_id)
        if provider_id:
            query = query.where(BillingClaim.provider_id == provider_id)
        if status:
            query = query.where(BillingClaim.status == status)
        if start_date:
            query = query.where(BillingClaim.service_date_from >= start_date)
        if end_date:
            query = query.where(BillingClaim.service_date_from <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(BillingClaim.service_date_from.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        claims = list(result.scalars().all())

        return claims, total

    async def get_claim_by_id(
        self,
        claim_id: UUID,
        patient_id: UUID,
    ) -> BillingClaim | None:
        """Get a specific claim by ID."""
        query = select(BillingClaim).where(
            and_(
                BillingClaim.id == claim_id,
                BillingClaim.patient_id == patient_id,
                BillingClaim.practice_id == self.practice_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_claim(
        self,
        claim_data: BillingClaimCreate,
        created_by: UUID,
    ) -> BillingClaim:
        """Create a new claim."""
        # Generate unique claim number
        claim_number = await self._generate_claim_number()

        claim = BillingClaim(
            **claim_data.model_dump(),
            practice_id=self.practice_id,
            claim_number=claim_number,
            created_by=created_by,
        )
        self.db.add(claim)
        await self.db.flush()
        await self.db.refresh(claim)

        # Create initial transaction if claim is in SUBMITTED or higher status
        if claim.status != ClaimStatus.DRAFT:
            await self._create_claim_transaction(claim, created_by)

        return claim

    async def update_claim(
        self,
        claim_id: UUID,
        patient_id: UUID,
        claim_data: BillingClaimUpdate,
    ) -> BillingClaim | None:
        """Update a claim."""
        claim = await self.get_claim_by_id(claim_id, patient_id)
        if not claim:
            return None

        for field, value in claim_data.model_dump(exclude_unset=True).items():
            setattr(claim, field, value)

        await self.db.flush()
        await self.db.refresh(claim)
        return claim

    async def submit_claim(
        self,
        claim_id: UUID,
        patient_id: UUID,
        submission_method: str,
        submitted_by: UUID,
    ) -> BillingClaim | None:
        """Submit a claim."""
        claim = await self.get_claim_by_id(claim_id, patient_id)
        if not claim:
            return None

        if claim.status != ClaimStatus.DRAFT:
            raise ValueError("Only draft claims can be submitted")

        claim.status = ClaimStatus.SUBMITTED
        claim.submission_date = datetime.now().date().isoformat()
        claim.submission_method = submission_method
        claim.submitted_by = submitted_by

        await self.db.flush()

        # Create transaction for charge
        await self._create_claim_transaction(claim, submitted_by)

        await self.db.refresh(claim)
        return claim

    async def update_claim_status(
        self,
        claim_id: UUID,
        patient_id: UUID,
        new_status: ClaimStatus,
        denial_reason: Optional[str] = None,
        denial_code: Optional[str] = None,
    ) -> BillingClaim | None:
        """Update claim status."""
        claim = await self.get_claim_by_id(claim_id, patient_id)
        if not claim:
            return None

        claim.status = new_status
        claim.response_date = datetime.now().date().isoformat()

        if new_status in (ClaimStatus.DENIED, ClaimStatus.REJECTED):
            claim.denial_reason = denial_reason
            claim.denial_code = denial_code

        await self.db.flush()
        await self.db.refresh(claim)
        return claim

    async def delete_claim(
        self,
        claim_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete a claim (only drafts)."""
        claim = await self.get_claim_by_id(claim_id, patient_id)
        if not claim:
            return False

        if claim.status != ClaimStatus.DRAFT:
            raise ValueError("Only draft claims can be deleted")

        await self.db.delete(claim)
        await self.db.flush()
        return True

    async def _generate_claim_number(self) -> str:
        """Generate unique claim number."""
        # Format: CLM-YYYYMMDD-XXXXXX
        date_part = datetime.now().strftime("%Y%m%d")
        unique_part = str(uuid4())[:6].upper()
        return f"CLM-{date_part}-{unique_part}"

    async def _create_claim_transaction(
        self,
        claim: BillingClaim,
        created_by: UUID,
    ) -> None:
        """Create a transaction for a claim charge."""
        balance = await self._get_patient_balance(claim.patient_id)
        new_balance = balance + claim.total_charge

        transaction = BillingTransaction(
            patient_id=claim.patient_id,
            claim_id=claim.id,
            practice_id=self.practice_id,
            transaction_date=claim.service_date_from,
            transaction_type=TransactionType.CHARGE,
            amount=claim.total_charge,
            balance_after=new_balance,
            description=f"Claim {claim.claim_number} - {claim.claim_type.value}",
            provider_id=claim.provider_id,
            created_by=created_by,
        )
        self.db.add(transaction)
        await self.db.flush()

    # ========================================================================
    # Payments Management
    # ========================================================================

    async def list_payments(
        self,
        patient_id: Optional[UUID] = None,
        claim_id: Optional[UUID] = None,
        payment_source: Optional[PaymentSource] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BillingPayment], int]:
        """List payments with filtering."""
        query = select(BillingPayment).where(BillingPayment.practice_id == self.practice_id)

        if patient_id:
            query = query.where(BillingPayment.patient_id == patient_id)
        if claim_id:
            query = query.where(BillingPayment.claim_id == claim_id)
        if payment_source:
            query = query.where(BillingPayment.payment_source == payment_source)
        if start_date:
            query = query.where(BillingPayment.payment_date >= start_date)
        if end_date:
            query = query.where(BillingPayment.payment_date <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(BillingPayment.payment_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        payments = list(result.scalars().all())

        return payments, total

    async def get_payment_by_id(
        self,
        payment_id: UUID,
        patient_id: UUID,
    ) -> BillingPayment | None:
        """Get a specific payment by ID."""
        query = select(BillingPayment).where(
            and_(
                BillingPayment.id == payment_id,
                BillingPayment.patient_id == patient_id,
                BillingPayment.practice_id == self.practice_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_payment(
        self,
        payment_data: BillingPaymentCreate,
        processed_by: UUID,
    ) -> BillingPayment:
        """Create a new payment."""
        # Generate unique payment number
        payment_number = await self._generate_payment_number()

        payment = BillingPayment(
            **payment_data.model_dump(),
            practice_id=self.practice_id,
            payment_number=payment_number,
            processed_by=processed_by,
            posted_date=datetime.now().date().isoformat(),
        )
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)

        # Create transaction for payment
        await self._create_payment_transaction(payment, processed_by)

        # Update claim if payment is linked
        if payment.claim_id:
            await self._update_claim_payment(payment)

        return payment

    async def update_payment(
        self,
        payment_id: UUID,
        patient_id: UUID,
        payment_data: BillingPaymentUpdate,
    ) -> BillingPayment | None:
        """Update a payment."""
        payment = await self.get_payment_by_id(payment_id, patient_id)
        if not payment:
            return None

        for field, value in payment_data.model_dump(exclude_unset=True).items():
            setattr(payment, field, value)

        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def refund_payment(
        self,
        payment_id: UUID,
        patient_id: UUID,
        refund_amount: Decimal,
        refund_reason: str,
        processed_by: UUID,
    ) -> BillingPayment | None:
        """Refund a payment."""
        payment = await self.get_payment_by_id(payment_id, patient_id)
        if not payment:
            return None

        if payment.status not in (PaymentStatus.COMPLETED, PaymentStatus.PARTIALLY_REFUNDED):
            raise ValueError("Only completed or partially refunded payments can be refunded")

        current_refunded = payment.refunded_amount or Decimal("0.00")
        total_refunded = current_refunded + refund_amount

        if total_refunded > payment.payment_amount:
            raise ValueError("Refund amount exceeds payment amount")

        payment.refunded_amount = total_refunded
        payment.refund_date = datetime.now().date().isoformat()
        payment.refund_reason = refund_reason

        if total_refunded == payment.payment_amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        await self.db.flush()

        # Create refund transaction
        await self._create_refund_transaction(payment, refund_amount, processed_by)

        await self.db.refresh(payment)
        return payment

    async def _generate_payment_number(self) -> str:
        """Generate unique payment number."""
        # Format: PMT-YYYYMMDD-XXXXXX
        date_part = datetime.now().strftime("%Y%m%d")
        unique_part = str(uuid4())[:6].upper()
        return f"PMT-{date_part}-{unique_part}"

    async def _create_payment_transaction(
        self,
        payment: BillingPayment,
        created_by: UUID,
    ) -> None:
        """Create a transaction for a payment."""
        balance = await self._get_patient_balance(payment.patient_id)
        new_balance = balance - payment.payment_amount

        transaction = BillingTransaction(
            patient_id=payment.patient_id,
            claim_id=payment.claim_id,
            payment_id=payment.id,
            practice_id=self.practice_id,
            transaction_date=payment.payment_date,
            transaction_type=TransactionType.PAYMENT,
            amount=-payment.payment_amount,  # Negative for payment
            balance_after=new_balance,
            description=f"Payment {payment.payment_number} - {payment.payment_source.value}",
            created_by=created_by,
        )
        self.db.add(transaction)
        await self.db.flush()

    async def _create_refund_transaction(
        self,
        payment: BillingPayment,
        refund_amount: Decimal,
        created_by: UUID,
    ) -> None:
        """Create a transaction for a refund."""
        balance = await self._get_patient_balance(payment.patient_id)
        new_balance = balance + refund_amount

        transaction = BillingTransaction(
            patient_id=payment.patient_id,
            claim_id=payment.claim_id,
            payment_id=payment.id,
            practice_id=self.practice_id,
            transaction_date=payment.refund_date,
            transaction_type=TransactionType.REFUND,
            amount=refund_amount,  # Positive for refund
            balance_after=new_balance,
            description=f"Refund for {payment.payment_number}: {payment.refund_reason}",
            created_by=created_by,
        )
        self.db.add(transaction)
        await self.db.flush()

    async def _update_claim_payment(self, payment: BillingPayment) -> None:
        """Update claim with payment information."""
        if not payment.claim_id:
            return

        query = select(BillingClaim).where(BillingClaim.id == payment.claim_id)
        result = await self.db.execute(query)
        claim = result.scalar_one_or_none()

        if not claim:
            return

        # Update paid amount
        current_paid = claim.paid_amount or Decimal("0.00")
        claim.paid_amount = current_paid + payment.payment_amount
        claim.payment_date = payment.payment_date

        # Update status based on payment
        if claim.is_fully_paid:
            claim.status = ClaimStatus.PAID
        elif claim.paid_amount > 0:
            claim.status = ClaimStatus.PARTIALLY_PAID

        await self.db.flush()

    # ========================================================================
    # Transactions and Balance
    # ========================================================================

    async def get_patient_transactions(
        self,
        patient_id: UUID,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        limit: int = 100,
    ) -> list[BillingTransaction]:
        """Get transaction history for a patient."""
        query = select(BillingTransaction).where(
            and_(
                BillingTransaction.patient_id == patient_id,
                BillingTransaction.practice_id == self.practice_id,
            )
        )

        if start_date:
            query = query.where(BillingTransaction.transaction_date >= start_date)
        if end_date:
            query = query.where(BillingTransaction.transaction_date <= end_date)
        if transaction_type:
            query = query.where(BillingTransaction.transaction_type == transaction_type)

        query = query.order_by(
            BillingTransaction.transaction_date.desc(),
            BillingTransaction.created_at.desc(),
        ).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_patient_balance(self, patient_id: UUID) -> PatientBillingBalance:
        """Get comprehensive billing balance for a patient."""
        balance = await self._get_patient_balance(patient_id)

        # Get total charges
        charges_query = select(func.sum(BillingTransaction.amount)).where(
            and_(
                BillingTransaction.patient_id == patient_id,
                BillingTransaction.practice_id == self.practice_id,
                BillingTransaction.transaction_type == TransactionType.CHARGE,
            )
        )
        charges_result = await self.db.execute(charges_query)
        total_charges = charges_result.scalar_one() or Decimal("0.00")

        # Get total payments
        payments_query = select(func.sum(BillingTransaction.amount)).where(
            and_(
                BillingTransaction.patient_id == patient_id,
                BillingTransaction.practice_id == self.practice_id,
                BillingTransaction.transaction_type == TransactionType.PAYMENT,
            )
        )
        payments_result = await self.db.execute(payments_query)
        total_payments = abs(payments_result.scalar_one() or Decimal("0.00"))

        # Get total adjustments
        adjustments_query = select(func.sum(BillingTransaction.amount)).where(
            and_(
                BillingTransaction.patient_id == patient_id,
                BillingTransaction.practice_id == self.practice_id,
                BillingTransaction.transaction_type == TransactionType.ADJUSTMENT,
            )
        )
        adjustments_result = await self.db.execute(adjustments_query)
        total_adjustments = abs(adjustments_result.scalar_one() or Decimal("0.00"))

        # Calculate insurance pending and patient responsibility
        # (simplified - would need more complex logic in production)
        insurance_pending = Decimal("0.00")
        patient_responsibility = balance

        # Get unapplied credits
        unapplied_query = select(func.sum(BillingPayment.unapplied_amount)).where(
            and_(
                BillingPayment.patient_id == patient_id,
                BillingPayment.practice_id == self.practice_id,
                BillingPayment.status == PaymentStatus.COMPLETED,
            )
        )
        unapplied_result = await self.db.execute(unapplied_query)
        unapplied_credits = unapplied_result.scalar_one() or Decimal("0.00")

        return PatientBillingBalance(
            patient_id=patient_id,
            total_charges=total_charges,
            total_payments=total_payments,
            total_adjustments=total_adjustments,
            current_balance=balance,
            insurance_pending=insurance_pending,
            patient_responsibility=patient_responsibility,
            unapplied_credits=unapplied_credits,
        )

    async def _get_patient_balance(self, patient_id: UUID) -> Decimal:
        """Get current balance for a patient."""
        # Get the most recent transaction
        query = (
            select(BillingTransaction.balance_after)
            .where(
                and_(
                    BillingTransaction.patient_id == patient_id,
                    BillingTransaction.practice_id == self.practice_id,
                )
            )
            .order_by(BillingTransaction.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        balance = result.scalar_one_or_none()
        return balance or Decimal("0.00")
