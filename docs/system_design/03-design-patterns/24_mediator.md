# Mediator Pattern

## Overview
Encapsulates how objects interact. Objects communicate through mediator instead of directly.

## Problem Statement
Objects directly reference each other, creating tight coupling. Complex interactions between many objects.

## Solution
Create mediator object. All interactions go through mediator.

## When to Use

**Use Mediator when:**
- Objects heavily interconnected (coupling issues)
- Complex interactions between multiple objects
- Reusability limited by dependencies
- Need centralized control logic
- Behavior depends on multiple objects' state

**Examples:**
- Dialog with multiple controls (button, checkbox, textbox communicate through dialog)
- Chat room (users communicate through chat room, not directly)
- Air traffic control (planes communicate through controller, not directly)
- UI component interaction (form mediates between fields)

## Real-World Scenarios

**Dialog Mediator:**
```
Dialog contains button, textbox, checkbox
Button enables/disables based on checkbox
Textbox updates button label
Without mediator: button ← checkbox, textbox directly (complex)
With mediator: all talk to dialog, dialog coordinates
```

**Chat Room Mediator:**
```
Users don't send messages directly to each other
Users send to chat room
Chat room broadcasts to appropriate users
Decouples users from knowing each other
```

## Implementation Patterns

### Mediator Coordination
```python
class Mediator:
    def send_message(self, message, sender):
        pass

class Colleague:
    def __init__(self, mediator, name):
        self.mediator = mediator
        self.name = name

    def send(self, message):
        self.mediator.send_message(message, self)

    def receive(self, message):
        print(f"{self.name} received: {message}")

class ConcreteMediator(Mediator):
    def __init__(self):
        self.colleagues = []

    def add_colleague(self, colleague):
        self.colleagues.append(colleague)

    def send_message(self, message, sender):
        for colleague in self.colleagues:
            if colleague != sender:
                colleague.receive(message)

# Usage
mediator = ConcreteMediator()
user1 = Colleague(mediator, "Alice")
user2 = Colleague(mediator, "Bob")
mediator.add_colleague(user1)
mediator.add_colleague(user2)

user1.send("Hello!")  # Bob receives
```

## Trade-Offs

**Pros:**
- Decouples objects (less coupling)
- Centralizes control logic
- Reusability improved
- Easy to modify interactions

**Cons:**
- Mediator becomes complex ("God object")
- Extra indirection (performance)
- Harder to understand flow (centralized)
- Testing complex (mediator's responsibility)

## Production Considerations

- Keep mediator focused (don't add unrelated logic)
- Monitor mediator complexity (if too complex, redesign)
- Document interaction patterns
- Consider alternative designs (observer often simpler)
- Test thoroughly (many interaction paths)
