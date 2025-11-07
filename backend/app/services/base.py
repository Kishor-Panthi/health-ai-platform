"""Shared service utilities."""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.audit_service import AuditService

ModelT = TypeVar("ModelT")


class BaseService(Generic[ModelT]):
    def __init__(self, session: AsyncSession, practice_id: uuid.UUID):
        self.session = session
        self.practice_id = practice_id
        self.audit = AuditService(session)

    def scoped_query(self, model: type[ModelT], *criterions: Any) -> Select[tuple[ModelT]]:
        stmt = select(model).where(model.practice_id == self.practice_id, *criterions)
        return stmt

    async def soft_delete(self, model: type[ModelT], record_id: uuid.UUID) -> None:
        result = await self.session.execute(
            self.scoped_query(model).where(model.id == record_id)
        )
        instance = result.scalar_one()
        setattr(instance, "is_deleted", True)
        await self.session.commit()
        await self.audit.log(
            practice_id=self.practice_id,
            actor_id=None,
            action="soft_delete",
            entity=model.__name__,
            entity_id=record_id,
            payload={"record_id": str(record_id)},
        )
