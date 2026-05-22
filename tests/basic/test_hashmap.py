import pytest
from python.basic.hashmap import ChainingHashMap


class TestHashMap:
    def test_put_and_get(self):
        h = ChainingHashMap()
        h.put("a", 1)
        assert h.get("a") == 1

    def test_overwrite_key(self):
        h = ChainingHashMap()
        h.put("x", 10)
        h.put("x", 20)
        assert h.get("x") == 20

    def test_get_missing_key(self):
        h = ChainingHashMap()
        with pytest.raises(KeyError):
            h.get("missing")

    def test_delete(self):
        h = ChainingHashMap()
        h.put("k", 5)
        h.delete("k")
        with pytest.raises(KeyError):
            h.get("k")

    def test_multiple_keys(self):
        h = ChainingHashMap()
        for i in range(20):
            h.put(str(i), i * 2)
        for i in range(20):
            assert h.get(str(i)) == i * 2

    def test_contains(self):
        h = ChainingHashMap()
        h.put("z", 99)
        assert h.contains("z")
        assert not h.contains("missing")
