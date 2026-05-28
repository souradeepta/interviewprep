# Connection Pooling

**Level:** L4-L5
**Time to read:** ~30 min

Manage database connections efficiently to reduce overhead, prevent connection exhaustion, and maximize throughput under high concurrency.

---

## ⚖️ Connection Pool Trade-offs

| Strategy | Pool Size | Memory/Conn | Latency | Throughput | Best For |
|----------|-----------|-------------|---------|------------|---------|
| **Minimal** | 5–10 | 1–5 MB | High (queue) | Low | Development, tiny apps |
| **Balanced** | 10–25 | 10–25 MB | Medium | Medium | Most web applications |
| **Large** | 50–100 | 50–100 MB | Low | High | High-concurrency APIs |
| **Dedicated** | 200–500 | 200–500 MB | Very low | Very high | Data warehouses, analytics |

### Pooler Comparison

| Feature | PgBouncer | HikariCP | pgpool-II | AWS RDS Proxy |
|---------|-----------|----------|-----------|---------------|
| Protocol | TCP-level | JDBC | TCP-level | Managed |
| Mode | Session/Transaction/Statement | Connection-level | Multi-mode | Transaction |
| Max connections | 10K+ | JVM-limited | 10K+ | DB-limited |
| Failover | Manual | Auto | Auto | Auto |
| Overhead | <1ms | <1ms | 1–3ms | 1–2ms |
| Best for | PostgreSQL | Java apps | PG + HA | AWS/serverless |

### Connection Pool Sizing Formula

```
pool_size = (cores × 2) + effective_spindle_count

Example: 4-core server, SSD (spindle = 0):
  pool_size = (4 × 2) + 0 = 8

Rule of thumb: start at 10, measure, adjust.
Never exceed: DB's max_connections ÷ app_instance_count

PostgreSQL default max_connections = 100
For 5 app servers: 100 / 5 = 20 connections per pool
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Application-Level Pool (HikariCP)

```
┌─────────────────────────────────────────────────┐
│              Application Server                  │
│                                                  │
│  Request → ThreadPool → HikariCP Pool            │
│                              │                   │
│            ┌─────────────────┴──────────────┐   │
│            │  [conn1] [conn2] [conn3] [conn4]│   │
│            │  [idle ] [busy ] [idle ] [busy ]│   │
│            └─────────────────┬──────────────┘   │
│                              │                   │
│                     TCP Connection               │
└─────────────────────────────────────────────────┘
                               │
                        PostgreSQL DB
```

### Pattern 2: External Pooler (PgBouncer)

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  App Server │      │  PgBouncer   │      │ PostgreSQL  │
│  (1000 req) │ ──── │ (1000 client │ ──── │ (20 server  │
│             │      │  connections)│      │  connections)│
└─────────────┘      └──────────────┘      └─────────────┘

PgBouncer multiplexes N client connections onto M DB connections.
Clients see immediate "connection accepted"; DB only allocates on query.
```

### Pattern 3: Pool Exhaustion Handling (Circuit Breaker)

```
┌───────────────────────────────────────────────────────┐
│                   Circuit Breaker States               │
│                                                        │
│   Closed ──── (failures > threshold) ──► Open          │
│      │                                     │           │
│      │◄── (timeout, test success) ──── Half-Open       │
│      │                                     │           │
│   Normal requests            Probe one request        │
│   pass through               → success: Closed        │
│                              → fail: stay Open        │
└───────────────────────────────────────────────────────┘
```

---

## 📊 Connection Pool Implementation

