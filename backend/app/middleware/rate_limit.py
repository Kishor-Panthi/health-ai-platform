from __future__ import annotations

import asyncio
import time
from collections import defaultdict

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit_per_minute: int = 120):
        super().__init__(app)
        self.limit = limit_per_minute
        self.lock = asyncio.Lock()
        self.buckets: dict[str, tuple[int, float]] = defaultdict(lambda: (0, time.time() + 60))

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_id = request.client.host if request.client else 'anonymous'
        async with self.lock:
            count, reset_at = self.buckets[client_id]
            now = time.time()
            if now > reset_at:
                count = 0
                reset_at = now + 60
            if count >= self.limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={'detail': 'Rate limit exceeded', 'retry_after': int(reset_at - now)},
                )
            self.buckets[client_id] = (count + 1, reset_at)
        return await call_next(request)