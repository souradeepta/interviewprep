# Singleton Pattern

## Overview
Ensures a class has only one instance and provides a global point of access to it.

## Problem Statement
Some classes should have exactly one instance (logger, database connection pool, configuration manager). Multiple instances waste resources and cause inconsistency.

## Solution
Restrict instantiation to a single instance. Provide a static method to access that instance.

## When to Use

**Use Singleton when:**
- Only one instance should exist (database connections, thread pools, logging)
- Instance needs global access (configuration, cache manager)
- Lazy initialization improves startup time (expensive initialization)
- Thread-safe access required to shared resource

**Examples:**
- Logger instance: share across entire application
- Database connection pool: single pool manages all connections
- Configuration manager: load config once, access everywhere
- Cache manager: one cache instance for entire system

## Real-World Scenarios

**Logging System:**
```
Application needs logging everywhere.
Create single Logger instance.
All classes access Logger.getInstance().log()
Ensures single log file, consistent formatting.
```

**Database Connection Pool:**
```
Multiple threads need DB connections.
Create ConnectionPool singleton.
Pool manages connections, prevents resource exhaustion.
Threads request connections from pool via getInstance().
```

## When NOT to Use

**Avoid Singleton when:**
- Multiple instances needed for different contexts (multi-tenancy)
- Testing requires mocking (hard to test, breaks encapsulation)
- Adds unnecessary coupling (classes depend on singleton)
- Simple factory would suffice

## Implementation Patterns

### Thread-Safe Lazy Initialization (Python)
```python
class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = super().__new__(cls)
        return cls._instance

logger = Singleton()  # First call creates instance
logger2 = Singleton()  # Returns same instance
```

### Static Holder Pattern (Java)
```java
public class Singleton {
    private Singleton() {}

    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;  // Lazy, thread-safe
    }
}
```

## Trade-Offs

**Pros:**
- Ensures single instance (resource efficiency)
- Global access point (convenient)
- Lazy initialization (deferred costly operations)
- Thread-safe implementations available

**Cons:**
- Hard to test (dependency on singleton instance)
- Hides dependencies (implicit global state)
- Violates single responsibility (manages creation + business logic)
- Can mask poor design (excessive global state)

## Production Considerations

- Use dependency injection instead (pass instance to classes that need it)
- If you need singleton, use static factory method
- Avoid nested singletons (cascade of globals)
- Make instance immutable if possible (thread safety)
- Add monitoring: track instance lifecycle, access patterns
