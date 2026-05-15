# System Design Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add comprehensive system design section with 13 OOP design problems (caches, rate limiter, URL shortener, parking lot, design patterns, pub-sub, thread pool, load balancer) in Python + Java with detailed documentation, architectural diagrams, and ASCII visualizations.

**Architecture:** Create `docs/system_design/` for detailed walkthroughs, `python/system_design/` and `java/system_design/` for implementations. Each problem gets: markdown doc (problem statement, design walkthrough, ASCII diagrams, trade-offs, complexity), Python implementation (clean code + runnable demo), Java implementation (idiomatic Java).

**Tech Stack:** Python 3.8+, Java 11+, ASCII art for diagrams, Markdown for documentation.

---

## File Structure

```
docs/system_design/
├── README.md                          # Overview, learning path, list of problems
├── 01_lru_cache.md
├── 02_lfu_cache.md
├── 03_rate_limiter.md
├── 04_url_shortener.md
├── 05_parking_lot.md
├── 06_observer_pattern.md
├── 07_strategy_pattern.md
├── 08_factory_pattern.md
├── 09_decorator_pattern.md
├── 10_adapter_pattern.md
├── 11_pub_sub_system.md
├── 12_thread_pool.md
└── 13_load_balancer.md

python/system_design/
├── __init__.py
├── lru_cache.py
├── lfu_cache.py
├── rate_limiter.py
├── url_shortener.py
├── parking_lot.py
├── observer_pattern.py
├── strategy_pattern.py
├── factory_pattern.py
├── decorator_pattern.py
├── adapter_pattern.py
├── pub_sub_system.py
├── thread_pool.py
└── load_balancer.py

java/system_design/
├── LRUCache.java
├── LFUCache.java
├── RateLimiter.java
├── URLShortener.java
├── ParkingLot.java
├── ObserverPattern.java
├── StrategyPattern.java
├── FactoryPattern.java
├── DecoratorPattern.java
├── AdapterPattern.java
├── PubSubSystem.java
├── ThreadPool.java
└── LoadBalancer.java

tests/system_design/
├── test_lru_cache.py
├── test_lfu_cache.py
├── test_rate_limiter.py
├── test_url_shortener.py
├── test_parking_lot.py
├── test_observer_pattern.py
├── test_strategy_pattern.py
├── test_factory_pattern.py
├── test_decorator_pattern.py
├── test_adapter_pattern.py
├── test_pub_sub_system.py
├── test_thread_pool.py
└── test_load_balancer.py
```

---

## Phase 1: Setup & Documentation Infrastructure

### Task 1: Create system_design README and structure

**Files:**
- Create: `docs/system_design/README.md`
- Create: `python/system_design/__init__.py`
- Create: `java/system_design/` directory marker

- [ ] **Step 1: Create system_design README**

Create `docs/system_design/README.md`:

```markdown
# System Design Problems

Comprehensive collection of real-world system design problems solved with detailed walkthroughs, architectural diagrams, and implementations in Python and Java.

## Problems Covered

### Caching Systems
1. **LRU Cache** — Least Recently Used eviction, O(1) all operations
2. **LFU Cache** — Least Frequently Used eviction, track access frequency

### Real-World Systems
3. **Rate Limiter** — Token bucket and sliding window algorithms
4. **URL Shortener** — Encoding, collision handling, distributed generation
5. **Parking Lot System** — OOP design, spot allocation, payment tracking

### Design Patterns (Gang of Four)
6. **Observer Pattern** — Event publishing, loose coupling
7. **Strategy Pattern** — Runtime algorithm switching
8. **Factory Pattern** — Object creation abstraction
9. **Decorator Pattern** — Dynamic behavior extension
10. **Adapter Pattern** — Interface compatibility layer

### Distributed Systems
11. **Pub-Sub System** — Publish-subscribe messaging, topic management
12. **Thread Pool** — Task scheduling, worker threads, queue management
13. **Load Balancer** — Request distribution, health checks, multiple strategies

## How to Use

1. **Read the design doc** (`docs/system_design/NN_*.md`) — understand problem, constraints, trade-offs
2. **Study Python implementation** (`python/system_design/`) — cleaner syntax, easier to follow
3. **Study Java implementation** (`java/system_design/`) — production patterns, type safety
4. **Run the demo** — each implementation has executable `main` block
5. **Run tests** — verify behavior under different scenarios

## Study Path

**Week 1: Caching & Storage**
- Day 1-2: LRU Cache (eviction policy, linked list + hash map)
- Day 3: LFU Cache (frequency tracking, tie-breaking)
- Day 4-5: Rate Limiter (token bucket, time windows)
- Day 6-7: URL Shortener (encoding, uniqueness)

**Week 2: System Design**
- Day 1: Parking Lot (state management, OOP)
- Day 2-4: Design Patterns (Observer, Strategy, Factory, Decorator, Adapter)
- Day 5: Pub-Sub (event distribution)
- Day 6-7: Thread Pool (concurrency, work queues)

**Week 3: Advanced Systems**
- Day 1-2: Load Balancer (multiple algorithms)
- Day 3-5: Combined problems (rate limiting + caching, etc.)
- Day 6-7: Mock system design interviews

## Common Patterns Across Problems

| Problem | Key Data Structure | Time Complexity | Space Complexity |
|---------|-------------------|-----------------|------------------|
| LRU Cache | Doubly Linked List + HashMap | O(1) | O(capacity) |
| LFU Cache | HashMap + Min-Heap + Frequency Map | O(1) | O(capacity) |
| Rate Limiter (Token Bucket) | Deque | O(1) | O(capacity) |
| URL Shortener | HashMap | O(1) | O(n) |
| Parking Lot | HashMap | O(1) | O(spots) |
| Thread Pool | Queue | O(1) | O(tasks) |
| Load Balancer | Array + Index | O(1) | O(servers) |
```

