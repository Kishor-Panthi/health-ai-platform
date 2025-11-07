"""Provider service for business logic."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.provider import Provider
from app.models.user import User
from app.api.v1.schemas.provider import ProviderCreate, ProviderUpdate
from app.services.base import BaseService


class ProviderService(BaseService[Provider]):
    """Service for provider management."""

    def __init__(self, db: AsyncSession):
        super().__init__(Provider, db)

    async def list_providers(
        self,
        practice_id: UUID,
        skip: int = 0,
        limit: int = 100,
        specialty: Optional[str] = None,
        department: Optional[str] = None,
        accepting_new_patients: Optional[bool] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        include_user: bool = False,
        include_schedules: bool = False,
    ) -> tuple[list[Provider], int]:
        """
        List providers with filtering and search.

        Args:
            practice_id: Practice ID for multi-tenancy
            skip: Number of records to skip
            limit: Maximum number of records to return
            specialty: Filter by specialty
            department: Filter by department
            accepting_new_patients: Filter by accepting new patients
            is_active: Filter by active status
            search: Search by name, NPI, specialty
            include_user: Include related user data
            include_schedules: Include related schedule data

        Returns:
            Tuple of (providers list, total count)
        """
        query = self.scoped_query(practice_id)

        # Apply filters
        if specialty:
            query = query.where(Provider.specialty.ilike(f'%{specialty}%'))
        if department:
            query = query.where(Provider.department.ilike(f'%{department}%'))
        if accepting_new_patients is not None:
            query = query.where(Provider.accepting_new_patients == accepting_new_patients)
        if is_active is not None:
            query = query.where(Provider.is_active == is_active)

        # Search across multiple fields
        if search:
            search_filter = or_(
                Provider.npi.ilike(f'%{search}%'),
                Provider.specialty.ilike(f'%{search}%'),
                Provider.title.ilike(f'%{search}%'),
            )
            query = query.where(search_filter)

        # Include relationships
        if include_user:
            query = query.options(selectinload(Provider.user))
        if include_schedules:
            query = query.options(selectinload(Provider.schedules))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Provider.specialty, Provider.created_at)
        result = await self.db.execute(query)
        providers = list(result.scalars().all())

        return providers, total

    async def get_provider_by_id(
        self,
        provider_id: UUID,
        practice_id: UUID,
        include_user: bool = False,
        include_schedules: bool = False,
    ) -> Optional[Provider]:
        """Get provider by ID with optional relationships."""
        query = self.scoped_query(practice_id).where(Provider.id == provider_id)

        if include_user:
            query = query.options(selectinload(Provider.user))
        if include_schedules:
            query = query.options(selectinload(Provider.schedules))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_provider_by_user_id(
        self,
        user_id: UUID,
        practice_id: UUID,
    ) -> Optional[Provider]:
        """Get provider by user ID."""
        query = self.scoped_query(practice_id).where(Provider.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_provider_by_npi(
        self,
        npi: str,
        practice_id: Optional[UUID] = None,
    ) -> Optional[Provider]:
        """Get provider by NPI (optionally scoped to practice)."""
        query = select(Provider).where(Provider.npi == npi)
        if practice_id:
            query = query.where(Provider.practice_id == practice_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_provider(
        self,
        practice_id: UUID,
        provider_data: ProviderCreate,
        created_by: UUID,
    ) -> Provider:
        """
        Create new provider.

        Args:
            practice_id: Practice ID for multi-tenancy
            provider_data: Provider creation data
            created_by: User ID who created the provider

        Returns:
            Created provider

        Raises:
            ValueError: If user doesn't exist or already has provider profile
            ValueError: If NPI already exists
        """
        # Verify user exists and belongs to practice
        user_query = select(User).where(
            User.id == provider_data.user_id,
            User.practice_id == practice_id
        )
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError('User not found or does not belong to this practice')

        # Check if user already has provider profile
        existing = await self.get_provider_by_user_id(provider_data.user_id, practice_id)
        if existing:
            raise ValueError('User already has a provider profile')

        # Check NPI uniqueness if provided
        if provider_data.npi:
            existing_npi = await self.get_provider_by_npi(provider_data.npi)
            if existing_npi:
                raise ValueError(f'Provider with NPI {provider_data.npi} already exists')

        # Create provider
        provider = Provider(
            **provider_data.model_dump(),
            practice_id=practice_id,
        )
        self.db.add(provider)
        await self.db.flush()

        # Audit log
        await self.log_action(
            user_id=created_by,
            action='CREATE',
            entity_id=provider.id,
            changes={'new': provider_data.model_dump()}
        )

        return provider

    async def update_provider(
        self,
        provider_id: UUID,
        practice_id: UUID,
        provider_data: ProviderUpdate,
        updated_by: UUID,
    ) -> Optional[Provider]:
        """Update provider with audit logging."""
        provider = await self.get_provider_by_id(provider_id, practice_id)
        if not provider:
            return None

        # Check NPI uniqueness if being updated
        if provider_data.npi and provider_data.npi != provider.npi:
            existing_npi = await self.get_provider_by_npi(provider_data.npi)
            if existing_npi and existing_npi.id != provider_id:
                raise ValueError(f'Provider with NPI {provider_data.npi} already exists')

        # Track changes for audit
        update_data = provider_data.model_dump(exclude_unset=True)
        old_values = {k: getattr(provider, k) for k in update_data.keys()}

        # Update fields
        for field, value in update_data.items():
            setattr(provider, field, value)

        # Audit log
        await self.log_action(
            user_id=updated_by,
            action='UPDATE',
            entity_id=provider.id,
            changes={'old': old_values, 'new': update_data}
        )

        return provider

    async def delete_provider(
        self,
        provider_id: UUID,
        practice_id: UUID,
        deleted_by: UUID,
    ) -> bool:
        """Delete provider (hard delete - removes profile but keeps user)."""
        provider = await self.get_provider_by_id(provider_id, practice_id)
        if not provider:
            return False

        # Audit log
        await self.log_action(
            user_id=deleted_by,
            action='DELETE',
            entity_id=provider.id,
            changes={}
        )

        await self.db.delete(provider)
        return True

    async def get_providers_by_specialty(
        self,
        practice_id: UUID,
        specialty: str,
        accepting_only: bool = True,
    ) -> list[Provider]:
        """Get providers by specialty."""
        query = self.scoped_query(practice_id).where(
            Provider.specialty.ilike(f'%{specialty}%'),
            Provider.is_active == True
        )

        if accepting_only:
            query = query.where(Provider.accepting_new_patients == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_available_providers(
        self,
        practice_id: UUID,
        department: Optional[str] = None,
    ) -> list[Provider]:
        """Get all active providers accepting new patients."""
        query = self.scoped_query(practice_id).where(
            Provider.is_active == True,
            Provider.accepting_new_patients == True
        )

        if department:
            query = query.where(Provider.department == department)

        result = await self.db.execute(query)
        return list(result.scalars().all())
