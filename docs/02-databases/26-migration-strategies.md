# Database Migration Strategies

Execute major schema changes and data migrations safely with zero downtime, full rollback capability, and consistent validation at every phase.

---

## ⚖️ Migration Strategy Trade-offs

| Strategy | Downtime | Risk | Rollback Speed | DB Complexity | Best For |
|----------|----------|------|----------------|---------------|---------|
| **Big Bang** | Hours | Very High | Hard | Low | Tiny dev databases |
| **Expand-Contract** | ~0 | Low | <5 min | Medium | Column/schema changes |
| **Dual Write** | ~0 | Medium | <5 min | High | DB-to-DB platform migration |
| **Blue-Green** | ~0 | Low | Instant | High | Full stack cutover |
| **Canary** | ~0 | Very Low | Per-tenant | Very High | Large, risk-averse migrations |
| **Shadow** | ~0 | Very Low | N/A | Very High | Validation without switching |

### Timeline Comparison (1 TB table)

```
Strategy         Duration     Downtime    Rollback
──────────────────────────────────────────────────
Big Bang         8h total     8h          Restore backup
Expand-Contract  12h total    0           Instant
Dual Write       24h total    0           Stop dual writes
Blue-Green       16h total    <1 min      DNS flip
Canary           48h total    0           Roll back batch
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Expand-Contract (Column Rename / Schema Change)

```
Timeline:

 T+0h  ┌──────────────────────────────────────────────────────────────┐
       │ EXPAND: Add new column, keep old. App writes both.           │
       │   ALTER TABLE users ADD COLUMN email_new TEXT;               │
       │   App: INSERT INTO users (email, email_new) VALUES ($1, $1); │
       └──────────────────────────────────────────────────────────────┘
 T+2h  ┌──────────────────────────────────────────────────────────────┐
       │ MIGRATE: Backfill old → new for existing rows.               │
       │   UPDATE users SET email_new = email WHERE email_new IS NULL; │
       │   (batch, 1K rows/sec, avoids lock contention)               │
       └──────────────────────────────────────────────────────────────┘
 T+10h ┌──────────────────────────────────────────────────────────────┐
       │ VALIDATE: Ensure 100% rows backfilled, checksums match.      │
       │   SELECT COUNT(*) FROM users WHERE email_new IS NULL; → 0    │
       └──────────────────────────────────────────────────────────────┘
 T+11h ┌──────────────────────────────────────────────────────────────┐
       │ CONTRACT: App reads/writes new column only.                  │
       │   Deploy app v2 (uses email_new).                            │
       │   Wait 1 deployment cycle (canary), then drop old column.    │
       │   ALTER TABLE users DROP COLUMN email;                       │
       └──────────────────────────────────────────────────────────────┘
```

### Pattern 2: Dual-Write (Platform Migration)

```
Phase 1 — Dual Write
  ┌──────────────┐    Write     ┌─────────────┐
  │  Application │ ──────────► │ Old DB      │ (primary reads)
  │              │ ──────────► │ New DB      │ (background validation)
  └──────────────┘             └─────────────┘

Phase 2 — Shift Reads
  ┌──────────────┐    Write     ┌─────────────┐
  │  Application │ ──────────► │ Old DB      │
  │              │ ──────────► │ New DB      │ ← reads move here 10% → 100%
  └──────────────┘             └─────────────┘

Phase 3 — Retire Old
  ┌──────────────┐    Write     ┌─────────────┐
  │  Application │ ──────────► │ New DB      │ (only)
  └──────────────┘             └─────────────┘
  Old DB shut down after 30 days of silence.
```

### Pattern 3: Blue-Green Cutover

```
                  Load Balancer
                       │
              ┌────────┴────────┐
     Traffic  │                 │
              ▼                 ▼
        [Blue Env]         [Green Env]    ← syncs from Blue via CDC
        (old schema)       (new schema)
        
  1. Green catches up to Blue (replication lag < 1s)
  2. Make Blue read-only (stop new writes)
  3. Wait for Green to drain lag → 0 rows behind
  4. Flip DNS/LB to Green (< 30s)
  5. Blue becomes standby for 24h, then retire
```

---

## 📊 Migration Executor

```python
import time
import logging
from dataclasses import dataclass
from typing import Callable, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class MigrationPhase(Enum):
    NOT_STARTED = "not_started"
    EXPAND = "expand"
    BACKFILL = "backfill"
    VALIDATE = "validate"
    CONTRACT = "contract"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class MigrationState:
    phase: MigrationPhase = MigrationPhase.NOT_STARTED
    rows_total: int = 0
    rows_migrated: int = 0
    errors: list = None

    def __post_init__(self):
        self.errors = self.errors or []

    @property
    def progress_pct(self) -> float:
        if self.rows_total == 0:
            return 0.0
        return round(100 * self.rows_migrated / self.rows_total, 1)


