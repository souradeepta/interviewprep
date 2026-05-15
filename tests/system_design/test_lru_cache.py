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
        assert cache.get(1) == 1
        cache.put(3, 3)
        assert cache.get(2) == -1

    def test_duplicate_key_update(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(1, 10)
        assert cache.get(1) == 10

    def test_get_updates_recency(self):
        cache = LRUCache(3)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)
        cache.get(1)
        cache.put(4, 4)
        assert cache.get(2) == -1
        assert cache.get(1) == 1

    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put(1, 1)
        assert cache.get(1) == 1
        cache.put(2, 2)
        assert cache.get(1) == -1
        assert cache.get(2) == 2
