# Multi-tenancy Patterns

Design databases to serve multiple independent customers (tenants) efficiently with strong data isolation.

---

## ⚖️ Multi-tenancy Architecture Trade-offs

| Pattern | Isolation | Cost | Scalability | Risk |
|---------|-----------|------|---|---|
| **Shared DB** | Row-level | Low | Unlimited | Noisy neighbors |
| **Schema/DB** | Logical | Medium | Good | Many connections |
| **Container** | Physical | High | Limited | Over-provisioned |

---

## 🏗️ Multi-tenancy Patterns

### Pattern 1: Shared Database, Row-level Isolation

```
Single database, many tenants:
  
Table: users
  tenant_id | user_id | name
  1         | 100     | Alice (tenant 1)
  2         | 101     | Bob (tenant 2)
  1         | 102     | Carol (tenant 1)

Queries must include tenant_id:
  SELECT * FROM users WHERE tenant_id = 1

Risks:
  - Accidental data leak if tenant_id filter missing
  - Noisy neighbor (tenant 2 uses all CPU)
```

### Pattern 2: Schema per Tenant

```
Single database, separate schema per tenant:
  
database.tenant_1_schema.users
database.tenant_2_schema.users
database.tenant_3_schema.users

Benefits:
  - Logical isolation (can't leak between schemas)
  - Can backup/restore tenant independently
  
Risks:
  - Many schema connections
  - More complex deployment
```

### Pattern 3: Separate Database per Tenant

```
Separate database per tenant:

DB 1: users (tenant 1)
DB 2: users (tenant 2)
DB 3: users (tenant 3)

Benefits:
  - Complete isolation
  - Per-tenant backups
  - Tenant-specific optimization
  
Risks:
  - Operationally complex
  - Many connections to manage
  - Expensive (many DB instances)
```

---

## ❓ Interview Q&A

**Q1: Design multi-tenant system for 1000 customers**

A:
- Solution: Shared database with row-level isolation
  1. Add tenant_id column to all tables
  2. Index on (tenant_id, entity_id)
  3. Row-level security (RLS) in database
  4. App middleware verifies tenant_id
  
- Cost: $1K/month (1 database)
- Risk: Developer accidentally omits tenant_id filter
  - Mitigation: ORM enforces tenant_id, code review

**Q2: One tenant using 90% of CPU - solution?**

A:
- Problem: Noisy neighbor in shared database
- Solutions:
  1. Rate limiting per tenant
  2. Move heavy tenant to own database
  3. Query timeouts (prevent runaway queries)
  4. Resource quotas per tenant

---

**Last updated:** 2026-05-22
