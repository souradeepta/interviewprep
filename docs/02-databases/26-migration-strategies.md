# Database Migration Strategies

Execute major schema changes and data migrations safely with zero downtime.

---

## ⚖️ Migration Strategy Trade-offs

| Strategy | Downtime | Risk | Rollback | Best For |
|----------|----------|------|----------|----------|
| **Big Bang** | Yes | High | Hard | Small DBs |
| **Blue-Green** | Minimal | Low | Easy | Critical systems |
| **Canary** | None | Low | Easy | Large user base |
| **Shadow** | None | Low | Easy | Validation |

---

## 🏗️ Migration Patterns

### Expand-Contract Pattern

```
Phase 1: EXPAND
  - Add new column
  - Keep old column
  - App writes to both

Phase 2: MIGRATE
  - Background job: Copy old → new
  - Validate data

Phase 3: CONTRACT
  - Stop writing to old
  - Delete old column

Benefits:
  - Zero downtime
  - Can rollback at any phase
  - Validates new schema first
```

### Dual Write Pattern

```
Phase 1: Parallel writes
  - App writes to old DB AND new DB
  - Verify both have same data

Phase 2: Switch reads
  - Reads from new DB
  - Writes to both

Phase 3: Retire old
  - Stop writing to old
  - Delete old DB

Risk: Inconsistency between old/new
Solution: Periodic reconciliation
```

---

## ❓ Interview Q&A

**Q1: 1TB database, 0 downtime migration required**

A:
- Solution: Expand-contract
  1. Add new schema (1 hour)
  2. Background migration (8 hours)
  3. Validate (1 hour)
  4. Switch writes to new (5 minutes)
  5. Delete old (1 hour)
  
- Total downtime: 5 minutes (DNS failover time)

**Q2: Migration fails, how to rollback?**

A:
- Expand-Contract:
  - Keep old column/table
  - Revert app code
  - Switch back in < 5 minutes
  
- Blue-Green:
  - Both versions running
  - Switch DNS back
  - Instant rollback

---

**Last updated:** 2026-05-22
