# Distributed Transactions

## Problem Statement
Design a system coordinating transactions across multiple databases or services.

**Approaches:**
- 2-Phase Commit: Atomic across services
- Saga Pattern: Long-running distributed tx
- Event Sourcing: Immutable event log

## Design

### 2-Phase Commit

```
Phase 1 (Prepare): All nodes ready?
Phase 2 (Commit): All nodes commit
Blocking: Waits for slowest node
```

### Saga Pattern

```
Orchestration: Coordinator directs steps
Choreography: Services listen to events
Compensation: Undo on failure
Eventually consistent
```

### Conflict Resolution

```
Optimistic locking: Check version on update
Pessimistic locking: Lock row before access
Last-write-wins: Latest timestamp wins
Custom logic: Application-specific
```

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| 2PC | Atomic | Blocking, slow |
| Saga | Flexible | Complex, eventual consistency |
| ES | Audit trail | Storage overhead |
