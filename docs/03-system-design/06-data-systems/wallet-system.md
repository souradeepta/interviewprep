# Wallet System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A digital wallet allows users to store value and transfer it between accounts: topping up from
a bank account, paying merchants, and withdrawing back to a bank. Unlike a payment system that
routes charges to external PSPs, a wallet system manages an internal ledger: every dollar that
enters must equal every dollar that leaves (conservation of value). The core invariant — no wallet
goes negative, and no value is created or destroyed — must hold even during concurrent transfers
and system failures.

The design challenge is implementing atomic balance updates across multiple accounts, handling
distributed transfers without distributed locks, and maintaining an auditable ledger that can
reconstruct any account balance at any point in time from the transaction history alone.

## Functional Requirements

- Top up wallet from external payment source (bank, card)
- Transfer between two wallets (atomic: debit sender, credit receiver)
- Withdraw from wallet to bank account
- Query current balance
- View transaction history with pagination

## Non-Functional Requirements

- **Scale:** 100M wallets; 50K transfers/sec; 500K balance reads/sec
- **Latency:** P99 < 200 ms for transfers; P99 < 10 ms for balance reads
- **Availability:** 99.99%; wallet is financial infrastructure — downtime is unacceptable
- **Consistency:** Strong — balance must never go negative; no money created/destroyed;
  no dirty reads of in-progress transfers

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Wallets:          100M users * 1 wallet each
Balance row size: ~100 bytes (wallet_id + balance + version)
Total balance:    100M * 100 bytes = 10 GB → easily fits in DB buffer pool
Transactions/day: 50K/sec * 86400 sec = 4.3B transactions/day
Ledger row size:  ~200 bytes per ledger entry
Ledger/day:       4.3B * 2 entries/transfer (debit + credit) * 200 bytes = 1.7 TB/day
Ledger/year:      1.7 * 365 = 621 TB/year (retain 7 years = 4.3 PB total)
Balance reads:    500K/sec → primary-key lookup on wallets table → requires caching or replicas
Write throughput: 50K transfers/sec * 2 rows (debit + credit) = 100K rows/sec on ledger table
```

### Architecture Diagram

```
  User Action: "Transfer $50 from wallet_A to wallet_B"
        |
  POST /transfers { from: A, to: B, amount: 5000 }
        |
  +-----v-----------+
  | Wallet API      |  ← auth, input validation, idempotency check
  +-----+-----------+
        |
  +-----v-----------+
  | Transfer Service|
  |                 |
  | BEGIN TRANSACTION
  | 1. SELECT wallet_A FOR UPDATE  (lock)
  | 2. CHECK balance >= amount     (no overdraft)
  | 3. SELECT wallet_B FOR UPDATE  (lock)
  | 4. UPDATE wallet_A balance - amount
  | 5. UPDATE wallet_B balance + amount
  | 6. INSERT ledger (debit entry for A)
  | 7. INSERT ledger (credit entry for B)
  | COMMIT
  +-----+-----------+
        |
  +-----v-----------+       +------------------+
  | Wallets DB      |       | Ledger DB        |
  | (hot balances)  |       | (append-only,    |
  | Postgres w/     |       |  partitioned by  |
  | row locking     |       |  wallet + date)  |
  +-----------------+       +------------------+
        |
  +-----v-----------+
  | Balance Cache   |  ← Redis, invalidated on write
  | (Redis)         |
  +-----------------+

For cross-service transfers (distributed saga):
  Kafka → Transfer Orchestrator → Step 1: Debit A → Step 2: Credit B
          ↓ on failure: Compensating transaction (Credit A back)
```

### Data Model

```sql
-- Wallets table (hot, frequently read and updated)
CREATE TABLE wallets (
    wallet_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       BIGINT NOT NULL UNIQUE,
    balance_cents BIGINT NOT NULL DEFAULT 0 CHECK (balance_cents >= 0),
    currency      CHAR(3) NOT NULL DEFAULT 'USD',
    version       BIGINT NOT NULL DEFAULT 0,   -- optimistic lock version
    status        ENUM('active','frozen','closed') NOT NULL DEFAULT 'active',
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_user_id (user_id)
);

