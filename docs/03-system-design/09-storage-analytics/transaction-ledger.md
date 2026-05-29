# Transaction Ledger

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Financial systems, digital wallets, and payment platforms require an immutable, auditable record of every monetary movement. Unlike a simple balance column that is updated in-place, a ledger records every debit and credit as an append-only entry. The balance at any point in time is the sum of all prior entries — an approach called double-entry bookkeeping used by banks for centuries.

The design must guarantee that money is never created or destroyed (every debit has a matching credit), the ledger is tamper-evident (unauthorized changes are detectable), and the system meets regulatory requirements for 7-year retention and audit trail completeness.

## Functional Requirements

- Record every monetary transaction as a debit/credit pair (double-entry bookkeeping)
- Calculate account balance at any point in time (current or historical)
- Support multi-currency accounts with explicit FX rate recording at transaction time
- Export transaction history for tax/audit purposes with cryptographic proof of integrity
- Enforce that debits cannot exceed available balance (no negative balances unless overdraft is explicitly enabled)
- Retain all records for 7 years (regulatory requirement)

## Non-Functional Requirements

- **Scale:** 10M transactions/day = 116 TPS average; 1,000 TPS peak
- **Latency:** Write P99 < 100ms; balance read P99 < 20ms; historical query P99 < 2s
- **Availability:** 99.99% — financial transactions cannot be silently lost
- **Consistency:** Strong — balance correctness is non-negotiable; eventual is not acceptable

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Transactions: 10M/day = 116 TPS average; peak 1,000 TPS
Ledger entries: 2 per transaction (debit + credit) = 20M entries/day

Entry size:
  - entry_id (16B) + account_id (8B) + txn_id (16B) + amount (8B) + currency (4B)
    + direction (1B) + timestamp (8B) + balance_after (8B) + memo (50B) = ~120 bytes
  - 20M entries/day * 120B = 2.4 GB/day
  - Annual: 876 GB (7-year retention: 6.1 TB — fits on one PostgreSQL server with SSDs)

Accounts: 100M accounts * ~500 bytes of account metadata = 50 GB (trivial)

Balance cache (Redis):
  - 100M accounts * 8 bytes per cached balance = 800 MB
  - Fit in a single r6g.large (16 GB RAM Redis)

Hot vs. cold:
  - Hot (current year): ~876 GB — keep in PostgreSQL on SSD
  - Cold (prior years): archive to S3 as Parquet; serve via Athena for audit queries
  - Total 7-year: 6.1 TB — keep all in PostgreSQL on large SSD (2 TB per year × 3 years hot,
    rest archived) or use tablespaces
```

### Architecture Diagram

```
Client (App, API)
  |
  | POST /transactions
  v
+------------------+
| Transaction API  |  <-- Validates request, checks balance, begins transaction
+------------------+
  |
  | BEGIN TRANSACTION (serializable isolation)
  |
  +-- 1. Check source account balance >= debit amount
  |      (SELECT balance FROM accounts WHERE id=X FOR UPDATE)
  |
  +-- 2. INSERT INTO ledger_entries (debit entry)
  |
  +-- 3. INSERT INTO ledger_entries (credit entry)
  |
  +-- 4. UPDATE accounts SET balance = balance - amount WHERE id=source
  |
  +-- 5. UPDATE accounts SET balance = balance + amount WHERE id=dest
  |
  +-- 6. INSERT INTO transactions (metadata row)
  |
  | COMMIT
  v
+------------------+
| PostgreSQL       |  <-- Serializable transactions; WAL-based replication
| (Primary)        |
+------------------+
  |
  | WAL streaming replication
  v
+------------------+       +------------------+
| PostgreSQL       |       | Kafka (audit log |
| (Read Replica)   |       |  events)         |
+------------------+       +------------------+
                                    |
                           +------------------+
                           | S3 Archive       |
                           | (Parquet, cold)  |
                           +------------------+

Balance Read:
  Client → API → Redis (cache hit: <1ms)
                  ↓ (cache miss)
               PostgreSQL replica → UPDATE Redis → return
```

### Data Model

```sql
-- Accounts: one row per account; balance is a cached denormalization
CREATE TABLE accounts (
    account_id    BIGSERIAL PRIMARY KEY,
    owner_id      BIGINT NOT NULL,
    currency      CHAR(3) NOT NULL,   -- ISO 4217: USD, EUR, BTC
    balance       NUMERIC(20,8) NOT NULL DEFAULT 0,   -- 8 decimal places for crypto
    overdraft_limit NUMERIC(20,8) DEFAULT 0,
    status        VARCHAR(20) DEFAULT 'ACTIVE',       -- ACTIVE, FROZEN, CLOSED
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT balance_check CHECK (balance + overdraft_limit >= 0)
);

