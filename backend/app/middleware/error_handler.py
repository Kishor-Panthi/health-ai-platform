from __future__ import annotations

import structlog
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger('errors')


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - fallback path
            request_id = getattr(request.state, 'request_id', 'unknown')
            logger.exception('unhandled_error', request_id=request_id)
            return JSONResponse(
                status_code=500,
                content={'detail': 'Internal server error', 'request_id': request_id},
            )