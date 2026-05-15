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


## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│      Subject (Stock Price)                  │
│  ┌──────────────────────────────────────┐   │
│  │  - price: float                      │   │
│  │  - observers: List<Observer>         │   │
│  │                                      │   │
│  │  + attach(observer)                  │   │
│  │  + detach(observer)                  │   │
│  │  + notify()                          │   │
│  │  + setPrice(newPrice)                │   │
│  └──────────────────────────────────────┘   │
│              ↓ notify()                      │
│  ┌──────────────────┬──────────────────┐    │
│  │                  │                  │    │
│  ▼                  ▼                  ▼    │
│ Observer1      Observer2           Observer3│
│ (PortfolioMgr) (AlertService)      (Logger)│
│ + update()     + update()           + update()
└─────────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Should Subject hold strong references to Observers?**
A: Use weak references in distributed systems to prevent memory leaks when observers are GC'd. Strong references in single-process apps are fine. Be careful with circular references (Subject holds Observer, Observer holds Subject).

**Q: What if an observer throws exception during update()?**
A: Catch exceptions and continue notifying other observers (isolated failure). Log exception and alert admin. Option: implement observer timeout, unsubscribe failed observers automatically. Never let one broken observer block others.

**Q: How to pass data to observers—pull or push model?**
A: Push model: notify(data) passes changed state directly. More efficient, explicit. Pull model: notify() calls subject.getData() in observer. Decouples subject from Observer interface. Choose based on data volume and update frequency.

**Q: How does this scale with millions of observers?**
A: Single Subject can't handle millions efficiently (O(n) notification time). Partition into hierarchical subjects or use event broker (message queue). Async notifications via queue decouple subject from observer latency.

## Back-of-Envelope Calculations

For typical UI event system with 1000 observers:
- Storage: 1000 observers × 8 bytes/reference = 8KB per subject
- Throughput: Notify 1000 observers sequentially: 1000 × 1ms = 1s per change (slow)
- Latency: Single observer update = 100-500μs, 1000 total = 100-500ms p99
- Bandwidth: Each notification ~100 bytes × 1000 = 100KB per state change

Optimization: Batch notifications, use weak references, async task queue for heavy observers.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Direct Observer List | Simple, clear | O(n) notifications, tight coupling |
| Event Bus / Message Queue | Async, decoupled, scalable | Extra infrastructure, eventual consistency |
| Weakly-Referenced List | Prevents memory leaks | Observers can disappear silently |

## Follow-up Interview Questions

1. How would you handle observer priority (some observers must execute before others)?
2. What if an observer should only be notified of certain state changes? Implement filters/topics.
3. How to debug observer notification chains with 100+ observers? Add instrumentation/tracing.
4. What's the bottleneck at 10x scale (10K observers)? Notification time O(n). Use event bus/sharding.
5. How would you implement observer unsubscribe safely during iteration?

## Example Scenario Walkthrough

Scenario: Stock price changes, notify portfolio manager and logging service

Initial state:
- Subject: Stock(symbol="AAPL", price=150.0)
- Observer1: PortfolioManager
- Observer2: PriceLogger
- Both attached to Stock

Step 1: Portfolio manager attaches
- Stock.attach(portfolioMgr)
- observers list = [portfolioMgr]

Step 2: Logger attaches
- Stock.attach(logger)
- observers list = [portfolioMgr, logger]

Step 3: Stock price changes
- Stock.setPrice(152.5)
- Old price = 150.0, new price = 152.5
- Call notify()

Step 4: Notify all observers (push model)
- for each observer in observers:
  - observer.update(oldPrice=150.0, newPrice=152.5)

Step 5: PortfolioManager.update() executes
- Recalculate portfolio value
- Rebalance if needed
- Update dashboard: +$2.5 per share

Step 6: PriceLogger.update() executes
- Log: "AAPL: 150.0 → 152.5 at 2026-05-14 14:32:10"
- Send to analytics DB

Step 7: Observer detaches (cleanup)
- Stock.detach(logger)
- observers list = [portfolioMgr]
- Next price change only notifies portfolio manager

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
