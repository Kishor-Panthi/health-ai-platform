from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class PracticeBase(BaseModel):
    name: str
    domain: str
    timezone: str = \"UTC\"
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None


class PracticeCreate(PracticeBase):
    pass


class PracticeUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None


class PracticeInDBBase(PracticeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., alias=\"id\")


class PracticeResponse(PracticeInDBBase):
    pass
