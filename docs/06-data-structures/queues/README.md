# Queues — FIFO Order, O(1) Enqueue/Dequeue

**Level:** L3-L4
**Time to read:** ~20 min

First-In, First-Out. The data structure behind BFS, task scheduling, rate limiting, and producer-consumer pipelines.

---

## Quick Summary

A queue stores elements with FIFO (First-In, First-Out) access. Enqueue adds to the back; dequeue removes from the front. Use when processing order must match arrival order — BFS traversal, request queues, event streams. Key property: O(1) both ends, but no random access or priority ordering.

---

## Operations & Complexity Table

| Operation     | Time (avg) | Time (worst) | Space | Notes                                      |
|---------------|-----------|-------------|-------|--------------------------------------------|
| Enqueue       | O(1)      | O(1)        | O(1)  | Add to rear                                |
| Dequeue       | O(1)      | O(1)        | O(1)  | Remove from front                          |
| Peek/Front    | O(1)      | O(1)        | O(1)  | View front without removing                |
| Search        | O(n)      | O(n)        | O(1)  | No direct access                           |
| isEmpty       | O(1)      | O(1)        | O(1)  | Size == 0                                  |
| Size          | O(1)      | O(1)        | O(1)  | Maintain a counter                         |

---

## Memory Layout / Internal Structure

```
Array-Backed Queue (Naive — O(n) dequeue!)
──────────────────────────────────────────────────────────
front → [10 | 20 | 30 | 40 | __ | __]
Dequeue(10): shift everything left → O(n)!
          → [20 | 30 | 40 | __ | __ | __]

Circular Buffer Queue (O(1) dequeue)
──────────────────────────────────────────────────────────
Capacity = 6
front=1, rear=4, size=3
Index: [0]  [1]  [2]  [3]  [4]  [5]
       [__] [20] [30] [40] [__] [__]
              ↑              ↑
            front           rear

Enqueue(50): rear=(4+1)%6=5, size=4
Index: [0]  [1]  [2]  [3]  [4]  [5]
       [__] [20] [30] [40] [__] [50]

Dequeue(): returns arr[front=1]=20, front=(1+1)%6=2, size=3

Wrap-around example:
front=4, rear=2 (rear wrapped past end)
Index: [0]  [1]  [2]  [3]  [4]  [5]
       [70] [80] [__] [__] [50] [60]
                              ↑front ↑rear wraps

Linked-List-Backed Queue (collections.deque)
──────────────────────────────────────────────────────────
front                                          rear
 │                                              │
 ▼                                              ▼
[10] ←→ [20] ←→ [30] ←→ [40]
Enqueue: append to rear  → O(1)
Dequeue: remove from front → O(1)
No wasted capacity; grows dynamically

Priority Queue (Min-Heap backed)
──────────────────────────────────────────────────────────
         1
        / \
       3   2
      / \ / \
     7  4 5  6
Dequeue always returns the minimum element.
Backed by a heap array: [1, 3, 2, 7, 4, 5, 6]
Enqueue: O(log n) (sift up), Dequeue: O(log n) (sift down)
```

---

## Trade-offs vs Alternatives

| Feature              | Queue          | Stack          | Heap (Priority Queue) |
|----------------------|----------------|----------------|-----------------------|
| Order                | FIFO           | LIFO           | Priority-based        |
| Enqueue/Push         | O(1)           | O(1)           | O(log n)              |
| Dequeue/Pop          | O(1)           | O(1)           | O(log n)              |
| Peek                 | O(1) front     | O(1) top       | O(1) min/max          |
| Random access        | No             | No             | No                    |
| Order preservation   | Yes (arrival)  | Yes (reverse)  | No (by priority)      |
| BFS traversal        | Natural        | DFS instead    | Dijkstra/A*           |
| Memory overhead      | Low (deque)    | Low (list)     | Low (array heap)      |

```
Queue variant decision:
┌──────────────────────────────────────────────────────────────┐
│ Simple FIFO?                         → collections.deque     │
│ Need FIFO + peek both ends?          → deque                 │
│ Priority-ordered retrieval?          → heapq                 │
│ Fixed-size circular buffer?          → Circular queue array  │
│ Thread-safe producer-consumer?       → queue.Queue           │
│ BFS graph traversal?                 → deque (popleft)       │
└──────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Need LIFO order** — use a stack; queue processes in the wrong order.
- **Need priority-based retrieval** — use a min/max heap; plain queue doesn't sort.
- **Need random access** — queues only expose front/back; use a list or deque with indexing.
- **Need to cancel or reorder items** — queues don't support arbitrary deletion; use a heap or sorted structure.
- **Single-threaded, no ordering requirement** — a simple list may be clearer without the FIFO abstraction.

---

## Core Operations (Code)

```python
from collections import deque
import heapq

