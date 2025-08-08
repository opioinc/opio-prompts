# FastAPI Testing Guidelines

## Test Structure
- Organize tests in **`tests/`** directory mirroring source structure
- Create **`conftest.py`** at tests root for shared fixtures
- Use **`test_` prefix** for all test files
- Group tests by **feature/domain** in subdirectories
- Separate **unit tests** from **integration tests**
- Create **`fixtures/`** directory for test data files
- Use **`__init__.py`** files to make test modules importable
- Implement **end-to-end tests** in `tests/e2e/` directory
- Keep **test files small** and focused on single functionality
- Name tests with **descriptive function names** indicating what's being tested

## Essential Fixtures
- Create **async test database** fixture with in-memory SQLite
- Implement **test client** fixture using httpx.AsyncClient
- Create **authenticated client** fixture with valid JWT token
- Define **test user** fixture with known credentials
- Implement **mock Redis** fixture for caching tests
- Create **test data factory** fixtures using Factory Boy
- Define **cleanup fixtures** to reset state between tests
- Implement **mock email** fixture to capture sent emails
- Create **mock storage** fixture for file upload tests
- Define **time control** fixture for testing time-dependent code

## Pytest Configuration
- Use **pytest-asyncio** for async test support
- Configure **pytest-cov** for code coverage reporting
- Use **pytest-mock** for mocking external dependencies
- Enable **pytest-env** for test environment variables
- Configure **pytest-xdist** for parallel test execution
- Use **pytest-timeout** to prevent hanging tests
- Enable **pytest-benchmark** for performance testing
- Configure **markers** for test categorization (slow, integration, unit)
- Set **minimum coverage** threshold at 80%
- Use **pytest.ini** or **pyproject.toml** for configuration

## Database Testing
- Use **in-memory SQLite** for fast unit tests
- Create **test database** for integration tests
- Implement **transaction rollback** between tests for isolation
- Use **factory pattern** for generating test data
- Test **migrations** with separate test database
- Verify **cascade deletes** and foreign key constraints
- Test **concurrent database access** for race conditions
- Mock **repository methods** for service layer tests
- Test **database connection** pool exhaustion
- Verify **optimistic locking** behavior

## API Testing Patterns
- Test **all HTTP methods** (GET, POST, PUT, DELETE, PATCH)
- Verify **correct status codes** for success and error cases
- Validate **response schemas** match Pydantic models
- Test **pagination parameters** (skip, limit)
- Verify **sorting and filtering** functionality
- Test **invalid input** handling and validation errors
- Check **authentication requirements** on protected endpoints
- Test **authorization** for different user roles
- Verify **CORS headers** in responses
- Test **rate limiting** behavior

## Authentication Testing
- Test **login endpoint** with valid and invalid credentials
- Verify **JWT token generation** and structure
- Test **token expiration** handling
- Verify **refresh token** functionality
- Test **logout/token revocation** if implemented
- Check **password reset** flow end-to-end
- Test **account lockout** after failed attempts
- Verify **OAuth2 flows** if implemented
- Test **API key authentication** if used
- Verify **multi-factor authentication** if implemented

## Mocking Strategies
- Mock **external API calls** with responses fixture
- Use **monkeypatch** for environment variables
- Mock **datetime.now()** for time-dependent tests
- Create **fake implementations** for complex services
- Mock **file system operations** for upload/download tests
- Use **dependency override** for FastAPI dependencies
- Mock **email sending** to capture sent messages
- Create **test doubles** for database repositories
- Mock **Redis cache** for caching logic tests
- Use **spy objects** to verify method calls

## Test Data Management
- Use **Factory Boy** for complex test object creation
- Create **builder pattern** for flexible test data
- Implement **data fixtures** for common test scenarios
- Use **Faker** for generating realistic test data
- Create **seed data** scripts for integration tests
- Implement **test data cleanup** in teardown
- Use **parameterized tests** for multiple test cases
- Create **snapshot tests** for complex response validation
- Generate **random test data** for property-based testing
- Maintain **test data versioning** for backwards compatibility

