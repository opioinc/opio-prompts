# FastAPI Development Rules (2025)

## Core Principles
- Always use the latest stable FastAPI with Pydantic v2. Install with `pip install "fastapi[standard]"`.
- Prefer `typing.Annotated` for parameters and dependencies. Keep all functions fully type-annotated.
- Use async I/O everywhere that touches the network or disk; use `asyncio.to_thread` for CPU-bound work.
- Keep handlers lean; put business logic in services. Apply SOLID and clear separation of concerns.
- Return Pydantic models (not raw dicts/ORM objects) from endpoints. Never expose secrets.

## Project Structure
- Organize by feature/domain: `src/{feature}/router.py`, `schemas.py`, `service.py`, `models.py`, `deps.py`.
- Place cross-cutting utilities in `src/core/` (config, security, db, middleware, logging).
- Use application factory plus lifespan context (see below). Keep entrypoint `main.py` minimal.
- Mirror source structure in `tests/{feature}/` with a shared `tests/conftest.py`.
- Use `alembic/` for migrations and a `.env.example` for required variables (never commit real `.env`).

## Application Lifecycle
- Prefer lifespan over deprecated `@app.on_event`:
  - Provide `lifespan=lifespan_context` to `FastAPI(...)` and initialize/cleanup resources there.
  - Initialize DB engine/session factories, caches, metrics, and other clients at startup; dispose on shutdown.
- Use dependency injection for per-request resources; avoid global mutable state.

## Async Patterns
- Define route handlers as `async def` and await all I/O (DB via SQLAlchemy AsyncSession, HTTP via `httpx.AsyncClient`).
- Use `asyncio.gather` for safe concurrency; guard against thundering herds and timeouts.
- Never block the event loop (`time.sleep`, CPU-bound loops). Use `asyncio.sleep` or `asyncio.to_thread`.
- Stream large responses with async generators when applicable.

## API Design
- Follow RESTful conventions and correct status codes:
  - POST create: 201 Created and include `Location` header to new resource.
  - DELETE success with no body: 204 No Content.
  - Missing resource: 404; validation errors: 422; rate-limited: 429.
- Use path params for identity, query params for filtering, pagination, sort.
- Implement pagination consistently. For large lists, prefer cursor-based pagination; for small lists, `skip`/`limit` is acceptable.
- Document with `response_model`, `status_code`, `tags`, `summary`, `description`, `responses={...}`.
- Keep error shape consistent. Consider Problem Details (RFC 9457) or a single structured error schema.

## Pydantic v2 Usage
- Define all request/response models as `BaseModel` and use `model_config = ConfigDict(from_attributes=True)` for ORM compatibility.
- Use `Annotated[T, Field(...)]` for constraints (`min_length`, `ge`, `le`, `regex`).
- Prefer `@field_validator`/`@model_validator` for custom validation.
- For partial updates, use `model_dump(exclude_unset=True)`; for JSON-safe output, `model_dump(mode="json")`.
- Separate Create/Update/Read models. Never return secret fields (passwords, tokens, keys).

## Database Patterns (SQLAlchemy 2.0 async)
- Use `sqlalchemy.ext.asyncio.create_async_engine` and `async_sessionmaker(bind=engine, expire_on_commit=False)`.
- Use `Mapped[...]` with `mapped_column()` and `DeclarativeBase` for models.
- Prefer 2.0 Core/ORM patterns: `select(Model)`, `insert(Model)`, `update(Model)`, `delete(Model)` via `session.execute`.
- Avoid legacy `Query` API and implicit lazy loading (not supported in async). Use `selectinload`/`joinedload` as needed.
- Keep repositories thin and typed; one repository per aggregate/root entity.
- Use transactions: `async with session.begin(): ...` for atomic operations.
- Add indexes (including composite/partial) for high-cardinality and frequent filters.

## Dependency Injection
- Provide request-scoped dependencies with `Depends(...)` returning typed resources (e.g., `AsyncSession`, current user, settings slice).
- Build reusable query param dependencies (pagination, sorting, filtering) with `Annotated`.
- Override dependencies in tests via `app.dependency_overrides`.

## Security (see security.md for details)
- Use OAuth2/OIDC for auth where possible. Prefer Argon2id (or bcrypt) for password hashing.
- Prefer asymmetric JWTs (RS256/ES256) with JWKS and `kid` for rotation; keep access tokens short-lived.
- Apply CORS with explicit origins in production, `TrustedHostMiddleware`, and strict security headers.
- Rate-limit at the edge (reverse proxy/API gateway). App-level rate limiting only as an additional layer.

## Testing
- Use `pytest` with `pytest-anyio` for async tests (works across anyio backends).
- Prefer `httpx.AsyncClient` with ASGI transport; ensure lifespan runs during tests.
- Test happy paths, errors, authorization, and schema validation; assert status codes and response models.
- Achieve ≥80% coverage overall; 100% for critical security/business logic.

## Error Handling
- Raise `HTTPException` with informative `detail`. Avoid leaking internals in production.
- Add global exception handlers (`@app.exception_handler`) for domain errors and validation normalization.
- Log errors with correlation/request IDs and relevant context.

## Performance
- Install `fastapi[standard]` to enable `uvloop`, `httptools`, etc.
- Consider `ORJSONResponse` as default response class for large JSON payloads.
- Cache expensive reads (Redis) with explicit invalidation. Avoid N+1 DB access.
- Use gzip at the proxy; optionally `GZipMiddleware` for app-level compression.
- Profile hot paths (py-spy) and monitor slow queries; add proper DB indexes.

## Observability
- Emit structured JSON logs (one line per event). Include `trace_id`/`request_id`.
- Use OpenTelemetry for traces/metrics/logs; add ASGI, SQLAlchemy, HTTPX instrumentation.
- Expose `/health` and `/ready` endpoints. Export Prometheus metrics when applicable.

## Configuration
- Use `pydantic-settings` for typed configuration. Cache `get_settings()` with `@lru_cache`.
- Validate environment at startup; keep `.env` for local only. Document required variables in `README`.
- Configure log levels and sensitive toggles (debug, docs enabled) per-environment.

## Deployment
- Development: `fastapi dev path/to/main.py` for reload and debug.
- Production: `fastapi run path/to/main.py --host 0.0.0.0 --port 8000` (no reload). Or use Gunicorn with `uvicorn.workers.UvicornWorker`.
- Behind proxies, pass `--proxy-headers` and configure trusted proxies / forwarded IPs correctly.
- Use Docker multi-stage builds; run one process per container and scale horizontally. Terminate TLS at a reverse proxy (nginx/traefik/caddy) with HTTP/2 or HTTP/3.
- Implement health checks, readiness gates, graceful shutdown, and appropriate timeouts.