```python
import threading
import time
import queue
import contextlib
from dataclasses import dataclass, field
from typing import Optional
from collections import deque

@dataclass
class PoolConfig:
    min_size: int = 5
    max_size: int = 20
    acquire_timeout: float = 5.0   # seconds to wait for a connection
    max_lifetime: float = 3600.0   # seconds before connection replaced
    idle_timeout: float = 600.0    # seconds before idle connection closed
    validation_query: str = "SELECT 1"

class DBConnection:
    """Simulated DB connection with lifecycle tracking."""
    _counter = 0

    def __init__(self, pool_id: int):
        DBConnection._counter += 1
        self.id = DBConnection._counter
        self.pool_id = pool_id
        self.created_at = time.time()
        self.last_used = time.time()
        self.is_valid = True
        self._closed = False

    def execute(self, sql: str) -> str:
        if self._closed:
            raise RuntimeError("Connection closed")
        self.last_used = time.time()
        return f"[conn-{self.id}] result of: {sql}"

    def close(self):
        self._closed = True
        self.is_valid = False

    def validate(self) -> bool:
        return self.is_valid and not self._closed

    def is_expired(self, max_lifetime: float) -> bool:
        return time.time() - self.created_at > max_lifetime

    def is_idle_too_long(self, idle_timeout: float) -> bool:
        return time.time() - self.last_used > idle_timeout


class ConnectionPool:
    """Thread-safe connection pool with lifecycle management."""

    def __init__(self, pool_id: int = 1, config: Optional[PoolConfig] = None):
        self.pool_id = pool_id
        self.config = config or PoolConfig()
        self._pool: queue.Queue = queue.Queue(maxsize=self.config.max_size)
        self._all_connections: list = []
        self._lock = threading.Lock()
        self._total_created = 0
        self._total_acquired = 0
        self._total_timeouts = 0
        self._active_count = 0

        # Pre-warm with min connections
        for _ in range(self.config.min_size):
            conn = self._create_connection()
            self._pool.put(conn)

        # Background eviction thread
        self._eviction_thread = threading.Thread(target=self._eviction_loop, daemon=True)
        self._eviction_thread.start()

    def _create_connection(self) -> DBConnection:
        conn = DBConnection(self.pool_id)
        with self._lock:
            self._total_created += 1
            self._all_connections.append(conn)
        return conn

    @contextlib.contextmanager
    def acquire(self):
        """Context manager: borrow a connection, auto-return on exit."""
        conn = self._acquire_connection()
        try:
            yield conn
        except Exception:
            conn.is_valid = False  # Mark unhealthy on exception
            raise
        finally:
            self._release_connection(conn)

    def _acquire_connection(self) -> DBConnection:
        deadline = time.time() + self.config.acquire_timeout
        while time.time() < deadline:
            try:
                conn = self._pool.get(timeout=0.1)
                if conn.validate() and not conn.is_expired(self.config.max_lifetime):
                    with self._lock:
                        self._total_acquired += 1
                        self._active_count += 1
                    return conn
                else:
                    conn.close()  # Discard expired/invalid
                    conn = self._create_connection()
                    with self._lock:
                        self._total_acquired += 1
                        self._active_count += 1
                    return conn
            except queue.Empty:
                # Pool exhausted — try to grow
                with self._lock:
                    if len(self._all_connections) < self.config.max_size:
                        conn = self._create_connection()
                        self._total_acquired += 1
                        self._active_count += 1
                        return conn

        with self._lock:
            self._total_timeouts += 1
        raise TimeoutError(
            f"Pool exhausted: {self._active_count} active / {self.config.max_size} max. "
            f"Waited {self.config.acquire_timeout}s."
        )

    def _release_connection(self, conn: DBConnection):
        with self._lock:
            self._active_count = max(0, self._active_count - 1)
        if conn.validate():
            try:
                self._pool.put_nowait(conn)
            except queue.Full:
                conn.close()
        else:
            conn.close()

    def _eviction_loop(self):
        """Background: evict idle/expired connections, keep min warm."""
        while True:
            time.sleep(30)
            with self._lock:
                to_remove = [
                    c for c in self._all_connections
                    if not c.is_valid or c.is_expired(self.config.max_lifetime)
                ]
                for c in to_remove:
                    self._all_connections.remove(c)
                    c.close()

    def stats(self) -> dict:
        return {
            "pool_size": self._pool.qsize(),
            "active": self._active_count,
            "total_created": self._total_created,
            "total_acquired": self._total_acquired,
            "total_timeouts": self._total_timeouts,
        }


# Demo
pool = ConnectionPool(config=PoolConfig(min_size=2, max_size=5, acquire_timeout=2.0))

with pool.acquire() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = 1")
    print(result)

print("Pool stats:", pool.stats())
```

---

## 🔧 PgBouncer Configuration

```ini
; pgbouncer.ini
[databases]
mydb = host=postgres-primary port=5432 dbname=production

[pgbouncer]
; Mode: session (safest) | transaction (best multiplexing) | statement (fastest)
pool_mode = transaction

; Connections from apps to PgBouncer
listen_port = 6432
listen_addr = *

; Max clients PgBouncer accepts
max_client_conn = 1000

; Pool size per (database, user) pair
default_pool_size = 20

; Keep spare idle connections
min_pool_size = 5

; Add connections if queue exceeds
reserve_pool_size = 5
reserve_pool_timeout = 3.0

; Kill idle server connections after
server_idle_timeout = 600

; Kill client connections idle beyond
client_idle_timeout = 60

; Reconnect if server connection older than
server_lifetime = 3600

; Authentication
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Admin
admin_users = pgbouncer_admin
stats_users = pgbouncer_stats
logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid
```