- [ ] **Step 2: Create python/system_design/__init__.py**

Create `python/system_design/__init__.py`:

```python
"""System Design Problems - Python implementations"""

__all__ = [
    'LRUCache',
    'LFUCache',
    'RateLimiter',
    'URLShortener',
    'ParkingLot',
    'ObserverPattern',
    'StrategyPattern',
    'FactoryPattern',
    'DecoratorPattern',
    'AdapterPattern',
    'PubSubSystem',
    'ThreadPool',
    'LoadBalancer',
]
```

- [ ] **Step 3: Update main README to reference system_design**

Read `/home/sbisw/github/datastructures/README.md` and add section after "Problem-Solving Guides":

```markdown
### System Design Problems

For real-world design problems (caching, rate limiting, parking lot, design patterns, distributed systems), see [`docs/system_design/`](docs/system_design/README.md).

| Problem | Category | Difficulty |
|---------|----------|-----------|
| LRU/LFU Cache | Caching | ★★★★☆ |
| Rate Limiter | Real-world Systems | ★★★★☆ |
| URL Shortener | Real-world Systems | ★★★★☆ |
| Parking Lot | OOP Design | ★★★★☆ |
| Design Patterns (5) | Patterns | ★★★☆☆ |
| Pub-Sub System | Distributed | ★★★★★ |
| Thread Pool | Concurrency | ★★★★★ |
| Load Balancer | Distributed | ★★★★★ |
```

- [ ] **Step 4: Commit infrastructure**

```bash
git add docs/system_design/README.md python/system_design/__init__.py README.md
git commit -m "chore: add system design section infrastructure"
```

---

## Phase 2: LRU Cache

### Task 2: LRU Cache documentation

**Files:**
- Create: `docs/system_design/01_lru_cache.md`

- [ ] **Step 1: Write LRU Cache design document**

Create `docs/system_design/01_lru_cache.md`:

```markdown
# LRU Cache

## Problem Statement

Implement an LRU (Least Recently Used) Cache with fixed capacity. When capacity is exceeded, evict the least recently used item.

**Operations:**
- `get(key)` — return value, mark as recently used
- `put(key, value)` — insert/update, evict LRU if over capacity

**Constraints:**
- Both operations must be O(1)
- Capacity is fixed
- Track access order, not insertion order

## Design

### Data Structures

```
Doubly Linked List (tracks order)
    head <-> Node1 <-> Node2 <-> Node3 <-> tail
    |most recent            least recent|

HashMap (for O(1) lookup)
    {key -> Node*}
```

**Why this works:**
- Doubly linked list maintains insertion/access order
- Removing node from middle and adding to front = O(1) with pointers
- HashMap gives O(1) access to node

### Key Operations

```
GET(3):
Before: 1 <-> 2 <-> 3 <-> 4
After:  1 <-> 2 <-> 4 <-> 3  (3 moves to front = most recent)

