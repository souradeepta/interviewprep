# Design Patterns Reference: Gang of Four in System Design

The 23 Gang of Four design patterns and where they appear in real system designs.

---

## Creational Patterns (Object Creation)

### Singleton
**Definition:** Ensure only one instance of a class exists globally.

**System Design Use:**
- Connection pool (one shared pool of DB connections)
- Logger (one global logger)
- Configuration manager (one config object)
- Cache manager (one cache instance per service)

**Your repo:** `python/system_design/rate_limiter.py`, `python/system_design/load_balancer.py`

---

### Factory
**Definition:** Create objects without specifying exact classes.

**System Design Use:**
- Message queue choice (KafkaQueueFactory, RabbitMQQueueFactory)
- Database choice (SQLDatabaseFactory, NoSQLDatabaseFactory)
- Cache layer (RedisFactory, MemcachedFactory)
- Load balancer strategy (RoundRobinFactory, ConsistentHashFactory)

**Your repo:** `python/system_design/factory_pattern.py`, `python/system_design/load_balancer.py`

---

## Structural Patterns (Object Composition)

### Adapter
**Definition:** Convert interface of one class to another.

**System Design Use:**
- Legacy system integration
- Different payment gateway APIs → unified interface
- Different database drivers → abstracted interface

**Your repo:** `python/system_design/adapter_pattern.py`

---

### Decorator
**Definition:** Attach additional responsibilities dynamically.

**System Design Use:**
- Caching decorator (transparently cache function results)
- Logging decorator (log function calls)
- Rate limiting decorator (throttle function calls)
- Retry decorator (retry on failure)

**Your repo:** `python/system_design/decorator_pattern.py`

---

### Facade
**Definition:** Provide unified interface to subsystem.

**System Design Use:**
- API gateway (facade for multiple microservices)
- Order service facade (coordinates inventory, payment, shipping)

**Your repo:** `python/system_design/api_gateway.py`

---

### Proxy
**Definition:** Placeholder for another object to control access.

**System Design Use:**
- Lazy loading (load resource only when accessed)
- Access control (validate permissions before delegating)
- Caching proxy (return cached result if available)
- Remote proxy (forward calls to remote service)

---

## Behavioral Patterns (Object Interaction)

### Observer
**Definition:** Define one-to-many dependency; notify all observers on state change.

**System Design Use:**
- Event-driven architecture (publish-subscribe)
- User notifications (observer pattern)
- Reactive systems

**Your repo:** `python/system_design/observer_pattern.py`

---

### Strategy
**Definition:** Define family of algorithms, make them interchangeable.

**System Design Use:**
- Caching strategies (LRU, LFU, TTL)
- Load balancing strategies (round-robin, consistent hash, least connections)
- Ranking algorithms (for search, feed)

**Your repo:** `python/system_design/strategy_pattern.py`, `python/system_design/load_balancer.py`

---

### State
**Definition:** Allow object to change behavior when state changes.

**System Design Use:**
- Order state machine (pending → paid → shipped → delivered)
- Payment authorization states
- User session states

---

### Template Method
**Definition:** Define algorithm skeleton; let subclasses fill in steps.

**System Design Use:**
- Database migration framework
- Data processing pipeline
- Request/response handling flow

---

### Chain of Responsibility
**Definition:** Pass request through chain of handlers until one handles it.

**System Design Use:**
- Middleware chains (HTTP request processing)
- Logging levels (DEBUG → INFO → WARN)
- Approval workflows

---

### Command
**Definition:** Encapsulate request as object for queuing, undoing.

**System Design Use:**
- Command queues (async processing)
- Undo/redo functionality
- Scheduled jobs

---

## Distributed Systems Patterns

### Circuit Breaker
**Definition:** Stop calling failing service to prevent cascading failures.

**Your repo:** `python/system_design/circuit_breaker.py`

**Usage:** If payment service fails 5x, open circuit (stop calling) for 60 seconds, then half-open (try again)

---

### Retry with Exponential Backoff
**Definition:** Retry failed requests with increasing delays.

**Usage:** On 503 error, wait 1s, then 2s, then 4s, etc. Prevents thundering herd.

---

### Saga Pattern
**Definition:** Distributed transaction across services via choreography or orchestration.

**Your repo:** `python/system_design/saga_pattern.py`

**Usage:** Order saga: OrderService → PaymentService → InventoryService, with compensating transactions on failure

---

### Event Sourcing
**Definition:** Store state changes as immutable event log; rebuild state by replaying events.

**Usage:** Order service: store "OrderCreated", "OrderPaid", "OrderShipped" events. State = replay all events.

---

### CQRS (Command Query Responsibility Segregation)
**Definition:** Separate read model from write model.

**Usage:** Write to normalized schema, read from denormalized cache. Cache updates via events.

---

See `python/system_design/` for implementations of each pattern.