### HikariCP Configuration (Java/Spring Boot)

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/production
    username: app_user
    password: ${DB_PASSWORD}
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 600000        # 10 minutes
      max-lifetime: 1800000       # 30 minutes
      connection-timeout: 5000    # 5 seconds
      connection-test-query: SELECT 1
      pool-name: MainPool
      leak-detection-threshold: 10000  # warn if connection held > 10s
      data-source-properties:
        cachePrepStmts: true
        prepStmtCacheSize: 250
        prepStmtCacheSqlLimit: 2048
```

---

## ❓ Interview Q&A

**Q1: Pool exhausted — 1,000 requests are queuing. What's your runbook?**

A: Triage in priority order:
1. **Identify cause** (`SHOW PROCESSLIST` / `pg_stat_activity`): are connections idle-in-transaction? Slow queries? Connection leak?
2. **Immediate relief**: Temporarily increase `max_pool_size` (if DB headroom exists) or add a read replica to offload SELECTs
3. **Kill idle-in-transaction** connections older than 30s (`pg_terminate_backend`)
4. **Root cause**: Long-running query → add index / kill job. Leak → find code path not releasing. Traffic spike → scale app instances with separate pool budgets

**Q2: What's the difference between PgBouncer transaction mode and session mode?**

A: In **session mode**, each client connection maps 1:1 to a server connection for the session lifetime — safe for `SET`/`PREPARE`/advisory locks, but no multiplexing benefit. In **transaction mode**, a server connection is only held for the duration of a single transaction — enables 1,000 clients to share 20 server connections, but breaks SET, PREPARE, and advisory locks. **Rule**: use transaction mode for stateless HTTP APIs; use session mode only if you need session-level state.

**Q3: How do you detect a connection leak in production?**

A: Three signals:
1. `pool.active_count` grows monotonically while `pool.idle_count` → 0 even during low traffic
2. `pg_stat_activity` shows connections in `idle in transaction` state for >60s
3. HikariCP `leak-detection-threshold` fires a stack trace log pointing to the code path

Fix: wrap every connection in `try/finally` or use context managers (`with pool.acquire() as conn`). Enable HikariCP leak detection in staging.

**Q4: Should you use one global pool or per-tenant pools in a multi-tenant SaaS?**

A: Depends on isolation requirements:
- **Global pool** (default): simpler, lower overhead; all tenants share connections; one noisy tenant can exhaust the pool
- **Per-tenant pool**: strong isolation, independent sizing; 100 tenants × 10 min connections = 1,000 DB connections — may exceed DB limit
- **Hybrid (recommended)**: global pool with per-tenant quotas enforced via semaphore; fair-sharing without per-tenant overhead

**Q5: How do you right-size a connection pool?**

A: Formula: `pool_size = (cpu_cores × 2) + disk_spindles`. For SSDs: `pool_size ≈ cpu_cores × 2`. Then:
1. Load test at peak traffic, watch `pool_wait_time` histogram
2. If p99 wait > 5ms → increase pool or reduce query latency
3. Watch `pg_stat_activity` — if connections always active, you're undersized; if mostly idle, you're oversized
4. Benchmark: Netflix found optimal was 16–20 connections per 4-core instance

---

## 🧪 Practical Exercises

### Exercise 1: Pool Size Calculator (Easy)

**Problem:** Given traffic profile, compute optimal pool size with margin.

```python
import math

