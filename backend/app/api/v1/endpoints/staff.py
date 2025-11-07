"""Staff management API endpoints."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.staff import (
    Staff,
    StaffCreate,
    StaffUpdate,
    StaffWithUser,
    StaffListFilters,
)
from app.models.user import User
from app.models.staff import StaffRole
from app.services.staff_service import StaffService

router = APIRouter()


@router.get('/', response_model=PaginatedResponse[Staff])
async def list_staff(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[StaffRole] = None,
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_full_time: Optional[bool] = None,
    search: Optional[str] = None,
    include_user: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """List staff members with filtering and search."""
    service = StaffService(db)
    staff, total = await service.list_staff(
        practice_id=current_user.practice_id,
        skip=skip,
        limit=limit,
        role=role,
        department=department,
        is_active=is_active,
        is_full_time=is_full_time,
        search=search,
        include_user=include_user,
    )

    return PaginatedResponse(
        items=staff,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post('/', response_model=Staff, status_code=status.HTTP_201_CREATED)
async def create_staff(
    staff_in: StaffCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create new staff member.

    Requires:
    - user_id must be a valid user in the practice
    - employee_id must be unique if provided
    """
    service = StaffService(db)
    try:
        staff = await service.create_staff(
            practice_id=current_user.practice_id,
            staff_data=staff_in,
            created_by=current_user.id,
        )
        await db.commit()
        return staff
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{staff_id}', response_model=StaffWithUser)
async def get_staff(
    staff_id: UUID,
    include_user: bool = Query(True),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get staff member by ID with optional relationships."""
    service = StaffService(db)
    staff = await service.get_staff_by_id(
        staff_id=staff_id,
        practice_id=current_user.practice_id,
        include_user=include_user,
    )

    if not staff:
        raise HTTPException(status_code=404, detail='Staff member not found')

    return staff


@router.patch('/{staff_id}', response_model=Staff)
async def update_staff(
    staff_id: UUID,
    staff_in: StaffUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update staff member information."""
    service = StaffService(db)
    try:
        staff = await service.update_staff(
            staff_id=staff_id,
            practice_id=current_user.practice_id,
            staff_data=staff_in,
            updated_by=current_user.id,
        )

        if not staff:
            raise HTTPException(status_code=404, detail='Staff member not found')

        await db.commit()
        return staff
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/{staff_id}', response_model=SuccessResponse)
async def delete_staff(
    staff_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete staff profile (keeps user account)."""
    service = StaffService(db)
    deleted = await service.delete_staff(
        staff_id=staff_id,
        practice_id=current_user.practice_id,
        deleted_by=current_user.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail='Staff member not found')

    await db.commit()
    return SuccessResponse(message='Staff member deleted successfully')


@router.post('/{staff_id}/terminate', response_model=Staff)
async def terminate_staff(
    staff_id: UUID,
    termination_date: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$'),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark staff as terminated with date."""
    service = StaffService(db)
    staff = await service.terminate_staff(
        staff_id=staff_id,
        practice_id=current_user.practice_id,
        termination_date=termination_date,
        terminated_by=current_user.id,
    )

    if not staff:
        raise HTTPException(status_code=404, detail='Staff member not found')

    await db.commit()
    return staff


@router.get('/by-user/{user_id}', response_model=Staff)
async def get_staff_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get staff by user ID."""
    service = StaffService(db)
    staff = await service.get_staff_by_user_id(
        user_id=user_id,
        practice_id=current_user.practice_id,
    )

    if not staff:
        raise HTTPException(status_code=404, detail='Staff not found for this user')

    return staff


@router.get('/by-employee/{employee_id}', response_model=Staff)
async def get_staff_by_employee_id(
    employee_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get staff by employee ID."""
    service = StaffService(db)
    staff = await service.get_staff_by_employee_id(
        employee_id=employee_id,
        practice_id=current_user.practice_id,
    )

    if not staff:
        raise HTTPException(status_code=404, detail='Staff not found with this employee ID')

    return staff


@router.get('/by-role/{role}', response_model=list[Staff])
async def get_staff_by_role(
    role: StaffRole,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get staff members by role."""
    service = StaffService(db)
    staff = await service.get_staff_by_role(
        practice_id=current_user.practice_id,
        role=role,
        active_only=active_only,
    )

    return staff


@router.get('/by-department/{department}', response_model=list[Staff])
async def get_staff_by_department(
    department: str,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get staff members by department."""
    service = StaffService(db)
    staff = await service.get_staff_by_department(
        practice_id=current_user.practice_id,
        department=department,
        active_only=active_only,
    )

    return staff


@router.get('/active/list', response_model=list[Staff])
async def get_active_staff(
    full_time_only: bool = Query(False),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all active staff members."""
    service = StaffService(db)
    staff = await service.get_active_staff(
        practice_id=current_user.practice_id,
        full_time_only=full_time_only,
    )

    return staff
