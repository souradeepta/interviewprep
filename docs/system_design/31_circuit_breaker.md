# Circuit Breaker Pattern

## Problem Statement
Design a circuit breaker preventing cascading failures when calling failing services.

**States:**
- Closed: Normal operation
- Open: Reject requests
- Half-open: Test if service recovered

## Design

### State Transitions

```
Closed → Open: Failure threshold exceeded
Open → Half-open: After timeout
Half-open → Closed: Test succeeds
Half-open → Open: Test fails
```

### Configuration

```
Failure threshold: N failures trigger open
Timeout: How long to wait before testing
Test request rate: How many to test when half-open
Success threshold: Successes to close
```

### Monitoring

```
Track failure rate
Alert on state changes
Metrics: Success, failure, timeout
Dashboard: Service health
```

## Complexity

| Operation | Time |
|-----------|------|
| Check state | O(1) |
| Record success/failure | O(1) |
| State transition | O(1) |
