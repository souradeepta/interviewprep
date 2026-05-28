# Concurrency & Parallelism — Handling Multiple Tasks

**Level:** L4-L5
**Time to read:** ~10 min

Critical for building responsive, performant systems.

---

## 🔄 Concurrency vs. Parallelism

**Concurrency:** Multiple tasks progress (may interleave)
**Parallelism:** Multiple tasks run simultaneously

```
Single core: Concurrency (time-slicing)
Multiple cores: Parallelism (true simultaneous)
```

---

## 🧵 Threading Models

### Threads

Multiple execution paths in same process

```
Pros: Share memory, fast communication
Cons: Race conditions, deadlocks, complexity

Problem: Race condition
Thread 1: Read x (=0), Add 1
Thread 2: Read x (=0), Add 1
Result: x=1 (expected: x=2)
```

### Async/Await (Coroutines)

Lightweight, don't block on I/O

```
Event loop manages multiple coroutines
Good for I/O-bound (network, disk)
Poor for CPU-bound (computation)
```

### Process-Based

Separate process per task

```
Pros: Isolation, simple
Cons: Memory overhead, slower communication
```

---

## 🔒 Synchronization

**Mutex/Lock:** Exclusive access to resource
**Semaphore:** Limited access (counting)
**Condition Variable:** Wait for event

```
Problem: Deadlock
- Thread A holds lock 1, waits for lock 2
- Thread B holds lock 2, waits for lock 1
- Both stuck forever

Solution: Lock ordering, timeout
```

---

## 🚀 Performance Patterns

**Thread Pool:** Reuse threads, avoid creation overhead
**Producer-Consumer:** Decouple producers from consumers
**Work Stealing:** Idle threads take work from busy threads

---

## 💡 When to Use What

**Concurrency (async):** I/O-bound (1000s concurrent connections)
**Parallelism (threads/processes):** CPU-bound (utilize cores)
**Hybrid:** Both I/O and CPU work

---

## ❓ Interview Q&A

**Q: Threads vs. async, when use each?**
A: Threads for CPU-bound. Async for I/O-bound (1000s concurrent). Hybrid for mixed workload.

**Q: How to prevent race conditions?**
A: Mutexes, atomic operations, immutable data structures.

**Q: Deadlock, how to detect and prevent?**
A: Detect: Watchdog timeout. Prevent: Lock ordering, no circular waits.

---

**Last updated:** 2026-05-22
