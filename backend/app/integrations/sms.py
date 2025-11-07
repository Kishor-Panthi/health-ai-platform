from __future__ import annotations

import structlog

from app.core.config import settings

logger = structlog.get_logger('sms')


def get_sms_provider() -> 'BaseSMSProvider':
    if settings.twilio_account_sid and settings.twilio_auth_token:
        return TwilioSMSProvider(settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number)
    return ConsoleSMSProvider()


class BaseSMSProvider:
    async def send_sms(self, *, to: str, body: str) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class ConsoleSMSProvider(BaseSMSProvider):
    async def send_sms(self, *, to: str, body: str) -> None:
        logger.info('sms.send', to=to)


class TwilioSMSProvider(BaseSMSProvider):
    def __init__(self, account_sid: str, auth_token: str, from_number: str | None):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    async def send_sms(self, *, to: str, body: str) -> None:
        logger.info('twilio.send', to=to)