-- Ledger table (append-only, never updated or deleted)
CREATE TABLE ledger_entries (
    entry_id          BIGSERIAL,           -- monotonically increasing
    transfer_id       UUID NOT NULL,       -- groups debit + credit pair
    wallet_id         UUID NOT NULL,
    amount_cents      BIGINT NOT NULL,     -- positive = credit, negative = debit
    balance_after     BIGINT NOT NULL,     -- running balance snapshot
    entry_type        ENUM('TOPUP','TRANSFER_DEBIT','TRANSFER_CREDIT',
                           'WITHDRAWAL','FEE','REVERSAL') NOT NULL,
    reference_id      VARCHAR(256),        -- external reference (bank transfer ID)
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (entry_id, created_at),    -- composite for partitioning
    INDEX idx_wallet_created (wallet_id, created_at)
) PARTITION BY RANGE (created_at);
-- Monthly partitions: ledger_2024_01, ledger_2024_02, ...

-- Pending transfers (for saga pattern / distributed transfers)
CREATE TABLE pending_transfers (
    transfer_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_wallet   UUID NOT NULL,
    to_wallet     UUID NOT NULL,
    amount_cents  BIGINT NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    status        ENUM('INITIATED','DEBITED','COMPLETED','REVERSED','FAILED') NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at  TIMESTAMP,
    error_message TEXT
);
```

### API Design

```
# Get balance
GET /wallets/{wallet_id}/balance
  Response: 200 { wallet_id, balance_cents: 10000, currency: "USD", as_of: "..." }

# Top up wallet
POST /wallets/{wallet_id}/topup
  Headers: Idempotency-Key: <UUID>
  Body: { amount_cents: 10000, source: "bank_account", external_reference: "ACH_abc123" }
  Response: 201 { entry_id, new_balance_cents: 10000 }

# Transfer between wallets
POST /transfers
  Headers: Idempotency-Key: <UUID>
  Body: { from_wallet_id: "uuid-A", to_wallet_id: "uuid-B", amount_cents: 5000, note: "Rent" }
  Response: 201 {
    transfer_id: "uuid",
    status: "COMPLETED",
    from_balance_after: 5000,
    to_balance_after: 15000
  }

# Withdraw to bank
POST /wallets/{wallet_id}/withdraw
  Headers: Idempotency-Key: <UUID>
  Body: { amount_cents: 3000, bank_account_id: "bank_abc" }
  Response: 202 { withdrawal_id, status: "PENDING", estimated_arrival: "1-3 business days" }

# Transaction history
GET /wallets/{wallet_id}/transactions?limit=50&before=<entry_id>
  Response: 200 {
    entries: [{ entry_id, amount_cents, entry_type, balance_after, created_at }, ...],
    has_more: true,
    next_cursor: <entry_id>
  }
```

### Basic Scaling

- **Row locking:** `SELECT FOR UPDATE` on both wallets within a single DB transaction ensures
  atomic balance update; always lock in consistent order (lower wallet_id first) to prevent deadlock
- **Optimistic locking:** For lower-contention scenarios, use version column: `UPDATE wallets SET
  balance=X, version=version+1 WHERE wallet_id=? AND version=expected_version`; retry on mismatch
- **Balance cache:** Cache balance in Redis (TTL = 30s) for high-frequency reads; invalidate on
  every write; acceptable slight staleness for display purposes (transfers are always authoritative)
- **Ledger partitioning:** Partition ledger_entries by month; queries for recent transactions
  only scan the current partition; old partitions archived to cold storage

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Wallets DB (hot balances):
  100M rows * 100 bytes = 10 GB → fits in DB buffer pool (128 GB RAM node)
  50K transfers/sec * 2 updates/transfer = 100K row updates/sec → HEAVY write load
  Postgres with NVMe SSD: ~50K writes/sec sustainable per node
  Sharding needed: 100K/sec / 50K per node = 2 shards minimum → use 8 for headroom
  Shard key: wallet_id (hash) → same-shard transfers when both wallets on same shard

Ledger DB (append-only):
  100K rows/sec * 200 bytes = 20 MB/sec write throughput
  Single Postgres node (WAL-heavy, sequential write) handles 50 MB/sec easily
  Partition by month: query performance stable as table grows
  Archive: move partitions older than 2 years to S3 Parquet via pg_dump + S3 export

Cross-shard transfer (wallets on different shards):
  Frequency: if wallet_ids randomly distributed across 8 shards → 87.5% of transfers cross shards
  Approach: saga pattern (two-phase, no distributed lock)
  Phase 1: Debit from_wallet (local transaction on shard A)
  Phase 2: Credit to_wallet (local transaction on shard B)
  Compensation: if Phase 2 fails → reverse Phase 1 debit

Balance read cache (Redis):
  500K reads/sec * 100 bytes = 50 MB/sec → 3-node Redis cluster trivially handles
  Cache hit rate target: 90% (most read wallets are active, re-read frequently)
  Cache miss: DB read, ~1-5 ms → acceptable
```

