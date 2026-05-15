import pytest
from python.system_design.lfu_cache import LFUCache


class TestLFUCache:
    def test_get_and_put(self):
        cache = LFUCache(2)
        cache.put(1, 1)
        assert cache.get(1) == 1

    def test_eviction_least_frequent(self):
        cache = LFUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)  # freq[1] = 2
        cache.put(3, 3)  # evict 2 (freq=1)
        assert cache.get(2) == -1
        assert cache.get(1) == 1

    def test_lru_on_frequency_tie(self):
        cache = LFUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)  # Both have freq=1, evict 1 (least recent)
        assert cache.get(1) == -1
        assert cache.get(2) == 2

    def test_duplicate_key_update(self):
        cache = LFUCache(2)
        cache.put(1, 1)
        cache.put(1, 10)
        assert cache.get(1) == 10

    def test_frequency_tracking(self):
        cache = LFUCache(3)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)
        cache.get(1)  # freq[1] = 2
        cache.get(1)  # freq[1] = 3
        cache.get(2)  # freq[2] = 2
        cache.put(4, 4)  # evict 3 (freq=1)
        assert cache.get(3) == -1