class ExpandContractMigration:
    """
    Generic expand-contract executor.
    Caller provides callables for each phase.
    """

    def __init__(
        self,
        name: str,
        expand_fn: Callable,
        backfill_fn: Callable,
        validate_fn: Callable[[], bool],
        contract_fn: Callable,
        batch_size: int = 1000,
        dry_run: bool = False,
    ):
        self.name = name
        self.expand_fn = expand_fn
        self.backfill_fn = backfill_fn
        self.validate_fn = validate_fn
        self.contract_fn = contract_fn
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.state = MigrationState()

    def run(self) -> MigrationState:
        logger.info(f"[{self.name}] Starting migration (dry_run={self.dry_run})")

        try:
            self._run_phase(MigrationPhase.EXPAND, self.expand_fn)
            self._run_phase(MigrationPhase.BACKFILL, self.backfill_fn)

            self.state.phase = MigrationPhase.VALIDATE
            logger.info(f"[{self.name}] Validating...")
            if not self.validate_fn():
                raise ValueError("Validation failed — migration aborted before contract phase")

            self._run_phase(MigrationPhase.CONTRACT, self.contract_fn)
            self.state.phase = MigrationPhase.COMPLETE
            logger.info(f"[{self.name}] Migration COMPLETE ✓")

        except Exception as e:
            self.state.phase = MigrationPhase.FAILED
            self.state.errors.append(str(e))
            logger.error(f"[{self.name}] FAILED at {self.state.phase}: {e}")
            raise

        return self.state

    def _run_phase(self, phase: MigrationPhase, fn: Callable):
        self.state.phase = phase
        logger.info(f"[{self.name}] Phase: {phase.value}")
        if not self.dry_run:
            fn()


# Demo with simulated DB calls

class FakeDB:
    """Simulates a DB with an old 'email' column being renamed to 'email_address'."""
    def __init__(self):
        self.users = [{"id": i, "email": f"user{i}@example.com", "email_address": None}
                      for i in range(1, 10001)]
        self.has_new_column = False

    def add_column(self):
        self.has_new_column = True
        logger.info("Added column email_address")

    def backfill(self):
        count = 0
        for user in self.users:
            if user["email_address"] is None:
                user["email_address"] = user["email"]
                count += 1
        logger.info(f"Backfilled {count} rows")

    def validate(self) -> bool:
        nulls = sum(1 for u in self.users if u["email_address"] is None)
        logger.info(f"Validation: {nulls} rows with NULL email_address")
        return nulls == 0

    def drop_old_column(self):
        for user in self.users:
            del user["email"]
        logger.info("Dropped column email")


logging.basicConfig(level=logging.INFO, format="%(message)s")
db = FakeDB()

migration = ExpandContractMigration(
    name="rename-email-column",
    expand_fn=db.add_column,
    backfill_fn=db.backfill,
    validate_fn=db.validate,
    contract_fn=db.drop_old_column,
)

state = migration.run()
print(f"Final state: {state.phase.value}, errors: {state.errors}")
print(f"Sample user: {db.users[0]}")
```

---

## 🔧 Feature Flag-Gated Migration

```python
class FeatureFlagMigration:
    """
    Use feature flags to control which users get new schema.
    Enables gradual rollout and instant rollback.
    """

    def __init__(self):
        self.flag_enabled_pct = 0   # 0–100
        self.old_db = {}
        self.new_db = {}

    def set_rollout(self, pct: int):
        """Set % of users using new schema."""
        self.flag_enabled_pct = pct
        print(f"Rollout: {pct}% of users on new schema")

    def write(self, user_id: int, data: dict):
        """Dual-write: always write both, control reads by flag."""
        self.old_db[user_id] = data
        self.new_db[user_id] = {**data, "migrated": True}

    def read(self, user_id: int) -> dict:
        """Reads come from new DB for flag-enabled users."""
        use_new = (user_id % 100) < self.flag_enabled_pct
        source = self.new_db if use_new else self.old_db
        result = source.get(user_id, {})
        result["_source"] = "new_db" if use_new else "old_db"
        return result

# Gradual rollout
fm = FeatureFlagMigration()
for uid in range(1, 11):
    fm.write(uid, {"name": f"User {uid}", "email": f"user{uid}@example.com"})

fm.set_rollout(10)   # 10% on new DB
print(fm.read(5))    # user 5 → 5 % 100 = 5 < 10 → new_db
print(fm.read(15))   # user 15 → 15 % 100 = 15 ≥ 10 → old_db

