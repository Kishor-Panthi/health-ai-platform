from __future__ import annotations

import structlog

from app.core.config import settings

logger = structlog.get_logger('email')


def get_email_provider() -> 'BaseEmailProvider':
    if settings.sendgrid_api_key:
        return SendGridEmailProvider(api_key=settings.sendgrid_api_key)
    return ConsoleEmailProvider()


class BaseEmailProvider:
    async def send_email(self, *, to: str, subject: str, body: str) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class ConsoleEmailProvider(BaseEmailProvider):
    async def send_email(self, *, to: str, subject: str, body: str) -> None:
        logger.info('email.send', to=to, subject=subject)


class SendGridEmailProvider(BaseEmailProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def send_email(self, *, to: str, subject: str, body: str) -> None:
        # Placeholder for actual SendGrid integration
        logger.info('sendgrid.send', to=to, subject=subject)