def calculate_pool_size(
    peak_rps: int,
    avg_query_ms: float,
    cpu_cores: int,
    safety_factor: float = 1.5,
) -> dict:
    """
    Little's Law: N = λ × W
    N = concurrent DB connections needed
    λ = queries/sec, W = avg query duration (sec)
    """
    queries_per_second = peak_rps
    query_duration_sec = avg_query_ms / 1000

    # Theoretical min by Little's Law
    littles_law = math.ceil(queries_per_second * query_duration_sec)

    # Hardware-based formula
    hardware_formula = cpu_cores * 2

    # Recommended (higher of the two, with safety margin)
    recommended = math.ceil(max(littles_law, hardware_formula) * safety_factor)

    return {
        "little_s_law": littles_law,
        "hardware_formula": hardware_formula,
        "recommended_pool_size": recommended,
        "max_pool_size": recommended * 2,     # hard ceiling
        "min_pool_size": max(5, recommended // 4),  # warm floor
    }

# Example: API server, 500 RPS peak, 20ms avg query, 4-core machine
profile = calculate_pool_size(peak_rps=500, avg_query_ms=20, cpu_cores=4)
print(profile)
# → {'little_s_law': 10, 'hardware_formula': 8, 'recommended_pool_size': 15, ...}
```

---

### Exercise 2: Connection Leak Detector (Medium)

**Problem:** Track connection borrow duration; alert if any connection held > threshold.

```python
import threading
import time
import traceback
from typing import Optional

class LeakDetectingPool:
    def __init__(self, pool, leak_threshold_sec: float = 10.0):
        self.pool = pool
        self.leak_threshold_sec = leak_threshold_sec
        self._borrows: dict = {}  # conn_id → (borrow_time, stack)
        self._lock = threading.Lock()
        self._alerts: list = []

        # Background watchdog
        self._watchdog = threading.Thread(target=self._watch, daemon=True)
        self._watchdog.start()

    def _watch(self):
        while True:
            time.sleep(5)
            now = time.time()
            with self._lock:
                for conn_id, (borrow_time, stack) in list(self._borrows.items()):
                    held = now - borrow_time
                    if held > self.leak_threshold_sec:
                        alert = {
                            "conn_id": conn_id,
                            "held_sec": round(held, 1),
                            "stack": stack,
                        }
                        self._alerts.append(alert)
                        print(f"⚠️  LEAK DETECTED: conn-{conn_id} held {held:.1f}s\n{stack}")

    def borrow(self, conn):
        """Call after acquiring connection."""
        stack = "".join(traceback.format_stack()[:-1])  # caller's stack
        with self._lock:
            self._borrows[conn.id] = (time.time(), stack)

    def return_conn(self, conn):
        """Call before releasing connection."""
        with self._lock:
            self._borrows.pop(conn.id, None)

    def get_alerts(self) -> list:
        return list(self._alerts)

# Integration with ConnectionPool
pool = ConnectionPool(config=PoolConfig(min_size=2, max_size=5))
leak_detector = LeakDetectingPool(pool, leak_threshold_sec=3.0)

def fetch_user(user_id: int):
    with pool.acquire() as conn:
        leak_detector.borrow(conn)
        result = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
        time.sleep(0.1)  # Normal query
        leak_detector.return_conn(conn)
        return result

# Simulate leak
def leaky_operation():
    conn = pool._acquire_connection()  # Not using context manager!
    leak_detector.borrow(conn)
    time.sleep(5)  # Hold forever
    # Never released → leak

thread = threading.Thread(target=leaky_operation, daemon=True)
thread.start()
time.sleep(4)
print("Alerts:", leak_detector.get_alerts())
```

---

### Exercise 3: Circuit Breaker for Pool Exhaustion (Hard)

**Problem:** When pool is exhausted, implement circuit breaker to fail fast instead of queuing.

```python
import time
import threading
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # Normal: all requests pass
    OPEN = "open"           # Failed: all requests fail fast
    HALF_OPEN = "half_open" # Testing: one request probes

class DBCircuitBreaker:
    def __init__(
        self,
        pool: ConnectionPool,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_sec: float = 30.0,
    ):
        self.pool = pool
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_sec = timeout_sec

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time > self.timeout_sec:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
            return self._state

    def call(self, func, *args, **kwargs):
        state = self.state
        if state == CircuitState.OPEN:
            raise RuntimeError("Circuit OPEN — DB unavailable, failing fast")

        try:
            with self.pool.acquire() as conn:
                result = func(conn, *args, **kwargs)
                self._on_success()
                return result
        except (TimeoutError, RuntimeError) as e:
            self._on_failure()
            raise

    def _on_success(self):
        with self._lock:
            self._failure_count = 0
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    print("✅ Circuit CLOSED — DB recovered")

    def _on_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                print(f"🔴 Circuit OPEN — {self._failure_count} failures, backing off {self.timeout_sec}s")

# Demo
pool = ConnectionPool(config=PoolConfig(min_size=1, max_size=2, acquire_timeout=0.5))
breaker = DBCircuitBreaker(pool, failure_threshold=3, timeout_sec=5)

def query_user(conn, user_id):
    return conn.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Normal traffic
try:
    print(breaker.call(query_user, 1))
except Exception as e:
    print(f"Error: {e}")

print(f"State: {breaker.state.value}")
```

---

**Last updated:** 2026-05-22
