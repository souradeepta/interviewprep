# Multi-Tenancy Patterns

Design databases to serve multiple independent customers (tenants) with strong data isolation, fair resource allocation, and efficient operations at scale.

---

## ⚖️ Multi-Tenancy Architecture Trade-offs

| Pattern | Isolation | Cost/Tenant | Scalability | Query Overhead | Best For |
|---------|-----------|-------------|-------------|----------------|---------|
| **Shared DB, shared schema** | Logical (RLS) | ~$0.01 | Unlimited | +1 WHERE clause | SaaS, 1K–100K tenants |
| **Shared DB, schema-per-tenant** | Logical | ~$0.10 | Good (~5K) | None | Mid-market SaaS |
| **Database-per-tenant** | Physical | ~$5–50 | Limited (~1K) | None | Enterprise, compliance |
| **Silo (instance-per-tenant)** | Total | ~$200+ | Very limited | None | Healthcare, finance |

### Cost Comparison (100 Tenants)

```
Pattern                Monthly Cost    Connections/DB    Isolation
────────────────────────────────────────────────────────────────────
Shared + RLS           $100            1 pool            Logical
Shared + Schemas       $100            1 per tenant      Logical
Database per Tenant    $5,000          1 per tenant      Physical
Silo                   $20,000+        Fully isolated    Total
```

### Isolation Hierarchy

```
Total Isolation     Network/OS boundary
      ▲             ┌──────────────────────────────┐
      │             │  Separate EC2 + RDS per tenant│
      │             └──────────────────────────────┘
      │             ┌──────────────────────────────┐
      │             │  Separate RDS database per   │
      │             │  tenant, shared EC2           │
      │             └──────────────────────────────┘
      │             ┌──────────────────────────────┐
      │             │  Schema per tenant, shared DB│
      │             └──────────────────────────────┘
Minimal isolation   ┌──────────────────────────────┐
                    │  RLS rows in shared tables   │
                    └──────────────────────────────┘
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Shared Schema with Row-Level Security (RLS)

```sql
-- Every table has a tenant_id column
CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    tenant_id   UUID NOT NULL,          -- Never nullable
    user_id     BIGINT NOT NULL,
    amount      NUMERIC(10,2),
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Composite index: tenant first (cardinality filter before sorting)
CREATE INDEX idx_orders_tenant_created ON orders (tenant_id, created_at DESC);

-- Row-Level Security enforced in DB (not app layer)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- App sets context before every query
SET app.tenant_id = '550e8400-e29b-41d4-a716-446655440000';
SELECT * FROM orders;  -- RLS automatically filters to this tenant
```

### Pattern 2: Schema-Per-Tenant Routing

```
Database: prod
  ├── schema: tenant_acme
  │     ├── orders
  │     ├── users
  │     └── products
  ├── schema: tenant_initech
  │     ├── orders
  │     ├── users
  │     └── products
  └── schema: public (shared metadata)
        ├── tenants (registry)
        └── billing
```

```python
class SchemaRouter:
    """Routes queries to the correct tenant schema."""

    def get_connection(self, tenant_slug: str):
        return f"SET search_path TO tenant_{tenant_slug}, public"

    def create_tenant_schema(self, tenant_slug: str):
        """Provision schema for new tenant."""
        return [
            f"CREATE SCHEMA tenant_{tenant_slug}",
            f"SET search_path TO tenant_{tenant_slug}",
            "CREATE TABLE orders (id BIGSERIAL PRIMARY KEY, ...)",
        ]
```

### Pattern 3: Noisy Neighbor Detection and Isolation

```
Shared DB with RLS:

Tenant A: 1,000 queries/min  ← Normal
Tenant B: 50,000 queries/min ← HOT (noisy neighbor)
Tenant C: 800 queries/min    ← Normal

Detection: Alert when any tenant > 5× median
Action: Move Tenant B to dedicated shard
```

---

## 📊 Tenant-Aware Implementation

```python
import threading
import time
from typing import Optional
from contextlib import contextmanager

# Thread-local storage for tenant context
_tenant_context = threading.local()

class TenantContext:
    """Thread-safe tenant identifier storage."""

    @staticmethod
    def set(tenant_id: str):
        _tenant_context.tenant_id = tenant_id

    @staticmethod
    def get() -> Optional[str]:
        return getattr(_tenant_context, "tenant_id", None)

    @staticmethod
    def clear():
        _tenant_context.tenant_id = None

    @staticmethod
    @contextmanager
    def scope(tenant_id: str):
        """Context manager for scoped tenant execution."""
        TenantContext.set(tenant_id)
        try:
            yield
        finally:
            TenantContext.clear()