### Failure Modes

```
FAILURE: DB node crash during transfer (mid-transaction)
  Postgres behavior: uncommitted transaction rolled back automatically on restart
  Client sees: 500 error or connection timeout → retry with same idempotency key
  Idempotency: transfer not in pending_transfers → treated as new attempt → safe to retry
  Data integrity: ACID guarantees; partial transfer impossible

FAILURE: Phase 1 succeeds (debit), Phase 2 fails (credit) — saga partial failure
  Detection: Transfer orchestrator detects Phase 2 failure (timeout or error)
  Compensation: POST /wallets/{from_wallet}/credit {amount, transfer_id} → reversal
  Reversal entry type: "REVERSAL" in ledger; balance restored
  Idempotency: reversal uses transfer_id as key → safe to retry reversal
  User experience: user sees pending → failed; balance restored within 30 sec

FAILURE: Overdraft race condition (two concurrent transfers exhaust balance simultaneously)
  Scenario: wallet has $100; two transfers of $80 submitted simultaneously
  Prevention: SELECT FOR UPDATE or CHECK (balance_cents >= 0) constraint
              DB rejects second transfer with check violation → returns "insufficient funds"
  With optimistic locking: one transfer fails version check → retry loop
  Result: at most one transfer succeeds; no negative balance

FAILURE: Balance cache inconsistency (Redis shows $100, DB has $80 after transfer)
  Window: 30s TTL on cache; user sees stale balance for up to 30 sec
  Mitigation: invalidate cache immediately on balance update (DELETE key after DB commit)
  Accept: race where cache is repopulated with stale value after invalidation
  Resolution: next cache miss reads from DB; short window of staleness acceptable for display
```

### Consistency Boundaries

```
DOUBLE-ENTRY BOOKKEEPING:
  Every transfer creates exactly 2 ledger entries: debit (negative) + credit (positive)
  Conservation law: SUM(amount_cents) across all ledger entries for all wallets = 0
  This invariant lets you detect bugs: if sum != 0, a bug created or destroyed money
  Nightly audit job: SELECT SUM(amount_cents) FROM ledger_entries → must equal 0

OPTIMISTIC vs SERIALIZABLE ISOLATION:
  Optimistic locking (version column):
    - Read wallet: {balance: 100, version: 5}
    - UPDATE wallets SET balance = 50, version = 6 WHERE wallet_id = ? AND version = 5
    - If 0 rows updated: concurrent write occurred → retry
    - Good for low contention (most wallets not simultaneously contested)
    
  SERIALIZABLE isolation (Postgres):
    - All transactions serializable → DB detects conflicts, aborts loser
    - Higher throughput than SELECT FOR UPDATE (no lock held during PSP call)
    - Good for high-concurrency, short transactions

DISTRIBUTED TRANSFER ATOMICITY (saga):
  NOT atomic in the traditional sense: at any moment, money can be "in flight"
  (deducted from sender, not yet credited to receiver)
  SLO: transfer completes or reverses within 30 seconds
  Audit: pending_transfers table shows all in-flight transfers for reconciliation
```

### Cost Model