# ── Python deque as queue (idiomatic, O(1) both ends) ─────────────────────
q = deque()
q.append(10)          # enqueue to right → O(1)
q.append(20)
q.append(30)
front = q[0]          # peek  → O(1)
val = q.popleft()     # dequeue from left → O(1)
is_empty = not q      # check → O(1)

# Deque can also act as a double-ended queue:
q.appendleft(5)       # enqueue to front
q.pop()               # dequeue from rear

# ── BFS using queue (canonical pattern) ───────────────────────────────────
def bfs(graph: dict, start) -> list:
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

# ── Priority queue using heapq (min-heap) ────────────────────────────────
pq = []
heapq.heappush(pq, (3, "task_c"))   # (priority, item)
heapq.heappush(pq, (1, "task_a"))
heapq.heappush(pq, (2, "task_b"))
priority, item = heapq.heappop(pq)  # returns (1, "task_a")

# Max-heap: negate priorities
heapq.heappush(pq, (-5, "urgent"))  # highest priority = most negative

# ── Thread-safe queue for producer-consumer ───────────────────────────────
from queue import Queue
q = Queue(maxsize=100)   # bounded buffer
q.put("task_1")          # blocks if full (producer)
task = q.get()           # blocks if empty (consumer)
q.task_done()            # signal task completed
```

---

## 3 Worked Problems

---

### Problem 1 — Implement Queue using Stacks (LeetCode #232)

**Clarifying Questions**
- Can the queue use only push/pop/peek/empty operations of stacks? (Yes)
- All operations amortized O(1)? (Yes — that's the goal)
- Is peek the same as getting front without removing? (Yes)

**Brute Force (Two Stacks — O(n) per dequeue)**
```python
class QueueBrute:
    def __init__(self):
        self.s1 = []   # main stack
        self.s2 = []   # temp for reversal

    def push(self, x):
        self.s1.append(x)

    def pop(self):
        # Move all to s2 (reversed = queue order), pop from s2
        while self.s1:
            self.s2.append(self.s1.pop())
        val = self.s2.pop()
        while self.s2:
            self.s1.append(self.s2.pop())
        return val   # O(n) per call — moves everything twice
```

**Optimization (Lazy Transfer — Amortized O(1))**

Keep elements in `inbox` until dequeue is needed. On dequeue, transfer inbox to `outbox` only when outbox is empty. Each element moves from inbox to outbox exactly once.

```python
class MyQueue:
    def __init__(self):
        self.inbox = []    # push stack
        self.outbox = []   # pop stack

    def push(self, x: int) -> None:
        self.inbox.append(x)             # O(1)

    def pop(self) -> int:
        self._transfer()
        return self.outbox.pop()         # O(1) amortized

    def peek(self) -> int:
        self._transfer()
        return self.outbox[-1]           # O(1) amortized

    def empty(self) -> bool:
        return not self.inbox and not self.outbox

    def _transfer(self) -> None:
        if not self.outbox:              # only transfer when outbox empty
            while self.inbox:
                self.outbox.append(self.inbox.pop())

# Amortized analysis:
# Each element crosses from inbox to outbox exactly once.
# Total work for n operations = 2n moves → O(1) amortized per operation.
```

**Edge Cases**
- `peek` then `pop`: both use `_transfer`, second call does nothing (outbox non-empty).
- Single element: push to inbox, transfer to outbox, pop.

**Complexity**
- Time: O(1) amortized all operations
- Space: O(n)

**Follow-ups**
- "Implement Stack using Queues?" → LeetCode #225 — push is O(n) (rotate queue), pop is O(1).
- "Why is this amortized O(1)?" → Each element transferred at most once; amortize transfer cost over all pushes.

---

### Problem 2 — Number of Recent Calls (LeetCode #933)

**Clarifying Questions**
- What defines "recent"? Calls within the last 3000 ms (i.e., within [t - 3000, t])?
- Is `t` strictly increasing? (Yes per problem)
- Return count including the current call? (Yes)

**Brute Force**
```python
class RecentCounterBrute:
    def __init__(self):
        self.calls = []

    def ping(self, t: int) -> int:
        self.calls.append(t)
        return sum(1 for c in self.calls if c >= t - 3000)
    # O(n) per ping — scans all historical calls
```

**Optimization (Sliding Window with Queue)**

Old calls (outside the 3000 ms window) are never needed again. Evict them from the front of the queue.

```python
from collections import deque

