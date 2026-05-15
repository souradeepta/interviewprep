# Thread Pool

## Problem Statement

Implement a thread pool to manage a fixed number of worker threads executing tasks from a queue.

**Requirements:**
- Fixed number of worker threads
- Task queue for pending tasks
- Thread-safe operations
- Graceful shutdown
- Reuse threads to avoid creation overhead

## Design

### Architecture

```
Task Queue (FIFO)
    │
    ├→ Worker1 (busy)
    ├→ Worker2 (idle, waiting)
    ├→ Worker3 (busy)
    └→ Worker4 (idle, waiting)
```

### Key Components

```
Worker: Thread that executes tasks
Task: Runnable/callable work unit
ThreadPool: Manages workers and task queue
TaskQueue: Holds pending tasks (BlockingQueue)
```

### Operations

```
execute(task):
  taskQueue.add(task)
  // Worker picks it up

Worker loop:
  while not shutdown:
    task = taskQueue.take()  // blocking, waits if empty
    task.run()

shutdown():
  Wait for all workers to finish
  Terminate threads
```

## Trade-offs

| Approach | Pro | Con |
|----------|-----|-----|
| Fixed pool | Predictable, fast | Fixed capacity |
| Dynamic pool | Scales with load | Overhead, complexity |
| Blocking queue | Thread-safe | Blocking calls |

## Complexity

| Operation | Time |
|-----------|------|
| execute | O(1) |
| worker.run | O(task time) |
| shutdown | O(n) where n=workers |
