# Distributed Transactions

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

When a business operation spans multiple services or databases, you need all steps to either succeed together or fail together. A bank transfer that debits Account A on one database node and credits Account B on another must be atomic — partial updates leave the system in an inconsistent, unrecoverable state.

Distributed transactions coordinate multiple participants (databases, services, message queues) so that a transaction either commits on all participants or rolls back on all of them, preserving the ACID guarantee across distributed boundaries.

## Functional Requirements

- Atomic commit or rollback across 2+ participants (databases, services, queues)
- Coordinator tracks transaction state and drives the protocol
- Participants must be able to recover to a consistent state after crashes
- Transaction log must survive coordinator restarts
- Support for both homogeneous (same DB engine) and heterogeneous participants

## Non-Functional Requirements

- **Scale:** 10K transactions/sec, each touching 2-5 participants
- **Latency:** P99 < 200ms for commit path; rollback < 500ms
- **Availability:** 99.99% — coordinator must not be a single point of failure
- **Consistency:** Strong — no partial commits; all-or-nothing semantics required

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Transactions: 10K TPS
Participants per txn: 3 (average)
Network round trips per 2PC: 4 (prepare + vote + commit + ack)
Total RPCs: 10K * 3 * 4 = 120K RPCs/sec

Transaction log writes:
  - Per transaction: 2 log entries (prepare + commit/abort)
  - 10K TPS * 2 = 20K log writes/sec
  - Log entry: ~256 bytes
  - Log throughput: 20K * 256B = ~5 MB/sec (easily handled by SSD)

Lock duration:
  - During 2PC prepare → commit window: ~10-50ms per txn
  - 10K TPS * 50ms lock hold = 500 concurrent locked rows at any time
```

### Architecture Diagram

```
Client
  |
  v
+------------------+
| Transaction       |
| Coordinator       |  <-- Manages txn state, drives protocol
| (TM / TxManager) |
+------------------+
      |          |
      |          |
  PREPARE      PREPARE
      |          |
      v          v
+----------+ +----------+
| DB Node  | | DB Node  |   Participants (Resource Managers)
| (RM 1)   | | (RM 2)   |
|  - Lock  | |  - Lock  |
|  - Log   | |  - Log   |
+----------+ +----------+
      |          |
  VOTE YES   VOTE YES
      |          |
      +----+-----+
           |
           v
      COMMIT to both
           |
      +----+-----+
      |          |
      v          v
  ACK         ACK
      |          |
      v
  Release Locks

Two-Phase Commit (2PC) Protocol Flow:
Phase 1 (Prepare):
  Coordinator -> RM: PREPARE txn_id
  RM: Acquire locks, write prepare record to WAL
  RM -> Coordinator: VOTE_YES / VOTE_NO

Phase 2 (Commit or Abort):
  All YES: Coordinator -> RM: COMMIT txn_id
  Any NO:  Coordinator -> RM: ABORT txn_id
  RM: Apply changes, release locks, write commit/abort to WAL
  RM -> Coordinator: ACK
```

### Data Model

```sql
-- Coordinator: Transaction log (survives restarts)
CREATE TABLE transaction_log (
    txn_id        UUID PRIMARY KEY,
    state         VARCHAR(20),   -- PREPARING, PREPARED, COMMITTING, COMMITTED, ABORTED
    participants  JSONB,         -- List of participant endpoints
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    decided_at    TIMESTAMPTZ,
    timeout_at    TIMESTAMPTZ    -- Auto-abort after this time
);

-- Participant: Participant log (per RM, survives restarts)
CREATE TABLE participant_log (
    txn_id      UUID,
    participant VARCHAR(100),
    vote        VARCHAR(10),   -- YES / NO
    state       VARCHAR(20),   -- PREPARED, COMMITTED, ABORTED
    logged_at   TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (txn_id, participant)
);