fm.set_rollout(100)  # Full cutover
print(fm.read(15))   # now new_db
```

---

## ❓ Interview Q&A

**Q1: 1 TB table, 0 downtime required. Walk me through your migration plan.**

A: Use expand-contract over 12–16 hours:
1. **Expand** (30 min): `ALTER TABLE users ADD COLUMN email_new TEXT` — Postgres adds column instantly (no table rewrite for nullable columns)
2. **Dual write** (deploy app v1.5): writes to both `email` and `email_new`; reads still from `email`
3. **Backfill** (8h): `UPDATE users SET email_new = email WHERE email_new IS NULL` in batches of 1,000 rows with `pg_sleep(10ms)` between batches to avoid I/O saturation
4. **Validate** (1h): `SELECT COUNT(*) FROM users WHERE email_new IS NULL` = 0; spot-check 1,000 random rows
5. **Contract** (1h): deploy app v2 (reads `email_new`), wait 1 hour, then `ALTER TABLE users DROP COLUMN email`

Total downtime: **0**. Rollback at any step: revert app code, data stays intact.

**Q2: Your backfill job is running 10× slower than expected. What do you check?**

A: Four bottlenecks in priority order:
1. **Lock contention** — large batch sizes take row locks; reduce to 500 rows, add `LIMIT` and sleep between batches
2. **Index writes** — each UPDATE touches all indexes on the table; check `pg_stat_user_indexes` for hot indexes
3. **WAL generation** — bulk updates generate huge WAL; monitor `pg_wal_lsn_diff` and disk throughput
4. **Autovacuum conflicts** — UPDATE creates dead rows; ensure autovacuum is not blocked (`pg_stat_user_tables.n_dead_tup`)

**Q3: How do you handle a migration that touches a foreign key relationship?**

A: In dependency order:
1. Expand parent table first (add new column)
2. Backfill parent
3. Expand child table (add FK column, set `NOT VALID` constraint to defer validation)
4. Backfill child
5. Validate FK with `VALIDATE CONSTRAINT` (table scan but no lock)
6. Contract parent, then child

`NOT VALID` avoids a full-table scan lock when adding FK to large child tables.

**Q4: How do you validate that a dual-write migration is consistent?**

A: Three validation levels:
1. **Row count**: `SELECT COUNT(*) FROM old_table` = `SELECT COUNT(*) FROM new_table`
2. **Checksum sampling**: SHA-256 of 10,000 random rows' primary data must match
3. **Canary reads**: 1% of production reads check both databases; alert if `new_result != old_result`

Run validation hourly during dual-write phase. Investigate any discrepancy before proceeding.

**Q5: Your migration is halfway done and you find a bug in the transformation logic. What now?**

A: Don't panic — expand-contract was designed for this:
1. **Stop backfill job** immediately
2. **Don't contract** — old column is still intact
3. **Fix transformation logic** in code
4. **Truncate new column** (`UPDATE SET email_new = NULL WHERE migrated_at < now()`) to restart clean
5. **Re-run backfill** from scratch with corrected logic
6. Validate thoroughly before proceeding to contract phase

The "never drop the old column before validation" rule is why expand-contract is safe.

---

## 🧪 Practical Exercises

### Exercise 1: Batch Backfill with Rate Limiting (Easy)

**Problem:** Backfill 10M rows without killing the database.

```python
import time

def backfill_batched(
    table: list,
    transform_fn,
    batch_size: int = 1000,
    sleep_ms: float = 10.0,
) -> dict:
    """
    Backfill in small batches with sleep between.
    Returns metrics: rows_processed, duration, rows/sec.
    """
    start = time.time()
    processed = 0
    errors = 0

    # Find rows that need backfill
    pending = [row for row in table if row.get("email_new") is None]
    total = len(pending)

    for i in range(0, total, batch_size):
        batch = pending[i:i + batch_size]
        for row in batch:
            try:
                row["email_new"] = transform_fn(row["email"])
                processed += 1
            except Exception as e:
                errors += 1

        time.sleep(sleep_ms / 1000)  # yield to other DB operations

        if i % (batch_size * 10) == 0:
            pct = round(100 * processed / max(total, 1), 1)
            print(f"  Progress: {pct}% ({processed}/{total})")

    elapsed = time.time() - start
    return {
        "rows_processed": processed,
        "errors": errors,
        "duration_sec": round(elapsed, 2),
        "rows_per_sec": round(processed / max(elapsed, 0.001)),
    }

# Setup
users = [{"id": i, "email": f"u{i}@example.com", "email_new": None} for i in range(10000)]
metrics = backfill_batched(users, transform_fn=str.lower, batch_size=500, sleep_ms=5)
print(metrics)
```

---

### Exercise 2: Migration State Machine with Rollback (Medium)

**Problem:** Build a migration runner that tracks phase state to a durable log (so it can resume after restart).

```python
import json, os, time

