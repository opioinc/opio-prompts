# FastAPI Development Rules

## Core Principles
- **Always use FastAPI 0.116.0+** with Pydantic v2 for latest features and performance
- Install with **`pip install "fastapi[standard]"`** to include all recommended dependencies
- Use **async/await** for all I/O operations; never use synchronous I/O in async routes
- Structure projects by **domain/feature**, not by file type (routers, models, schemas)
- Use **dependency injection** for database sessions, authentication, and shared resources
- Apply **SOLID principles** with emphasis on single responsibility and dependency inversion
- Prefer **functional programming** for stateless operations; use classes only for models and repositories
- Use **type hints** for all function signatures, including return types
- Handle errors with **guard clauses and early returns** to avoid nested conditionals
- Return **Pydantic models** from endpoints, never raw dictionaries or database objects

## Project Structure
- Organize code in **`src/{feature}/`** directories containing router, schemas, models, service, and dependencies
- Place shared utilities in **`src/core/`** including config, database, security, and middleware
- Keep **`main.py`** at src root as the application entry point
- Use **`alembic/`** directory for database migrations
- Structure tests to mirror source code in **`tests/{feature}/`**
- Use **`conftest.py`** for shared test fixtures at tests root
- Create **`.env`** files for environment-specific configuration, never commit them
- Define all models in **`models.py`**, schemas in **`schemas.py`**, and routes in **`router.py`** per feature

## Async Patterns
- Use **`async def`** for all route handlers and I/O operations
- Use **`await`** for all database queries, external API calls, and file operations
- Use regular **`def`** only for pure functions and CPU-bound operations
- Create async context managers with **`async with`** for database sessions and connections
- Use **`asyncio.gather()`** for concurrent operations when appropriate
- Implement **connection pooling** for databases with appropriate pool sizes
- Never use **blocking operations** like `time.sleep()` in async code; use `asyncio.sleep()`
- Use **`AsyncSession`** from SQLAlchemy for all database operations
- Implement **async generators** for streaming responses and large datasets

## API Design
- Use **RESTful conventions** with appropriate HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Return **201 Created** for successful POST requests with the created resource
- Return **204 No Content** for successful DELETE requests
- Return **404 Not Found** when resources don't exist
- Return **400 Bad Request** for validation errors with clear error messages
- Return **401 Unauthorized** for authentication failures
- Return **403 Forbidden** for authorization failures
- Use **path parameters** for resource identification (`/users/{user_id}`)
- Use **query parameters** for filtering, pagination, and sorting
- Implement **pagination** with `skip` and `limit` parameters
- Version APIs with **`/api/v1/`** prefix for backward compatibility
- Use **response_model** parameter to define return types explicitly
- Document endpoints with **docstrings** that appear in auto-generated docs

## Pydantic Usage
- Define **all request/response models** as Pydantic BaseModel subclasses
- Use **Pydantic v2** with `model_config` instead of the deprecated Config class
- Set **`from_attributes=True`** in model_config for ORM model compatibility
- Use **Field()** for validation constraints (min_length, max_length, ge, le)
- Implement **custom validators** with `@field_validator` decorator
- Use **EmailStr**, **HttpUrl**, and other Pydantic types for automatic validation
- Apply **`model_dump(exclude_unset=True)`** for partial updates
- Use **`model_dump(mode='json')`** for JSON-safe serialization
- Create separate models for **Create, Update, and Response** operations
- Never expose **sensitive fields** like passwords in response models

## Database Patterns
- Use **SQLAlchemy 2.0** with async support via `sqlalchemy.ext.asyncio`
- Define models with **Mapped** type hints and `mapped_column()`
- Use **DeclarativeBase** as the base class for all models
- Implement **repository pattern** for database operations
- Create **one repository per model** with standard CRUD operations
- Use **`select()`** statements instead of legacy Query API
- Apply **eager loading** with `selectinload()` or `joinedload()` to prevent N+1 queries
- Implement **soft deletes** with `is_deleted` flag when audit trails are needed
- Add **created_at** and **updated_at** timestamps to all models
- Use **database transactions** with `async with session.begin()` for atomic operations
- Configure **connection pooling** with appropriate pool_size and max_overflow
- Run **Alembic migrations** on startup in development, manually in production