-- XA-compatible prepare record (stored in RM's WAL)
-- XID: Format "txn_id:branch_qualifier"
-- Written atomically before voting YES
```

### API Design

```
POST /transactions
  Body: { participants: ["db1", "db2"], timeout_ms: 5000 }
  Response: { txn_id: "uuid", expires_at: "ISO timestamp" }

POST /transactions/{txn_id}/prepare
  Body: { participant: "db1", operations: [...] }
  Response: { vote: "YES" | "NO", reason?: "..." }

POST /transactions/{txn_id}/commit
  (Coordinator calls this after all YES votes)
  Response: { status: "COMMITTED" }

POST /transactions/{txn_id}/abort
  Response: { status: "ABORTED" }

GET /transactions/{txn_id}
  Response: { state: "COMMITTED", participants: [...], decided_at: "..." }
```

### Basic Scaling

- Keep coordinator stateless; persist log to replicated storage (PostgreSQL + streaming replica or etcd)
- Shard coordinators by transaction ID range — each shard owns a subset of txn_ids
- Set aggressive timeouts (default 5s) to prevent lock pile-up from stuck transactions
- Use connection pooling to reduce coordinator-to-RM connection overhead

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Coordinator cluster: 3 nodes (Raft-replicated)
  - RAM: 4 GB per node (in-flight txn state: 10K txns * 1KB = 10MB; mostly idle)
  - CPU: 4 cores per node (coordinator is I/O bound, not compute bound)
  - Disk: 50 GB SSD (WAL for txn log; 20K writes/sec * 256B * 86400s / 1e9 = ~440 MB/day)
  - Network: 1 Gbps (120K RPCs * ~1KB = 120MB/sec, well within limit)

Participant nodes (per RM):
  - Lock table RAM: 500 concurrent rows * 200B = ~100KB (trivial)
  - WAL write amplification: 2x for prepare + commit records
  - Prepare-to-commit window holds row locks: ensure P99 < 50ms to bound contention

Failure probability math:
  - P(single node crash) = 0.001 per hour (commodity hardware)
  - P(2PC blocks for N=3 participants) = P(coordinator crash after PREPARE, before COMMIT)
    = P(coordinator crash) * P(crash in [prepare_sent, commit_received] window)
    = 0.001/hr * (50ms / 3600000ms) = 1.4e-8 per transaction
  - At 10K TPS: 10K * 1.4e-8 = 0.00014 blocked txns/sec = ~0.5 blocked/hour
  - Mitigation: coordinator timeout + recovery process resolves blocks within 30s
```

### Failure Modes

```
Failure: Coordinator crashes after sending PREPARE but before deciding
  Impact: Participants are stuck with locks (the "blocking problem" of 2PC)
  Mitigation:
    - Coordinator recovery process reads txn_log, re-drives decision
    - Coordinator replicated (3-node Raft): new leader takes over within 1-2s
    - Participant timeout: after N seconds in PREPARED state, participant
      can contact other participants or coordinator replica to learn outcome

Failure: Participant crashes after voting YES but before receiving COMMIT
  Impact: Participant restarts, reads its WAL, sees PREPARED record
  Mitigation:
    - Participant calls coordinator on startup: GET /transactions/{txn_id}
    - Coordinator responds with COMMITTED or ABORTED → participant applies

Failure: Network partition between coordinator and one participant
  Impact: Coordinator cannot deliver COMMIT to isolated participant
  Mitigation:
    - Coordinator retries indefinitely until participant acknowledges
    - Participant holds locks until it receives decision (no timeout on locks
      after voting YES — this is correct; locks must be held until resolved)

Failure: All coordinator replicas crash simultaneously (rare)
  Impact: All in-flight transactions block until coordinator recovers
  Mitigation:
    - Participants expose /prepare-status endpoint
    - External recovery daemon scans participant_log for orphaned txns
    - After coordinator TTL (e.g., 60s), recovery daemon makes abort decision
```

### Consistency Boundaries

```
Strong consistency across participants:
  - 2PC guarantees atomic commit — all commit or all abort
  - Once coordinator writes COMMITTED to its log, outcome is final
  - Participants must durably persist vote before sending YES

Where 2PC does NOT help:
  - Long-running transactions (hold locks for seconds → contention)
  - High-latency participants (each extra hop adds to commit latency)
  - Cross-cloud transactions (50ms+ RTT makes 2PC impractical)

3PC partial solution:
  - Adds a "pre-commit" phase to avoid blocking on coordinator crash
  - But introduces new failure window: participant cannot distinguish
    coordinator crash from network partition → not widely used in production

Saga alternative (for long-running flows):
  - Each step executes locally and publishes an event
  - On failure, compensating transactions undo completed steps
  - Eventual consistency — not suitable when intermediate states must be hidden
  - See saga-pattern.md for full treatment
```

### Cost Model

```
Coordinator cluster (3 x c5.large on AWS):
  - Compute: 3 * $0.085/hr = $0.255/hr = ~$185/month
  - Storage (50GB SSD gp3): 3 * $4/month = $12/month

Coordinator total: ~$197/month

Per-transaction cost:
  - Compute per txn: $0.255/hr / 10K TPS / 3600s = $7e-9 per txn = $0.007 per 1M txns
  - WAL storage (30-day retention): 20K * 256B * 86400s * 30 / 1e9 = 13 GB = $0.30/month

Total at 10K TPS: ~$200/month coordinator overhead
  - Amortized cost per 1M transactions: ~$0.007 (negligible vs. business value)
```

---

## Trade-off Comparison

| Approach          | Pros                                      | Cons                                          | Best For                            |
|-------------------|-------------------------------------------|-----------------------------------------------|-------------------------------------|
| 2PC (two-phase)   | True atomicity, strong consistency        | Blocking on coordinator crash, high latency   | Financial systems, inventory deduct |
| 3PC               | Non-blocking on coordinator crash         | Complex, new failure window (partition)       | Rarely used in practice             |
| Saga (choreography) | Loosely coupled, no coordinator         | Eventually consistent, complex rollback       | Long-running business workflows     |
| Saga (orchestration)| Single coordinator, clear rollback order| Central failure point, more code              | Order fulfillment, booking flows    |
| TCC (Try-Confirm-Cancel) | Business-level reservation       | Application must implement reserve/release    | Hotel booking, seat reservation     |
| Outbox pattern    | Reliable message publish with local txn  | Eventual delivery, not true atomic commit     | Event publishing from DB write      |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What are the two phases of 2PC?
   → Phase 1 (Prepare): coordinator asks each participant to lock resources and vote YES/NO. Phase 2 (Commit/Abort): coordinator broadcasts commit if all voted YES, abort if any voted NO.

2. **(L3)** Why can 2PC block?
   → If the coordinator crashes after sending PREPARE but before sending COMMIT/ABORT, participants are stuck holding locks. They voted YES and cannot unilaterally decide — they must wait for the coordinator to recover.

3. **(L4)** How does coordinator replication solve the blocking problem?
   → A 3-node Raft cluster for the coordinator means a new leader is elected within 1-2 seconds of coordinator failure. The new leader reads the transaction log, discovers in-flight transactions, and re-drives the decision — participants receive COMMIT or ABORT without waiting for the original coordinator to restart.

4. **(L4)** What is an XA transaction? How does it differ from application-level 2PC?
   → XA is a standard interface (X/Open XA) that databases expose to an external transaction manager. The TM calls xa_prepare() and xa_commit() on each RM. Application-level 2PC implements the same protocol but without the standard interface, using explicit API calls to each service. XA lets you use existing database infrastructure; application-level 2PC gives you more control over the protocol details.

5. **(L5)** How would you handle a participant that is slow to respond during Phase 1?
   → Set per-participant prepare timeouts (e.g., 2s). If a participant does not respond in time, the coordinator treats it as a VOTE_NO and aborts the transaction. This prevents slow participants from blocking coordinators and accumulating locks. The trade-off is false aborts under transient network latency — acceptable for most systems. For critical paths, distinguish between timeout-as-abort and timeout-as-unknown, and retry with exponential backoff before aborting.

6. **(L5)** What is a compensating transaction and when is it used instead of 2PC rollback?
   → A compensating transaction is a semantically inverse operation applied after a step has already committed. For example, if Payment Service committed a charge, a compensating transaction issues a refund rather than rolling back the SQL. Compensating transactions are used in Saga patterns where each step commits independently. Unlike 2PC rollback (which undoes uncommitted changes invisibly), compensating transactions are visible in the system audit log and may have business side effects (e.g., refund confirmation emails). They are preferred when transaction duration is too long for lock-holding (>1 second) or when participants do not support XA.

7. **(L5+)** How would you implement distributed transaction support for a system where participants include a relational database, a Kafka topic, and an object store (S3)?
   → S3 and Kafka do not support XA. Use the Outbox pattern: instead of writing to Kafka/S3 directly in the transaction, write to an outbox table in the same relational database transaction as the business data update. A separate relay process reads committed outbox rows and publishes to Kafka/S3. This reduces the distributed participants to one (the relational DB), eliminating the need for 2PC. For the object store, generate a pre-signed upload URL and treat the upload as an eventually-consistent side effect. Reconciliation jobs detect and retry failed uploads. This trades perfect atomicity for simplicity and availability — appropriate when the cost of duplicate messages is lower than the operational cost of 2PC.

## Anti-patterns / Things NOT to Say

- **"Just use 2PC everywhere"** — 2PC is blocking and high-latency. For microservices with P99 < 50ms targets or steps that hold locks for seconds, 2PC causes cascading lock contention. Use Saga for long-running workflows.
- **"Add a timeout to participants after they vote YES"** — A participant that voted YES cannot time out and self-abort without coordinator confirmation. Doing so risks committing on the coordinator and aborting on the participant — a split-brain inconsistency. Locks must be held until the coordinator's decision is received.
- **"3PC is strictly better than 2PC"** — 3PC avoids the blocking problem under crash failures but introduces a new failure window under network partitions. In practice, most production systems use replicated 2PC coordinators (Raft/Paxos) instead of 3PC because it is simpler and better understood.
- **"Distributed transactions are not needed if you use idempotent APIs"** — Idempotency prevents duplicate processing but does not ensure atomicity across services. If Payment succeeds but Inventory update fails, idempotency on individual steps does not prevent the partial-commit inconsistency. You still need either 2PC, Saga with compensation, or the Outbox pattern.
- **"Use a distributed lock instead of 2PC"** — Distributed locks (Redis Redlock) serialize access but do not provide atomic commit semantics across multiple data stores. A lock ensures only one writer at a time; 2PC ensures all-or-nothing commit. These solve different problems.

## Python Implementation (sketch)

```python
import uuid
import time
import enum
from dataclasses import dataclass, field
from typing import List, Optional

class TxnState(enum.Enum):
    PREPARING = "PREPARING"
    PREPARED  = "PREPARED"
    COMMITTING = "COMMITTING"
    COMMITTED = "COMMITTED"
    ABORTED   = "ABORTED"

@dataclass
class Participant:
    url: str
    vote: Optional[str] = None  # "YES" or "NO"
    acked: bool = False

@dataclass
class Transaction:
    txn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: TxnState = TxnState.PREPARING
    participants: List[Participant] = field(default_factory=list)
    timeout_at: float = field(default_factory=lambda: time.time() + 10.0)

class TwoPhaseCoordinator:
    """Simplified 2PC coordinator — real impl uses durable log + Raft replication."""

    def __init__(self, log_store):
        self.log = log_store  # Durable log (e.g., PostgreSQL)

    def begin(self, participant_urls: List[str]) -> Transaction:
        txn = Transaction(participants=[Participant(u) for u in participant_urls])
        self.log.write(txn)
        return txn

    def run(self, txn: Transaction, operations: dict) -> bool:
        """Drive full 2PC protocol. Returns True on commit."""
        # Phase 1: Prepare
        all_yes = self._phase1_prepare(txn, operations)

        # Phase 2: Commit or Abort
        if all_yes:
            return self._phase2_commit(txn)
        else:
            self._phase2_abort(txn)
            return False

    def _phase1_prepare(self, txn: Transaction, ops: dict) -> bool:
        txn.state = TxnState.PREPARING
        self.log.write(txn)

        for p in txn.participants:
            if time.time() > txn.timeout_at:
                p.vote = "NO"  # Treat timeout as NO
                continue
            try:
                # HTTP POST /prepare with txn_id + operations for this participant
                response = self._rpc(p.url, "prepare", {
                    "txn_id": txn.txn_id,
                    "operations": ops.get(p.url, [])
                }, timeout=2.0)
                p.vote = response.get("vote", "NO")
            except Exception:
                p.vote = "NO"

        all_yes = all(p.vote == "YES" for p in txn.participants)
        txn.state = TxnState.PREPARED if all_yes else TxnState.ABORTED
        self.log.write(txn)
        return all_yes

    def _phase2_commit(self, txn: Transaction) -> bool:
        txn.state = TxnState.COMMITTING
        self.log.write(txn)
        for p in txn.participants:
            self._retry_rpc(p.url, "commit", {"txn_id": txn.txn_id})
        txn.state = TxnState.COMMITTED
        self.log.write(txn)
        return True

    def _phase2_abort(self, txn: Transaction):
        for p in txn.participants:
            if p.vote == "YES":  # Only abort participants that prepared
                self._retry_rpc(p.url, "abort", {"txn_id": txn.txn_id})
        txn.state = TxnState.ABORTED
        self.log.write(txn)

    def _rpc(self, url, action, body, timeout=2.0):
        # Placeholder: real impl uses requests or httpx
        raise NotImplementedError

    def _retry_rpc(self, url, action, body, max_retries=10):
        # Commit and abort RPCs retry indefinitely — participants must ack
        for attempt in range(max_retries):
            try:
                return self._rpc(url, action, body, timeout=5.0)
            except Exception:
                time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"Failed to deliver {action} to {url} after {max_retries} retries")
```