class RecentCounter:
    def __init__(self):
        self.q = deque()

    def ping(self, t: int) -> int:
        self.q.append(t)
        while self.q[0] < t - 3000:   # evict calls outside window
            self.q.popleft()
        return len(self.q)

# Trace: t=1 → q=[1], len=1
# t=100 → q=[1,100], len=2
# t=3001 → q=[1,100,3001], len=3
# t=3002 → evict 1 (1 < 3002-3000=2), q=[100,3001,3002], len=3
```

**Edge Cases**
- First call: queue empty, append t, no eviction needed.
- Dense calls in window: queue grows; no eviction.
- Large gap: many evictions but each element evicted at most once — O(1) amortized.

**Complexity**
- Time: O(1) amortized per ping (each call added and removed once)
- Space: O(W) where W = max calls in any 3000 ms window

**Follow-ups**
- "Variable window size?" → Pass window to ping; same approach.
- "Rate limiter?" → This is the core algorithm; wrap with user-ID keying and Redis for distributed rate limiting.
- "Sliding window maximum?" → Use a monotonic deque (LeetCode #239).

---

### Problem 3 — Design Circular Queue (LeetCode #622)

**Clarifying Questions**
- Fixed capacity given at construction time? (Yes)
- What to return on enqueue when full / dequeue when empty? (False)
- Thread-safety required? (No per problem)

**Why circular?** A naive array queue wastes space (front pointer drifts right, leaving dead slots). A circular buffer reuses slots by wrapping indices modulo capacity.

```python
class MyCircularQueue:
    def __init__(self, k: int):
        self.data = [0] * k
        self.head = 0          # index of front element
        self.size = 0          # current number of elements
        self.cap = k

    def enQueue(self, value: int) -> bool:
        if self.isFull():
            return False
        tail = (self.head + self.size) % self.cap    # next empty slot
        self.data[tail] = value
        self.size += 1
        return True

    def deQueue(self) -> bool:
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % self.cap       # advance front
        self.size -= 1
        return True

    def Front(self) -> int:
        return -1 if self.isEmpty() else self.data[self.head]

    def Rear(self) -> int:
        if self.isEmpty():
            return -1
        tail = (self.head + self.size - 1) % self.cap
        return self.data[tail]

    def isEmpty(self) -> bool:
        return self.size == 0

    def isFull(self) -> bool:
        return self.size == self.cap

# Trace (cap=3):
# enQueue(1): head=0, size=1, data=[1,_,_]
# enQueue(2): head=0, size=2, data=[1,2,_]
# enQueue(3): head=0, size=3, data=[1,2,3]  (full)
# deQueue():  head=1, size=2, data=[1,2,3]  returns True, front now at index 1
# enQueue(4): tail=(1+2)%3=0, data=[4,2,3], size=3  (wrapped!)
# Front(): data[head=1] = 2
# Rear():  tail=(1+3-1)%3=0, data[0]=4
```

**Edge Cases**
- Size-1 capacity: enQueue then deQueue leaves head advanced, size=0.
- Full detection: `size == cap` (not `head == tail` — that's ambiguous).
- Wrap-around: modulo arithmetic handles all cases uniformly.

**Complexity**
- Time: O(1) all operations
- Space: O(k) — fixed-size array

**Follow-ups**
- "Thread-safe version?" → Add a mutex around each operation; or use `queue.Queue` in Python.
- "Circular deque?" → Two pointers (head moving left, tail moving right), both wrap (LeetCode #641).

---

## Interview Q&A

**Q1 (Easy): What does FIFO mean and name two real-world examples?**

FIFO = First-In, First-Out. The first element enqueued is the first one dequeued.

Examples:
1. **Print spooler** — documents print in the order submitted.
2. **BFS traversal** — nodes are explored level by level in arrival order.
3. **Request queue in a web server** — HTTP requests served in order received.
4. **CPU ready queue** — processes scheduled in arrival order (round-robin).

---

**Q2 (Easy): Why is `list.pop(0)` in Python O(n) but `deque.popleft()` O(1)?**

`list` is backed by a contiguous array. Removing index 0 shifts all n-1 remaining elements left — O(n).

`deque` is backed by a doubly-linked list of fixed-size blocks. Removing from the front advances a head pointer within the first block — O(1). When a block is exhausted, it's freed and the next block becomes the head. No shifting occurs.

---

**Q3 (Medium): Explain how BFS uses a queue and why it gives the shortest path in an unweighted graph.**

BFS explores all nodes at distance d before any node at distance d+1. The queue maintains this level-ordering: enqueuing neighbors adds them to the "current level + 1" bucket; dequeuing processes the earliest-seen (closest) nodes first.

Proof of shortest path: by induction, when a node is first dequeued, its distance label is minimal. If a shorter path existed, that path's final node would have been enqueued earlier, contradicting our FIFO processing order.

---

**Q4 (Medium): What is a priority queue? How does it differ from a regular queue?**

A priority queue dequeues the element with the highest (or lowest) priority, not the one that arrived first. Internally backed by a binary heap — enqueue is O(log n), dequeue-min/max is O(log n), peek is O(1).

Use when: Dijkstra's shortest path, A* search, task scheduling with deadlines, top-k streaming problems.

A regular queue gives O(1) dequeue but no ordering by priority. A priority queue sacrifices O(1) dequeue for O(log n) but gains ordering.

---

**Q5 (Medium): Describe the circular buffer pattern and why it's used in practice.**

A circular buffer uses a fixed-size array with two indices (head and tail) that wrap modulo capacity. It avoids the O(n) shifting of a naive array queue and the pointer overhead of a linked-list queue. Space is preallocated — no dynamic allocation during operation.

Used in: OS kernel ring buffers (network packets, I/O), audio processing (fixed-latency stream), UART hardware FIFOs, lock-free inter-thread communication (disruptor pattern).

---

**Q6 (Hard): Design a rate limiter supporting "at most N requests per W seconds per user."**

```python
from collections import defaultdict, deque
import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_req = max_requests
        self.window = window_seconds
        self.user_queues: dict[str, deque] = defaultdict(deque)

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        q = self.user_queues[user_id]

        # Evict timestamps outside the sliding window
        while q and q[0] <= now - self.window:
            q.popleft()

        if len(q) < self.max_req:
            q.append(now)
            return True
        return False