```
Wallet DB (8 shards, each db.r6g.2xlarge RDS Multi-AZ):
  8 * $0.576/hr * 8760 = $40,373/yr

Ledger DB (1 large write node + 2 read replicas):
  3 * db.r6g.4xlarge ($1.152/hr): 3 * $1.152 * 8760 = $30,279/yr
  Ledger storage (RDS): 20 MB/sec * 86400 * 365 = 630 TB/yr
    Hot 2yr: 1.26 PB * $0.115/GB = $145K/yr (dominant cost!)
  S3 Glacier (cold): additional 5 years * 630 TB * $0.004/GB = $13K/yr

Redis balance cache: 3-node r6g.large: $4,073/yr
App servers: 20× c6g.xlarge ($0.136/hr): $23,827/yr

Total: ~$243K/yr for 100M wallets
Per wallet/month: $0.0002/wallet/month

Optimization: ledger compression
  Compress ledger entries (amounts are mostly small ints): Parquet columnar + Snappy
  After 30 days: move to S3 Parquet → 10× storage reduction → $14K/yr vs $145K/yr for cold
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Single DB atomic transaction (SELECT FOR UPDATE) | Simple; ACID; no saga complexity; easy to reason about | Doesn't scale cross-shard; lock contention under high concurrency | Same-database transfers, small-scale wallets (< 1M users) |
| Optimistic locking (version column) | No lock held; higher concurrency; lower deadlock risk | Retry logic needed; bad for high-contention wallets | Most wallet use cases; celebrity wallets need separate handling |
| Saga pattern (distributed) | Cross-service/cross-shard; no distributed lock; high availability | Complex compensating logic; money "in flight"; eventual consistency | Microservice architectures, multi-shard setups |
| Double-entry bookkeeping | Self-auditing; conservation invariant; detects bugs | More storage (2 rows per transfer); more complex queries | Financial systems, any system requiring audit trail and integrity |

## Follow-up Questions (escalating difficulty)

1. **(L3)** How do you prevent a wallet from going negative during concurrent transfers?
   → In a single DB transaction: `SELECT FOR UPDATE` locks the wallet row, check that balance
   >= amount before deducting. The lock prevents concurrent transactions from reading the
   (old) balance simultaneously. Alternatively, add a `CHECK (balance_cents >= 0)` DB constraint
   that rejects the update at the DB level as a last defense.

2. **(L3)** What is double-entry bookkeeping and why is it useful?
   → Every transfer creates two ledger entries: a debit (negative) on the sender and a credit
   (positive) on the receiver. The sum of all entries across all wallets must equal zero
   (money is conserved). This makes it easy to audit: if SUM != 0, a bug created or destroyed
   money. It also makes balance reconstruction from history trivial.

3. **(L4)** How do you prevent deadlocks when two transfers concurrently lock the same two wallets
   in opposite order?
   → Always acquire locks in a canonical order: by wallet_id ascending (lower ID first). Transfer
   A→B and concurrent B→A both lock the lower-ID wallet first. One succeeds; the other waits —
   no cycle → no deadlock. This is the standard "ordered locking" deadlock prevention technique.

4. **(L4)** How would you reconstruct a wallet balance from ledger history if the wallets table
   was corrupted?
   → `SELECT SUM(amount_cents) FROM ledger_entries WHERE wallet_id = ?`. The ledger is the source
   of truth; the wallets.balance_cents column is a materialized cache of the running sum. Nightly
   reconciliation job compares wallet.balance vs SUM(ledger) for each wallet — alerts on mismatch.

5. **(L5)** Describe the saga pattern for a cross-shard transfer. What happens if compensation
   also fails?
   → Steps: (1) Write pending_transfer record (status=INITIATED). (2) Debit sender shard
   (status=DEBITED). (3) Credit receiver shard (status=COMPLETED). If step 3 fails: post
   reversal (credit back to sender), status=REVERSED. If reversal also fails: status=FAILED,
   alert + manual review. The pending_transfers table always has the ground truth of where money
   is. A monitoring job finds any transfers stuck in DEBITED for > 30 sec and triggers compensation.

6. **(L5)** How do you handle a top-up that comes from an external bank transfer that might
   take 1-3 days to settle?
   → Two-phase: (1) Record pending_topup (status=PENDING) with external_reference (ACH trace ID).
   Do NOT credit wallet yet. (2) When bank settlement confirms (webhook or reconciliation):
   mark SETTLED, credit wallet in a DB transaction, insert ledger entry. User sees "pending top-up"
   in history. This prevents crediting a wallet for a bank transfer that ultimately bounces (NSF).

7. **(L5+)** How would you design the system to handle a "hot wallet" — a wallet that receives
   100K transfers per second (e.g., a merchant wallet)?
   → Single-row locking creates a serialization bottleneck at 100K TPS. Solutions:
   (1) Sharded wallet: split merchant wallet into N sub-wallets (wallet_0 to wallet_N);
   credit to a randomly chosen sub-wallet; balance = SUM of all sub-wallets. (2) Append-only
   credit: credits don't need to read current balance (only debits do); use insert-only approach
   for credits, aggregation for reads. (3) CRDT counter: credits are commutative → use
   distributed counter (like Redis INCRBY) with eventual consistency for balance reporting.

## Anti-patterns / Things NOT to Say

- **"Read balance, subtract in application code, write back"** — Read-modify-write without
  locking is a classic race condition: two concurrent reads see the same balance $100; both
  subtract $80; both write $20. User has $160 debited. Always use atomic DB operations
  (UPDATE + WHERE balance >= amount, or SELECT FOR UPDATE).
- **"Store balance only in Redis"** — Redis is not a transactional database. If Redis fails
  between crediting one wallet and debiting another, money is created. Use Redis only as a
  read cache; the DB is the source of truth.
- **"Use eventual consistency for balance updates"** — An "eventually consistent" balance can
  temporarily show more money than a user has, enabling fraudulent withdrawals. Balance updates
  must be strongly consistent within a transfer operation.
- **"Deleting ledger entries to save space"** — Ledger entries are the audit trail and the only
  way to reconstruct balances after corruption. They should be append-only forever (or archived
  to cold storage). Deleting them destroys the ability to investigate disputes.
- **"One global lock for all transfers"** — A global mutex serializes all 50K transfers/sec
  through a single chokepoint. Lock at the wallet level (individual rows), not globally.

## Python Implementation (sketch)

```python
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional
import threading