## Async Testing
- Use **`@pytest.mark.asyncio`** for async test functions
- Create **async fixtures** with `async def` syntax
- Use **`await`** for all async operations in tests
- Test **concurrent requests** with asyncio.gather()
- Verify **async context managers** work correctly
- Test **background tasks** execution
- Use **async mocks** for async dependencies
- Test **WebSocket connections** if used
- Verify **async generators** and streaming responses
- Test **timeout behavior** for long-running operations

## Integration Testing
- Test **complete request flow** from router to database
- Verify **middleware execution** order and behavior
- Test **dependency injection** chain
- Verify **transaction boundaries** work correctly
- Test **error propagation** through layers
- Verify **caching behavior** with real Redis
- Test **file upload/download** end-to-end
- Verify **email sending** with test SMTP server
- Test **third-party integrations** with sandbox environments
- Verify **background job** execution

## Performance Testing
- Use **pytest-benchmark** for performance regression testing
- Test **API response times** under load
- Verify **database query performance**
- Test **concurrent user** handling
- Measure **memory usage** for large operations
- Test **file upload** performance with large files
- Verify **pagination performance** with large datasets
- Test **caching effectiveness** for repeated queries
- Measure **startup time** for application
- Profile **hot code paths** with py-spy

## Security Testing
- Test **SQL injection** prevention with malicious inputs
- Verify **XSS protection** with script injection attempts
- Test **authentication bypass** attempts
- Verify **authorization** for all endpoints
- Test **rate limiting** effectiveness
- Verify **file upload** restrictions
- Test **CORS policy** enforcement
- Check **security headers** presence
- Test **password strength** validation
- Verify **token expiration** and refresh

## Error Testing
- Test **404 responses** for non-existent resources
- Verify **400 responses** for invalid input
- Test **401 responses** for unauthenticated requests
- Verify **403 responses** for unauthorized access
- Test **409 responses** for conflicts
- Verify **422 responses** for validation errors
- Test **500 response** handling and error messages
- Verify **timeout handling** for slow operations
- Test **database connection** failure handling
- Verify **external service** failure handling

## Coverage Requirements
- Maintain **minimum 80% code coverage**
- Achieve **100% coverage** for critical paths
- Exclude **generated code** from coverage
- Cover **all API endpoints** with tests
- Test **all Pydantic model** validations
- Cover **error handling** paths
- Test **all business logic** functions
- Verify **all database queries** are tested
- Cover **edge cases** and boundary conditions
- Generate **HTML coverage reports** for review

## CI/CD Integration
- Run tests on **every pull request**
- Fail builds if **coverage drops** below threshold
- Run **different test suites** in parallel
- Execute **integration tests** against test database
- Run **security scans** in CI pipeline
- Generate **test reports** for review
- Cache **dependencies** for faster builds
- Run tests against **multiple Python versions**
- Execute **end-to-end tests** in staging environment
- Implement **smoke tests** for production deployments

## Test Best Practices
- Keep tests **independent** and isolated
- Use **descriptive test names** that explain what's being tested
- Follow **Arrange-Act-Assert** pattern
- Make tests **deterministic** and reproducible
- Avoid **testing implementation details**
- Focus on **behavior** not internal structure
- Keep tests **fast** by using mocks appropriately
- Write tests **before fixing bugs** (regression tests)
- Review **test code** as carefully as production code
- Document **complex test setups** with comments

## Common Testing Utilities
- Create **custom assertions** for domain-specific checks
- Implement **test helpers** for common operations
- Create **custom markers** for test categorization
- Build **test client wrappers** for common API calls
- Implement **database helpers** for test data setup
- Create **time helpers** for date/time testing
- Build **file helpers** for upload/download tests
- Implement **auth helpers** for token generation
- Create **validation helpers** for schema checking
- Build **comparison utilities** for complex objects