# Time: O(N) per request in worst case (eviction), O(1) amortized
# Space: O(users × max_requests) — at most max_requests timestamps per user

# Production additions:
# - Redis sorted set per user (timestamp as score, ZREMRANGEBYSCORE to evict)
# - Token bucket for smoother bursting
# - Leaky bucket for strict rate (constant outflow)
```

---

**Q7 (Hard): Design a task scheduler supporting enqueue, dequeue-min-priority, and increase-priority.**

This is a decrease-key priority queue — a standard heap doesn't support O(log n) key changes.

Options:
1. **Lazy deletion heap** — push (new_priority, task_id); on pop, skip stale entries. O(log n) enqueue/dequeue, O(1) "increase priority" (just push duplicate). Works well when increases are rare.
2. **Fibonacci heap** — O(1) amortized decrease-key, O(log n) delete-min. Complex to implement; used in theoretical Dijkstra analysis.
3. **Indexed binary heap** — maintain a hash map from task_id to heap index. On key change, update index and sift up/down. O(log n) all operations, O(n) space. Practical and interview-appropriate.

```python
import heapq

class TaskScheduler:
    def __init__(self):
        self.heap = []          # (priority, task_id)
        self.entry_finder = {}  # task_id → [priority, task_id, active]
        self.REMOVED = object()

    def add_task(self, task_id, priority):
        if task_id in self.entry_finder:
            self._mark_removed(task_id)
        entry = [priority, task_id]
        self.entry_finder[task_id] = entry
        heapq.heappush(self.heap, entry)

    def _mark_removed(self, task_id):
        entry = self.entry_finder.pop(task_id)
        entry[-1] = self.REMOVED   # invalidate old entry

    def pop_task(self):
        while self.heap:
            priority, task_id = heapq.heappop(self.heap)
            if task_id is not self.REMOVED and task_id in self.entry_finder:
                del self.entry_finder[task_id]
                return task_id, priority
        raise KeyError("empty scheduler")
```

---

## Interview Tips

- **Always use `collections.deque`** for queue problems in Python — never `list.pop(0)`. State explicitly that `popleft()` is O(1) vs O(n).
- **BFS template is mandatory** — queue + visited set + level tracking. Practice until it's muscle memory.
- **Circular buffer index math** — `tail = (head + size) % cap` is the cleanest formulation. Avoid storing a separate tail pointer.
- **Priority queue vs queue** — know that `heapq` is a min-heap, so negate priorities for max-heap behavior. Always state this in interviews.
- **Rate limiting** is the canonical queue system design question — sliding window with a deque is the standard answer; know its trade-offs vs token bucket and leaky bucket.
- **Queue using two stacks** — a classic interview problem; lead with the amortized analysis to show depth.
- **Deque = Double-Ended Queue** — Python's `collections.deque` supports O(1) append/pop on both ends. It subsumes both stack and queue.