## Dependency Injection
- Create **database session dependency** with `async def get_db()` yielding sessions
- Implement **authentication dependency** returning current user
- Chain dependencies with **`Depends()`** for complex authorization logic
- Use **dependency overrides** in tests to inject mock implementations
- Create **reusable dependencies** for common query parameters
- Implement **role-based dependencies** for authorization checks
- Use **BackgroundTasks** dependency for async task scheduling
- Apply **cache dependencies** for expensive computations
- Never instantiate dependencies directly; always use **Depends()**

## Security
- Hash passwords with **bcrypt** via passlib's CryptContext
- Generate **JWT tokens** with python-jose for authentication
- Store **secrets in environment variables**, never in code
- Set **short expiration times** for access tokens (15-30 minutes)
- Implement **refresh tokens** for long-lived sessions
- Use **OAuth2PasswordBearer** for token-based authentication
- Apply **CORS middleware** with specific allowed origins in production
- Validate all inputs with **Pydantic models** to prevent injection attacks
- Use **parameterized queries** via SQLAlchemy, never string concatenation
- Implement **rate limiting** with slowapi or similar libraries
- Add **security headers** (HSTS, X-Frame-Options, CSP) via middleware
- Enable **HTTPS only** in production with proper TLS certificates

## Testing
- Use **pytest** with pytest-asyncio for async test support
- Create **test fixtures** in conftest.py for database and client setup
- Use **in-memory SQLite** or test database for integration tests
- Mock external services with **pytest-mock** or unittest.mock
- Test **happy paths and error cases** for all endpoints
- Verify **status codes and response schemas** in API tests
- Use **TestClient** from FastAPI for synchronous tests
- Use **AsyncClient** from httpx for async tests
- Override dependencies with **app.dependency_overrides** in tests
- Achieve **minimum 80% code coverage** with pytest-cov
- Run tests in **CI/CD pipeline** on every commit

## Error Handling
- Raise **HTTPException** with appropriate status codes and detail messages
- Create **custom exception classes** for domain-specific errors
- Implement **global exception handlers** with `@app.exception_handler`
- Log exceptions with **full context** including request details
- Never expose **internal error details** to clients in production
- Use **status.HTTP_*_*` constants** instead of magic numbers
- Provide **user-friendly error messages** in the detail field
- Include **error codes** for client-side error handling
- Implement **retry logic** for transient failures in external services
- Return **validation errors** in a consistent format

## Performance
- Enable **connection pooling** for databases and Redis
- Implement **Redis caching** for frequently accessed data
- Use **lazy loading** for relationships by default
- Apply **eager loading** selectively to prevent N+1 queries
- Implement **pagination** for all list endpoints
- Use **background tasks** for time-consuming operations
- Enable **gzip compression** middleware for responses
- Implement **database indexes** on frequently queried columns
- Use **composite indexes** for multi-column queries
- Monitor **slow queries** and optimize with EXPLAIN ANALYZE
- Profile code with **py-spy** or similar tools in development
- Use **CDN** for static assets in production

## Configuration
- Use **pydantic-settings** for environment-based configuration
- Load settings from **`.env`** files via python-dotenv
- Define **separate settings** for development, staging, and production
- Never commit **`.env` files** to version control
- Use **`@lru_cache`** decorator on get_settings() for performance
- Validate **all environment variables** at startup
- Provide **sensible defaults** for optional settings
- Use **environment-specific** database URLs and API keys
- Configure **logging levels** based on environment
- Document all **required environment variables** in README

## Deployment
- Use **uvicorn** as the ASGI server
- Run with **multiple workers** using `--workers` flag
- Configure **gunicorn** with uvicorn workers for production
- Set **`--host 0.0.0.0`** to accept external connections
- Use **Docker** with multi-stage builds for containerization
- Implement **health check endpoints** at `/health` or `/ping`
- Configure **reverse proxy** (nginx, traefik) for SSL termination
- Enable **auto-reload** only in development with `--reload`
- Set **appropriate timeouts** for long-running requests
- Monitor with **Prometheus/Grafana** or similar tools
- Implement **graceful shutdown** handlers for cleanup
- Use **environment variables** for all configuration