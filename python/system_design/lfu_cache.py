"""LFU Cache - Least Frequently Used eviction policy"""

from collections import defaultdict, OrderedDict


class LFUCache:
    """O(1) LFU Cache using frequency map + doubly linked list"""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> value
        self.freq_map = defaultdict(int)  # key -> frequency
        self.freq_list = defaultdict(OrderedDict)  # freq -> OrderedDict(keys)
        self.min_freq = 0

    def get(self, key: int) -> int:
        """Get value and increment frequency"""
        if key not in self.cache:
            return -1

        value = self.cache[key]
        self._increment_freq(key)
        return value

    def put(self, key: int, value: int) -> None:
        """Insert/update key-value pair"""
        if self.capacity <= 0:
            return

        if key in self.cache:
            self.cache[key] = value
            self._increment_freq(key)
            return

        if len(self.cache) >= self.capacity:
            self._evict_lfu()

        self.cache[key] = value
        self.freq_map[key] = 1
        self.freq_list[1][key] = None
        self.min_freq = 1

    def _increment_freq(self, key):
        """Increment frequency and update structure"""
        freq = self.freq_map[key]
        del self.freq_list[freq][key]

        if not self.freq_list[freq]:
            del self.freq_list[freq]
            if freq == self.min_freq:
                self.min_freq = freq + 1

        new_freq = freq + 1
        self.freq_map[key] = new_freq
        self.freq_list[new_freq][key] = None

    def _evict_lfu(self):
        """Evict least frequently used (and least recently used among same frequency)"""
        evict_key = next(iter(self.freq_list[self.min_freq]))
        del self.freq_list[self.min_freq][evict_key]
        del self.freq_map[evict_key]
        del self.cache[evict_key]


if __name__ == "__main__":
    cache = LFUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(f"get(1): {cache.get(1)}")  # 1
    cache.put(3, 3)
    print(f"get(2): {cache.get(2)}")  # -1 (evicted, freq=1)
    print(f"get(3): {cache.get(3)}")  # 3
    cache.put(4, 4)
    print(f"get(1): {cache.get(1)}")  # 1 (not evicted, freq=2)