class DurableMigrationRunner:
    """
    Tracks migration phase in a JSON file so it survives crashes.
    On restart, resumes from last completed phase.
    """

    PHASES = ["expand", "backfill", "validate", "contract"]

    def __init__(self, name: str, state_file: str):
        self.name = name
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                return json.load(f)
        return {"phase": "not_started", "completed": [], "errors": []}

    def _save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def run_phase(self, phase: str, fn) -> bool:
        if phase in self.state["completed"]:
            print(f"[{self.name}] Skipping {phase} (already done)")
            return True

        print(f"[{self.name}] Running {phase}...")
        self.state["phase"] = phase
        self._save_state()

        try:
            fn()
            self.state["completed"].append(phase)
            self._save_state()
            print(f"[{self.name}] {phase} ✓")
            return True
        except Exception as e:
            self.state["errors"].append({"phase": phase, "error": str(e)})
            self._save_state()
            print(f"[{self.name}] {phase} FAILED: {e}")
            return False

    def rollback(self):
        print(f"[{self.name}] Rolling back...")
        # Reset completed phases (keep errors)
        self.state["completed"] = []
        self.state["phase"] = "rolled_back"
        self._save_state()


# Demo
runner = DurableMigrationRunner(
    name="add-email-index",
    state_file="/tmp/migration_state.json",
)

runner.run_phase("expand", lambda: print("  CREATE INDEX CONCURRENTLY..."))
runner.run_phase("backfill", lambda: print("  UPDATE users SET..."))
runner.run_phase("validate", lambda: print("  SELECT COUNT(*)..."))
runner.run_phase("contract", lambda: print("  DROP COLUMN old_email..."))

print("Final state:", runner.state)
os.remove("/tmp/migration_state.json")
```

---

### Exercise 3: Blue-Green Cutover Simulator (Hard)

**Problem:** Simulate blue-green DB migration with lag monitoring and instant rollback.

```python
import threading, time, random

class DBNode:
    def __init__(self, name: str, initial_lsn: int = 0):
        self.name = name
        self.lsn = initial_lsn       # Log Sequence Number (replication position)
        self.data: dict = {}
        self.read_only = False

    def write(self, key, value):
        if self.read_only:
            raise RuntimeError(f"{self.name} is read-only")
        self.data[key] = value
        self.lsn += 1

    def read(self, key):
        return self.data.get(key)


class BlueGreenMigration:
    def __init__(self, blue: DBNode, green: DBNode):
        self.blue = blue
        self.green = green
        self._active = blue
        self._replication_lag = 0
        self._syncing = True

        # Simulate replication from blue to green
        thread = threading.Thread(target=self._replicate, daemon=True)
        thread.start()

    def _replicate(self):
        """Green lags behind blue by 0-500ms."""
        while self._syncing:
            lag = random.uniform(0, 0.5)
            time.sleep(lag)
            self._replication_lag = self.blue.lsn - self.green.lsn
            # Apply blue's data to green
            self.green.data = dict(self.blue.data)
            self.green.lsn = self.blue.lsn

    def lag_seconds(self) -> float:
        return self._replication_lag * 0.01   # synthetic: lsn diff → seconds

    def cutover(self, max_lag_sec: float = 0.1):
        """Switch traffic to green. Abort if lag too high."""
        lag = self.lag_seconds()
        print(f"Replication lag: {lag:.3f}s (max allowed: {max_lag_sec}s)")

        if lag > max_lag_sec:
            raise RuntimeError(f"Cutover aborted: lag {lag:.3f}s exceeds {max_lag_sec}s")

        self.blue.read_only = True       # Freeze blue
        time.sleep(0.05)                 # Final sync window
        self._active = self.green
        print(f"✅ Cutover complete → now serving from {self.green.name}")

    def rollback(self):
        """Instant: flip traffic back to blue."""
        self.blue.read_only = False
        self._active = self.blue
        print(f"🔄 Rolled back → now serving from {self.blue.name}")

    def write(self, key, value):
        self._active.write(key, value)

    def read(self, key):
        return self._active.read(key)


# Demo
blue = DBNode("blue-v1", initial_lsn=500)
green = DBNode("green-v2", initial_lsn=0)

migration = BlueGreenMigration(blue, green)

# Write traffic hits blue
migration.write("user:1", "Alice")
migration.write("user:2", "Bob")
time.sleep(0.6)   # Let replication catch up

# Attempt cutover
try:
    migration.cutover(max_lag_sec=0.5)
    print("Post-cutover read:", migration.read("user:1"))
except RuntimeError as e:
    print(f"Cutover failed: {e}")
    migration.rollback()
```

---

**Last updated:** 2026-05-22
