"""API endpoints for patient insurance management."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import SuccessResponse
from app.api.v1.schemas.insurance import (
    InsurancePolicy,
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
    InsurancePolicyWithVerifications,
    InsuranceVerification,
    InsuranceVerificationCreate,
    InsuranceVerificationUpdate,
)
from app.models.user import User
from app.services.insurance_service import InsuranceService
from app.services.patient_service import PatientService

router = APIRouter()


# Helper function to verify patient access
async def verify_patient_access(
    patient_id: UUID,
    current_user: User,
    db: AsyncSession,
) -> None:
    """Verify current user has access to patient."""
    patient_service = PatientService(db, current_user.practice_id)
    patient = await patient_service.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')


# ============================================================================
# Insurance Policies
# ============================================================================


@router.get('/patients/{patient_id}/policies', response_model=list[InsurancePolicy])
async def list_patient_policies(
    patient_id: UUID,
    active_only: bool = Query(False),
    include_verifications: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all insurance policies for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    policies = await service.get_patient_policies(
        patient_id,
        active_only=active_only,
        include_verifications=include_verifications,
    )
    return policies


@router.get('/patients/{patient_id}/policies/primary', response_model=InsurancePolicy)
async def get_primary_policy(
    patient_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get the primary insurance policy for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    policy = await service.get_primary_policy(patient_id)
    if not policy:
        raise HTTPException(status_code=404, detail='No primary insurance policy found')
    return policy


@router.post('/patients/{patient_id}/policies', response_model=InsurancePolicy, status_code=status.HTTP_201_CREATED)
async def create_policy(
    patient_id: UUID,
    policy_in: InsurancePolicyCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new insurance policy for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    if policy_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail='Patient ID mismatch')

    service = InsuranceService(db, current_user.practice_id)
    policy = await service.create_policy(policy_in)
    await db.commit()
    return policy


@router.get('/policies/{policy_id}', response_model=InsurancePolicyWithVerifications)
async def get_policy(
    policy_id: UUID,
    patient_id: UUID = Query(...),
    include_verifications: bool = Query(True),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific insurance policy by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    policy = await service.get_policy_by_id(policy_id, patient_id, include_verifications=include_verifications)
    if not policy:
        raise HTTPException(status_code=404, detail='Insurance policy not found')
    return policy


@router.patch('/policies/{policy_id}', response_model=InsurancePolicy)
async def update_policy(
    policy_id: UUID,
    policy_in: InsurancePolicyUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update an insurance policy."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    policy = await service.update_policy(policy_id, patient_id, policy_in)
    if not policy:
        raise HTTPException(status_code=404, detail='Insurance policy not found')

    await db.commit()
    return policy


@router.delete('/policies/{policy_id}', response_model=SuccessResponse)
async def delete_policy(
    policy_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete an insurance policy."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    deleted = await service.delete_policy(policy_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Insurance policy not found')

    await db.commit()
    return SuccessResponse(message='Insurance policy deleted successfully')


@router.post('/policies/{policy_id}/terminate', response_model=InsurancePolicy)
async def terminate_policy(
    policy_id: UUID,
    patient_id: UUID = Query(...),
    termination_date: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$'),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark an insurance policy as terminated."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    policy = await service.terminate_policy(policy_id, patient_id, termination_date)
    if not policy:
        raise HTTPException(status_code=404, detail='Insurance policy not found')

    await db.commit()
    return policy


# ============================================================================
# Insurance Verifications
# ============================================================================


@router.get('/policies/{policy_id}/verifications', response_model=list[InsuranceVerification])
async def list_policy_verifications(
    policy_id: UUID,
    patient_id: UUID = Query(...),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get verification history for an insurance policy."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    verifications = await service.get_policy_verifications(policy_id, patient_id, limit=limit)
    return verifications


@router.get('/policies/{policy_id}/verifications/latest', response_model=InsuranceVerification)
async def get_latest_verification(
    policy_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get the most recent verification for a policy."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    verification = await service.get_latest_verification(policy_id, patient_id)
    if not verification:
        raise HTTPException(status_code=404, detail='No verification found for this policy')
    return verification


@router.post('/policies/{policy_id}/verifications', response_model=InsuranceVerification, status_code=status.HTTP_201_CREATED)
async def create_verification(
    policy_id: UUID,
    verification_in: InsuranceVerificationCreate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new insurance verification record."""
    await verify_patient_access(patient_id, current_user, db)

    if verification_in.policy_id != policy_id:
        raise HTTPException(status_code=400, detail='Policy ID mismatch')

    service = InsuranceService(db, current_user.practice_id)
    try:
        verification = await service.create_verification(verification_in, patient_id)
        await db.commit()
        return verification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/verifications/{verification_id}', response_model=InsuranceVerification)
async def get_verification(
    verification_id: UUID,
    policy_id: UUID = Query(...),
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific verification by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    verification = await service.get_verification_by_id(verification_id, policy_id)
    if not verification:
        raise HTTPException(status_code=404, detail='Verification not found')
    return verification


@router.patch('/verifications/{verification_id}', response_model=InsuranceVerification)
async def update_verification(
    verification_id: UUID,
    verification_in: InsuranceVerificationUpdate,
    policy_id: UUID = Query(...),
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a verification record."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    verification = await service.update_verification(
        verification_id,
        policy_id,
        patient_id,
        verification_in,
    )
    if not verification:
        raise HTTPException(status_code=404, detail='Verification not found')

    await db.commit()
    return verification


@router.delete('/verifications/{verification_id}', response_model=SuccessResponse)
async def delete_verification(
    verification_id: UUID,
    policy_id: UUID = Query(...),
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a verification record."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    deleted = await service.delete_verification(verification_id, policy_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Verification not found')

    await db.commit()
    return SuccessResponse(message='Verification deleted successfully')


# ============================================================================
# Verification Status Utilities
# ============================================================================


@router.get('/patients/{patient_id}/policies/needs-verification', response_model=list[InsurancePolicy])
async def get_policies_needing_verification(
    patient_id: UUID,
    days_threshold: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all policies for a patient that need verification."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    policies = await service.get_policies_needing_verification(patient_id, days_threshold)
    return policies


@router.get('/policies/{policy_id}/needs-verification')
async def check_policy_needs_verification(
    policy_id: UUID,
    patient_id: UUID = Query(...),
    days_threshold: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Check if a policy needs verification."""
    await verify_patient_access(patient_id, current_user, db)

    service = InsuranceService(db, current_user.practice_id)
    needs_verification = await service.needs_verification(policy_id, patient_id, days_threshold)

    return {
        'policy_id': policy_id,
        'needs_verification': needs_verification,
        'days_threshold': days_threshold,
    }
