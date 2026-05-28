# Thread Pool

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A thread pool is a concurrency management pattern where a fixed (or bounded) set of worker threads
reuses itself to execute a stream of incoming tasks, rather than spawning and destroying a thread per
task. Thread creation costs 1-10ms of OS time and 512KB-8MB of stack memory on most JVMs; a web
server handling 10K requests/sec cannot afford to pay that cost per request.

Thread pools appear in interviews both as a standalone design problem ("implement a thread pool in
Python/Java") and as an architectural sub-component ("how does your HTTP server handle concurrent
requests?", "how do you process 1M user events per hour with bounded memory?"). L5+ candidates are
expected to discuss dynamic sizing, work stealing, priority scheduling, and deadlock hazards.

## Functional Requirements

- Accept submitted tasks (Runnable/Callable) and execute them asynchronously
- Bound the number of concurrently running threads (core and max pool size)
- Buffer pending tasks in a queue when all workers are busy
- Return a Future/Promise for each submitted task so callers can retrieve results or cancel
- Apply a rejection policy when the queue is full (abort, caller-runs, discard-oldest, discard)
- Support graceful shutdown: drain queued tasks, wait for in-progress tasks to finish

## Non-Functional Requirements

- **Scale:** Handle 100K task submissions/sec with < 1ms scheduling overhead per task
- **Latency:** Task execution begins within 1ms of submission when a thread is free; P99 queue wait < 10ms at 80% utilization
- **Availability:** Worker thread crash must not kill the pool; replace dead threads automatically
- **Consistency:** Tasks submitted before shutdown() completes must be executed (unless caller requests immediate shutdown)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
CPU-bound sizing (N = CPU cores):
  Optimal threads = N + 1  (one extra covers the thread waiting on page faults)
  Example: 16-core machine → 17 CPU-bound workers

I/O-bound sizing (Little's Law):
  If a task waits 90ms for I/O out of 100ms total → wait ratio = 0.9
  Optimal threads = N × (1 + wait_time / compute_time) = 16 × (1 + 90/10) = 160 threads

Queue sizing:
  At 100K submissions/sec with 17 workers, each taking 1ms:
  Throughput = 17 workers × 1000 tasks/sec/worker = 17,000 tasks/sec
  If burst lasts 500ms: backlog = (100K - 17K) × 0.5s = 41,500 tasks
  → Queue capacity of 50K covers a 500ms burst at 100K/sec

Memory:
  17 threads × 512KB stack = ~8.5 MB (trivial)
  50K queued tasks × 1KB per task object = 50 MB (bounded)
```

### Architecture Diagram

```
                        Thread Pool
   ┌────────────┐
   │  Caller A  │──────►┌────────────────────────────────────────────┐
   └────────────┘        │  submit(task) → Future                     │
   ┌────────────┐        │                                            │
   │  Caller B  │──────►│  ┌──────────────────────────┐             │
   └────────────┘        │  │     Work Queue (FIFO)     │             │
   ┌────────────┐        │  │  [Task][Task][Task][Task] │             │
   │  Caller C  │──────►│  └──────────────┬───────────┘             │
   └────────────┘        │                 │ (blocking take)          │
                         │         ┌───────┼───────┐                 │
                         │         ▼       ▼       ▼                 │
                         │    ┌────────┐ ┌────────┐ ┌────────┐      │
                         │    │Worker 1│ │Worker 2│ │Worker N│      │
                         │    │(Thread)│ │(Thread)│ │(Thread)│      │
                         │    └───┬────┘ └───┬────┘ └───┬────┘      │
                         │        │          │          │            │
                         │        ▼          ▼          ▼            │
                         │   execute()   execute()  execute()        │
                         │   set Future  set Future  set Future      │
                         └────────────────────────────────────────────┘

Queue full? → Rejection Handler:
  ABORT       → throw RejectedExecutionException
  CALLER_RUNS → caller thread executes the task directly (natural back-pressure)
  DISCARD     → silently drop the new task
  DISCARD_OLD → drop oldest queued task, enqueue new one
```

### Data Model

```python
# Core data structures

class Task:
    callable: Callable       # the work to perform
    future: Future           # handle for caller to get result
    priority: int = 0        # used in PriorityQueue variant
    submitted_at: float      # epoch; for timeout detection

class Future:
    _result: Any             # set by worker on completion
    _exception: Exception    # set by worker on failure
    _done: threading.Event   # callers block on this

class WorkerThread(threading.Thread):
    pool: "ThreadPool"       # reference back to pool (for replacement logic)
    idle: bool               # True when waiting on queue
    tasks_completed: int     # metrics counter

class ThreadPool:
    core_pool_size: int      # threads always kept alive (even idle)
    max_pool_size: int       # absolute thread ceiling
    work_queue: Queue        # bounded FIFO (or Priority)
    workers: List[WorkerThread]
    rejection_policy: RejectionPolicy
    state: PoolState         # RUNNING | SHUTDOWN | TERMINATED
```

### API Design

```
# Java-style interface (maps directly to Python implementation below)

ThreadPool(core_size=4, max_size=16, queue_capacity=1000,
           keep_alive_sec=60, rejection=CALLER_RUNS)

Future  submit(callable)               -- non-blocking; returns handle
void    execute(callable)              -- fire-and-forget
bool    await_termination(timeout_sec) -- blocks until drained
void    shutdown()                     -- stop accepting, finish queued
void    shutdown_now()                 -- interrupt workers, return pending tasks
int     active_count()                 -- threads currently executing
int     queue_size()                   -- tasks waiting in queue
float   utilization()                  -- active_count / core_pool_size
```

### Basic Scaling

- **Core vs max threads:** Core threads never die (idle threads stay alive to minimize startup latency). Extra threads created when queue is full; they die after keep_alive_sec of idleness. Java's ThreadPoolExecutor uses this exact model.
- **Queue type matters:** Unbounded queue (LinkedBlockingQueue) → max_size is irrelevant, queue absorbs all bursts; risk: OOM under sustained overload. Bounded queue (ArrayBlockingQueue) → triggers rejection policy and max thread creation; explicit back-pressure.
- **Separate pools per workload:** I/O-bound tasks (DB calls, HTTP) in a large pool (100-200 threads); CPU-bound tasks in N+1 pool. Mixing them causes thread starvation: I/O tasks block CPU-bound workers while waiting for network.
- **Monitor via metrics:** Expose `queue_depth`, `active_threads`, `completed_tasks/sec`, `rejection_count` to your monitoring system. Alert on queue_depth > 80% of capacity or rejection_count > 0.

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Web server scenario: 10K concurrent HTTP connections, each request takes 20ms average
  Required throughput: 10K / 0.020s = 500K req/sec
  CPU cores: 32 (modern application server)
  DB I/O wait: 15ms per request, compute: 5ms
  Optimal threads: 32 × (1 + 15/5) = 32 × 4 = 128 threads

Memory per thread (JVM):
  Stack: 512KB default (reducible to 128KB with -Xss128k for shallow call stacks)
  128 threads × 512KB = 64MB stack space (acceptable)
  Thread-local storage (ThreadLocal caches, PRNG state): ~4KB/thread = 0.5MB total

Queue memory:
  Each pending task: ~200 bytes (lambda closure + future + metadata)
  10K queued tasks: 2MB (trivial)
  50K queued tasks (burst): 10MB

Throughput validation (Little's Law):
  L = λ × W  →  128 threads = λ × 0.020s  →  λ = 6,400 req/sec sustained
  To hit 500K/sec: need 500K × 0.020s = 10,000 concurrent threads
  → Solution: async I/O (Netty, asyncio) not more threads; see L5+ note below
```

### Failure Modes

```
Scenario 1: Worker thread dies (uncaught exception)
  - Thread exits; pool size drops below core_pool_size
  - Fix: ThreadFactory wraps run() in try/catch; on exit, pool spawns replacement thread
  - Java ThreadPoolExecutor does this automatically
  - Python: use daemon threads + monitoring loop to detect and replace dead workers

Scenario 2: Thread starvation deadlock
  - Task A submits Task B to the SAME pool and blocks waiting for B's result
  - If pool is at max capacity, B is queued but no thread is free (all blocked on A)
  - Result: deadlock — pool is 100% utilized but makes no progress
  - Fix: never submit tasks that wait for other tasks in the same pool
  - Fix: use a separate "continuation" pool, or use async/await instead of blocking futures
  - Fix: detect via timeout (Future.get(timeout=5s)) + alerting on timed-out tasks

Scenario 3: Slow poison task monopolizes workers
  - One task takes 60s (network timeout), monopolizes 1/N workers for 60s
  - Under high load, all N workers get stuck on slow tasks
  - Fix: per-task deadline/timeout (cancel via interrupt after threshold)
  - Fix: circuit breaker on downstream dependency — fast-fail instead of blocking

Scenario 4: Queue overflow under burst
  - CALLER_RUNS rejection policy: caller's thread executes the task, acting as natural
    back-pressure; slows down the producer proportionally
  - ABORT: throws exception; caller must implement retry with exponential backoff
  - Neither is right for all workloads; choose based on producer's ability to retry

Scenario 5: CPU thread pool starved by GC pauses (JVM)
  - Stop-the-world GC pause of 500ms → all workers pause → queue builds up
  - Fix: tune GC (G1GC, ZGC for <1ms pauses); limit heap to force more frequent minor GC
  - Fix: size the queue to absorb expected GC pause bursts
```

### Consistency Boundaries

```
Task ordering guarantees:
  FIFO queue: tasks start in submission order within priority class
  Priority queue: high-priority tasks may preempt (skip ahead of) pending low-priority
  No guarantee that Task A completes before Task B even if submitted first
    (worker count > 1 means tasks execute concurrently)

Work stealing (ForkJoinPool model):
  Each worker has its own private deque (double-ended queue)
  Worker takes tasks from its own deque head (LIFO for cache locality on recursion)
  Idle workers steal from other workers' deque tails (FIFO for fairness)
  Result: better CPU cache utilization for recursive divide-and-conquer workloads
  Java's ForkJoinPool (used by CompletableFuture.supplyAsync) implements this

Dynamic pool sizing:
  Monitor queue depth + active thread count every 100ms
  Scale up rule: queue_depth > threshold AND active == max_size → log warning, emit metric
  Scale down: threads idle for keep_alive_sec → allow to die (reduces to core_pool_size)
  Adaptive sizing: Netflix's concurrency limiter uses gradient descent on latency to find
    the optimal number of concurrent requests dynamically (Netflix Concurrency Limiter)
```

### Cost Model

```
On-prem / cloud VM cost comparison:

Option A: Thread-per-request (naive)
  10K concurrent req × 512KB stack = 5 GB stack space
  OS thread context switches at 10K threads: 2-5ms overhead per switch
  Usable throughput degrades significantly above ~1K threads (Linux scheduling overhead)
  Cost: 1 × 32-core VM @ $1.50/hr = $1,080/month → saturates at ~6,400 req/sec

Option B: Thread pool (128 threads, async I/O)
  Same VM handles 10K concurrent connections via non-blocking I/O + 128 worker threads
  Throughput: I/O handled by kernel epoll; threads only run when data is ready
  Effective capacity: 50,000+ req/sec on same hardware
  Cost per req/sec: 7× better utilization vs thread-per-request

Option C: Async/await (Python asyncio, Node.js, Java virtual threads)
  1 OS thread per CPU core; thousands of coroutines multiplexed
  Memory: each coroutine ~4KB (vs 512KB per OS thread) → 128× more concurrent tasks
  Throughput: can saturate 10Gbps NIC before running out of "threads"
  Best for: I/O-bound workloads (>80% wait time)
  Worst for: CPU-bound workloads (GIL in Python, single-threaded JS event loop)

Recommendation:
  CPU-bound: thread pool with N+1 threads per CPU core
  I/O-bound (Python): asyncio + thread pool for blocking libs (run_in_executor)
  I/O-bound (Java): virtual threads (Project Loom, Java 21) or Netty
  Mixed: separate pools (CPU pool + I/O pool) with clear task routing
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Fixed thread pool** | Predictable memory, no sizing logic needed | Under-provisioned during spikes, over-provisioned at low load | Batch processing, offline jobs with known concurrency |
| **Cached thread pool (unbounded)** | Auto-scales to demand, no queue buildup | Unbounded thread creation → OOM under burst | Low-volume background tasks, dev/test environments |
| **Fork/Join pool (work-stealing)** | High CPU utilization, recursive tasks efficient | Harder to debug, blocking tasks starve workers | Recursive algorithms (mergesort, tree traversal), parallel streams |
| **Async/await (coroutines)** | 128× more concurrent tasks per MB RAM | Cannot use blocking libraries without wrapping, steep learning curve | High-concurrency I/O (web servers, API gateways) |
| **Actor model (Akka/Erlang)** | No shared state, built-in message passing, fault isolation | Different programming model, harder to adopt incrementally | Distributed systems, event-sourced services |

## Follow-up Questions (escalating difficulty)

1. **(L3)** Why not create a new thread for every task?
   → Thread creation costs ~1ms and ~512KB of memory. At 10K tasks/sec, that's 10K thread creations/sec = 10s worth of CPU just on thread management, plus 5 GB of stack space. Thread pools amortize this cost by reusing threads.

2. **(L3)** What is the difference between `core_pool_size` and `max_pool_size`?
   → Core threads are kept alive even when idle (pre-warmed for low-latency task pickup). Extra threads (up to max) are created only when the queue is full; they die after `keep_alive` seconds of idleness. This allows bursting without permanent resource commitment.

3. **(L4)** When would you use a bounded vs unbounded queue?
   → Bounded queue: provides explicit back-pressure; when queue fills, rejection policy fires, which is a signal the system is overloaded. Unbounded queue: masks overload by growing the queue indefinitely, eventually causing OOM. Prefer bounded queues in production with CALLER_RUNS or circuit-breaker rejection for controlled back-pressure.

4. **(L4)** How do you size a thread pool for a service that makes DB calls?
   → Use Little's Law: threads = throughput × latency. If you want 1,000 req/sec and each request holds a DB connection for 50ms, you need 1,000 × 0.050 = 50 threads. Match thread pool size to connection pool size; having more threads than DB connections just wastes threads waiting on connection acquisition.

5. **(L5)** Explain thread starvation deadlock and how to prevent it.
   → Occurs when Task A blocks waiting for Task B, but B cannot run because all threads are occupied by tasks waiting on other tasks. Prevention: (1) never block a pool thread waiting for another task in the same pool; (2) use separate pools for tasks with dependency relationships; (3) use async/await (coroutines yield the thread rather than blocking it); (4) enforce task timeouts so blocked tasks fail fast rather than holding threads indefinitely.

6. **(L5)** How does ForkJoinPool's work stealing differ from a shared queue approach?
   → In a shared queue, all workers contend on one lock to dequeue tasks — this becomes a bottleneck at high task submission rates. In work stealing, each worker has a private deque. Workers push/pop from their own deque (LIFO, lock-free), and idle workers steal from others' deque tails (FIFO, only needs one CAS). This distributes the lock contention and improves cache locality: a worker is likely to steal tasks related to what the victim was doing.

7. **(L5+)** How would you design a priority-aware thread pool that prevents starvation of low-priority tasks?
   → Use a priority queue (min-heap keyed on task priority). To prevent starvation: implement aging — every N seconds, increase the effective priority of tasks that have been waiting longer than a threshold (priority = original_priority - (now - submitted_at) / aging_factor). Set a floor: low-priority tasks are guaranteed execution within T seconds regardless of high-priority load. Track wait time per priority tier as a metric; alert if P99 wait for LOW-priority exceeds SLA.

## Anti-patterns / Things NOT to Say

- **"Just use an unbounded queue so we never reject tasks"** — Unbounded queues hide overload. The queue grows until OOM kills the process. A bounded queue with rejection policy provides explicit back-pressure and is observable (rejection_count metric). Always bound your queues in production.
- **"More threads always means more throughput"** — True only up to the hardware concurrency limit. Beyond N CPU cores for CPU-bound work, adding threads adds context-switching overhead and cache pollution. For I/O-bound work, the limit is OS thread scheduling (Linux degrades significantly above ~10K threads per process).
- **"One global thread pool for everything"** — Mixing CPU-bound and I/O-bound tasks in one pool causes priority inversion: I/O-bound tasks block CPU-bound workers. Use separate pools: one sized for CPU (N+1 threads) and one for I/O (100-500 threads).
- **"Thread pools are not needed with async/await"** — False. Even async frameworks need a thread pool for: (1) blocking library calls (file I/O, most DB drivers), (2) CPU-bound work that would block the event loop, (3) legacy synchronous code. Python's `asyncio.run_in_executor` wraps a ThreadPoolExecutor for exactly this reason.
- **"Shutdown gracefully means just calling shutdown()"** — Graceful shutdown also requires: waiting for in-flight tasks to finish (awaitTermination), closing upstream connections to stop new submissions, setting a timeout after which remaining tasks are abandoned, and logging tasks that were abandoned so operators can investigate.

## Python Implementation (sketch)

```python
import threading
import queue
import time
from concurrent.futures import Future
from typing import Callable, Any, Optional
from enum import Enum

class RejectionPolicy(Enum):
    ABORT = "abort"
    CALLER_RUNS = "caller_runs"
    DISCARD = "discard"
    DISCARD_OLDEST = "discard_oldest"

class ThreadPool:
    """Bounded thread pool with core/max sizing and rejection policies."""

    def __init__(self, core_size: int = 4, max_size: int = 16,
                 queue_capacity: int = 500,
                 keep_alive_sec: float = 60.0,
                 rejection: RejectionPolicy = RejectionPolicy.CALLER_RUNS):
        self.core_size = core_size
        self.max_size = max_size
        self.keep_alive_sec = keep_alive_sec
        self.rejection = rejection
        self._queue: queue.Queue = queue.Queue(maxsize=queue_capacity)
        self._workers: list[threading.Thread] = []
        self._lock = threading.Lock()
        self._shutdown = threading.Event()
        self._active_count = 0
        self._completed = 0
        # Pre-start core threads
        for _ in range(core_size):
            self._spawn_worker(is_core=True)

    def _spawn_worker(self, is_core: bool = False) -> None:
        t = threading.Thread(target=self._worker_loop,
                             args=(is_core,), daemon=True)
        t.start()
        with self._lock:
            self._workers.append(t)

    def _worker_loop(self, is_core: bool) -> None:
        timeout = None if is_core else self.keep_alive_sec
        while not self._shutdown.is_set():
            try:
                task, future = self._queue.get(timeout=timeout)
            except queue.Empty:
                if not is_core:
                    break  # non-core thread idle-timeout
                continue
            with self._lock:
                self._active_count += 1
            try:
                result = task()
                if not future.cancelled():
                    future.set_result(result)
            except Exception as exc:
                if not future.cancelled():
                    future.set_exception(exc)
            finally:
                with self._lock:
                    self._active_count -= 1
                    self._completed += 1
                self._queue.task_done()

    def submit(self, fn: Callable[..., Any], *args, **kwargs) -> Future:
        if self._shutdown.is_set():
            raise RuntimeError("Pool is shut down")
        future: Future = Future()
        task = lambda: fn(*args, **kwargs)
        try:
            self._queue.put_nowait((task, future))
        except queue.Full:
            self._handle_rejection(task, future)
        return future

    def _handle_rejection(self, task: Callable, future: Future) -> None:
        if self.rejection == RejectionPolicy.ABORT:
            future.set_exception(RuntimeError("Queue full — task rejected"))
        elif self.rejection == RejectionPolicy.CALLER_RUNS:
            try:
                future.set_result(task())   # caller's thread executes it
            except Exception as e:
                future.set_exception(e)
        elif self.rejection == RejectionPolicy.DISCARD:
            future.cancel()
        elif self.rejection == RejectionPolicy.DISCARD_OLDEST:
            try:
                self._queue.get_nowait()    # remove oldest
            except queue.Empty:
                pass
            self._queue.put_nowait((task, future))

    def shutdown(self, wait: bool = True, timeout: float = 30.0) -> None:
        self._shutdown.set()
        if wait:
            self._queue.join()  # blocks until all tasks processed

    @property
    def stats(self) -> dict:
        return {
            "active": self._active_count,
            "queued": self._queue.qsize(),
            "completed": self._completed,
            "utilization": self._active_count / self.core_size,
        }


# Demo
if __name__ == "__main__":
    pool = ThreadPool(core_size=4, max_size=8, queue_capacity=20,
                      rejection=RejectionPolicy.CALLER_RUNS)

    def work(task_id: int) -> str:
        time.sleep(0.01)   # simulate 10ms task
        return f"done-{task_id}"

    futures = [pool.submit(work, i) for i in range(30)]
    results = [f.result(timeout=5) for f in futures]
    print(f"Completed {len(results)} tasks: {results[:5]}...")
    print(f"Stats: {pool.stats}")
    pool.shutdown(wait=True)
```
