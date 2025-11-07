"""Provider management API endpoints."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.provider import (
    Provider,
    ProviderCreate,
    ProviderUpdate,
    ProviderWithUser,
    ProviderWithSchedules,
    ProviderListFilters,
)
from app.models.user import User
from app.services.provider_service import ProviderService

router = APIRouter()


@router.get('/', response_model=PaginatedResponse[Provider])
async def list_providers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    specialty: Optional[str] = None,
    department: Optional[str] = None,
    accepting_new_patients: Optional[bool] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    include_user: bool = Query(False),
    include_schedules: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """List providers with filtering and search."""
    service = ProviderService(db)
    providers, total = await service.list_providers(
        practice_id=current_user.practice_id,
        skip=skip,
        limit=limit,
        specialty=specialty,
        department=department,
        accepting_new_patients=accepting_new_patients,
        is_active=is_active,
        search=search,
        include_user=include_user,
        include_schedules=include_schedules,
    )

    return PaginatedResponse(
        items=providers,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post('/', response_model=Provider, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_in: ProviderCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create new provider.

    Requires:
    - user_id must be a valid user in the practice
    - NPI must be unique if provided
    """
    service = ProviderService(db)
    try:
        provider = await service.create_provider(
            practice_id=current_user.practice_id,
            provider_data=provider_in,
            created_by=current_user.id,
        )
        await db.commit()
        return provider
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{provider_id}', response_model=ProviderWithUser)
async def get_provider(
    provider_id: UUID,
    include_user: bool = Query(True),
    include_schedules: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get provider by ID with optional relationships."""
    service = ProviderService(db)
    provider = await service.get_provider_by_id(
        provider_id=provider_id,
        practice_id=current_user.practice_id,
        include_user=include_user,
        include_schedules=include_schedules,
    )

    if not provider:
        raise HTTPException(status_code=404, detail='Provider not found')

    return provider


@router.patch('/{provider_id}', response_model=Provider)
async def update_provider(
    provider_id: UUID,
    provider_in: ProviderUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update provider information."""
    service = ProviderService(db)
    try:
        provider = await service.update_provider(
            provider_id=provider_id,
            practice_id=current_user.practice_id,
            provider_data=provider_in,
            updated_by=current_user.id,
        )

        if not provider:
            raise HTTPException(status_code=404, detail='Provider not found')

        await db.commit()
        return provider
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/{provider_id}', response_model=SuccessResponse)
async def delete_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete provider profile (keeps user account)."""
    service = ProviderService(db)
    deleted = await service.delete_provider(
        provider_id=provider_id,
        practice_id=current_user.practice_id,
        deleted_by=current_user.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail='Provider not found')

    await db.commit()
    return SuccessResponse(message='Provider deleted successfully')


@router.get('/by-user/{user_id}', response_model=Provider)
async def get_provider_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get provider by user ID."""
    service = ProviderService(db)
    provider = await service.get_provider_by_user_id(
        user_id=user_id,
        practice_id=current_user.practice_id,
    )

    if not provider:
        raise HTTPException(status_code=404, detail='Provider not found for this user')

    return provider


@router.get('/by-npi/{npi}', response_model=Provider)
async def get_provider_by_npi(
    npi: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get provider by NPI."""
    service = ProviderService(db)
    provider = await service.get_provider_by_npi(
        npi=npi,
        practice_id=current_user.practice_id,
    )

    if not provider:
        raise HTTPException(status_code=404, detail='Provider not found with this NPI')

    return provider


@router.get('/specialty/{specialty}', response_model=list[Provider])
async def get_providers_by_specialty(
    specialty: str,
    accepting_only: bool = Query(True),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get providers by specialty."""
    service = ProviderService(db)
    providers = await service.get_providers_by_specialty(
        practice_id=current_user.practice_id,
        specialty=specialty,
        accepting_only=accepting_only,
    )

    return providers


@router.get('/available/list', response_model=list[Provider])
async def get_available_providers(
    department: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all active providers accepting new patients."""
    service = ProviderService(db)
    providers = await service.get_available_providers(
        practice_id=current_user.practice_id,
        department=department,
    )

    return providers
