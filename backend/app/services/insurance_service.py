"""Service for managing patient insurance policies and verifications."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.schemas.insurance import (
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
    InsuranceVerificationCreate,
    InsuranceVerificationUpdate,
)
from app.models.insurance_policy import InsurancePolicy, PolicyStatus
from app.models.insurance_verification import InsuranceVerification, VerificationStatus


class InsuranceService:
    """Service for managing patient insurance."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ========================================================================
    # Insurance Policies
    # ========================================================================

    async def get_patient_policies(
        self,
        patient_id: UUID,
        active_only: bool = False,
        include_verifications: bool = False,
    ) -> list[InsurancePolicy]:
        """Get all insurance policies for a patient."""
        query = select(InsurancePolicy).where(
            and_(
                InsurancePolicy.patient_id == patient_id,
                InsurancePolicy.practice_id == self.practice_id,
            )
        )

        if active_only:
            query = query.where(InsurancePolicy.status == PolicyStatus.ACTIVE)

        if include_verifications:
            query = query.options(selectinload(InsurancePolicy.verifications))

        query = query.order_by(InsurancePolicy.priority_order, InsurancePolicy.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_policy_by_id(
        self,
        policy_id: UUID,
        patient_id: UUID,
        include_verifications: bool = False,
    ) -> InsurancePolicy | None:
        """Get a specific insurance policy by ID."""
        query = select(InsurancePolicy).where(
            and_(
                InsurancePolicy.id == policy_id,
                InsurancePolicy.patient_id == patient_id,
                InsurancePolicy.practice_id == self.practice_id,
            )
        )

        if include_verifications:
            query = query.options(selectinload(InsurancePolicy.verifications))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_primary_policy(
        self,
        patient_id: UUID,
    ) -> InsurancePolicy | None:
        """Get the primary insurance policy for a patient."""
        query = (
            select(InsurancePolicy)
            .where(
                and_(
                    InsurancePolicy.patient_id == patient_id,
                    InsurancePolicy.practice_id == self.practice_id,
                    InsurancePolicy.is_primary == True,
                    InsurancePolicy.status == PolicyStatus.ACTIVE,
                )
            )
            .order_by(InsurancePolicy.priority_order)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_policy(
        self,
        policy_data: InsurancePolicyCreate,
    ) -> InsurancePolicy:
        """Create a new insurance policy."""
        # If this is marked as primary, unmark other policies
        if policy_data.is_primary:
            await self._unmark_other_primary_policies(policy_data.patient_id)

        policy = InsurancePolicy(
            **policy_data.model_dump(),
            practice_id=self.practice_id,
        )
        self.db.add(policy)
        await self.db.flush()
        await self.db.refresh(policy)
        return policy

    async def update_policy(
        self,
        policy_id: UUID,
        patient_id: UUID,
        policy_data: InsurancePolicyUpdate,
    ) -> InsurancePolicy | None:
        """Update an insurance policy."""
        policy = await self.get_policy_by_id(policy_id, patient_id)
        if not policy:
            return None

        # If changing to primary, unmark other policies
        update_dict = policy_data.model_dump(exclude_unset=True)
        if update_dict.get('is_primary') is True:
            await self._unmark_other_primary_policies(patient_id, exclude_policy_id=policy_id)

        for field, value in update_dict.items():
            setattr(policy, field, value)

        await self.db.flush()
        await self.db.refresh(policy)
        return policy

    async def delete_policy(
        self,
        policy_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete an insurance policy and its verifications."""
        policy = await self.get_policy_by_id(policy_id, patient_id)
        if not policy:
            return False

        await self.db.delete(policy)
        await self.db.flush()
        return True

    async def terminate_policy(
        self,
        policy_id: UUID,
        patient_id: UUID,
        termination_date: str,
    ) -> InsurancePolicy | None:
        """Mark a policy as terminated."""
        policy = await self.get_policy_by_id(policy_id, patient_id)
        if not policy:
            return None

        policy.status = PolicyStatus.TERMINATED
        policy.termination_date = termination_date

        await self.db.flush()
        await self.db.refresh(policy)
        return policy

    async def _unmark_other_primary_policies(
        self,
        patient_id: UUID,
        exclude_policy_id: Optional[UUID] = None,
    ) -> None:
        """Helper to unmark other policies as primary."""
        query = select(InsurancePolicy).where(
            and_(
                InsurancePolicy.patient_id == patient_id,
                InsurancePolicy.practice_id == self.practice_id,
                InsurancePolicy.is_primary == True,
            )
        )

        if exclude_policy_id:
            query = query.where(InsurancePolicy.id != exclude_policy_id)

        result = await self.db.execute(query)
        policies = result.scalars().all()

        for policy in policies:
            policy.is_primary = False

        await self.db.flush()

    # ========================================================================
    # Insurance Verifications
    # ========================================================================

    async def get_policy_verifications(
        self,
        policy_id: UUID,
        patient_id: UUID,
        limit: int = 50,
    ) -> list[InsuranceVerification]:
        """Get verification history for a policy."""
        # First verify the policy belongs to the patient and practice
        policy = await self.get_policy_by_id(policy_id, patient_id)
        if not policy:
            return []

        query = (
            select(InsuranceVerification)
            .where(InsuranceVerification.policy_id == policy_id)
            .order_by(InsuranceVerification.verification_date.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_verification_by_id(
        self,
        verification_id: UUID,
        policy_id: UUID,
    ) -> InsuranceVerification | None:
        """Get a specific verification by ID."""
        query = select(InsuranceVerification).where(
            and_(
                InsuranceVerification.id == verification_id,
                InsuranceVerification.policy_id == policy_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_verification(
        self,
        policy_id: UUID,
        patient_id: UUID,
    ) -> InsuranceVerification | None:
        """Get the most recent verification for a policy."""
        # Verify policy belongs to patient
        policy = await self.get_policy_by_id(policy_id, patient_id)
        if not policy:
            return None

        query = (
            select(InsuranceVerification)
            .where(InsuranceVerification.policy_id == policy_id)
            .order_by(InsuranceVerification.verification_date.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_verification(
        self,
        verification_data: InsuranceVerificationCreate,
        patient_id: UUID,
    ) -> InsuranceVerification | None:
        """Create a new insurance verification."""
        # Verify the policy exists and belongs to the patient
        policy = await self.get_policy_by_id(verification_data.policy_id, patient_id)
        if not policy:
            raise ValueError('Policy not found or does not belong to patient')

        verification = InsuranceVerification(**verification_data.model_dump())
        self.db.add(verification)
        await self.db.flush()
        await self.db.refresh(verification)

        # Update policy with verified information if status is verified
        if verification.status == VerificationStatus.VERIFIED:
            await self._update_policy_from_verification(policy, verification)

        return verification

    async def update_verification(
        self,
        verification_id: UUID,
        policy_id: UUID,
        patient_id: UUID,
        verification_data: InsuranceVerificationUpdate,
    ) -> InsuranceVerification | None:
        """Update a verification record."""
        # Verify policy belongs to patient
        policy = await self.get_policy_by_id(policy_id, patient_id)
        if not policy:
            return None

        verification = await self.get_verification_by_id(verification_id, policy_id)
        if not verification:
            return None

        for field, value in verification_data.model_dump(exclude_unset=True).items():
            setattr(verification, field, value)

        await self.db.flush()
        await self.db.refresh(verification)

        # Update policy if verification status changed to verified
        if verification.status == VerificationStatus.VERIFIED:
            await self._update_policy_from_verification(policy, verification)

        return verification

    async def delete_verification(
        self,
        verification_id: UUID,
        policy_id: UUID,
        patient_id: UUID,
    ) -> bool:
        """Delete a verification record."""
        # Verify policy belongs to patient
        policy = await self.get_policy_by_id(policy_id, patient_id)
        if not policy:
            return False

        verification = await self.get_verification_by_id(verification_id, policy_id)
        if not verification:
            return False

        await self.db.delete(verification)
        await self.db.flush()
        return True

    async def _update_policy_from_verification(
        self,
        policy: InsurancePolicy,
        verification: InsuranceVerification,
    ) -> None:
        """Update policy fields from verified information."""
        if verification.copay_verified is not None:
            policy.copay = verification.copay_verified
        if verification.deductible_verified is not None:
            policy.deductible = verification.deductible_verified
        if verification.deductible_met_verified is not None:
            policy.deductible_met = verification.deductible_met_verified
        if verification.out_of_pocket_max_verified is not None:
            policy.out_of_pocket_max = verification.out_of_pocket_max_verified
        if verification.out_of_pocket_met_verified is not None:
            policy.out_of_pocket_met = verification.out_of_pocket_met_verified
        if verification.effective_date_verified:
            policy.effective_date = verification.effective_date_verified
        if verification.termination_date_verified:
            policy.termination_date = verification.termination_date_verified

        await self.db.flush()

    # ========================================================================
    # Verification Status Checks
    # ========================================================================

    async def needs_verification(
        self,
        policy_id: UUID,
        patient_id: UUID,
        days_threshold: int = 30,
    ) -> bool:
        """Check if a policy needs verification (no verification in last N days)."""
        from datetime import date, timedelta

        latest_verification = await self.get_latest_verification(policy_id, patient_id)

        if not latest_verification:
            return True

        # Check if latest verification is older than threshold
        verification_date = date.fromisoformat(latest_verification.verification_date)
        threshold_date = date.today() - timedelta(days=days_threshold)

        return verification_date < threshold_date

    async def get_policies_needing_verification(
        self,
        patient_id: UUID,
        days_threshold: int = 30,
    ) -> list[InsurancePolicy]:
        """Get all policies for a patient that need verification."""
        policies = await self.get_patient_policies(patient_id, active_only=True)
        needs_verification = []

        for policy in policies:
            if await self.needs_verification(policy.id, patient_id, days_threshold):
                needs_verification.append(policy)

        return needs_verification
