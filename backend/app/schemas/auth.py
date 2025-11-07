"\"\"\"Authentication schemas.\""

from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    practice_domain: str


class RegisterRequest(BaseModel):
    practice_name: str
    practice_domain: str
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class AuthenticatedUser(BaseModel):
    id: uuid.UUID
    practice_id: uuid.UUID
    email: EmailStr
    full_name: str | None = None