PUT(5) with capacity=4:
Before: 1 <-> 2 <-> 4 <-> 3
After:  2 <-> 4 <-> 3 <-> 5  (evict 1, add 5 at front)
```

### Complexity

| Operation | Time | Space |
|-----------|------|-------|
| get | O(1) | — |
| put | O(1) | — |
| Space | — | O(capacity) |

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Doubly LL + HashMap | O(1) all ops, simple | More memory overhead per node |
| OrderedDict (Python) | Built-in, clean | Language-specific |
| Single LL + HashMap | Less memory | O(n) to find/remove node |

## Edge Cases

1. Capacity = 1: only one item at a time
2. Duplicate keys: update value, move to front
3. Access pattern: get should update recency
4. Empty cache: get returns None/null
```

- [ ] **Step 2: Commit doc**

```bash
git add docs/system_design/01_lru_cache.md
git commit -m "docs: add LRU Cache design documentation"
```

---

### Task 3: LRU Cache Python implementation

**Files:**
- Create: `python/system_design/lru_cache.py`
- Create: `tests/system_design/test_lru_cache.py`

- [ ] **Step 1: Write test file**

Create `tests/system_design/test_lru_cache.py`:

```python
import pytest
from python.system_design.lru_cache import LRUCache


class TestLRUCache:
    def test_get_and_put(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        assert cache.get(1) == 1
        
    def test_eviction(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1  # move 1 to front
        cache.put(3, 3)  # evict 2
        assert cache.get(2) == -1  # 2 is gone
        assert cache.get(3) == 3
        
    def test_duplicate_key(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(1, 10)  # update
        assert cache.get(1) == 10
        
    def test_get_updates_recency(self):
        cache = LRUCache(3)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)
        cache.get(1)  # access 1, make it recent
        cache.put(4, 4)  # evict 2 (least recent), not 1
        assert cache.get(2) == -1
        assert cache.get(1) == 1
        
    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put(1, 1)
        assert cache.get(1) == 1
        cache.put(2, 2)
        assert cache.get(1) == -1
        assert cache.get(2) == 2
```

- [ ] **Step 2: Write Python implementation**

Create `python/system_design/lru_cache.py`:

```python
"""LRU Cache - Least Recently Used eviction policy"""

from collections import deque


class Node:
    """Doubly linked list node"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """O(1) LRU Cache using doubly linked list + hash map"""
    
    def __init__(self, capacity: int):
        """
        Initialize cache with fixed capacity.
        
        Args:
            capacity: Maximum number of items
        """
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.head = Node(0, 0)  # dummy head (most recent)
        self.tail = Node(0, 0)  # dummy tail (least recent)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def get(self, key: int) -> int:
        """
        Get value and mark as recently used.
        
        Returns:
            Value if exists, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair."""
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)
            
            if len(self.cache) > self.capacity:
                # Remove least recently used (before tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
    
    def _remove(self, node):
        """Remove node from linked list"""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_front(self, node):
        """Add node after head (most recent)"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node


if __name__ == "__main__":
    # Demo
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(f"get(1): {cache.get(1)}")  # 1
    cache.put(3, 3)
    print(f"get(2): {cache.get(2)}")  # -1 (evicted)
    cache.put(4, 4)
    print(f"get(1): {cache.get(1)}")  # -1 (evicted)
    print(f"get(3): {cache.get(3)}")  # 3
    print(f"get(4): {cache.get(4)}")  # 4
```

- [ ] **Step 3: Run tests**

```bash
cd /home/sbisw/github/datastructures
python -m pytest tests/system_design/test_lru_cache.py -v
```

Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add python/system_design/lru_cache.py tests/system_design/test_lru_cache.py
git commit -m "feat: implement LRU Cache in Python"
```

---

### Task 4: LRU Cache Java implementation

**Files:**
- Create: `java/system_design/LRUCache.java`

- [ ] **Step 1: Write Java implementation**

Create `java/system_design/LRUCache.java`:

```java
import java.util.HashMap;
import java.util.Map;

/**
 * LRU Cache - O(1) all operations using doubly linked list + HashMap
 */
public class LRUCache {
    
    private static class Node {
        int key;
        int value;
        Node prev;
        Node next;
        
        Node(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }
    
    private final int capacity;
    private final Map<Integer, Node> cache;
    private final Node head;  // dummy, most recent
    private final Node tail;  // dummy, least recent
    
    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();
        this.head = new Node(0, 0);
        this.tail = new Node(0, 0);
        head.next = tail;
        tail.prev = head;
    }
    
    public int get(int key) {
        if (!cache.containsKey(key)) {
            return -1;
        }
        Node node = cache.get(key);
        remove(node);
        addToFront(node);
        return node.value;
    }
    
