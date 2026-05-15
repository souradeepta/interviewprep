# Saga Pattern

## Problem Statement
Design long-running distributed transactions with compensation.

**Types:**
- Orchestration: Coordinator service
- Choreography: Event-driven

## Design

### Orchestration Saga

```
1. Coordinator receives request
2. Call Service A
3. Wait for A's response
4. Call Service B
5. On failure: Compensate A
```

### Choreography Saga

```
1. Service A starts
2. Publishes event
3. Service B listens, executes
4. Publishes next event
5. On failure: Publish compensation
```

### Compensation Strategy

```
Undo operation: Reverse transaction
Backward compensation: Fix state
Forward compensation: Continue with mitigation
```

### Ordering Guarantees

```
Idempotent operations: Safe to retry
Deterministic: Same input → Same output
Timeout handling: Assume failure after timeout
```


## Architecture Diagram

```
┌───────────────────────────────┐
│   Saga (Long-running Txn)    │
│  Choreography                 │
│  - Event-driven, no orchestor │
│  - Services listen & react    │
│  Orchestration                │
│  - Saga controller            │
│  - Defines flow explicitly    │
│  Compensating Txns            │
│  - Undo each step on failure  │
│  - Reverse order              │
└───────────────────────────────┘
```

## Common Questions & Answers

**Q: Choreography vs Orchestration?** A: Chore: loose coupling, hard debug. Orch: clear flow, SPOF. Hybrid.

**Q: Visibility?** A: Trace IDs for sagas. Event sourcing for history. Monitor latencies, failures.

**Q: Compensation complexity?** A: Simple reverse. Complex: partial states. Test thoroughly.

**Q: Idempotency?** A: Retry compensation multiple times. Track event IDs, no double-charge.

## Back-of-Envelope Calculations

Order saga: 5 steps, 200ms avg. Total: 1s happy. Retry: 7s worst case. Throughput: 1000 sagas/sec.
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Saga (async) | Eventual, scalable | Complex debug |
| 2PC (sync) | Strong, simple | Blocking |
| Batch | Decoupled | Delayed |

## Follow-up Interview Questions

1. Deadlock (circular comp)? 2. State machine definition? 3. Test failures? 4. Service latency bottleneck? 5. Migrate from 2PC?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Pattern | Latency | Coupling |
|---------|---------|----------|
| Orchestration | Higher | Low |
| Choreography | Lower | High |
