"""Thread Pool - Worker threads executing tasks from queue"""

import threading
from queue import Queue
from typing import Callable


class ThreadPool:
    """Thread pool with fixed number of workers"""

        """__init__ implementation.

        Time: O(n)
        Space: O(1)
        """
    def __init__(self, num_workers: int):
        self.num_workers = num_workers
        self.task_queue = Queue()
        self.workers = []
        self.shutdown = False

        # Start worker threads
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
        print(f"ThreadPool started with {num_workers} workers")

    def _worker(self):
        """Worker thread that processes tasks"""
        while not self.shutdown:
            try:
                # Get task from queue with timeout
                task_func, args, kwargs = self.task_queue.get(timeout=1)

                if task_func is None:  # Poison pill for shutdown
                    break

                # Execute task
                try:
                    task_func(*args, **kwargs)
                except Exception as e:
                    print(f"Error executing task: {e}")
                finally:
                    self.task_queue.task_done()

            except:  # Queue.Empty exception
                continue

    def submit(self, func: Callable, *args, **kwargs):
        """Submit task to pool"""
        if self.shutdown:
            raise RuntimeError("Cannot submit task to shut down pool")
        self.task_queue.put((func, args, kwargs))

    def shutdown_pool(self, wait: bool = True):
        """Shutdown the thread pool"""
        self.shutdown = True

        if wait:
            self.task_queue.join()

        # Send poison pills
        for _ in range(self.num_workers):
            self.task_queue.put((None, None, None))

        for worker in self.workers:
            worker.join()

        print("ThreadPool shut down")


def sample_task(task_id: int, value: str):
    """Sample task function"""
    print(f"Task {task_id}: {value}")
    import time
    time.sleep(0.5)


if __name__ == "__main__":
    pool = ThreadPool(3)

    print("Submitting tasks...")
    for i in range(8):
        pool.submit(sample_task, i, f"Processing item {i}")

    print("Waiting for completion...")
    pool.shutdown_pool(wait=True)