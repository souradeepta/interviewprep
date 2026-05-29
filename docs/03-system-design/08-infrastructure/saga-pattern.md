# Saga Pattern

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Long-running business workflows span multiple services and can take seconds or minutes to complete — far too long to hold database locks across all participants as 2PC requires. An order fulfillment flow might touch Inventory, Payment, Shipping, and Notification services, each with their own database. If Payment succeeds but Shipping fails, you cannot roll back Payment using a database rollback — the charge was already processed.

The Saga pattern breaks a distributed transaction into a sequence of local transactions, each of which publishes events or sends commands to trigger the next step. If any step fails, the saga executes compensating transactions in reverse order to undo the effects of already-completed steps.

## Functional Requirements

- Execute a multi-step business workflow across 2+ services
- On success: each step completes and the workflow proceeds to the end
- On failure: compensating transactions undo completed steps in reverse order
- Each step must be idempotent (safe to retry)
- The saga state must be durable — survives process restarts
- Support both choreography (event-driven) and orchestration (coordinator-driven) styles

## Non-Functional Requirements

- **Scale:** 100K orders/day = ~1.2 sagas/sec; peak 10x = 12 sagas/sec
- **Latency:** Each saga step: P99 < 500ms; full saga completion: P99 < 5s
- **Availability:** 99.99% — saga log must be durable; steps must be retryable
- **Consistency:** Eventual — intermediate states are visible; compensation restores consistency

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Scale: 100K orders/day
Peak factor: 10x → 12 sagas/sec
Steps per saga: 5 (Reserve Inventory, Process Payment, Create Shipment, Send Notification, Confirm Order)
Events per saga: 5 commands + 5 replies = 10 messages
Kafka throughput: 12 * 10 = 120 messages/sec (trivial for Kafka)

Saga state storage:
  - Active sagas: 12/sec * 5s average duration = 60 concurrent sagas
  - Saga state per row: ~500 bytes
  - DB storage: 60 * 500B = 30KB in-flight state (trivial)
  - Completed saga log (90-day retention):
    100K/day * 90 days = 9M rows * 500B = 4.5 GB (manageable)

Compensation frequency:
  - Assume 2% of sagas fail and need compensation
  - 100K/day * 2% = 2000 compensations/day = ~1.4/min
  - Compensation steps (reverse order): up to 4 compensating transactions per saga
  - Compensation event throughput: 2000 * 4 = 8000 events/day (negligible)
```

### Architecture Diagram

```
CHOREOGRAPHY SAGA (event-driven, no central coordinator):

Order Service          Inventory Service      Payment Service
     |                       |                     |
     |--[OrderCreated]------> |                     |
     |                  Reserve items               |
     |                  [InventoryReserved]-------> |
     |                       |              Charge payment
     |                       |              [PaymentProcessed]
     |                       |                     |
     |<---[PaymentProcessed]-------------------------
     |
   Confirm order

On Failure (Payment fails):
  Payment Service publishes [PaymentFailed]
  Inventory Service listens → releases reservation (compensating tx)
  Order Service listens → marks order as FAILED

---

ORCHESTRATION SAGA (single coordinator drives steps):

     +------------------+
     |  Saga Orchestrator|
     |  (Order Saga)     |
     +------------------+
          |    ^   |    ^
          |    |   |    |
   Command|    |   |Command
   Reserve|  OK|   |Payment  OK|
          |    |   |           |
          v    |   v           |
     Inventory   Payment     Shipping
      Service     Service     Service
          |           |           |
    Reserve       Charge      Create
    Items         Card        Label

Saga Log (durable state):
  saga_id | step       | status    | compensate?
  --------+------------+-----------+------------
  ord-123 | RESERVE_INV | COMPLETED | release_inventory(ord-123)
  ord-123 | PAYMENT     | COMPLETED | refund_payment(ord-123)
  ord-123 | SHIPMENT    | FAILED    | — (not started, no compensation needed)
