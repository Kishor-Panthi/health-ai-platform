\"\"\"Helpers for encrypting sensitive fields using Fernet.\"\"\"

from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import String, TypeDecorator

from app.core.config import settings


@lru_cache(maxsize=1)
def get_fernet() -> Fernet:
    return Fernet(settings.encryption_key.encode())


def encrypt_value(value: str | None) -> str | None:
    if value is None:
        return None
    return get_fernet().encrypt(value.encode()).decode()


def decrypt_value(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return get_fernet().decrypt(value.encode()).decode()
    except InvalidToken:
        # Already plain text
        return value


class EncryptedString(TypeDecorator):
    \"\"\"SQLAlchemy column type that transparently encrypts text.\"\"\"

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return encrypt_value(value)

    def process_result_value(self, value, dialect):
        return decrypt_value(value)