    public void put(int key, int value) {
        if (cache.containsKey(key)) {
            Node node = cache.get(key);
            node.value = value;
            remove(node);
            addToFront(node);
        } else {
            Node node = new Node(key, value);
            cache.put(key, node);
            addToFront(node);
            
            if (cache.size() > capacity) {
                Node lru = tail.prev;
                remove(lru);
                cache.remove(lru.key);
            }
        }
    }
    
    private void remove(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
    
    private void addToFront(Node node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }
    
    public static void main(String[] args) {
        LRUCache cache = new LRUCache(2);
        cache.put(1, 1);
        cache.put(2, 2);
        System.out.println("get(1): " + cache.get(1));  // 1
        cache.put(3, 3);
        System.out.println("get(2): " + cache.get(2));  // -1
        cache.put(4, 4);
        System.out.println("get(1): " + cache.get(1));  // -1
        System.out.println("get(3): " + cache.get(3));  // 3
        System.out.println("get(4): " + cache.get(4));  // 4
    }
}
```

- [ ] **Step 2: Compile and run**

```bash
cd /home/sbisw/github/datastructures/java/system_design
javac LRUCache.java
java LRUCache
```

Expected: Demo output shows correct values

- [ ] **Step 3: Commit**

```bash
git add java/system_design/LRUCache.java
git commit -m "feat: implement LRU Cache in Java"
```

---

## Phase 3: LFU Cache (Similar structure - compress for brevity)

### Task 5: LFU Cache - Doc, Python, Java, Tests

**Note:** Follow same pattern as LRU Cache. LFU differs in:
- Track frequency count per key
- Evict least frequently used (break ties by least recently used)
- Key data structures: `freq_map` (key -> freq), `freq_list` (freq -> OrderedDict of keys)

Files to create:
- `docs/system_design/02_lfu_cache.md`
- `python/system_design/lfu_cache.py`
- `tests/system_design/test_lfu_cache.py`
- `java/system_design/LFUCache.java`

This task batch includes:
- [ ] Write LFU design doc (explain frequency tracking, ties)
- [ ] Write Python tests and implementation
- [ ] Run tests
- [ ] Write Java implementation and compile
- [ ] Commit all files

---

## Phase 4: Rate Limiter

### Task 6: Rate Limiter - Doc, Python, Java, Tests

**Implementations:** Token Bucket + Sliding Window Algorithms

Key concepts:
- Token bucket: refill tokens at rate, consume on request
- Sliding window: count requests in last N seconds
- Distributable tokens per second or per minute

Files to create:
- `docs/system_design/03_rate_limiter.md`
- `python/system_design/rate_limiter.py` (TokenBucketLimiter, SlidingWindowLimiter)
- `tests/system_design/test_rate_limiter.py`
- `java/system_design/RateLimiter.java`

This task batch includes:
- [ ] Write rate limiter design doc with ASCII diagrams
- [ ] Write Python implementation (both algorithms)
- [ ] Write and run tests
- [ ] Write Java implementation
- [ ] Commit all

---

## Phase 5: URL Shortener

### Task 7: URL Shortener - Doc, Python, Java, Tests

Key concepts:
- Base62 encoding
- Collision handling
- Distributed generation with sharding hints
- Reverse mapping (short -> long)

Files to create:
- `docs/system_design/04_url_shortener.md`
- `python/system_design/url_shortener.py` (encode/decode, distributed generation)
- `tests/system_design/test_url_shortener.py`
- `java/system_design/URLShortener.java`

This task batch includes:
- [ ] Write URL shortener design doc
- [ ] Write Python implementation
- [ ] Write and run tests
- [ ] Write Java implementation
- [ ] Commit all

---

## Phase 6: Parking Lot System

### Task 8: Parking Lot System - Doc, Python, Java, Tests

Key concepts:
- Level/floor abstraction
- Spot availability tracking
- Vehicle types (compact, regular, large)
- Allocation strategy (nearest available)

Files to create:
- `docs/system_design/05_parking_lot.md`
- `python/system_design/parking_lot.py` (ParkingLot, Level, Spot, Vehicle)
- `tests/system_design/test_parking_lot.py`
- `java/system_design/ParkingLot.java`

This task batch includes:
- [ ] Write parking lot design doc with ASCII layout
- [ ] Write Python implementation with OOP design
- [ ] Write and run tests
- [ ] Write Java implementation
- [ ] Commit all

---

## Phase 7: Design Patterns (5 patterns)

### Task 9: Observer Pattern - Doc, Python, Java

Files to create:
- `docs/system_design/06_observer_pattern.md`
- `python/system_design/observer_pattern.py` (Subject, Observer, ConcreteObserver)
- `java/system_design/ObserverPattern.java`

### Task 10: Strategy Pattern - Doc, Python, Java

Files to create:
- `docs/system_design/07_strategy_pattern.md`
- `python/system_design/strategy_pattern.py` (Context, Strategy, ConcreteStrategy)
- `java/system_design/StrategyPattern.java`

### Task 11: Factory Pattern - Doc, Python, Java

Files to create:
- `docs/system_design/08_factory_pattern.md`
- `python/system_design/factory_pattern.py` (Factory, ConcreteFactory)
- `java/system_design/FactoryPattern.java`

### Task 12: Decorator Pattern - Doc, Python, Java

Files to create:
- `docs/system_design/09_decorator_pattern.md`
- `python/system_design/decorator_pattern.py` (Component, Decorator, ConcreteDecorator)
- `java/system_design/DecoratorPattern.java`

### Task 13: Adapter Pattern - Doc, Python, Java

Files to create:
- `docs/system_design/10_adapter_pattern.md`
- `python/system_design/adapter_pattern.py` (Target, Adaptee, Adapter)
- `java/system_design/AdapterPattern.java`

Each design pattern task batch includes:
- [ ] Write pattern design doc with UML diagram (ASCII)
- [ ] Write Python implementation with example usage
- [ ] Write Java implementation
- [ ] Commit all

---

## Phase 8: Pub-Sub System

### Task 14: Pub-Sub System - Doc, Python, Java, Tests

Key concepts:
- Publisher, Subscriber, Topic
- Event queue per topic
- Thread-safe subscription management
- Subscriber notification

Files to create:
- `docs/system_design/11_pub_sub_system.md`
- `python/system_design/pub_sub_system.py` (PubSubSystem, Publisher, Subscriber, Topic)
- `tests/system_design/test_pub_sub_system.py`
- `java/system_design/PubSubSystem.java`

This task batch includes:
- [ ] Write pub-sub design doc
- [ ] Write Python implementation (thread-safe)
- [ ] Write and run tests
- [ ] Write Java implementation
- [ ] Commit all

---

## Phase 9: Thread Pool

### Task 15: Thread Pool - Doc, Python, Java, Tests

Key concepts:
- Worker threads
- Task queue
- Thread lifecycle (start, shutdown, await)
- Task execution

Files to create:
- `docs/system_design/12_thread_pool.md`
- `python/system_design/thread_pool.py` (ThreadPool, Worker, Task)
- `tests/system_design/test_thread_pool.py`
- `java/system_design/ThreadPool.java`

This task batch includes:
- [ ] Write thread pool design doc
- [ ] Write Python implementation using threading
- [ ] Write and run tests
- [ ] Write Java implementation using Executor framework
- [ ] Commit all

---

## Phase 10: Load Balancer

### Task 16: Load Balancer - Doc, Python, Java, Tests

Key concepts:
- Multiple algorithms (Round Robin, Least Connections, Random)
- Server health tracking
- Server selection strategy

Files to create:
- `docs/system_design/13_load_balancer.md`
- `python/system_design/load_balancer.py` (LoadBalancer, BalancingStrategy)
- `tests/system_design/test_load_balancer.py`
- `java/system_design/LoadBalancer.java`

This task batch includes:
- [ ] Write load balancer design doc
- [ ] Write Python implementation (3+ algorithms)
- [ ] Write and run tests
- [ ] Write Java implementation
- [ ] Commit all

---

## Phase 11: Final Integration

### Task 17: Update main README and system design README

- [ ] Add system design section to main README with table of all 13 problems
- [ ] Create comprehensive system design README with learning path
- [ ] Link all implementations from docs

### Task 18: Final verification and commit

- [ ] Run all tests to ensure no regressions
- [ ] Verify all files created match file structure
- [ ] Final commit with summary

---

## Summary

**Total deliverables:**
- 13 detailed design documents (ASCII diagrams, trade-offs, complexity analysis)
- 13 Python implementations (clean, with demos)
- 13 Java implementations (idiomatic, with main blocks)
- 10 test suites (LRU, LFU, Rate Limiter, URL Shortener, Parking Lot, Pub-Sub, Thread Pool, Load Balancer, + pattern tests)

**Time estimate:** 16-20 tasks, ~3-4 hours of focused implementation
```
