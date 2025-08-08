# FastAPI Database Guidelines (2025)

## SQLAlchemy Configuration
- Use SQLAlchemy 2.x async via `sqlalchemy.ext.asyncio`.
- Create engine with `create_async_engine(dsn, pool_pre_ping=True, echo=False)` using async drivers (`asyncpg`, `aiomysql`, `aiosqlite`).
- Use `async_sessionmaker(bind=engine, expire_on_commit=False)` for session factory.
- For Postgres/MySQL, tune pooling (e.g., `pool_size`, `max_overflow`, `pool_recycle`). For SQLite tests, prefer `NullPool`.
- Manage engine lifecycle inside app lifespan; dispose on shutdown.

## Models
- Inherit from `DeclarativeBase`; define columns with `Mapped[...]` and `mapped_column()`.
- Use explicit `__tablename__`; add created/updated timestamps where needed.
- Avoid implicit lazy-loading in async; specify loading strategies explicitly with `selectinload`/`joinedload`.
- Add indexes (composite/partial) for frequently filtered fields.

## Repository/Service Pattern
- Keep repositories thin and typed; expose `create`, `get`, `list`, `update`, `delete` with async semantics.
- Prefer `select(Model)`/`session.execute` and return scalars with `result.scalar_one_or_none()` etc.
- Keep business logic in services; repositories only orchestrate persistence.

## Queries & Optimization
- Use `select()` with `.options(selectinload(...))` to avoid N+1.
- For analytics, consider window functions/CTEs. Profile with EXPLAIN and add indexes.
- Batch writes with `session.execute(insert(Model).values([...]))` when appropriate.

## Transactions
- Use `async with session.begin():` for atomic write operations.
- For read-modify-write, use explicit transactions and appropriate isolation/locking (`with_for_update()` for pessimistic locks).
- Handle `IntegrityError` and retry transient failures with bounded backoff.

## Migrations (Alembic)
- Initialize async template: `alembic init -t async alembic`.
- Configure `sqlalchemy.url` from env; never hardcode.
- Use `--autogenerate` but always review diffs; add constraints and data migrations consciously.
- In production, run migrations in a separate job/container before app rollout; avoid multiple app instances running migrations.

## Connection Management
- Provide a request-scoped `AsyncSession` dependency that yields the session and ensures cleanup.
- Do not share sessions between requests/threads. Avoid global sessions.
- Set query timeouts at DB/proxy level; use application-level timeouts for external calls.

## Testing
- Use an ephemeral Postgres test container or `sqlite+aiosqlite:///:memory:` for unit tests depending on coverage needs.
- Run migrations against the test DB when integration testing.
- Use fixtures to create/drop schema and to rollback between tests for isolation.

## Common Pitfalls
- Building SQL strings manually (risk of injection); always parameterize.
- Relying on lazy-loading with async (unsupported); specify eager options.
- Large long-lived transactions leading to locks; keep transactions short.
- Forgetting indexes for frequent filters/sorts; monitor slow queries and add indexes.