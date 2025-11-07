\"\"\"Patient endpoints.\"\"\"

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.common import PaginatedResponse
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter()


@router.get('/', response_model=PaginatedResponse[PatientResponse])
async def list_patients(
    pagination: deps.PaginationParams = Depends(),
    search: str | None = Query(default=None, description='Case-insensitive search across MRN and name'),
    current_user=Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> PaginatedResponse[PatientResponse]:
    service = PatientService(session, current_user.practice_id)
    patients, total = await service.list(search=search, page=pagination.page, size=pagination.size)
    return PaginatedResponse[PatientResponse](
        data=[PatientResponse.model_validate(p) for p in patients],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.post('/', response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    current_user=Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> PatientResponse:
    service = PatientService(session, current_user.practice_id)
    try:
        patient = await service.create(payload, actor_id=current_user.id)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='MRN already exists')
    return PatientResponse.model_validate(patient)


@router.get('/{patient_id}', response_model=PatientResponse)
async def get_patient(
    patient_id: uuid.UUID,
    current_user=Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> PatientResponse:
    service = PatientService(session, current_user.practice_id)
    patient = await service.get(patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Patient not found')
    return PatientResponse.model_validate(patient)


@router.put('/{patient_id}', response_model=PatientResponse)
async def update_patient(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    current_user=Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> PatientResponse:
    service = PatientService(session, current_user.practice_id)
    try:
        patient = await service.update(patient_id, payload, actor_id=current_user.id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Patient not found')
    return PatientResponse.model_validate(patient)