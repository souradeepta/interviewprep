"""Rate Limiter implementations - Token Bucket and Sliding Window"""

import time
from collections import deque


class TokenBucketLimiter:
    """Token bucket rate limiter"""

    def __init__(self, rate: float, capacity: int):
        """
        rate: tokens per second
        capacity: max tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()

    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class SlidingWindowLimiter:
    """Sliding window counter rate limiter"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = deque()  # timestamps

    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()

        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False


if __name__ == "__main__":
    # Token bucket: 2 tokens/sec, max 5
    bucket = TokenBucketLimiter(2, 5)
    for i in range(7):
        print(f"Request {i+1}: {bucket.is_allowed()}")

    time.sleep(1)
    print(f"After 1s: {bucket.is_allowed()}")

    # Sliding window: 3 requests per 2 seconds
    window = SlidingWindowLimiter(3, 2)
    for i in range(5):
        print(f"Request {i+1}: {window.is_allowed()}")