class TenantAwareRepository:
    """All queries are automatically scoped to the current tenant."""

    def __init__(self, db):
        self.db = db

    def _require_tenant(self) -> str:
        tenant_id = TenantContext.get()
        if not tenant_id:
            raise ValueError("No tenant in context — possible data leak risk")
        return tenant_id

    def find_by_id(self, record_id: int) -> Optional[dict]:
        tenant_id = self._require_tenant()
        # In real DB: WHERE tenant_id = $1 AND id = $2
        return self.db.get(f"{tenant_id}:{record_id}")

    def create(self, data: dict) -> dict:
        tenant_id = self._require_tenant()
        record = {**data, "tenant_id": tenant_id, "id": id(data)}
        self.db[f"{tenant_id}:{record['id']}"] = record
        return record

    def list_all(self) -> list:
        tenant_id = self._require_tenant()
        return [v for k, v in self.db.items() if k.startswith(f"{tenant_id}:")]


# Demo
shared_db = {}
repo = TenantAwareRepository(shared_db)

# Tenant A session
with TenantContext.scope("tenant_acme"):
    order = repo.create({"amount": 100.00, "product": "Widget"})
    print("Tenant ACME orders:", repo.list_all())

# Tenant B session (isolated)
with TenantContext.scope("tenant_initech"):
    repo.create({"amount": 250.00, "product": "Gadget"})
    print("Tenant INITECH orders:", repo.list_all())

# Cross-tenant reads impossible
with TenantContext.scope("tenant_acme"):
    print("ACME sees:", len(repo.list_all()), "orders")  # Only ACME's orders
```

---

## 🔒 Row-Level Security (PostgreSQL)

```sql
-- Step 1: Create application role (never superuser)
CREATE ROLE app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Step 2: Enable RLS on sensitive tables
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE users  ENABLE ROW LEVEL SECURITY;

-- Step 3: Create policies (using session variable set by app)
CREATE POLICY orders_tenant_policy ON orders
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant', true)::UUID)
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true)::UUID);

-- Step 4: Application sets tenant before every transaction
-- In connection pool middleware:
-- SET LOCAL app.current_tenant = '{{tenant_uuid}}';

-- Step 5: Verify isolation (run as app_user)
SET app.current_tenant = '550e8400-e29b-41d4-a716-446655440000';
SELECT COUNT(*) FROM orders;  -- Returns only this tenant's rows
RESET app.current_tenant;
SELECT COUNT(*) FROM orders;  -- ERROR or 0 rows (null tenant rejects all)

-- Admin override (bypass RLS for reporting)
SET role = postgres;  -- superuser bypasses RLS
SELECT tenant_id, COUNT(*) FROM orders GROUP BY 1;

-- Cross-tenant analytics view
CREATE VIEW tenant_usage AS
    SELECT tenant_id, COUNT(*) AS order_count, SUM(amount) AS revenue
    FROM orders
    GROUP BY tenant_id;
-- Grant only to reporting role, not app_user
GRANT SELECT ON tenant_usage TO reporting_role;
```

---

## 🛡️ Noisy Neighbor Mitigation

```python
import time
from collections import defaultdict, deque

class TenantRateLimiter:
    """
    Token bucket per tenant. Prevents one tenant from consuming
    all query capacity in a shared database.
    """

    def __init__(self, queries_per_minute: int = 10000):
        self.qpm_limit = queries_per_minute
        self._buckets: dict = defaultdict(lambda: {
            "tokens": queries_per_minute,
            "last_refill": time.time(),
        })
        self._usage: dict = defaultdict(lambda: deque(maxlen=1000))

    def _refill(self, tenant_id: str):
        bucket = self._buckets[tenant_id]
        now = time.time()
        elapsed = now - bucket["last_refill"]
        refill = int(elapsed * self.qpm_limit / 60)
        bucket["tokens"] = min(self.qpm_limit, bucket["tokens"] + refill)
        bucket["last_refill"] = now

    def allow(self, tenant_id: str, cost: int = 1) -> bool:
        self._refill(tenant_id)
        bucket = self._buckets[tenant_id]
        if bucket["tokens"] >= cost:
            bucket["tokens"] -= cost
            self._usage[tenant_id].append(time.time())
            return True
        return False

    def current_qps(self, tenant_id: str) -> float:
        window = [t for t in self._usage[tenant_id] if time.time() - t < 1]
        return len(window)

    def get_stats(self) -> dict:
        return {
            tid: {
                "tokens_remaining": b["tokens"],
                "qps": self.current_qps(tid),
            }
            for tid, b in self._buckets.items()
        }


