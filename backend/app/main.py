from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware import AuditMiddleware, ErrorHandlingMiddleware, RateLimitMiddleware

configure_logging(settings.log_level)
logger = structlog.get_logger("lifespan")

app = FastAPI(
    title=settings.project_name,
    version='1.0.0',
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware, limit_per_minute=settings.rate_limit_per_minute)
app.add_middleware(ErrorHandlingMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, 'request_id', 'unknown')
    return JSONResponse(
        status_code=422,
        content={'detail': exc.errors(), 'request_id': request_id},
    )


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Codex Health API'}


@app.on_event('startup')
async def on_startup() -> None:
    logger.info('startup')


@app.on_event('shutdown')
async def on_shutdown() -> None:
    logger.info('shutdown')


app.include_router(api_router, prefix=settings.api_v1_prefix)
