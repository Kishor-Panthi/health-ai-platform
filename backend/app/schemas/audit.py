"\"\"\"Audit log schemas.\""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    practice_id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    entity: str | None
    entity_id: uuid.UUID | None
    payload: dict | None
    request_id: str | None
    created_at: datetime
