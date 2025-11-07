"""Staff service for business logic."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.staff import Staff, StaffRole
from app.models.user import User
from app.api.v1.schemas.staff import StaffCreate, StaffUpdate
from app.services.base import BaseService


class StaffService(BaseService[Staff]):
    """Service for staff management."""

    def __init__(self, db: AsyncSession):
        super().__init__(Staff, db)

    async def list_staff(
        self,
        practice_id: UUID,
        skip: int = 0,
        limit: int = 100,
        role: Optional[StaffRole] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_full_time: Optional[bool] = None,
        search: Optional[str] = None,
        include_user: bool = False,
    ) -> tuple[list[Staff], int]:
        """
        List staff members with filtering and search.

        Args:
            practice_id: Practice ID for multi-tenancy
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Filter by staff role
            department: Filter by department
            is_active: Filter by active status
            is_full_time: Filter by full-time status
            search: Search by name, employee_id, job_title
            include_user: Include related user data

        Returns:
            Tuple of (staff list, total count)
        """
        query = self.scoped_query(practice_id)

        # Apply filters
        if role:
            query = query.where(Staff.role == role)
        if department:
            query = query.where(Staff.department.ilike(f'%{department}%'))
        if is_active is not None:
            query = query.where(Staff.is_active == is_active)
        if is_full_time is not None:
            query = query.where(Staff.is_full_time == is_full_time)

        # Search across multiple fields
        if search:
            search_filter = or_(
                Staff.employee_id.ilike(f'%{search}%'),
                Staff.job_title.ilike(f'%{search}%'),
                Staff.department.ilike(f'%{search}%'),
            )
            query = query.where(search_filter)

        # Include relationships
        if include_user:
            query = query.options(selectinload(Staff.user))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Staff.role, Staff.created_at)
        result = await self.db.execute(query)
        staff = list(result.scalars().all())

        return staff, total

    async def get_staff_by_id(
        self,
        staff_id: UUID,
        practice_id: UUID,
        include_user: bool = False,
    ) -> Optional[Staff]:
        """Get staff by ID with optional relationships."""
        query = self.scoped_query(practice_id).where(Staff.id == staff_id)

        if include_user:
            query = query.options(selectinload(Staff.user))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_staff_by_user_id(
        self,
        user_id: UUID,
        practice_id: UUID,
    ) -> Optional[Staff]:
        """Get staff by user ID."""
        query = self.scoped_query(practice_id).where(Staff.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_staff_by_employee_id(
        self,
        employee_id: str,
        practice_id: UUID,
    ) -> Optional[Staff]:
        """Get staff by employee ID."""
        query = self.scoped_query(practice_id).where(Staff.employee_id == employee_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_staff(
        self,
        practice_id: UUID,
        staff_data: StaffCreate,
        created_by: UUID,
    ) -> Staff:
        """
        Create new staff member.

        Args:
            practice_id: Practice ID for multi-tenancy
            staff_data: Staff creation data
            created_by: User ID who created the staff

        Returns:
            Created staff member

        Raises:
            ValueError: If user doesn't exist or already has staff profile
            ValueError: If employee_id already exists
        """
        # Verify user exists and belongs to practice
        user_query = select(User).where(
            User.id == staff_data.user_id,
            User.practice_id == practice_id
        )
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError('User not found or does not belong to this practice')

        # Check if user already has staff profile
        existing = await self.get_staff_by_user_id(staff_data.user_id, practice_id)
        if existing:
            raise ValueError('User already has a staff profile')

        # Check employee_id uniqueness if provided
        if staff_data.employee_id:
            existing_emp = await self.get_staff_by_employee_id(staff_data.employee_id, practice_id)
            if existing_emp:
                raise ValueError(f'Staff with employee_id {staff_data.employee_id} already exists')

        # Create staff
        staff = Staff(
            **staff_data.model_dump(),
            practice_id=practice_id,
        )
        self.db.add(staff)
        await self.db.flush()

        # Audit log
        await self.log_action(
            user_id=created_by,
            action='CREATE',
            entity_id=staff.id,
            changes={'new': staff_data.model_dump()}
        )

        return staff

    async def update_staff(
        self,
        staff_id: UUID,
        practice_id: UUID,
        staff_data: StaffUpdate,
        updated_by: UUID,
    ) -> Optional[Staff]:
        """Update staff member with audit logging."""
        staff = await self.get_staff_by_id(staff_id, practice_id)
        if not staff:
            return None

        # Check employee_id uniqueness if being updated
        if staff_data.employee_id and staff_data.employee_id != staff.employee_id:
            existing_emp = await self.get_staff_by_employee_id(staff_data.employee_id, practice_id)
            if existing_emp and existing_emp.id != staff_id:
                raise ValueError(f'Staff with employee_id {staff_data.employee_id} already exists')

        # Track changes for audit
        update_data = staff_data.model_dump(exclude_unset=True)
        old_values = {k: getattr(staff, k) for k in update_data.keys()}

        # Update fields
        for field, value in update_data.items():
            setattr(staff, field, value)

        # Audit log
        await self.log_action(
            user_id=updated_by,
            action='UPDATE',
            entity_id=staff.id,
            changes={'old': old_values, 'new': update_data}
        )

        return staff

    async def delete_staff(
        self,
        staff_id: UUID,
        practice_id: UUID,
        deleted_by: UUID,
    ) -> bool:
        """Delete staff (hard delete - removes profile but keeps user)."""
        staff = await self.get_staff_by_id(staff_id, practice_id)
        if not staff:
            return False

        # Audit log
        await self.log_action(
            user_id=deleted_by,
            action='DELETE',
            entity_id=staff.id,
            changes={}
        )

        await self.db.delete(staff)
        return True

    async def get_staff_by_role(
        self,
        practice_id: UUID,
        role: StaffRole,
        active_only: bool = True,
    ) -> list[Staff]:
        """Get staff members by role."""
        query = self.scoped_query(practice_id).where(Staff.role == role)

        if active_only:
            query = query.where(Staff.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_staff_by_department(
        self,
        practice_id: UUID,
        department: str,
        active_only: bool = True,
    ) -> list[Staff]:
        """Get staff members by department."""
        query = self.scoped_query(practice_id).where(
            Staff.department.ilike(f'%{department}%')
        )

        if active_only:
            query = query.where(Staff.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_staff(
        self,
        practice_id: UUID,
        full_time_only: bool = False,
    ) -> list[Staff]:
        """Get all active staff members."""
        query = self.scoped_query(practice_id).where(Staff.is_active == True)

        if full_time_only:
            query = query.where(Staff.is_full_time == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def terminate_staff(
        self,
        staff_id: UUID,
        practice_id: UUID,
        termination_date: str,
        terminated_by: UUID,
    ) -> Optional[Staff]:
        """Mark staff as terminated with date."""
        staff = await self.get_staff_by_id(staff_id, practice_id)
        if not staff:
            return None

        old_values = {
            'termination_date': staff.termination_date,
            'is_active': staff.is_active
        }

        staff.termination_date = termination_date
        staff.is_active = False

        # Audit log
        await self.log_action(
            user_id=terminated_by,
            action='TERMINATE',
            entity_id=staff.id,
            changes={
                'old': old_values,
                'new': {
                    'termination_date': termination_date,
                    'is_active': False
                }
            }
        )

        return staff
