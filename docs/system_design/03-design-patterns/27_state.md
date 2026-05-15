# State Pattern

## Overview
Allows object to alter behavior when state changes. Object appears to change class.

## Problem Statement
Object behavior varies significantly by state. Large conditionals checking state throughout code.

## Solution
Create state object for each state. Context delegates to current state.

## When to Use

**Use State when:**
- Behavior varies significantly by state
- Large state-based conditionals throughout code
- Many state transitions
- State-specific logic isolated

**Examples:**
- Order workflow (pending → paid → shipped → delivered)
- Connection state machine (connecting → connected → disconnected)
- Document lifecycle (draft → review → published)
- TCP connection states (listen → established → closed)
- Player states in game (idle → running → jumping)

## Real-World Scenarios

**Order Workflow:**
```
Pending: can cancel, pay
Paid: can ship, refund (no cancel)
Shipped: can track, receive
Delivered: can review, return

Each state defines allowed operations.
Behavior changes based on state.
Transitions explicit.
```

## When NOT to Use

Avoid when: few states, limited transitions, simple behavior differences.

## Implementation Patterns

### Order State Machine
```python
class OrderState:
    def cancel(self, order):
        raise Exception("Cannot cancel")

class PendingState(OrderState):
    def cancel(self, order):
        order.state = CancelledState()
        return "Order cancelled"

    def pay(self, order):
        order.state = PaidState()
        return "Payment processed"

class PaidState(OrderState):
    def ship(self, order):
        order.state = ShippedState()
        return "Order shipped"

class Order:
    def __init__(self):
        self.state = PendingState()

    def pay(self):
        return self.state.pay(self)
```

## Trade-Offs

**Pros:** Eliminates long conditionals, encapsulates behavior, easy to add states

**Cons:** Many classes, overkill for few states, complex logic

## Production Considerations

- Document state transitions (state diagram)
- Prevent invalid transitions
- Monitor state distribution
- Test all state paths
