\"\"\"Appointment endpoints.\"\"\"

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.schemas.common import PaginatedResponse
from app.services.appointment_service import AppointmentService

router = APIRouter()


@router.get('/', response_model=PaginatedResponse[AppointmentResponse])
async def list_appointments(
    pagination: deps.PaginationParams = Depends(),
    current_user=Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> PaginatedResponse[AppointmentResponse]:
    service = AppointmentService(session, current_user.practice_id)
    appointments, total = await service.list(page=pagination.page, size=pagination.size)
    return PaginatedResponse[AppointmentResponse](
        data=[AppointmentResponse.model_validate(a) for a in appointments],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.post('/', response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreate,
    current_user=Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> AppointmentResponse:
    service = AppointmentService(session, current_user.practice_id)
    appointment = await service.create(payload, actor_id=current_user.id)
    return AppointmentResponse.model_validate(appointment)


@router.put('/{appointment_id}', response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentUpdate,
    current_user=Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> AppointmentResponse:
    service = AppointmentService(session, current_user.practice_id)
    try:
        appointment = await service.update(appointment_id, payload, actor_id=current_user.id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Appointment not found')
    return AppointmentResponse.model_validate(appointment)