# Factory Pattern

**Level:** L4
**Time to read:** ~15 min

## Problem Statement

Your application needs to connect to different databases (PostgreSQL in prod, MySQL at a client site, SQLite in tests). Each connection requires different drivers, connection strings, and pooling config. Scattering `if db_type == "postgres": ...` throughout the codebase makes it impossible to add a new database without touching dozens of files. Factory centralizes and abstracts object creation so callers only see a common interface, never the concrete classes.

## Structure

```
  Factory Method                     Abstract Factory
  ──────────────                     ────────────────
  Creator (base class)               AbstractFactory
  ┌──────────────────┐               ┌────────────────────────┐
  │+ create_conn()   │◄──subclass──  │+ create_connection()   │
  │  (factory method)│               │+ create_query_builder()│
  └──────────────────┘               └────────────┬───────────┘
         ▲                                        │
  ┌──────┴──────┐              ┌──────────────────┼────────────────┐
  │PostgresCreat│              │                  │                │
  │MySQLCreator │              ▼                  ▼                ▼
  └─────────────┘         PostgresFactory    MySQLFactory    SQLiteFactory
                          (returns Postgres   (returns MySQL   (returns SQLite
                           Connection)         Connection)      Connection)

  Common interface all factories return:
  ┌────────────────────────┐
  │ DatabaseConnection     │
  │ + execute(sql) → rows  │
  │ + close()              │
  │ + health_check() → bool│
  └────────────────────────┘
```

## Python Implementation

```python
from abc import ABC, abstractmethod
from typing import Any
import os

class DatabaseConnection(ABC):
    @abstractmethod
    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

class PostgresConnection(DatabaseConnection):
    def __init__(self, dsn: str, pool_size: int = 10):
        self._dsn = dsn
        self._pool_size = pool_size
        print(f"[Postgres] Connected pool_size={pool_size}")

    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        print(f"[Postgres] Executing: {sql[:50]}")
        return [{"id": 1, "name": "Alice"}]   # stub

    def close(self) -> None:
        print("[Postgres] Connection pool closed")

    def health_check(self) -> bool:
        return True

class SQLiteConnection(DatabaseConnection):
    def __init__(self, db_path: str):
        self._path = db_path
        print(f"[SQLite] Opened {db_path}")

    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        print(f"[SQLite] Executing: {sql[:50]}")
        return []

    def close(self) -> None:
        print("[SQLite] File closed")

    def health_check(self) -> bool:
        return os.path.exists(self._path) or self._path == ":memory:"

class DatabaseFactory:
    """Registry-based factory — open for extension without modification."""

    _registry: dict[str, type[DatabaseConnection]] = {}

    @classmethod
    def register(cls, name: str, klass: type[DatabaseConnection]) -> None:
        cls._registry[name] = klass

    @classmethod
    def create(cls, db_type: str, **kwargs) -> DatabaseConnection:
        klass = cls._registry.get(db_type)
        if klass is None:
            available = list(cls._registry.keys())
            raise ValueError(f"Unknown db_type '{db_type}'. Available: {available}")
        return klass(**kwargs)

# Register drivers — could be loaded from plugins/config
DatabaseFactory.register("postgres", PostgresConnection)
DatabaseFactory.register("sqlite", SQLiteConnection)

# Usage — caller never imports concrete classes
db_type = os.getenv("DB_TYPE", "sqlite")

if db_type == "postgres":
    conn = DatabaseFactory.create("postgres", dsn="postgresql://user:pw@host/db", pool_size=20)
else:
    conn = DatabaseFactory.create("sqlite", db_path=":memory:")

rows = conn.execute("SELECT * FROM users WHERE active = TRUE")
conn.health_check()
conn.close()

# Adding MySQL later: just register, zero other changes
# DatabaseFactory.register("mysql", MySQLConnection)
```

## Real-World Uses

- **Django ORM backends:** `DATABASES["ENGINE"] = "django.db.backends.postgresql"` — Django's `DatabaseWrapper` factory reads the engine string and instantiates the right backend class.
- **AWS SDK client factories:** `boto3.client("s3")` vs `boto3.client("dynamodb")` — Factory pattern returns service-specific clients with a consistent interface.
- **Plugin systems:** pytest's fixture system, Flask extensions, and Click command groups all use registry-based factories to discover and instantiate handlers without coupling.
- **Logging handlers:** `logging.handlers.SocketHandler`, `FileHandler`, `StreamHandler` — `logging.getLogger()` factory wires them together based on config.

## When to Apply

**Apply Factory when:**
- Object creation logic is complex or requires configuration
- You need to decouple callers from concrete classes (testability, swappability)
- You want to support multiple implementations of the same interface (drivers, providers)
- You need runtime selection of which class to instantiate (config, feature flags)

**Do NOT use when:**
- You're creating one simple object — `Connection(dsn)` is clearer than `ConnectionFactory.create("postgres", dsn=dsn)`
- The factory itself becomes a bloated "god class" knowing every possible type — prefer a registry pattern or plugin loader
- You just need dependency injection — pass the object in directly rather than having callers use a factory

## Common Interview Questions

**Q1. What's the difference between Factory Method and Abstract Factory?**
Factory Method: one method in a class that subclasses override to produce one type of object. Abstract Factory: a family of related factories producing multiple related objects (e.g., PostgresFactory creates both `PostgresConnection` AND `PostgresQueryBuilder`, ensuring they're compatible).

**Q2. How do you make a factory extensible without modifying it?**
Registry pattern — factories register themselves: `DatabaseFactory.register("mysql", MySQLConnection)`. The factory never needs to know about MySQL; the MySQL module registers itself on import. This is the plugin pattern used by pytest, SQLAlchemy dialects, and Click.

**Q3. How does Django use the Factory pattern?**
`django.db.backends` maps the `ENGINE` string to a backend class. `connection = DatabaseWrapper(settings)` is the factory call. Each backend (`postgresql`, `sqlite3`, `mysql`) implements the same `DatabaseWrapper` interface.

**Q4. How do you test code that uses a Factory?**
Register a mock/stub in tests: `DatabaseFactory.register("test", MockConnection)`, then set `DB_TYPE=test`. The real application code is unchanged — the factory handles the swap.

**Q5. Design a cloud storage factory for S3, GCS, Azure Blob.**
```python
class StorageFactory:
    _registry = {}

    @classmethod
    def register(cls, name, klass): cls._registry[name] = klass

    @classmethod
    def create(cls, provider: str, **config) -> "StorageClient":
        return cls._registry[provider](**config)

# Each provider registers on import:
# StorageFactory.register("s3", S3Client)
# StorageFactory.register("gcs", GCSClient)
```
Callers use `StorageFactory.create(os.getenv("CLOUD_PROVIDER"), bucket=...)`.

## Related Patterns

- **Abstract Factory:** Factory of factories — creates families of related objects (connection + query builder + schema migrator for one DB flavor).
- **Builder:** When construction is multi-step (chain of config calls) rather than a single create call — e.g., `QueryBuilder().select("*").from_("users").where("active=1").build()`.
- **Strategy:** Factory often instantiates strategies — `StrategyFactory.create("exponential_backoff")` returns a `RetryStrategy`.
- See `docs/03-system-design/03-design-patterns/02_factory_method.md` and `03_abstract_factory.md` for UML-level detail.
