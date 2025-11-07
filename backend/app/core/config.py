"""Application settings powered by pydantic."""

from functools import lru_cache
from typing import Literal
import secrets
import base64
from cryptography.fernet import Fernet

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Insecure default keys that should never be used in production
INSECURE_DEFAULT_SECRET_KEY = 'dev-secret-key-please-change-me-0123456789abcdef'
INSECURE_DEFAULT_ENCRYPTION_KEY = 'g0q2fZ4zG9XkA0RduCMsZ/HXXIQK5vCk1vZ1tcHTTXc='


class Settings(BaseSettings):
    """Central application configuration."""

    app_env: Literal['development', 'staging', 'production'] = 'development'
    api_v1_prefix: str = '/api/v1'
    project_name: str = 'Codex Health Platform'
    secret_key: str = Field(min_length=32, description='JWT signing secret key')
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5433/health_ai'
    sync_database_url: str = 'postgresql://postgres:postgres@localhost:5433/health_ai'
    database_pool_size: int = 5
    database_pool_max_overflow: int = 10
    log_level: str = 'INFO'
    rate_limit_per_minute: int = 120

    encryption_key: str = Field(
        description='Base64 encoded Fernet key for field-level encryption',
    )
    default_practice_domain: str = 'demo.practice.local'

    # CORS settings
    cors_origins: list[str] = Field(
        default=['http://localhost:3000'],
        description='Allowed CORS origins - comma-separated in .env as CORS_ORIGINS'
    )

    sendgrid_api_key: str | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None
    aws_s3_bucket: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_region: str | None = 'us-east-1'
    stripe_api_key: str | None = None

    first_superuser_email: str | None = 'admin@example.com'
    first_superuser_password: str | None = 'ChangeMe123!'
    first_superuser_practice_name: str | None = 'Codex Health'
    first_superuser_domain: str | None = 'codex.local'

    sentry_dsn: AnyHttpUrl | None = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Ensure secret_key is not using insecure default in non-development environments."""
        if v == INSECURE_DEFAULT_SECRET_KEY:
            app_env = info.data.get('app_env', 'development')
            if app_env != 'development':
                raise ValueError(
                    f'Cannot use default SECRET_KEY in {app_env} environment. '
                    'Please set a secure SECRET_KEY in your environment variables. '
                    f'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )
            print(
                "⚠️  WARNING: Using default SECRET_KEY. This is only acceptable in development. "
                "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )

        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')

        return v

    @field_validator('encryption_key')
    @classmethod
    def validate_encryption_key(cls, v: str, info) -> str:
        """Ensure encryption_key is valid Fernet key and not using insecure default."""
        if v == INSECURE_DEFAULT_ENCRYPTION_KEY:
            app_env = info.data.get('app_env', 'development')
            if app_env != 'development':
                raise ValueError(
                    f'Cannot use default ENCRYPTION_KEY in {app_env} environment. '
                    'Please set a secure ENCRYPTION_KEY in your environment variables. '
                    'Generate one with: python -c "from cryptography.fernet import Fernet; '
                    'print(Fernet.generate_key().decode())"'
                )
            print(
                "⚠️  WARNING: Using default ENCRYPTION_KEY. This is only acceptable in development. "
                "Generate a secure key with: python -c \"from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())\""
            )

        # Validate that it's a valid Fernet key
        try:
            Fernet(v.encode() if isinstance(v, str) else v)
        except Exception as e:
            raise ValueError(
                f'ENCRYPTION_KEY must be a valid base64-encoded Fernet key. '
                'Generate one with: python -c "from cryptography.fernet import Fernet; '
                f'print(Fernet.generate_key().decode())". Error: {e}'
            )

        return v

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v


@lru_cache
def get_settings() -> 'Settings':
    """Return cached settings instance so we do not re-parse env vars."""

    return Settings()


settings = get_settings()


def generate_secret_key() -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)


def generate_encryption_key() -> str:
    """Generate a secure Fernet encryption key."""
    return Fernet.generate_key().decode()
