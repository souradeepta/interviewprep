import pytest
import time
from python.system_design.rate_limiter import TokenBucketLimiter, SlidingWindowLimiter


class TestTokenBucketLimiter:
    def test_initial_tokens(self):
        limiter = TokenBucketLimiter(rate=2.0, capacity=5)
        for _ in range(5):
            assert limiter.is_allowed()
        assert not limiter.is_allowed()

    def test_refill(self):
        limiter = TokenBucketLimiter(rate=2.0, capacity=5)
        # Use all tokens
        for _ in range(5):
            assert limiter.is_allowed()
        # Should have no tokens
        assert not limiter.is_allowed()
        # Wait for refill
        time.sleep(0.6)
        # Should have at least 1 token
        assert limiter.is_allowed()

    def test_capacity_limit(self):
        limiter = TokenBucketLimiter(rate=1.0, capacity=3)
        assert limiter.tokens == 3
        time.sleep(2)
        # Should not exceed capacity
        assert limiter.tokens <= 3


class TestSlidingWindowLimiter:
    def test_limit_requests(self):
        limiter = SlidingWindowLimiter(max_requests=3, window_seconds=2)
        for _ in range(3):
            assert limiter.is_allowed()
        assert not limiter.is_allowed()

    def test_window_expiry(self):
        limiter = SlidingWindowLimiter(max_requests=2, window_seconds=1)
        assert limiter.is_allowed()
        assert limiter.is_allowed()
        assert not limiter.is_allowed()

        time.sleep(1.1)
        assert limiter.is_allowed()

    def test_requests_outside_window(self):
        limiter = SlidingWindowLimiter(max_requests=2, window_seconds=1)
        assert limiter.is_allowed()
        time.sleep(0.5)
        assert limiter.is_allowed()
        assert not limiter.is_allowed()

        time.sleep(0.6)  # Now first request is outside window
        assert limiter.is_allowed()
