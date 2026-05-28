# Observer Pattern

**Level:** L4
**Time to read:** ~15 min

## Problem Statement

You have a stock price feed and multiple displays (mobile app, web dashboard, email alerts) that all need to update when the price changes. Directly coupling each display to the price source creates a maintenance nightmare — adding a new display requires modifying the source. Observer decouples producers from consumers so any number of subscribers can react to state changes without the source knowing who they are.

## Structure

```
         Subject (Observable)
        ┌──────────────────────┐
        │ - observers: list    │
        │ + attach(observer)   │
        │ + detach(observer)   │
        │ + notify()           │
        └──────────┬───────────┘
                   │ notifies
        ┌──────────┼──────────────┐
        ▼          ▼              ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │Observer A│ │Observer B│ │Observer C│
  │+ update()│ │+ update()│ │+ update()│
  └──────────┘ └──────────┘ └──────────┘

  ConcreteSubject                  ConcreteObserver
  ┌──────────────────┐             ┌──────────────────┐
  │ - state          │──notifies──►│ - subject ref    │
  │ + get_state()    │             │ + update(data)   │
  │ + set_state(val) │             └──────────────────┘
  └──────────────────┘
```

## Python Implementation

```python
from abc import ABC, abstractmethod
from typing import Any

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: Any) -> None:
        pass

class Subject:
    def __init__(self):
        self._observers: dict[str, list[Observer]] = {}

    def attach(self, event: str, observer: Observer) -> None:
        self._observers.setdefault(event, []).append(observer)

    def detach(self, event: str, observer: Observer) -> None:
        self._observers.get(event, []).remove(observer)

    def notify(self, event: str, data: Any) -> None:
        for observer in self._observers.get(event, []):
            observer.update(event, data)

class StockFeed(Subject):
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
        self._price = 0.0

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value: float):
        old = self._price
        self._price = value
        if abs(value - old) / max(old, 1) > 0.05:   # >5% move
            self.notify("price_spike", {"symbol": self.symbol, "price": value})
        self.notify("price_update", {"symbol": self.symbol, "price": value})

class MobileDisplay(Observer):
    def update(self, event: str, data: Any) -> None:
        print(f"[Mobile] {data['symbol']}: ${data['price']:.2f}")

class EmailAlert(Observer):
    def __init__(self, threshold: float):
        self.threshold = threshold

    def update(self, event: str, data: Any) -> None:
        if event == "price_spike":
            print(f"[Email Alert] SPIKE on {data['symbol']}: ${data['price']:.2f}")

# Usage
feed = StockFeed("AAPL")
mobile = MobileDisplay()
alert = EmailAlert(threshold=150.0)

feed.attach("price_update", mobile)
feed.attach("price_spike", alert)

feed.price = 150.0   # Mobile gets update
feed.price = 162.0   # Both get notified (>5% spike)
feed.detach("price_update", mobile)
feed.price = 165.0   # Only email alert fires
```

## Real-World Uses

- **Django signals:** `post_save`, `pre_delete` are Observer hooks — models broadcast events, handlers subscribe without coupling.
- **React useState / Redux:** Component re-renders are observers on state slices; the store notifies only affected subscribers.
- **DOM events:** `element.addEventListener("click", handler)` — the DOM element is the Subject.
- **Kafka consumer groups:** Producers write to topics (Subject); multiple consumer groups (Observers) read independently at their own pace.

## When to Apply

**Apply Observer when:**
- One object's state change must cascade to an unknown number of dependents
- You want loose coupling — Subject shouldn't know observer types
- You need dynamic subscription (attach/detach at runtime)
- You're building event-driven or reactive systems

**Do NOT use when:**
- The notification chain is deep and unpredictable — risk of cascading updates that are hard to debug
- Observers need guaranteed ordering — Observer gives no delivery order guarantee
- You need synchronous request/response — use direct method calls instead
- Performance is critical at millions/sec — use ring buffers or lock-free queues (LMAX Disruptor)

## Common Interview Questions

**Q1. What's the difference between Observer and Pub-Sub?**
Observer: Subject knows its observers directly (in-process, tight coupling on registration). Pub-Sub: a message broker sits between producers and consumers — publishers don't know subscribers exist. Kafka is Pub-Sub; Django signals are Observer.

**Q2. How do you prevent memory leaks with Observer?**
Observers hold references that prevent GC. Use weak references (`weakref.ref`) for observers, or enforce explicit `detach()` calls (e.g., context managers). Java's `WeakHashMap` solves this automatically.

**Q3. How would you make Observer thread-safe?**
Protect the observer list with a `threading.Lock` on `attach`/`detach`/`notify`. Copy the list before iterating (`snapshot = list(self._observers)`) to avoid modification during notification.

**Q4. Can an Observer trigger another notification cycle?**
Yes — this causes cascading/infinite loops. Guard with a `_notifying` flag, or use an event queue (async dispatch) to break the cycle. React's batched state updates prevent this.

**Q5. How does Observer relate to the MVC pattern?**
Model is the Subject. View is the Observer. Controller mutates Model, which notifies View(s) via Observer. This keeps rendering logic out of business logic.

## Related Patterns

- **Mediator:** Instead of Subject→Observers, all communication routes through a central Mediator. Use when observer interactions get complex.
- **Event Queue / Async Observer:** Decouple notification from processing time; observers pull from queue (Kafka, RabbitMQ).
- **Command + Observer:** Commands are queued and replayed; Observers react to command execution — common in CQRS systems.
- See `docs/03-system-design/03-design-patterns/26_observer.md` for deeper MVC/reactive examples.