limiter = TenantRateLimiter(queries_per_minute=600)  # 10 QPS per tenant

for i in range(15):
    tenant = "tenant_a" if i < 12 else "tenant_b"
    allowed = limiter.allow(tenant, cost=1)
    if not allowed:
        print(f"[{tenant}] Rate limited at request {i}")

print(limiter.get_stats())
```

---

## ❓ Interview Q&A

**Q1: Design a multi-tenant system for 10,000 customers. Which pattern?**

A: Shared DB with Row-Level Security. Reasoning:
- 10,000 tenants × dedicated DB = $500K/month — unviable
- Schema-per-tenant = 10,000 schemas × 10 tables = 100,000 tables — Postgres max ~10,000 before degradation
- RLS: 1 DB, $2K/month, automatic isolation, no app logic change
- Add composite index `(tenant_id, sort_key)` on every table — first column eliminates 99.99% of rows immediately
- Migration strategy: for 50+ "enterprise" tenants with SLAs, provision dedicated schemas or DBs

**Q2: One tenant is using 90% of CPU. How do you handle it?**

A: Four escalating responses:
1. **Identify** — `SELECT tenant_id, count(*), avg(duration) FROM pg_stat_activity GROUP BY 1` — find the tenant
2. **Rate limit** — apply query-per-minute cap for that tenant via connection pooler (PgBouncer config)
3. **Kill** — `SELECT pg_cancel_backend(pid)` for their slow queries (graceful) or `pg_terminate_backend` (forceful)
4. **Move** — migrate that tenant to a dedicated DB/read replica; update tenant registry; redirect connection string

**Q3: How do you enforce tenant isolation at the application layer (defense in depth)?**

A: Three layers:
1. **DB layer**: RLS with `SET app.current_tenant` — even if app bug leaks, DB rejects cross-tenant reads
2. **ORM/repository layer**: `TenantAwareRepository` wraps all queries, enforces tenant ID from thread-local context
3. **Middleware layer**: Extract tenant from JWT/subdomain at request ingress, set thread-local, validate at every layer; block requests with missing or mismatched tenant

**Q4: Tenant needs their data completely deleted (GDPR right to erasure). How?**

A: Depends on isolation model:
- **Shared schema**: `DELETE FROM ... WHERE tenant_id = $1` across all tables (need dependency order); then zero-fill deleted rows from WAL (vacuum)
- **Schema-per-tenant**: `DROP SCHEMA tenant_X CASCADE` — single command, cascades all tables, very fast
- **DB-per-tenant**: Terminate connections, drop database, delete backups; update tenant registry
- In all cases: maintain deletion log (audit trail that deletion occurred), redact from backups (schedule backup expiry)

**Q5: How do you handle schema migrations for 10,000 tenant schemas?**

A: Two approaches:
- **Shared schema (RLS)**: One migration, zero orchestration — `ALTER TABLE orders ADD COLUMN ...` affects all tenants instantly
- **Per-schema**: Use a migration orchestrator that runs the same Alembic/Flyway migration in each schema sequentially or in parallel (50 at a time); log progress; resume on failure; estimated time: 10,000 schemas × 2s/migration = ~5.5 hours sequentially, ~12 minutes at 50-parallel

---

## 🧪 Practical Exercises

### Exercise 1: Tenant Registry with Routing (Easy)

**Problem:** Build a registry that maps tenant slugs to their DB connection string.

```python
import hashlib

class TenantRegistry:
    """Manages tenant metadata and routes to correct DB shard."""

    SHARDS = [
        "postgresql://shard1.internal/prod",
        "postgresql://shard2.internal/prod",
        "postgresql://shard3.internal/prod",
    ]

    def __init__(self):
        self._tenants: dict = {}

    def register(self, slug: str, plan: str = "shared") -> dict:
        tenant = {
            "slug": slug,
            "plan": plan,
            "db_dsn": self._assign_dsn(slug, plan),
            "schema": f"tenant_{slug}" if plan in ("pro", "enterprise") else "public",
        }
        self._tenants[slug] = tenant
        return tenant

    def _assign_dsn(self, slug: str, plan: str) -> str:
        if plan == "enterprise":
            return f"postgresql://dedicated-{slug}.internal/prod"
        # Hash-based shard assignment (stable)
        shard_idx = int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(self.SHARDS)
        return self.SHARDS[shard_idx]

    def get(self, slug: str) -> dict:
        if slug not in self._tenants:
            raise KeyError(f"Unknown tenant: {slug}")
        return self._tenants[slug]

