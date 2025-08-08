# FastAPI Database Guidelines

## SQLAlchemy Configuration
- Use **SQLAlchemy 2.0+** with async support via `sqlalchemy.ext.asyncio`
- Create async engine with **`create_async_engine()`** and appropriate driver (asyncpg, aiomysql)
- Configure **connection pooling** with pool_size=20, max_overflow=40 for production
- Enable **pool_pre_ping=True** to verify connections before use
- Set **pool_recycle=3600** to recycle connections every hour
- Use **NullPool** for SQLite in tests, **QueuePool** for PostgreSQL/MySQL
- Set **echo=False** in production, **echo=True** only for debugging
- Use **async_sessionmaker** to create session factory
- Set **expire_on_commit=False** to avoid lazy loading issues
- Implement **lifespan context manager** for startup/shutdown database operations

## Model Definition
- Inherit all models from **DeclarativeBase** or custom Base class
- Use **Mapped[]** type hints for all column definitions
- Define columns with **mapped_column()** instead of Column()
- Set **`__tablename__`** explicitly for each model
- Add **primary_key=True** to ID columns
- Use **String(length)** to specify varchar lengths
- Apply **index=True** to frequently queried columns
- Add **unique=True** for unique constraints
- Implement **ForeignKey** with ondelete="CASCADE" when appropriate
- Define **relationships** with back_populates for bidirectional access

## Common Model Patterns
- Add **id: Mapped[int]** with primary_key=True and autoincrement
- Include **created_at: Mapped[datetime]** with default=datetime.utcnow
- Include **updated_at: Mapped[datetime]** with onupdate=datetime.utcnow
- Implement **is_deleted: Mapped[bool]** for soft deletes with default=False
- Use **UUID** primary keys for distributed systems with uuid.uuid4
- Create **TimestampMixin** class for reusable timestamp fields
- Implement **SoftDeleteMixin** for soft delete functionality
- Use **@declared_attr** for dynamic table names in mixins
- Override **`__repr__`** for better debugging output
- Add **dict()** method to convert models to dictionaries

## Repository Pattern
- Create **one repository class per model** for data access
- Inherit from **BaseRepository[ModelType]** with generic typing
- Implement standard **CRUD methods**: create, get, update, delete, list
- Accept **AsyncSession** in repository constructor
- Use **select()** statements with method chaining
- Return **Optional[Model]** for single record queries
- Return **List[Model]** for multiple record queries
- Implement **get_or_create()** for idempotent operations
- Add **exists()** method to check record existence
- Include **count()** method for aggregations
- Use **filters** parameter as dict for dynamic filtering
- Implement **pagination** with skip and limit parameters

## Query Optimization
- Use **selectinload()** for one-to-many eager loading
- Use **joinedload()** for one-to-one eager loading
- Apply **contains_eager()** when filtering on joined tables
- Avoid **lazy loading** in production; use eager loading strategies
- Use **select().options()** to specify loading strategies
- Implement **subqueryload()** for complex nested relationships
- Use **Query.execution_options(synchronize_session=False)** for bulk updates
- Apply **index hints** for query optimization when needed
- Use **CTEs** (Common Table Expressions) for complex queries
- Implement **window functions** for analytics queries

## Transactions
- Use **async with session.begin()** for automatic transaction management
- Implement **nested transactions** with begin_nested() for savepoints
- Call **await session.commit()** explicitly when needed
- Use **await session.rollback()** in exception handlers
- Apply **session.flush()** to get generated IDs before commit
- Use **session.merge()** for updating detached instances
- Implement **optimistic locking** with version columns
- Use **with_for_update()** for pessimistic locking
- Handle **IntegrityError** for constraint violations
- Implement **retry logic** for deadlock recovery

## Migrations with Alembic
- Initialize with **`alembic init -t async alembic`** for async support
- Set **sqlalchemy.url** in alembic.ini from environment variable
- Use **`--autogenerate`** flag to detect model changes
- Review **generated migrations** before applying
- Add **meaningful messages** with `-m` flag
- Test migrations with **`alembic upgrade head`** and **`alembic downgrade -1`**
- Implement **data migrations** in separate upgrade/downgrade functions
- Use **batch operations** for SQLite ALTER TABLE operations
- Add **check constraints** in migrations for data validation
- Version control **all migration files** in alembic/versions/

## Connection Management
- Create **DatabaseManager** class for connection lifecycle
- Implement **connect()** and **disconnect()** methods
- Use **dependency injection** with `async def get_db()`
- Yield sessions with **try/finally** for proper cleanup
- Configure **connection pool monitoring** for performance metrics
- Implement **connection retry logic** for transient failures
- Use **context managers** for automatic session cleanup
- Set **appropriate timeouts** for long-running queries
- Monitor **connection pool usage** with logging
- Implement **health checks** for database connectivity

## Performance Best Practices
- Create **indexes** on foreign keys and frequently queried columns
- Use **composite indexes** for multi-column WHERE clauses
- Implement **partial indexes** for filtered queries
- Add **EXPLAIN ANALYZE** to optimize slow queries
- Use **bulk_insert_mappings()** for batch inserts
- Apply **bulk_update_mappings()** for batch updates
- Implement **pagination** with LIMIT and OFFSET
- Use **cursor-based pagination** for large datasets
- Cache **frequently accessed** data with Redis
- Monitor **query execution time** with event listeners

## Testing Database Code
- Use **in-memory SQLite** for unit tests with sqlite+aiosqlite:///:memory:
- Create **test fixtures** for database setup and teardown
- Use **factory pattern** for test data generation
- Implement **transaction rollback** in fixtures for test isolation
- Mock **repository methods** for unit testing business logic
- Test **migrations** separately with test database
- Verify **indexes and constraints** in integration tests
- Test **concurrent access** patterns for race conditions
- Validate **cascade deletes** behavior
- Test **connection pool** exhaustion scenarios

## Common Pitfalls to Avoid
- Never use **string concatenation** for SQL queries
- Don't share **sessions between requests** or threads
- Avoid **N+1 queries** by using proper eager loading
- Don't use **lazy loading** in async code
- Never commit **database credentials** to version control
- Don't ignore **database connection limits**
- Avoid **large transactions** that lock tables
- Don't use **SELECT *** in production queries
- Never skip **migration testing** before deployment
- Don't forget **database backups** before migrations