```

### Data Model

```sql
-- Saga log: tracks each saga instance and its current state
CREATE TABLE saga_log (
    saga_id       UUID PRIMARY KEY,
    saga_type     VARCHAR(50),          -- 'ORDER_FULFILLMENT'
    status        VARCHAR(20),          -- STARTED, COMPENSATING, COMPLETED, FAILED
    current_step  VARCHAR(50),          -- Which step is executing
    payload       JSONB,                -- Original saga input
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Saga steps: each step's outcome and compensating action
CREATE TABLE saga_step_log (
    saga_id       UUID REFERENCES saga_log(saga_id),
    step_name     VARCHAR(50),
    step_order    INT,
    status        VARCHAR(20),  -- PENDING, COMPLETED, COMPENSATED, COMPENSATION_FAILED
    request_id    UUID,         -- Idempotency key for the step call
    response      JSONB,        -- Step outcome stored for compensation use
    started_at    TIMESTAMPTZ,
    completed_at  TIMESTAMPTZ,
    PRIMARY KEY (saga_id, step_name)
);

-- Outbox: reliable event publishing (avoids dual-write problem)
CREATE TABLE saga_outbox (
    id            BIGSERIAL PRIMARY KEY,
    saga_id       UUID,
    event_type    VARCHAR(100),
    payload       JSONB,
    published     BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### API Design

```
# Saga management API (internal)

POST /sagas/orders
  Body: { order_id, customer_id, items: [...], payment_method_id }
  Response: { saga_id, status: "STARTED" }

GET /sagas/{saga_id}
  Response: { saga_id, status, current_step, steps: [...], created_at, updated_at }

POST /sagas/{saga_id}/cancel
  Body: { reason: "customer requested cancellation" }
  Response: { saga_id, status: "COMPENSATING" }

# Step callbacks (used by participant services to reply to orchestrator)

POST /sagas/{saga_id}/steps/{step_name}/complete
  Body: { request_id, result: {...} }
  Response: { next_step: "PROCESS_PAYMENT" }

POST /sagas/{saga_id}/steps/{step_name}/fail
  Body: { request_id, error: "Insufficient stock", retryable: false }
  Response: { action: "COMPENSATE", compensating_steps: [...] }
```

### Basic Scaling

- Use the orchestration style when you need clear visibility into saga state and easy debugging
- Persist saga log before executing each step — never lose state between steps
- Make every step idempotent using a request_id (UUID): retry is safe if the first attempt timed out
- For choreography, use Kafka consumer groups so each service processes events independently
- Separate compensation logic into explicit compensating transaction handlers — don't reuse forward logic

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Orchestrator cluster: 3 nodes (active-active, sharded by saga_id)
  - RAM: 2 GB per node (60 active sagas * 10KB state = 600KB; mostly idle)
  - CPU: 4 cores per node (I/O bound, not compute)
  - DB (saga_log + saga_step_log): PostgreSQL, 10 GB SSD
    100K sagas/day * 90 days * 2KB per saga = 18 GB (fits on single node; archive to S3 after 90d)

Kafka topics for choreography style:
  - saga-commands: 10 partitions (12 commands/sec → 1.2/partition → trivial)
  - saga-replies: 10 partitions
  - saga-compensation-commands: 5 partitions (compensations are rare)
  - Retention: 7 days (sagas complete in <5s; 7-day retention for replay/debugging)

Outbox relay (for reliable event publishing):
  - Polls saga_outbox table every 100ms for unpublished events
  - At 120 events/sec, relay processes <100ms batch easily
  - Alternatively: Debezium CDC reads PostgreSQL WAL → publishes to Kafka (zero polling lag)
```

### Failure Modes

```
Failure: Step 3 (Shipment) fails after Step 2 (Payment) succeeded
  Impact: Customer is charged but no shipment created → inconsistency
  Resolution:
    - Saga log shows SHIPMENT=FAILED, PAYMENT=COMPLETED
    - Orchestrator triggers compensation in reverse order:
      Step 2 compensation: refund_payment(saga_id, amount, payment_id)
      Step 1 compensation: release_inventory(saga_id, reservation_id)
    - Order marked FAILED with customer notification
  Key requirement: compensation for step 2 must use payment_id stored in saga_step_log
    at the time step 2 completed — do not re-query payment service for the ID

Failure: Compensating transaction for step 1 fails after step 2 compensation succeeds
  Impact: Inventory is not released; ghost reservation blocks stock
  Resolution:
    - Mark step 1 compensation as COMPENSATION_FAILED in saga_step_log
    - Alert on-call engineer with saga_id, step, and failure reason
    - Retry compensation on schedule: exponential backoff for up to 24 hours
    - If still failing after 24 hours: manual intervention workflow
    - Design invariant: compensating transactions should be simpler and more reliable
      than forward transactions (e.g., release reservation is idempotent via reservation_id)

Failure: Orchestrator crashes mid-saga
  Impact: Saga appears stuck; no more step commands are issued
  Resolution:
    - Recovery process on startup scans saga_log for status=STARTED, updated_at < 30s ago
    - Re-drives saga from current_step, re-issuing the command for that step
    - Step handler receives duplicate command → idempotency key (request_id) deduplicates
    - Saga resumes from where it left off without re-executing completed steps

Failure: Network timeout between orchestrator and step handler
  Impact: Step may have succeeded (handler processed) but orchestrator didn't receive reply
  Resolution:
    - Orchestrator retries command with same request_id
    - Step handler checks idempotency store: if request_id already processed → return prior result
    - This is why EVERY step must be idempotent — timeouts cause retries; retries must be safe
```

### Consistency Boundaries

```
What is eventually consistent in a saga:
  - During execution, intermediate states are visible across services
  - Example: Inventory is reserved but payment not yet processed
    → inventory count shows item as "reserved" (not available)
    → if another saga checks stock, it sees reduced availability
  - This is intentional and correct — it's optimistic locking at the saga level

What is NOT consistent until saga completes or compensates:
  - Cross-service balance (inventory reserved + payment pending + order STARTED)
  - A third-party observer sees partial state during the saga's execution window

Invariants that MUST hold even in partial states:
  - Money is never lost: if payment succeeds, either shipment follows or refund is issued
  - Inventory is never double-counted: each reservation has a unique reservation_id
  - Order status always reflects the latest known saga outcome (not stale)

Choreography vs Orchestration consistency:
  - Choreography: each service decides its next action based on received events
    Risk: cyclical event flows are hard to debug; no single source of truth for saga state
  - Orchestration: orchestrator is the single source of truth; participants are passive
    Risk: orchestrator becomes a bottleneck; but at 12 sagas/sec, this is not a concern

When to use strong consistency instead (2PC):
  - If the entire saga completes in <100ms and all participants support XA → consider 2PC
  - If any step holds a lock for >500ms (e.g., external payment processor call) → must use Saga
  - Rule of thumb: saga for anything involving external services or long processing time
```

### Cost Model

```
Orchestrator (3 x t3.medium on AWS):
  - Compute: 3 * $0.042/hr = $0.126/hr = ~$91/month

PostgreSQL (saga log, db.t3.medium):
  - $0.068/hr = ~$49/month
  - Storage (18 GB + indexes): $1.8/month
  - Backup (7-day): $0.5/month

Kafka (for choreography, MSK t3.small, 3 brokers):
  - 3 * $0.021/hr = $0.063/hr = ~$45/month
  - Storage (7-day, 120 events/sec * 1KB * 86400 * 7 = ~72 GB): $7/month

Total saga infrastructure: ~$200/month
  - Per saga cost at 100K/day: $200 / (100K * 30) = $0.000067 per saga
  - Business value saved per avoided inconsistency: $50-$500 (customer complaint handling + refund)
  - Break-even: preventing 1 inconsistency per 3 million sagas pays for itself
```

---

## Trade-off Comparison

| Approach                  | Pros                                            | Cons                                                     | Best For                                      |
|---------------------------|-------------------------------------------------|----------------------------------------------------------|-----------------------------------------------|
| Choreography saga         | Loose coupling, no central coordinator         | Hard to debug, no single source of truth for saga state  | Simple 2-3 step flows, highly decoupled teams |
| Orchestration saga        | Clear state, easy debugging, explicit rollback | Orchestrator is central (but rarely a bottleneck)        | Complex multi-step flows, audit requirements  |
| 2PC                       | True atomicity, strong consistency             | Blocking, high latency, requires XA support              | Short transactions (<100ms), XA-capable deps  |
| TCC (Try-Confirm-Cancel)  | Business-semantic reservation, no locks        | Each service must implement 3 methods (try/confirm/cancel)| Inventory reservation, seat booking          |
| Outbox pattern only       | Reliable event publishing                      | Not a full saga — no compensation coordination           | Event publishing alongside local DB writes    |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What is the difference between a saga and a 2PC distributed transaction?
   → 2PC uses a coordinator to lock resources across all participants and commits or rolls back atomically. A saga executes a sequence of local transactions without locking; if a step fails, it runs compensating transactions to undo earlier steps. Sagas are eventually consistent; 2PC is strongly consistent. Sagas are used when steps take too long to hold locks (seconds or minutes).

2. **(L3)** What is a compensating transaction? Give an example.
   → A compensating transaction is the logical inverse of a completed step. For example, if Step 2 charged a credit card, the compensating transaction issues a refund. Unlike a database rollback (which undoes uncommitted changes invisibly), a compensating transaction is a new operation that may be visible in the audit log. The refund appears as a separate ledger entry.

3. **(L4)** Why must each saga step be idempotent?
   → Because orchestrators retry failed or timed-out steps. If the step is not idempotent, a retry could double-charge a customer, double-reserve inventory, or create duplicate shipments. Idempotency is achieved by passing a request_id (UUID) with each step call; the handler checks if request_id was already processed and returns the prior result rather than executing again.

4. **(L4)** What is the outbox pattern and why is it used with sagas?
   → The outbox pattern solves the dual-write problem: a service cannot atomically write to its database AND publish to Kafka in a single operation. Instead, the service writes the event to an outbox table in the same database transaction as its business data update. A relay process (or Debezium CDC) reads committed outbox rows and publishes them to Kafka. This guarantees exactly-once event publishing relative to the database write, which is critical for saga step completion signals.

5. **(L5)** In step 3 of a saga succeeds but step 4 fails, in what order are compensations run and why?
   → Compensations run in reverse order of completed steps: step 3 compensation first, then step 2, then step 1. This is because later steps may depend on outputs of earlier steps. For example, if step 3 created a shipment using a payment_id from step 2, you must cancel the shipment (step 3 compensation) before refunding the payment (step 2 compensation) — otherwise the shipment is orphaned with no payment reference to void. Reverse-order compensation preserves referential integrity.

6. **(L5)** How do you handle a compensating transaction that itself fails?
   → Compensation failures must be retried with exponential backoff — compensation is semantically required for correctness. The saga_step_log records COMPENSATION_FAILED state and triggers a retry schedule. If compensation fails repeatedly (e.g., Inventory Service is down for 24 hours), alert on-call with the saga_id and step details for manual intervention. Design compensating transactions to be simpler and more reliable than forward transactions: use idempotent operations with stable IDs, prefer soft deletes over hard deletes, and avoid external service calls in compensating transactions when possible.

7. **(L5+)** How would you handle a partial failure scenario where step 4 of a 6-step saga times out (unknown outcome), and you cannot determine if it succeeded or failed?
   → This is the "lost response" problem. The orchestrator must distinguish between "step definitely failed" (received error response) and "step outcome unknown" (timeout). For an unknown outcome: (1) Re-query the step handler using the request_id to check its idempotency store — if the step completed, retrieve the result and proceed. (2) If the handler is unreachable, enter a WAITING state for up to N seconds (e.g., 30s) retrying the query. (3) If still unreachable after N seconds, treat as failure and begin compensation. The key design requirement: every step handler must expose a GET /status/{request_id} endpoint that returns the step's outcome by request_id, separate from re-executing the step. This way the orchestrator can distinguish "I don't know the outcome" from "the step failed."

## Anti-patterns / Things NOT to Say

- **"Use choreography for complex sagas because it's more scalable"** — Choreography has no performance advantage over orchestration at this scale (12 sagas/sec). What it sacrifices is debuggability: with choreography, there is no single place to see "saga X is at step 3, step 2 completed." For complex sagas (4+ steps, compensation logic), orchestration is almost always the right choice. Choreography works well only for simple 2-3 step flows between highly decoupled teams.
- **"Rollback the local transaction if a later step fails"** — In a saga, each step commits its local transaction immediately. There is nothing to roll back — the local transaction is already committed. The only way to undo a committed step is a compensating transaction. Confusion between database rollback and saga compensation is a common interview mistake.
- **"Sagas give you the same guarantees as 2PC"** — They do not. During saga execution, intermediate states are visible: inventory is reserved but payment is pending. A concurrent read will see this inconsistency. Sagas trade strong consistency for availability and long-running workflow support. If you need intermediate states to be hidden, use 2PC or a different isolation mechanism.
- **"You don't need the outbox pattern if Kafka is reliable"** — Kafka durability is irrelevant if the service crashes between writing to its database and publishing to Kafka. The service never got to publish the event, so Kafka never received it. The outbox pattern handles this pre-publish failure window. Without it, sagas can silently stall when a step completes locally but the completion event is never published.
- **"Compensation is always possible"** — Some actions are irreversible. An email was already sent. An SMS was delivered. A regulatory report was filed. Design steps that trigger irreversible side effects to be the LAST step of the saga, so compensation never needs to undo them. If an irreversible step must be in the middle, accept that compensation will be incomplete and design the business process accordingly (e.g., send a cancellation email rather than un-sending the confirmation email).

## Python Implementation (sketch)

```python
import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Callable, Optional, Any

class StepStatus(Enum):
    PENDING      = "PENDING"
    COMPLETED    = "COMPLETED"
    FAILED       = "FAILED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED  = "COMPENSATED"

@dataclass
class SagaStep:
    name: str
    action: Callable            # Forward action
    compensate: Callable        # Compensating action
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class OrderSagaOrchestrator:
    """Simplified saga orchestrator for order fulfillment."""

    def __init__(self, saga_log_store):
        self.log = saga_log_store

    def run_order_saga(self, order_id: str, payload: dict) -> bool:
        """Execute order saga: Reserve → Payment → Shipment → Notify → Confirm."""
        saga_id = str(uuid.uuid4())

        steps = [
            SagaStep(
                name="RESERVE_INVENTORY",
                action=lambda p: self._reserve_inventory(p["items"]),
                compensate=lambda r: self._release_inventory(r["reservation_id"])
            ),
            SagaStep(
                name="PROCESS_PAYMENT",
                action=lambda p: self._process_payment(p["customer_id"], p["amount"]),
                compensate=lambda r: self._refund_payment(r["payment_id"])
            ),
            SagaStep(
                name="CREATE_SHIPMENT",
                action=lambda p: self._create_shipment(p["items"], p["address"]),
                compensate=lambda r: self._cancel_shipment(r["shipment_id"])
            ),
            SagaStep(
                name="SEND_NOTIFICATION",
                action=lambda p: self._send_notification(p["customer_id"], "confirmed"),
                compensate=lambda r: None  # Irreversible — no compensation
            ),
        ]

        self.log.write(saga_id, "STARTED", payload)
        completed = []

        # Forward execution
        for step in steps:
            try:
                step.result = step.action(payload)
                step.status = StepStatus.COMPLETED
                completed.append(step)
                self.log.update_step(saga_id, step.name, "COMPLETED", step.result)
                print(f"[Saga {saga_id}] Step {step.name}: COMPLETED")
            except Exception as exc:
                step.status = StepStatus.FAILED
                self.log.update_step(saga_id, step.name, "FAILED", {"error": str(exc)})
                print(f"[Saga {saga_id}] Step {step.name}: FAILED — {exc}")
                # Trigger compensation in reverse order
                self._compensate(saga_id, completed)
                self.log.write(saga_id, "FAILED", payload)
                return False

        self.log.write(saga_id, "COMPLETED", payload)
        return True

    def _compensate(self, saga_id: str, completed_steps: List[SagaStep]):
        """Execute compensating transactions in reverse order."""
        for step in reversed(completed_steps):
            if step.compensate is None or step.result is None:
                continue
            try:
                step.compensate(step.result)
                step.status = StepStatus.COMPENSATED
                self.log.update_step(saga_id, step.name, "COMPENSATED", {})
                print(f"[Saga {saga_id}] Compensated: {step.name}")
            except Exception as exc:
                step.status = StepStatus.FAILED  # Compensation failed — needs manual intervention
                self.log.update_step(saga_id, step.name, "COMPENSATION_FAILED", {"error": str(exc)})
                print(f"[Saga {saga_id}] COMPENSATION FAILED for {step.name}: {exc} — alert on-call")

    # Stubs — real implementations call external services with request_id for idempotency
    def _reserve_inventory(self, items): return {"reservation_id": str(uuid.uuid4())}
    def _release_inventory(self, reservation_id): pass
    def _process_payment(self, customer_id, amount): return {"payment_id": str(uuid.uuid4())}
    def _refund_payment(self, payment_id): pass
    def _create_shipment(self, items, address): return {"shipment_id": str(uuid.uuid4())}
    def _cancel_shipment(self, shipment_id): pass
    def _send_notification(self, customer_id, message): return {"notification_id": str(uuid.uuid4())}
```
