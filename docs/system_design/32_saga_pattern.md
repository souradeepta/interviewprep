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

## Complexity

| Pattern | Latency | Coupling |
|---------|---------|----------|
| Orchestration | Higher | Low |
| Choreography | Lower | High |
