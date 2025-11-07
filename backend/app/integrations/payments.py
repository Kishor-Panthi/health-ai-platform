from __future__ import annotations

import structlog

from app.core.config import settings

logger = structlog.get_logger('payments')


class PaymentProvider:
    async def charge(self, *, customer_id: str, amount_cents: int, currency: str = 'usd') -> str:  # pragma: no cover
        raise NotImplementedError


class StripePaymentProvider(PaymentProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def charge(self, *, customer_id: str, amount_cents: int, currency: str = 'usd') -> str:
        logger.info('stripe.charge', customer_id=customer_id, amount_cents=amount_cents, currency=currency)
        return 'stub-charge-id'


def get_payment_provider() -> PaymentProvider:
    if settings.stripe_api_key:
        return StripePaymentProvider(settings.stripe_api_key)
    logger.info('payments.stub')
    return StripePaymentProvider('test')