@dataclass
class Wallet:
    wallet_id: str
    user_id: int
    balance_cents: int = 0
    version: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

@dataclass
class LedgerEntry:
    entry_id: str
    transfer_id: str
    wallet_id: str
    amount_cents: int      # negative = debit, positive = credit
    balance_after: int
    entry_type: str

class WalletService:
    """In-memory wallet with optimistic locking and double-entry bookkeeping."""

    def __init__(self):
        self._wallets: dict[str, Wallet] = {}
        self._ledger: list[LedgerEntry] = []
        self._global_lock = threading.Lock()  # for demo only; use DB row locking in prod

    def create_wallet(self, user_id: int) -> Wallet:
        w = Wallet(wallet_id=str(uuid.uuid4()), user_id=user_id)
        self._wallets[w.wallet_id] = w
        return w

    def get_balance(self, wallet_id: str) -> int:
        return self._wallets[wallet_id].balance_cents

    def transfer(
        self, from_id: str, to_id: str, amount_cents: int, idempotency_key: str
    ) -> dict:
        if amount_cents <= 0:
            raise ValueError("Amount must be positive")

        # Always lock in canonical order (lower wallet_id first) to prevent deadlock
        first, second = sorted([from_id, to_id])
        w1, w2 = self._wallets[first], self._wallets[second]
        sender = self._wallets[from_id]
        receiver = self._wallets[to_id]

        transfer_id = str(uuid.uuid4())
        with w1._lock:
            with w2._lock:
                if sender.balance_cents < amount_cents:
                    raise ValueError(
                        f"Insufficient funds: {sender.balance_cents} < {amount_cents}"
                    )
                # Atomic update
                sender.balance_cents -= amount_cents
                sender.version += 1
                receiver.balance_cents += amount_cents
                receiver.version += 1

                # Double-entry bookkeeping
                self._ledger.append(LedgerEntry(
                    entry_id=str(uuid.uuid4()), transfer_id=transfer_id,
                    wallet_id=from_id, amount_cents=-amount_cents,
                    balance_after=sender.balance_cents, entry_type="TRANSFER_DEBIT"
                ))
                self._ledger.append(LedgerEntry(
                    entry_id=str(uuid.uuid4()), transfer_id=transfer_id,
                    wallet_id=to_id, amount_cents=amount_cents,
                    balance_after=receiver.balance_cents, entry_type="TRANSFER_CREDIT"
                ))

        return {"transfer_id": transfer_id, "from_balance": sender.balance_cents,
                "to_balance": receiver.balance_cents}

    def audit(self) -> bool:
        """Conservation check: sum of all ledger entries must equal 0."""
        total = sum(e.amount_cents for e in self._ledger)
        assert total == 0, f"Money conservation violated! Ledger sum = {total}"
        return True


# Usage
svc = WalletService()
alice = svc.create_wallet(user_id=1)
bob = svc.create_wallet(user_id=2)

# Top up Alice
alice.balance_cents = 10000
svc._ledger.append(LedgerEntry(
    str(uuid.uuid4()), str(uuid.uuid4()), alice.wallet_id, 10000, 10000, "TOPUP"
))
# Corresponding system debit (external source):
svc._ledger.append(LedgerEntry(
    str(uuid.uuid4()), svc._ledger[-1].transfer_id, "external_source", -10000, 0, "TOPUP"
))

result = svc.transfer(alice.wallet_id, bob.wallet_id, 3000, str(uuid.uuid4()))
print(f"Transfer: {result}")
print(f"Alice: {svc.get_balance(alice.wallet_id)}, Bob: {svc.get_balance(bob.wallet_id)}")
print(f"Audit: {svc.audit()}")
```
