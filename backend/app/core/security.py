\"\"\"Security helpers for hashing passwords and issuing JWTs.\"\"\"

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app.core.config import settings


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class TokenPayload(BaseModel):
    \"\"\"Represents fields stored inside our JWT tokens.\"\"\"

    sub: str
    exp: int
    type: Literal['access', 'refresh'] = 'access'
    practice_id: str | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _default_expiry(token_type: Literal['access', 'refresh']) -> timedelta:
    if token_type == 'refresh':
        return timedelta(minutes=settings.refresh_token_expire_minutes)
    return timedelta(minutes=settings.access_token_expire_minutes)


def create_token(
    subject: Any,
    *,
    practice_id: Any | None = None,
    token_type: Literal['access', 'refresh'] = 'access',
    expires_delta: timedelta | None = None,
) -> str:
    \"\"\"Create a signed JWT for the given subject.\"\"\"

    expire = datetime.now(tz=timezone.utc) + (expires_delta or _default_expiry(token_type))
    to_encode: dict[str, Any] = {'exp': expire, 'sub': str(subject), 'type': token_type}
    if practice_id is not None:
        to_encode['practice_id'] = str(practice_id)
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenPayload | None:
    \"\"\"Decode a JWT and return its payload or None if invalid.\"\"\"

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return TokenPayload(**payload)
    except (JWTError, ValidationError):
        return None