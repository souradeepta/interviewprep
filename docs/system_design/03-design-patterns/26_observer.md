# Observer Pattern

## Overview
Defines one-to-many dependency where change to one object notifies dependents automatically.

## Problem Statement
Objects tightly coupled when one must notify many others of state change.

## Solution
Create subject that maintains observer list. Notifies observers when state changes.

## When to Use

**Use Observer when:**
- Objects loosely coupled (don't know details)
- Change to one affects many (event-driven)
- Dynamic subscription (add/remove observers)
- Broadcast notifications (MVC architecture)

**Examples:**
- Event systems (button click notifies listeners)
- MVC: model notifies views of changes
- Reactive programming (data changes flow to subscribers)
- Stock ticker (price changes notify investors)
- Chat: user joins, notifies others

## Real-World Scenarios

**MVC Pattern:**
```
Model changes: notifies views
Views update automatically
Controller updates model
Views don't know about model details
```

**Event System:**
```
Button clicked: notifies listeners
Listeners don't know about button
Button doesn't know about listeners
Decoupled communication
```

## Implementation Patterns

### Subject and Observer
```python
class Observer:
    def update(self, subject):
        pass

class Subject:
    def __init__(self):
        self.observers = []
        self.state = None

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)

    def set_state(self, state):
        self.state = state
        self.notify()

class ConcreteObserver(Observer):
    def update(self, subject):
        print(f"Observer notified: state = {subject.state}")

# Usage
subject = Subject()
observer1 = ConcreteObserver()
observer2 = ConcreteObserver()

subject.attach(observer1)
subject.attach(observer2)
subject.set_state("New State")  # Both notified
```

## Trade-Offs

**Pros:**
- Loose coupling (subject/observer independent)
- Dynamic subscriptions (add/remove at runtime)
- Broadcast communication (one-to-many)
- Push model (automatic updates)

**Cons:**
- Observer notification order unpredictable
- Memory leaks (forgotten detach())
- Performance (many observers)
- Hard to debug (implicit dependencies)

## Production Considerations

- Ensure observers always detach (prevent leaks)
- Order notifications carefully (if it matters)
- Make notifications synchronous or async (document)
- Handle exceptions in observers (don't crash subject)
- Monitor observer count (too many = performance)
