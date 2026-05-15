# Chain of Responsibility Pattern

## Overview
Passes request along chain of handlers. Each handler decides to process or pass to next.

## Problem Statement
Multiple objects can handle request, but only one should. Want to avoid coupling between requester and handler.

## Solution
Create chain of handlers. Request passes down until someone handles it.

## When to Use

**Use Chain of Responsibility when:**
- Multiple objects may handle request
- Handler not known in advance (runtime determination)
- Avoid coupling between sender and receiver
- Log messages with different levels (ERROR → WARN → INFO)
- Approval workflows (Manager → Director → VP)

**Examples:**
- Exception handling in try-catch chains
- Logging levels (critical → warning → info → debug)
- Event handling in GUI (button → panel → window → app)
- Authentication/authorization checks
- Help system (button help → panel help → app help)

## Real-World Scenarios

**Exception Handling:**
```
Try block catches specific exceptions
If handled, done
If not caught, passes to next handler
Finally reaches top-level handler
```

**Approval Workflow:**
```
Expense report < $100: manager approves
Expense < $1000: director approves
Expense < $10000: VP approves
Expense > $10000: CEO approves
```

## Implementation Patterns

### Handler Chain
```python
class Handler:
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def handle(self, request):
        pass

class ConcreteHandlerA(Handler):
    def handle(self, request):
        if request == "A":
            return f"Handled by A"
        elif self.next_handler:
            return self.next_handler.handle(request)
        return "No handler"

class ConcreteHandlerB(Handler):
    def handle(self, request):
        if request == "B":
            return f"Handled by B"
        elif self.next_handler:
            return self.next_handler.handle(request)
        return "No handler"

# Usage
handler_a = ConcreteHandlerA()
handler_b = ConcreteHandlerB()
handler_a.set_next(handler_b)

print(handler_a.handle("A"))  # Handled by A
print(handler_a.handle("B"))  # Handled by B (passed down)
print(handler_a.handle("C"))  # No handler
```

## Trade-Offs

**Pros:**
- Decouples sender from receiver
- Flexible handler ordering
- Easy to add new handlers
- Dynamic chain construction

**Cons:**
- Request not guaranteed handled (silence)
- Hard to debug (request path unclear)
- Performance (passes through multiple handlers)
- Chain setup complexity

## Production Considerations

- Ensure request handled somewhere (log unhandled requests)
- Keep handlers focused (single responsibility)
- Document chain order (what handles what)
- Monitor handler performance (which is slow?)
- Test with missing handlers (what if chain incomplete?)
