"""API endpoints for patient medical records."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import SuccessResponse
from app.api.v1.schemas.medical_records import (
    MedicalAllergy,
    MedicalAllergyCreate,
    MedicalAllergyUpdate,
    MedicalCondition,
    MedicalConditionCreate,
    MedicalConditionUpdate,
    MedicalImmunization,
    MedicalImmunizationCreate,
    MedicalImmunizationUpdate,
    MedicalMedication,
    MedicalMedicationCreate,
    MedicalMedicationUpdate,
    MedicalVitals,
    MedicalVitalsCreate,
    MedicalVitalsUpdate,
)
from app.models.user import User
from app.services.medical_record_service import MedicalRecordService
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
# Medical Allergies
# ============================================================================


@router.get('/patients/{patient_id}/allergies', response_model=list[MedicalAllergy])
async def list_patient_allergies(
    patient_id: UUID,
    active_only: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all allergies for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    allergies = await service.get_patient_allergies(patient_id, active_only=active_only)
    return allergies


@router.post('/patients/{patient_id}/allergies', response_model=MedicalAllergy, status_code=status.HTTP_201_CREATED)
async def create_allergy(
    patient_id: UUID,
    allergy_in: MedicalAllergyCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new allergy record for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    if allergy_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail='Patient ID mismatch')

    service = MedicalRecordService(db)
    allergy = await service.create_allergy(allergy_in)
    await db.commit()
    return allergy


@router.get('/allergies/{allergy_id}', response_model=MedicalAllergy)
async def get_allergy(
    allergy_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific allergy by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    allergy = await service.get_allergy_by_id(allergy_id, patient_id)
    if not allergy:
        raise HTTPException(status_code=404, detail='Allergy not found')
    return allergy


@router.patch('/allergies/{allergy_id}', response_model=MedicalAllergy)
async def update_allergy(
    allergy_id: UUID,
    allergy_in: MedicalAllergyUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update an allergy record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    allergy = await service.update_allergy(allergy_id, patient_id, allergy_in)
    if not allergy:
        raise HTTPException(status_code=404, detail='Allergy not found')

    await db.commit()
    return allergy


@router.delete('/allergies/{allergy_id}', response_model=SuccessResponse)
async def delete_allergy(
    allergy_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete an allergy record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    deleted = await service.delete_allergy(allergy_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Allergy not found')

    await db.commit()
    return SuccessResponse(message='Allergy deleted successfully')


# ============================================================================
# Medical Medications
# ============================================================================


@router.get('/patients/{patient_id}/medications', response_model=list[MedicalMedication])
async def list_patient_medications(
    patient_id: UUID,
    active_only: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all medications for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    medications = await service.get_patient_medications(patient_id, active_only=active_only)
    return medications


@router.post('/patients/{patient_id}/medications', response_model=MedicalMedication, status_code=status.HTTP_201_CREATED)
async def create_medication(
    patient_id: UUID,
    medication_in: MedicalMedicationCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new medication record for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    if medication_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail='Patient ID mismatch')

    service = MedicalRecordService(db)
    medication = await service.create_medication(medication_in)
    await db.commit()
    return medication


@router.get('/medications/{medication_id}', response_model=MedicalMedication)
async def get_medication(
    medication_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific medication by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    medication = await service.get_medication_by_id(medication_id, patient_id)
    if not medication:
        raise HTTPException(status_code=404, detail='Medication not found')
    return medication


@router.patch('/medications/{medication_id}', response_model=MedicalMedication)
async def update_medication(
    medication_id: UUID,
    medication_in: MedicalMedicationUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a medication record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    medication = await service.update_medication(medication_id, patient_id, medication_in)
    if not medication:
        raise HTTPException(status_code=404, detail='Medication not found')

    await db.commit()
    return medication


@router.delete('/medications/{medication_id}', response_model=SuccessResponse)
async def delete_medication(
    medication_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a medication record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    deleted = await service.delete_medication(medication_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Medication not found')

    await db.commit()
    return SuccessResponse(message='Medication deleted successfully')


# ============================================================================
# Medical Conditions
# ============================================================================


@router.get('/patients/{patient_id}/conditions', response_model=list[MedicalCondition])
async def list_patient_conditions(
    patient_id: UUID,
    active_only: bool = Query(False),
    chronic_only: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all conditions for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    conditions = await service.get_patient_conditions(
        patient_id,
        active_only=active_only,
        chronic_only=chronic_only,
    )
    return conditions


@router.post('/patients/{patient_id}/conditions', response_model=MedicalCondition, status_code=status.HTTP_201_CREATED)
async def create_condition(
    patient_id: UUID,
    condition_in: MedicalConditionCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new condition record for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    if condition_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail='Patient ID mismatch')

    service = MedicalRecordService(db)
    condition = await service.create_condition(condition_in)
    await db.commit()
    return condition


@router.get('/conditions/{condition_id}', response_model=MedicalCondition)
async def get_condition(
    condition_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific condition by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    condition = await service.get_condition_by_id(condition_id, patient_id)
    if not condition:
        raise HTTPException(status_code=404, detail='Condition not found')
    return condition


@router.patch('/conditions/{condition_id}', response_model=MedicalCondition)
async def update_condition(
    condition_id: UUID,
    condition_in: MedicalConditionUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a condition record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    condition = await service.update_condition(condition_id, patient_id, condition_in)
    if not condition:
        raise HTTPException(status_code=404, detail='Condition not found')

    await db.commit()
    return condition


@router.delete('/conditions/{condition_id}', response_model=SuccessResponse)
async def delete_condition(
    condition_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a condition record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    deleted = await service.delete_condition(condition_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Condition not found')

    await db.commit()
    return SuccessResponse(message='Condition deleted successfully')


# ============================================================================
# Medical Immunizations
# ============================================================================


@router.get('/patients/{patient_id}/immunizations', response_model=list[MedicalImmunization])
async def list_patient_immunizations(
    patient_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all immunizations for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    immunizations = await service.get_patient_immunizations(patient_id)
    return immunizations


@router.post('/patients/{patient_id}/immunizations', response_model=MedicalImmunization, status_code=status.HTTP_201_CREATED)
async def create_immunization(
    patient_id: UUID,
    immunization_in: MedicalImmunizationCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new immunization record for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    if immunization_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail='Patient ID mismatch')

    service = MedicalRecordService(db)
    immunization = await service.create_immunization(immunization_in)
    await db.commit()
    return immunization


@router.get('/immunizations/{immunization_id}', response_model=MedicalImmunization)
async def get_immunization(
    immunization_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific immunization by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    immunization = await service.get_immunization_by_id(immunization_id, patient_id)
    if not immunization:
        raise HTTPException(status_code=404, detail='Immunization not found')
    return immunization


@router.patch('/immunizations/{immunization_id}', response_model=MedicalImmunization)
async def update_immunization(
    immunization_id: UUID,
    immunization_in: MedicalImmunizationUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update an immunization record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    immunization = await service.update_immunization(immunization_id, patient_id, immunization_in)
    if not immunization:
        raise HTTPException(status_code=404, detail='Immunization not found')

    await db.commit()
    return immunization


@router.delete('/immunizations/{immunization_id}', response_model=SuccessResponse)
async def delete_immunization(
    immunization_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete an immunization record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    deleted = await service.delete_immunization(immunization_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Immunization not found')

    await db.commit()
    return SuccessResponse(message='Immunization deleted successfully')


# ============================================================================
# Medical Vitals
# ============================================================================


@router.get('/patients/{patient_id}/vitals', response_model=list[MedicalVitals])
async def list_patient_vitals(
    patient_id: UUID,
    start_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
    end_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get vitals for a patient with optional date filtering."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    vitals = await service.get_patient_vitals(
        patient_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return vitals


@router.post('/patients/{patient_id}/vitals', response_model=MedicalVitals, status_code=status.HTTP_201_CREATED)
async def create_vitals(
    patient_id: UUID,
    vitals_in: MedicalVitalsCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new vitals record for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    if vitals_in.patient_id != patient_id:
        raise HTTPException(status_code=400, detail='Patient ID mismatch')

    service = MedicalRecordService(db)
    vitals = await service.create_vitals(vitals_in)
    await db.commit()
    return vitals


@router.get('/vitals/{vitals_id}', response_model=MedicalVitals)
async def get_vitals(
    vitals_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get specific vitals by ID."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    vitals = await service.get_vitals_by_id(vitals_id, patient_id)
    if not vitals:
        raise HTTPException(status_code=404, detail='Vitals not found')
    return vitals


@router.patch('/vitals/{vitals_id}', response_model=MedicalVitals)
async def update_vitals(
    vitals_id: UUID,
    vitals_in: MedicalVitalsUpdate,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update a vitals record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    vitals = await service.update_vitals(vitals_id, patient_id, vitals_in)
    if not vitals:
        raise HTTPException(status_code=404, detail='Vitals not found')

    await db.commit()
    return vitals


@router.delete('/vitals/{vitals_id}', response_model=SuccessResponse)
async def delete_vitals(
    vitals_id: UUID,
    patient_id: UUID = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a vitals record."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    deleted = await service.delete_vitals(vitals_id, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Vitals not found')

    await db.commit()
    return SuccessResponse(message='Vitals deleted successfully')


# ============================================================================
# Comprehensive Medical Summary
# ============================================================================


@router.get('/patients/{patient_id}/medical-summary')
async def get_patient_medical_summary(
    patient_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get comprehensive medical summary for a patient."""
    await verify_patient_access(patient_id, current_user, db)

    service = MedicalRecordService(db)
    summary = await service.get_patient_medical_summary(patient_id)
    return summary