-- Transactions: metadata for a transfer (one row covers both entries)
CREATE TABLE transactions (
    txn_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    txn_type       VARCHAR(50) NOT NULL,   -- TRANSFER, DEPOSIT, WITHDRAWAL, FEE, REVERSAL
    source_account BIGINT REFERENCES accounts(account_id),
    dest_account   BIGINT REFERENCES accounts(account_id),
    amount         NUMERIC(20,8) NOT NULL,
    currency       CHAR(3) NOT NULL,
    fx_rate        NUMERIC(20,8),          -- FX rate at transaction time (for cross-currency)
    memo           VARCHAR(500),
    reference_id   VARCHAR(200) UNIQUE,    -- Idempotency key (from caller)
    status         VARCHAR(20) DEFAULT 'COMPLETED',  -- COMPLETED, PENDING, REVERSED, FAILED
    initiated_by   BIGINT,                -- user_id or service account
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Ledger entries: the immutable double-entry record
CREATE TABLE ledger_entries (
    entry_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    txn_id         UUID REFERENCES transactions(txn_id),
    account_id     BIGINT REFERENCES accounts(account_id),
    direction      CHAR(2) NOT NULL,       -- DR (debit) or CR (credit)
    amount         NUMERIC(20,8) NOT NULL,
    currency       CHAR(3) NOT NULL,
    balance_after  NUMERIC(20,8) NOT NULL, -- Running balance after this entry
    entry_date     DATE NOT NULL,          -- For partitioning
    created_at     TIMESTAMPTZ DEFAULT NOW()
    -- NO UPDATE, NO DELETE permissions granted on this table
)
PARTITION BY RANGE (entry_date);
-- Monthly partitions: ledger_entries_2026_01, ledger_entries_2026_02, ...
-- DROP PARTITION is the only allowed deletion — for archival, not individual rows

-- Indexes
CREATE INDEX ON ledger_entries (account_id, created_at DESC);
CREATE INDEX ON transactions (reference_id);   -- Idempotency lookups
CREATE INDEX ON transactions (source_account, created_at DESC);
```

### API Design

```
POST /v1/transactions
  Body: {
    reference_id: "client-generated-uuid",   // Idempotency key
    type: "TRANSFER",
    source_account: 1001,
    dest_account: 2002,
    amount: "125.50",
    currency: "USD",
    memo: "Invoice #4521 payment"
  }
  Response: { txn_id, status: "COMPLETED", source_balance: "374.50", created_at }
  Idempotent: second call with same reference_id returns original result without re-executing

GET /v1/accounts/{account_id}/balance
  Response: { account_id, balance: "374.50", currency: "USD", as_of: "2026-05-28T10:23:45Z" }
  (served from Redis cache, <1ms)

GET /v1/accounts/{account_id}/ledger?start=2026-01-01&end=2026-01-31&cursor=<...>&limit=20
  Response: { entries: [...], next_cursor: "...", opening_balance: "500.00", closing_balance: "374.50" }

GET /v1/transactions/{txn_id}
  Response: { txn_id, type, source_account, dest_account, amount, status, entries: [...] }

POST /v1/transactions/{txn_id}/reverse
  Body: { reason: "customer dispute", reference_id: "reversal-uuid" }
  Response: { reversal_txn_id, status: "COMPLETED" }
  (Creates new REVERSAL transaction; does NOT modify original entry)
```

### Basic Scaling

- Use serializable isolation level for all transaction writes: prevents phantom reads that could allow overdraft
- Cache current balance in Redis with write-through on every transaction commit; never read balance from DB for balance checks
- Partition ledger_entries by month: old partitions can be frozen, compressed, and archived to S3
- Use the `reference_id` uniqueness constraint for idempotency: duplicate requests with same reference_id return the original result

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
PostgreSQL primary (financial transactions):
  - Instance: db.r5.4xlarge (16 vCPU, 128 GB RAM, 2 TB gp3 SSD)
  - Write throughput: 1,000 TPS * 6 DB operations = 6,000 ops/sec (within PostgreSQL capacity)
  - WAL size: 6,000 ops * 200B = 1.2 MB/sec WAL generation
  - RAM: 128 GB → 16 GB shared_buffers (12% of DB); 876 GB/year data → mostly on SSD
  - Cost: ~$1,500/month (on-demand); $750/month (1-year reserved)

Read replicas (2 replicas for balance reads and reporting):
  - db.r5.2xlarge each: $750/month * 2 = $1,500/month
  - Replicas handle ledger history queries; primary handles writes only

Redis (balance cache):
  - r6g.large (16 GB RAM): 800 MB for 100M balances → less than 5% of RAM
  - Cost: $166/month; run 3-node cluster for HA: $500/month

Archival (S3 Parquet for cold ledger data older than 2 years):
  - 2 TB/year → 2 years hot (4 TB SSD) + 5 years cold (10 TB S3)
  - S3: $230/month; S3 Glacier for years 3-7: $40/month
  - Athena queries over cold data: $5 per TB scanned → rare audit queries = $5-50/query

Total monthly: ~$4,300/month at 10M transactions/day

At Stripe-scale (10B transactions/day):
  - 1,000x scale factor
  - Horizontal sharding: shard by account_id % 1000 across 1,000 PostgreSQL shards
  - Each shard: same r5.4xlarge, handles 1M transactions/day = ~12 TPS (trivial per shard)
  - Total: 1,000 * $1,500 = $1.5M/month for DB layer alone
```

### Failure Modes

```
Failure: Transaction commits to DB but Redis balance cache not updated
  Impact: Subsequent balance reads from Redis return stale balance
  Mitigation:
    - Use write-through cache: Redis update is part of the transaction (via Lua script or pipeline)
    - If Redis INCR fails after DB commit: accept brief inconsistency
      Balance reads that miss Redis fall back to DB SELECT with strong consistency
    - Reconciliation: every 5 minutes, compare Redis balances to DB balances for a sample
      of 1% of accounts; alert if any diverge by > $0.01

Failure: Primary PostgreSQL node fails mid-transaction
  Impact: Ongoing transactions roll back (uncommitted changes lost); some clients see timeout
  Mitigation:
    - PostgreSQL streaming replication with automatic failover (Patroni or RDS Multi-AZ)
    - Failover time: 30-60 seconds → clients receive 503, must retry with same reference_id
    - Idempotency via reference_id: retry is safe — transaction either committed (return stored result)
      or did not commit (re-execute successfully on new primary)

Failure: Concurrent transfers cause overdraft race condition
  Impact: Account A starts two transfers simultaneously; both check balance, both see
          sufficient funds, both commit → balance goes negative
  Mitigation:
    - SERIALIZABLE isolation: PostgreSQL serializable transactions detect the phantom read
      pattern and abort one of the conflicting transactions with serialization error
    - Application retries on serialization error (SQLSTATE 40001)
    - Alternative: SELECT ... FOR UPDATE on the accounts row → serializes concurrent reads
      but reduces concurrency (only one writer at a time per account)
    - Redis balance with atomic DECR: use DECRBY and check result < -overdraft_limit;
      if so, INCRBY to roll back → fail the transaction

Failure: Merkle tree root stored by attacker (for tamper-evidence)
  Impact: Attacker modifies ledger entry AND updates the Merkle root → tamper undetected
  Mitigation:
    - Publish daily Merkle root to a public blockchain or trusted timestamp service
    - Even if the attacker controls your database, they cannot retroactively change
      a hash that was published externally before the attack
    - Store Merkle roots in a separate append-only table with cross-referencing
      (each root references the previous root → chain of custody)
```

### Consistency Boundaries

```
Ledger invariant (must always hold):
  For every completed transaction:
    SUM(amount WHERE direction='DR') = SUM(amount WHERE direction='CR')
  Verified by reconciliation job running every 6 hours.
  Any imbalance triggers immediate alert and manual investigation.

Balance = sum of ledger entries (always reconstructable):
  current_balance = SUM(amount * CASE WHEN direction='CR' THEN 1 ELSE -1 END)
                    FROM ledger_entries WHERE account_id = X
  This is the ground truth. The accounts.balance column is a cached denormalization.
  If the cache and the sum ever differ: the sum is correct; the cache is updated.

Cross-currency transactions:
  - Record FX rate at transaction creation time (not at close of business)
  - Create TWO transactions: one in source currency (DR from source account),
    one in destination currency (CR to destination account) linked by a common parent_txn_id
  - Each entry records the exact currency and amount transacted
  - FX rate recorded for audit: "converted 100 EUR at 1.082 USD/EUR = $108.20"

When to use eventual consistency:
  - Balance display in notifications (email, push): acceptable to be 5 minutes stale
  - Monthly statement generation: runs from DB read replica, not primary (slight lag OK)
  - Never: for the actual transaction commit, overdraft check, or regulatory report
```

### Cost Model

```
Infrastructure: ~$4,300/month at 10M txn/day
Revenue model (payment platform):
  - Transaction fee: 0.1% + $0.05 per transaction
  - 10M txn/day * $50 avg: 0.1% * $50 = $0.05 + $0.05 = $0.10/txn
  - Daily revenue: 10M * $0.10 = $1M/day = $30M/month
  - Infrastructure as % of revenue: $4,300 / $30M = 0.014%

Regulatory compliance cost (7-year archive, audit tooling):
  - S3 storage for 7 years: $270/month
  - Audit query tooling (Athena): $100/month estimated
  - Compliance monitoring: $500/month (dedicated tool or Datadog)
  - Regulatory compliance subtotal: ~$870/month
  - Compared to regulatory fines for non-compliance: millions of dollars → negligible cost
```

---

## Trade-off Comparison

| Design Choice               | Pros                                               | Cons                                              | Best For                            |
|-----------------------------|----------------------------------------------------|---------------------------------------------------|-------------------------------------|
| Append-only ledger          | Immutable audit trail; tamper-evident              | Balance requires SUM of all entries (expensive)   | All financial systems (required)    |
| Balance column (denorm)     | O(1) balance read                                  | Must stay in sync with ledger; reconcile on drift | Cache only — never source of truth  |
| Double-entry bookkeeping    | Every dollar accounted for; books always balance   | More entries per transaction; slightly more code  | Financial systems (standard practice)|
| Merkle tree for integrity   | Detect any modification to any historical entry    | Additional computation; complexity                | High-assurance financial platforms  |
| Monthly partitioning        | Fast archive/delete of old data; parallel queries  | Cross-partition queries require UNION             | All ledgers with 7-year retention   |
| Account-per-currency        | Simple; each account has one currency              | Multi-currency wallets need many accounts per user| Crypto wallets, FX platforms        |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What is double-entry bookkeeping and why does a ledger system use it?
   → Double-entry bookkeeping records every transaction as two entries: a debit from one account and an equal credit to another. When Alice sends $100 to Bob: Alice's account is debited $100 and Bob's account is credited $100. The sum of all debits always equals the sum of all credits — if they don't match, there's a bug or fraud. This invariant makes it impossible to create money out of thin air (credit without a matching debit) and provides a self-validating audit trail.

2. **(L3)** Why should ledger entries never be updated or deleted?
   → Ledger entries are a financial audit trail. Regulators, auditors, and dispute resolution all depend on an immutable, complete record of every transaction. If entries could be modified, a fraudulent operator could change the amount of a past transaction to pocket money without trace. Corrections are made by inserting new REVERSAL entries that offset the incorrect amount — the original entry remains permanently visible.

3. **(L4)** How do you handle the idempotency requirement for transaction submission?
   → The client generates a unique `reference_id` (UUID) and includes it in every transaction request. The server does `INSERT INTO transactions (reference_id, ...) ON CONFLICT (reference_id) DO NOTHING`. If the insert affects 0 rows (duplicate), the server returns the original transaction by looking up `WHERE reference_id = X`. This means: if a client's request times out and they retry, the transaction executes exactly once regardless of how many times the request is sent.

4. **(L4)** How do you prevent race conditions where two concurrent transfers from the same account both see sufficient balance and both commit?
   → Use `SELECT balance FROM accounts WHERE id=X FOR UPDATE` inside the transaction — this acquires a row-level lock that prevents concurrent transactions from reading the same row until the first transaction commits. Alternatively, use SERIALIZABLE isolation level: PostgreSQL's serializable snapshot isolation detects the phantom read conflict and aborts one of the transactions with a serialization error (SQLSTATE 40001), which the application retries. The `CHECK CONSTRAINT (balance + overdraft_limit >= 0)` provides a last-resort guard at the DB level.

5. **(L5)** How would you implement a Merkle tree over the ledger for tamper detection?
   → At the end of each day, build a Merkle tree over all ledger entries for that day: leaf nodes are SHA-256 hashes of individual entries (serialized as canonical JSON). Internal nodes are SHA-256 of their two children's hashes concatenated. The root hash uniquely identifies the entire day's entries. Store this root in a separate table `ledger_merkle_roots(date, root_hash, prev_root_hash)` where `prev_root_hash` chains to the prior day (creating a blockchain-like chain of custody). Publish the daily root hash to an external public ledger (e.g., Ethereum) or a trusted timestamping service. To verify integrity: re-compute the Merkle tree from the DB entries for a given day and compare the root to the published root. Any modification to any entry changes the root, which won't match the externally published value.

6. **(L5)** How do you reconstruct a balance at any historical point in time?
   → Two approaches: (1) Full reconstruction: `SELECT SUM(amount * CASE WHEN direction='CR' THEN 1 ELSE -1 END) FROM ledger_entries WHERE account_id = X AND created_at <= '2025-12-31'`. Correct but O(N) over all historical entries — slow for old accounts with millions of entries. (2) Checkpoint + incremental: store monthly balance snapshots in `balance_snapshots(account_id, date, balance)`. To get balance at date D: find the most recent snapshot before D, then apply all entries from that snapshot's date to D. This reduces the query from O(all entries) to O(entries in one month). Snapshots are computed by the reconciliation job and stored as immutable records.

7. **(L5+)** Your ledger system must comply with PCI-DSS and retain 7 years of data. A regulatory audit demands an export of all transactions for a specific account over 7 years with a cryptographic proof that no records were deleted or modified. How do you provide this?
   → The export package includes: (1) All ledger entries for the account, sorted by created_at, exported as CSV with SHA-256 hash of the full file. (2) All daily Merkle roots for the date range, signed by the external timestamp service. (3) A verification script that: re-derives each daily Merkle root from the provided entries and compares to the signed roots — any mismatch indicates tampering. The auditor can independently verify: import the CSV, run the script, confirm all roots match the externally published (and independently timestamped) roots. This provides cryptographic non-repudiation: even if your organization wanted to fabricate records, they could not do so without invalidating the externally published Merkle roots.

## Anti-patterns / Things NOT to Say

- **"Update the balance column in-place — it's simpler than maintaining a ledger"** — An in-place balance update loses history. If your balance column shows $374.50, you cannot tell whether that came from 1,000 small credits or 2 large transactions. You cannot audit individual transactions, comply with regulatory reporting, or detect fraud. Financial systems always need an append-only ledger; the balance column is only a cache.
- **"Use eventual consistency for balance checks — it's faster"** — Eventual consistency means a user's "available balance" may be stale. If Alice's balance shows $500 (stale) but the committed balance is $200 due to a recent transaction, and she initiates a $400 transfer, the overdraft check succeeds on stale data — creating a $200 overdraft. Financial balance checks must always use strong consistency. Cache balances for display purposes, but always verify from the source before deducting.
- **"Store the FX rate at end-of-day for cross-currency transactions"** — The FX rate at transaction time is the contractually binding rate. A transaction executed at 14:23 at 1.082 USD/EUR must record 1.082 — not the end-of-day rate (which could be 1.075). Using a different rate from the actual transaction rate is both incorrect and potentially fraudulent. Always record the exact rate used to execute the transaction.
- **"Hard-delete old transactions after 7 years to save storage"** — 7 years is the minimum retention, not the maximum. Legal holds (litigation, government investigation) can extend this indefinitely. Once a record is deleted, it is unrecoverable. Instead, move old records to cold storage (S3 Glacier at $0.004/GB) where they remain queryable (via Athena) but cost almost nothing. Never hard-delete financial records without explicit legal authorization.
- **"One accounts table is sufficient — track balance there"** — When an account has millions of transactions, scanning all ledger entries to compute balance is O(N). You need the denormalized balance in the accounts table (or Redis) for fast reads, plus the ledger for accuracy. The balance column is a cache of the ledger sum; always reconcile them. If they diverge, the ledger is the ground truth.

## Python Implementation (sketch)

```python
import uuid
import hashlib
import json
from decimal import Decimal
from typing import Optional
from contextlib import contextmanager

class LedgerService:
    """Double-entry ledger with idempotency and balance caching."""

    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client

    def transfer(self, source_account: int, dest_account: int,
                 amount: Decimal, currency: str,
                 memo: str, reference_id: str) -> dict:
        """
        Execute a transfer. Idempotent via reference_id.
        Uses SERIALIZABLE isolation to prevent overdraft races.
        """
        # Idempotency check: return prior result if reference_id was already processed
        existing = self.db.fetchone(
            "SELECT txn_id, status FROM transactions WHERE reference_id = %s",
            reference_id
        )
        if existing:
            return {"txn_id": existing["txn_id"], "status": existing["status"], "idempotent": True}

        txn_id = str(uuid.uuid4())

        with self._serializable_tx() as conn:
            # Lock both accounts in consistent order (lower id first) to avoid deadlock
            accounts_ordered = sorted([source_account, dest_account])
            source = conn.fetchone(
                "SELECT balance, overdraft_limit FROM accounts WHERE account_id = %s FOR UPDATE",
                source_account
            )
            conn.fetchone(
                "SELECT account_id FROM accounts WHERE account_id = %s FOR UPDATE",
                dest_account if dest_account != accounts_ordered[0] else source_account
            )

            available = source["balance"] + source["overdraft_limit"]
            if amount > available:
                raise InsufficientFundsError(
                    f"Available: {available}, Required: {amount}"
                )

            new_source_balance = source["balance"] - amount
            # Credit destination
            dest = conn.fetchone("SELECT balance FROM accounts WHERE account_id=%s", dest_account)
            new_dest_balance = dest["balance"] + amount

            # Insert transaction metadata
            conn.execute(
                "INSERT INTO transactions (txn_id, txn_type, source_account, dest_account, "
                "amount, currency, memo, reference_id, status) VALUES (%s,'TRANSFER',%s,%s,%s,%s,%s,%s,'COMPLETED')",
                txn_id, source_account, dest_account, amount, currency, memo, reference_id
            )

            # Insert debit entry (source account)
            conn.execute(
                "INSERT INTO ledger_entries (txn_id, account_id, direction, amount, currency, balance_after, entry_date) "
                "VALUES (%s, %s, 'DR', %s, %s, %s, CURRENT_DATE)",
                txn_id, source_account, amount, currency, new_source_balance
            )

            # Insert credit entry (destination account)
            conn.execute(
                "INSERT INTO ledger_entries (txn_id, account_id, direction, amount, currency, balance_after, entry_date) "
                "VALUES (%s, %s, 'CR', %s, %s, %s, CURRENT_DATE)",
                txn_id, dest_account, amount, currency, new_dest_balance
            )

            # Update cached balances
            conn.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", new_source_balance, source_account)
            conn.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", new_dest_balance, dest_account)

        # Update Redis balance cache after successful commit
        self.redis.set(f"balance:{source_account}", str(new_source_balance))
        self.redis.set(f"balance:{dest_account}", str(new_dest_balance))

        return {"txn_id": txn_id, "status": "COMPLETED",
                "source_balance": str(new_source_balance)}

    def get_balance(self, account_id: int) -> Decimal:
        """Fast balance read from Redis cache with DB fallback."""
        cached = self.redis.get(f"balance:{account_id}")
        if cached:
            return Decimal(cached)
        row = self.db.fetchone("SELECT balance FROM accounts WHERE account_id=%s", account_id)
        balance = row["balance"]
        self.redis.set(f"balance:{account_id}", str(balance), ex=300)
        return balance

    def compute_merkle_root(self, date_str: str) -> str:
        """Build Merkle tree over all ledger entries for a given date."""
        entries = self.db.fetchall(
            "SELECT entry_id, txn_id, account_id, direction, amount, currency, created_at "
            "FROM ledger_entries WHERE entry_date = %s ORDER BY created_at, entry_id",
            date_str
        )
        if not entries:
            return hashlib.sha256(b"empty").hexdigest()

        # Leaf hashes: SHA-256 of canonical JSON for each entry
        leaves = [
            hashlib.sha256(json.dumps(dict(e), sort_keys=True, default=str).encode()).hexdigest()
            for e in entries
        ]
        return self._merkle_root(leaves)

    def _merkle_root(self, hashes: list) -> str:
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last node if odd count
            hashes = [
                hashlib.sha256((hashes[i] + hashes[i+1]).encode()).hexdigest()
                for i in range(0, len(hashes), 2)
            ]
        return hashes[0]

    @contextmanager
    def _serializable_tx(self):
        conn = self.db.connection()
        conn.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        try:
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

class InsufficientFundsError(Exception):
    pass
```
