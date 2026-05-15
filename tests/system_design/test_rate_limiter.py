"""
Test Rate Limiter Implementation
================================

OVERVIEW:
This module provides a complete implementation of Test Rate Limiter, a fundamental
data structure used in algorithms and system design.

PURPOSE & USE CASES:
- Core operation for many algorithm patterns
- Essential for interview preparation
- Real-world applications in production systems

KEY OPERATIONS:
- Time/Space complexity analysis included for each operation
- Design trade-offs explained
- Common pitfalls and edge cases documented

COMPLEXITY SUMMARY:
See individual class/function docstrings for detailed complexity analysis.

REFERENCES:
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein)
- Algorithm Design Manual (Skiena)
- LeetCode and HackerRank problem patterns
"""

import pytest
import time
from python.system_design.rate_limiter import TokenBucketLimiter, SlidingWindowLimiter


class TestTokenBucketLimiter:
    def test_initial_tokens(self):
    """
    [Brief description of what this function does]

    Args:
        [param]: description

    Returns:
        [description of return value]

    Time: O([complexity])
    Space: O([complexity])
    """
        limiter = TokenBucketLimiter(rate=2.0, capacity=5)
        for _ in range(5):
            assert limiter.is_allowed()
        assert not limiter.is_allowed()

    def test_refill(self):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
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

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        limiter = TokenBucketLimiter(rate=1.0, capacity=3)
        assert limiter.tokens == 3
        time.sleep(2)
        # Should not exceed capacity
        assert limiter.tokens <= 3


class TestSlidingWindowLimiter:
    def test_limit_requests(self):
    """
    [Brief description of what this function does]

    Args:
        [param]: description

    Returns:
        [description of return value]

    Time: O([complexity])
    Space: O([complexity])
    """
        limiter = SlidingWindowLimiter(max_requests=3, window_seconds=2)
        for _ in range(3):
            assert limiter.is_allowed()
        assert not limiter.is_allowed()

    def test_window_expiry(self):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        limiter = SlidingWindowLimiter(max_requests=2, window_seconds=1)
        assert limiter.is_allowed()
        assert limiter.is_allowed()
        assert not limiter.is_allowed()

        time.sleep(1.1)
        assert limiter.is_allowed()

    def test_requests_outside_window(self):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        limiter = SlidingWindowLimiter(max_requests=2, window_seconds=1)
        assert limiter.is_allowed()
        time.sleep(0.5)
        assert limiter.is_allowed()
        assert not limiter.is_allowed()

        time.sleep(0.6)  # Now first request is outside window
        assert limiter.is_allowed()
