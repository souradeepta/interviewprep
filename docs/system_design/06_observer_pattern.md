# Observer Pattern

## Problem Statement

Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified automatically.

**Use Cases:**
- Event systems (button clicks, form changes)
- MVC frameworks (model changes notify views)
- Real-time data updates (stock price changes)
- Publish-subscribe systems

## Design

### Class Diagram

```
        Subject (Observable)
        ├── attach(Observer)
        ├── detach(Observer)
        └── notify()
             │
             ├─→ Observer.update()
             ├─→ Observer.update()
             └─→ Observer.update()
```

### Key Components

```
Subject: Maintains list of observers, notifies on state change
Observer: Interface with update() method
ConcreteObserver: Implements Observer, performs action on update
ConcreteSubject: Concrete Subject that holds state
```

### Interaction

```
1. Observer registers with Subject (attach)
2. Subject state changes
3. Subject calls notify() -> calls update() on all observers
4. Each observer reacts to the change independently
```

## Trade-offs

| Pro | Con |
|-----|-----|
| Loose coupling | Order of notifications unpredictable |
| Dynamic subscriptions | Memory overhead (observer lists) |
| Supports broadcast | Debugging can be harder |
| Open/Closed principle | Observer must check what changed |

## Complexity

| Operation | Time |
|-----------|------|
| attach | O(1) |
| detach | O(n) where n=observers |
| notify | O(n) |