registry = TenantRegistry()
acme = registry.register("acme", plan="pro")
initech = registry.register("initech", plan="shared")
megacorp = registry.register("megacorp", plan="enterprise")

for t in [acme, initech, megacorp]:
    print(f"{t['slug']}: {t['db_dsn']}, schema={t['schema']}")
```

---

### Exercise 2: Tenant Quota Enforcement (Medium)

**Problem:** Enforce per-tenant storage and row count quotas.

```python
class TenantQuotaEnforcer:
    """Tracks per-tenant usage and blocks quota violations."""

    DEFAULT_QUOTAS = {
        "shared":     {"rows": 100_000,   "storage_mb": 500},
        "pro":        {"rows": 1_000_000, "storage_mb": 5000},
        "enterprise": {"rows": 999_999_999, "storage_mb": 999_999},
    }

    def __init__(self):
        self._usage: dict = {}
        self._quotas: dict = {}

    def set_quota(self, tenant_id: str, plan: str):
        self._quotas[tenant_id] = dict(self.DEFAULT_QUOTAS[plan])
        self._usage[tenant_id] = {"rows": 0, "storage_mb": 0.0}

    def check_row_insert(self, tenant_id: str, row_count: int = 1) -> bool:
        usage = self._usage.get(tenant_id, {"rows": 0})
        quota = self._quotas.get(tenant_id, {"rows": 0})
        if usage["rows"] + row_count > quota["rows"]:
            raise PermissionError(
                f"Tenant {tenant_id} row quota exceeded: "
                f"{usage['rows']}/{quota['rows']}"
            )
        self._usage[tenant_id]["rows"] += row_count
        return True

    def current_usage(self, tenant_id: str) -> dict:
        usage = self._usage.get(tenant_id, {})
        quota = self._quotas.get(tenant_id, {})
        return {k: {"used": usage.get(k, 0), "limit": quota.get(k, 0)} for k in quota}


enforcer = TenantQuotaEnforcer()
enforcer.set_quota("acme", "shared")   # 100K row limit
enforcer.check_row_insert("acme", 500)
print(enforcer.current_usage("acme"))

try:
    enforcer.check_row_insert("acme", 200_000)  # Over limit
except PermissionError as e:
    print(f"Blocked: {e}")
```

---

### Exercise 3: Tenant Data Export (Hard)

**Problem:** Export all data for a specific tenant on GDPR request (complete and consistent).

```python
import json, time

class TenantDataExporter:
    """
    Exports all data for a tenant as a consistent snapshot.
    Uses a logical snapshot_time to avoid reading partial writes.
    """

    def __init__(self, db: dict):
        self.db = db  # Simulated DB: {table: [{tenant_id, ...}, ...]}

    def export(self, tenant_id: str) -> dict:
        snapshot_time = time.time()
        export = {
            "tenant_id": tenant_id,
            "exported_at": snapshot_time,
            "tables": {},
        }

        for table_name, rows in self.db.items():
            tenant_rows = [
                r for r in rows
                if r.get("tenant_id") == tenant_id
                and r.get("created_at", 0) <= snapshot_time
            ]
            export["tables"][table_name] = tenant_rows

        export["row_counts"] = {t: len(rows) for t, rows in export["tables"].items()}
        return export

    def delete_tenant(self, tenant_id: str) -> dict:
        """Permanently delete all tenant data. Returns deletion receipt."""
        counts = {}
        for table_name in list(self.db.keys()):
            before = len(self.db[table_name])
            self.db[table_name] = [r for r in self.db[table_name] if r.get("tenant_id") != tenant_id]
            counts[table_name] = before - len(self.db[table_name])
        return {"tenant_id": tenant_id, "deleted_rows": counts, "deleted_at": time.time()}


# Setup
db = {
    "orders": [
        {"tenant_id": "acme", "id": 1, "amount": 100, "created_at": time.time() - 100},
        {"tenant_id": "initech", "id": 2, "amount": 200, "created_at": time.time() - 50},
        {"tenant_id": "acme", "id": 3, "amount": 300, "created_at": time.time() - 10},
    ],
    "users": [
        {"tenant_id": "acme", "id": 10, "email": "alice@acme.com", "created_at": time.time() - 200},
        {"tenant_id": "initech", "id": 11, "email": "bob@initech.com", "created_at": time.time() - 150},
    ],
}

exporter = TenantDataExporter(db)
export = exporter.export("acme")
print(f"Export: {json.dumps(export['row_counts'])}")

receipt = exporter.delete_tenant("acme")
print(f"Deletion receipt: {receipt['deleted_rows']}")
print(f"Orders remaining: {len(db['orders'])}")  # Only initech's orders
