\"\"\"Common pydantic schemas shared across endpoints.\"\"\"

from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')


class PaginatedResponse(GenericModel, Generic[T]):
    data: Sequence[T]
    total: int
    page: int
    size: int


class SuccessResponse(BaseModel):
    detail: str = 'ok'


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None