"""Centralized audit logging helper."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class AuditService:
    """Writes structured audit events to the database."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        *,
        practice_id: uuid.UUID,
        actor_id: uuid.UUID | None,
        action: str,
        entity: str | None = None,
        entity_id: uuid.UUID | None = None,
        payload: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        from app.models.audit import AuditLog  # Local import to avoid cycles

        audit_record = AuditLog(
            practice_id=practice_id,
            actor_id=actor_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            payload=json.loads(json.dumps(payload or {}, default=str)),
            request_id=request_id,
        )
        self.session.add(audit_record)
        await self.session.commit()
