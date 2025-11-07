# Healthcare Practice Management Backend

FastAPI-based backend for the Codex health platform. It implements multi-tenant primitives, authentication, patient + appointment workflows, and audit/rate limiting middleware so the Next.js frontend can integrate against a stable contract.

## Stack
- **Framework**: FastAPI 0.109 with async routes
- **ORM**: SQLAlchemy 2 async engine + Alembic migrations
- **Database**: PostgreSQL 15 (Docker), Redis 7 (rate limiting placeholder)
- **Security**: OAuth2 password flow with JWT access + refresh tokens, bcrypt hashing, Fernet field encryption
- **Observability**: Structlog JSON logging, request/audit middleware, request ID propagation
- **Integrations**: SendGrid/Twilio/Stripe/S3 facades with console fallbacks

## Getting Started
1. Copy the environment template and adjust secrets as needed:
   `ash
   cd backend
   cp .env.example .env
   `
2. Start the required services:
   `ash
   docker compose up -d db redis
   `
3. Apply database migrations (initial models provided via Alembic metadata):
   `ash
   alembic upgrade head
   `
4. Launch the API:
   `ash
   uvicorn app.main:app --reload
   `
5. Open http://localhost:8000/docs for interactive OpenAPI documentation.

## Testing
Pytest is configured for async tests using httpx.ASGITransport.
`ash
pytest --maxfail=1 --disable-warnings
`

## Data Seeding
Two helper scripts live in pp/db/:
- seed.py creates a practice, admin, and demo patient.
- create_superuser.py ensures the first superuser credentials from the environment exist.

Run them with:
`ash
python -m app.db.seed
python -m app.db.create_superuser
`

## Key Modules
| Area | Path | Notes |
| --- | --- | --- |
| Config & Secrets | pp/core/config.py | Pydantic settings, defaults for local dev |
| Database | pp/core/database.py | Async session factory + metadata naming conventions |
| Security | pp/core/security.py | Password hashing + JWT helpers |
| Models | pp/models/*.py | Practice, User, Patient, Appointment, AuditLog with mixins |
| Services | pp/services/*.py | Encapsulated domain logic w/ audit + multi-tenancy guards |
| API Layer | pp/api/v1/endpoints/ | Auth, Patients, Appointments, Health routers |
| Middleware | pp/middleware/ | Audit logging, error handling, in-memory rate limiting |
| Integrations | pp/integrations/ | SendGrid/Twilio/S3/Stripe facades with console stubs |

## Next Steps
- Expand the model + schema surface to cover all entities listed in CODEX_BACKEND_IMPLEMENTATION.xml.
- Flesh out Alembic migrations and automate schema generation.
- Implement WebSocket notifications for real-time updates.
- Back the rate limiting middleware with Redis for horizontal scalability.
- Add integration/unit tests for every endpoint and service plus negative-path coverage.

The provided slice is intentionally vertical (auth ? patient/appointment) so new modules can follow the same layering pattern (schema ? service ? router) without retooling infrastructure.