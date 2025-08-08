# FastAPI Testing Guidelines (2025)

## Test Structure
- Organize tests in `tests/` mirroring source structure; share fixtures in `tests/conftest.py`.
- Separate unit, integration, and e2e; use markers to filter (`-m "not e2e"`).
- Keep tests focused and descriptive; one behavior per test.

## Essential Fixtures
- Async test client based on `httpx.AsyncClient` with ASGI transport and lifespan support.
- Database fixture yielding an `AsyncSession` bound to a fresh test DB/schema.
- Authenticated client fixture to exercise protected endpoints.
- Clock/time control fixture for time-bound logic.
- Temporary storage/FS fixture for upload/download tests.

## Pytest Configuration
- Use `pytest-anyio` for async tests (preferable to `pytest-asyncio` in AnyIO-based stacks).
- Enable coverage (`pytest-cov`) and parallelization (`pytest-xdist`) as needed.
- Configure `pytest.ini`/`pyproject.toml` for markers, test paths, and timeouts.

## Database Testing
- For integration tests, use a containerized Postgres test DB; run Alembic migrations.
- Rollback/refresh between tests for isolation; avoid sharing state.
- Use factories/builders for test data; avoid brittle hand-crafted objects.

## API Testing Patterns
- Exercise all methods and verify status codes, schemas, and side effects.
- Validate pagination and filtering; cover invalid input and boundary conditions.
- Verify CORS headers when applicable; check auth and authorization flows.

## Authentication Testing
- Test login with valid/invalid credentials; verify token structure and expiry behavior.
- Verify refresh, logout/rotation, and revoked-token handling where implemented.
- Cover role/permission matrix on sensitive endpoints.

## Mocking Strategies
- Mock external HTTP with `respx`/`responses` for httpx.
- Monkeypatch environment vars; use fakes for disk/email/object storage.
- Use dependency overrides to inject fakes/mocks for FastAPI dependencies.

## Test Data Management
- Use factories and builders; prefer deterministic data and stable seeds.
- Snapshot complex responses only for stable contracts and after agreement.

## Async Testing
- Mark async tests with `@pytest.mark.anyio` (or configure globally).
- Use `asyncio.gather` in tests for concurrency behavior; assert ordering/limits when relevant.
- Test streaming endpoints and WebSockets when used.

## Integration & E2E
- Verify middleware order, dependency chains, transaction boundaries, and caching behavior.
- Run E2E tests against a realistic environment (compose/k8s namespace) before production deploys.

## Performance Testing
- Use `pytest-benchmark` or `locust`/`k6` for load tests on critical endpoints.
- Track P99 latency targets and DB query counts in performance tests.

## Security Testing
- Attempt SQLi, XSS payloads on inputs; verify rejection and logging.
- Test rate limits/abuse protections, password complexity, and header hardening.

## Error Testing
- Validate consistent error envelope and mapping to status codes (400/401/403/404/409/422/429/500).
- Simulate timeouts and failures of dependencies (DB, cache, HTTP).

## Coverage
- Maintain ≥80% overall coverage; 100% for critical auth, payments, and business invariants.
- Exclude generated code and migrations.

## CI/CD Integration
- Run unit + integration suites on PRs; gate merges on green and coverage threshold.
- Produce junit and coverage XML for CI reports; cache deps for speed.
- Run smoke/E2E in staging with environment-configured endpoints.

## Best Practices
- Keep tests independent and deterministic; avoid sleep unless testing timing explicitly.
- Assert on behavior and contracts, not internal implementation details.
- Add regression tests when fixing bugs.