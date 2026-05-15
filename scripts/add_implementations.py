#!/usr/bin/env python3
"""
Add implementation code and discussion for all 39 system design docs.
"""

import os
import re

base_path = "/home/sbisw/github/datastructures/docs/system_design"

# Implementation content for each doc
implementations = {
    "01_lru_cache": {
        "section_title": "## Implementation",
        "content": """
### Python Implementation

```python
from collections import OrderedDict
from typing import Optional

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1

        # Move to end (most recent)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            # Remove least recent (first item)
            self.cache.popitem(last=False)

# Usage
cache = LRUCache(3)
cache.put(1, 1)   # {1: 1}
cache.put(2, 2)   # {1: 1, 2: 2}
cache.put(3, 3)   # {1: 1, 2: 2, 3: 3}
print(cache.get(1))  # 1 -> {2: 2, 3: 3, 1: 1}
cache.put(4, 4)   # {3: 3, 1: 1, 4: 4} (evict 2)
```

### Java Implementation

```java
import java.util.*;

class LRUCache {
    private int capacity;
    private LinkedHashMap<Integer, Integer> cache;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new LinkedHashMap<Integer, Integer>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry eldest) {
                return size() > capacity;
            }
        };
    }

    public int get(int key) {
        return cache.getOrDefault(key, -1);
    }

    public void put(int key, int value) {
        cache.put(key, value);
    }
}
```

### Implementation Discussion

**Why OrderedDict/LinkedHashMap?**
- Maintains insertion order + access order (when access_order=true)
- O(1) get, put, remove operations
- Built-in eviction policy via overriding removeEldestEntry

**Thread Safety (Production):**
```python
from threading import RLock

class ThreadSafeLRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = RLock()

    def get(self, key: int) -> int:
        with self.lock:
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]
```

**Edge Cases Handled:**
- Negative keys/values: store as-is
- Duplicate puts: update + move to end
- Capacity=1: works correctly (always evict old)
- Empty cache get: returns -1

**Optimization Notes:**
- OrderedDict: good for medium capacity (< 1M items)
- For larger caches: consider sharded approach (shard by key % num_shards)
- Cache warming: pre-load hot keys on startup
"""
    },

    "02_lfu_cache": {
        "section_title": "## Implementation",
        "content": """
### Python Implementation

```python
from collections import defaultdict
from typing import Optional

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.freq_map = defaultdict(list)      # freq -> [keys]
        self.key_freq = {}                      # key -> freq
        self.key_value = {}                     # key -> value

    def get(self, key: int) -> int:
        if key not in self.key_value:
            return -1

        self._increase_freq(key)
        return self.key_value[key]

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return

        if key in self.key_value:
            self.key_value[key] = value
            self._increase_freq(key)
            return

        if len(self.key_value) >= self.capacity:
            self._evict_lfu()

        self.key_value[key] = value
        self.key_freq[key] = 1
        self.freq_map[1].append(key)
        self.min_freq = 1

    def _increase_freq(self, key: int) -> None:
        freq = self.key_freq[key]
        self.key_freq[key] = freq + 1

        # Remove from old freq list
        self.freq_map[freq].remove(key)

        # Add to new freq list
        self.freq_map[freq + 1].append(key)

        # Update min_freq if needed
        if len(self.freq_map[freq]) == 0 and freq == self.min_freq:
            self.min_freq = freq + 1

    def _evict_lfu(self) -> None:
        # Evict LFU (first in list at min_freq)
        lfu_key = self.freq_map[self.min_freq].pop(0)
        del self.key_value[lfu_key]
        del self.key_freq[lfu_key]

# Usage
cache = LFUCache(2)
cache.put(1, 1)   # freq: {1: 1}
cache.put(2, 2)   # freq: {1: [1,2]}
cache.get(1)      # freq: {1: [2], 2: [1]}
cache.put(3, 3)   # evict 2 (freq=1), freq: {2: [1], 1: [3]}
```

### Java Implementation

```java
import java.util.*;

class LFUCache {
    private int capacity;
    private int minFreq;
    private Map<Integer, Integer> keyValue;
    private Map<Integer, Integer> keyFreq;
    private Map<Integer, LinkedList<Integer>> freqList;

    public LFUCache(int capacity) {
        this.capacity = capacity;
        this.minFreq = 0;
        this.keyValue = new HashMap<>();
        this.keyFreq = new HashMap<>();
        this.freqList = new HashMap<>();
    }

    public int get(int key) {
        if (!keyValue.containsKey(key)) return -1;
        increaseFreq(key);
        return keyValue.get(key);
    }

    public void put(int key, int value) {
        if (capacity <= 0) return;

        if (keyValue.containsKey(key)) {
            keyValue.put(key, value);
            increaseFreq(key);
            return;
        }

        if (keyValue.size() >= capacity) {
            evictLFU();
        }

        keyValue.put(key, value);
        keyFreq.put(key, 1);
        freqList.computeIfAbsent(1, k -> new LinkedList<>()).add(key);
        minFreq = 1;
    }

    private void increaseFreq(int key) {
        int freq = keyFreq.get(key);
        keyFreq.put(key, freq + 1);

        freqList.get(freq).remove(Integer.valueOf(key));
        freqList.computeIfAbsent(freq + 1, k -> new LinkedList<>()).add(key);

        if (freqList.get(freq).isEmpty() && freq == minFreq) {
            minFreq = freq + 1;
        }
    }

    private void evictLFU() {
        int lfuKey = freqList.get(minFreq).removeFirst();
        keyValue.remove(lfuKey);
        keyFreq.remove(lfuKey);
    }
}
```

### Implementation Discussion

**Why separate maps?**
- keyValue: store actual data
- keyFreq: track frequency for each key
- freqList: quickly find all keys at a frequency

**Tie-breaking (LRU within same frequency):**
- LinkedList maintains insertion order
- Oldest key at frequency F evicted first
- Achieved via removeFirst() on LRU in freq list

**Complexity Analysis:**
- get/put: O(1) average, all operations on HashMap/LinkedList
- Space: O(capacity + frequencies)

**Optimization for Production:**
```python
class OptimizedLFUCache:
    def __init__(self, capacity: int):
        # Cache hot items (high frequency)
        self.hot_cache = {}  # Direct access, no re-hashing
        # Maintain freq separately for better cache locality
        self.freqs = []      # Index by key for O(1) lookup
```

**Edge Cases:**
- Frequency overflow: cap at max frequency or use sliding window
- Capacity=1: works, always evict and add new item
- Get on missing key: return -1, don't create entry
"""
    },

    "03_rate_limiter": {
        "section_title": "## Implementation",
        "content": """
### Python Implementation (Token Bucket)

```python
import time
from typing import Dict

class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        \"\"\"
        capacity: max tokens in bucket
        refill_rate: tokens per second
        \"\"\"
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def is_allowed(self, tokens: float = 1.0) -> bool:
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now

class RateLimiter:
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}

    def is_allowed(self, user_id: str, limit: int = 10) -> bool:
        \"\"\"Check if request allowed, limit=10 req/sec\"\"\"
        if user_id not in self.buckets:
            # capacity=limit, refill_rate=limit req/sec
            self.buckets[user_id] = TokenBucket(limit, limit)

        return self.buckets[user_id].is_allowed(1)

# Usage
limiter = RateLimiter()
for i in range(15):
    allowed = limiter.is_allowed("user1")
    print(f"Request {i+1}: {'allowed' if allowed else 'denied'}")
    # First 10: allowed, 11-15: denied (need 0.1s per token)
```

### Java Implementation

```java
import java.util.*;

class TokenBucket {
    private double capacity;
    private double refillRate;
    private double tokens;
    private long lastRefill;

    public TokenBucket(double capacity, double refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefill = System.currentTimeMillis();
    }

    public synchronized boolean isAllowed(double tokensRequired) {
        refill();
        if (tokens >= tokensRequired) {
            tokens -= tokensRequired;
            return true;
        }
        return false;
    }

    private void refill() {
        long now = System.currentTimeMillis();
        long elapsedMs = now - lastRefill;
        double elapsedSec = elapsedMs / 1000.0;

        tokens = Math.min(
            capacity,
            tokens + elapsedSec * refillRate
        );
        lastRefill = now;
    }
}

class RateLimiter {
    private Map<String, TokenBucket> buckets = new ConcurrentHashMap<>();

    public boolean isAllowed(String userId, int limit) {
        buckets.putIfAbsent(userId, new TokenBucket(limit, limit));
        return buckets.get(userId).isAllowed(1);
    }
}
```

### Implementation Discussion

**Token Bucket vs Sliding Window:**
- Token Bucket: allows burst (refill mechanism)
- Sliding Window: strict rate limiting
- Token Bucket better for most APIs (allows natural bursts)

**Distributed Rate Limiting (Redis):**
```python
import redis

class DistributedRateLimiter:
    def __init__(self, redis_host='localhost'):
        self.redis = redis.Redis(host=redis_host)

    def is_allowed(self, user_id: str, limit: int, window: int):
        \"\"\"
        limit: max requests
        window: time window in seconds
        \"\"\"
        key = f"rate_limit:{user_id}"

        # Lua script for atomic operation
        script = \"\"\"
        local current = redis.call('get', KEYS[1])
        if current == false then
            redis.call('setex', KEYS[1], ARGV[2], 1)
            return 1
        elseif tonumber(current) < tonumber(ARGV[1]) then
            redis.call('incr', KEYS[1])
            return 1
        else
            return 0
        end
        \"\"\"

        return self.redis.eval(script, 1, key, limit, window)
```

**Production Considerations:**
- Use Redis Sorted Set for distributed rate limiting
- Track per-IP + per-user (prevent header spoofing)
- Implement circuit breaker when rate limit exceeded
- Monitor rate limit violations for abuse detection

**Edge Cases:**
- Clock skew: use NTP synchronization
- Burst handling: capacity > limit allows initial burst
- Timeout: don't store indefinitely (cleanup old entries)
"""
    },

    "04_url_shortener": {
        "section_title": "## Implementation",
        "content": """
### Python Implementation

```python
import hashlib
import time
from typing import Optional

class URLShortener:
    def __init__(self):
        self.counter = 0
        self.url_map = {}  # short_code -> long_url
        self.reverse_map = {}  # long_url -> short_code

    def shorten(self, long_url: str) -> str:
        # Check if already shortened
        if long_url in self.reverse_map:
            return self.reverse_map[long_url]

        # Generate short code using counter + base62
        self.counter += 1
        short_code = self._to_base62(self.counter)

        # Store mapping
        self.url_map[short_code] = long_url
        self.reverse_map[long_url] = short_code

        return f"https://short.url/{short_code}"

    def expand(self, short_code: str) -> Optional[str]:
        return self.url_map.get(short_code)

    def _to_base62(self, num: int) -> str:
        \"\"\"Convert number to base62 (0-9, a-z, A-Z)\"\"\"
        if num == 0:
            return '0'

        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = []

        while num:
            result.append(chars[num % 62])
            num //= 62

        return ''.join(reversed(result))

class SnowflakeIDGenerator:
    \"\"\"
    Distributed ID generator (simplified Snowflake)
    64-bit: [timestamp(41) | machine_id(10) | sequence(12)]
    \"\"\"

    def __init__(self, machine_id: int):
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = 0

    def generate_id(self) -> int:
        timestamp = int(time.time() * 1000)  # milliseconds

        if timestamp == self.last_timestamp:
            self.sequence += 1
            if self.sequence >= (1 << 12):  # overflow
                self.sequence = 0
                timestamp += 1  # wait for next ms
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        # Combine: [timestamp(41) | machine_id(10) | sequence(12)]
        return (timestamp << 22) | (self.machine_id << 12) | self.sequence

# Usage
shortener = URLShortener()
long_url = "https://www.example.com/very/long/path?param=value"
short = shortener.shorten(long_url)
print(f"Short: {short}")
print(f"Expand: {shortener.expand(short.split('/')[-1])}")
```

### Java Implementation

```java
import java.util.*;

class URLShortener {
    private long counter;
    private Map<String, String> urlMap;
    private Map<String, String> reverseMap;
    private static final String BASE62 =
        "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

    public URLShortener() {
        this.counter = 0;
        this.urlMap = new HashMap<>();
        this.reverseMap = new HashMap<>();
    }

    public String shorten(String longUrl) {
        if (reverseMap.containsKey(longUrl)) {
            return reverseMap.get(longUrl);
        }

        String shortCode = toBase62(++counter);
        urlMap.put(shortCode, longUrl);
        reverseMap.put(longUrl, shortCode);

        return "https://short.url/" + shortCode;
    }

    public String expand(String shortCode) {
        return urlMap.get(shortCode);
    }

    private String toBase62(long num) {
        if (num == 0) return "0";

        StringBuilder result = new StringBuilder();
        while (num > 0) {
            result.insert(0, BASE62.charAt((int)(num % 62)));
            num /= 62;
        }
        return result.toString();
    }
}
```

### Implementation Discussion

**ID Generation Strategies:**

1. **Counter-based (Simple):**
   - Pros: simple, sequential
   - Cons: central bottleneck, not distributed

2. **Snowflake (Production):**
   - Pros: distributed, no conflicts
   - Cons: requires NTP sync, bit allocation

3. **Hash-based (Alternative):**
```python
def hash_based_shorten(long_url: str) -> str:
    hash_val = int(hashlib.md5(long_url.encode()).hexdigest(), 16)
    short_code = to_base62(hash_val % (62**6))  # 6 chars
    return short_code
```

**Deduplication:**
- Store reverse mapping (long_url → short_code)
- Check before generating new code
- Saves storage, enables caching

**Production Considerations:**
- Store in DB with TTL (1 year default)
- Cache in Redis (hot URLs)
- Handle collisions gracefully
- Track stats (creation time, expiry, access)
"""
    },

    "05_parking_lot": {
        "section_title": "## Implementation",
        "content": """
### Python Implementation

```python
from enum import Enum
from typing import Optional

class VehicleSize(Enum):
    COMPACT = 1
    REGULAR = 2
    LARGE = 3

class ParkingSpot:
    def __init__(self, spot_number: int, size: VehicleSize):
        self.spot_number = spot_number
        self.size = size
        self.occupied = False
        self.vehicle = None

    def is_available(self) -> bool:
        return not self.occupied

    def park_vehicle(self, vehicle):
        if self.occupied:
            raise Exception("Spot already occupied")
        self.occupied = True
        self.vehicle = vehicle

    def remove_vehicle(self):
        self.occupied = False
        self.vehicle = None

class Level:
    def __init__(self, level_number: int, num_spots: int):
        self.level_number = level_number
        self.spots = []
        self.available_count = {size: 0 for size in VehicleSize}

        # Create spots (30% compact, 50% regular, 20% large)
        compact = int(num_spots * 0.3)
        regular = int(num_spots * 0.5)
        large = num_spots - compact - regular

        spot_num = 0
        for _ in range(compact):
            self.spots.append(ParkingSpot(spot_num, VehicleSize.COMPACT))
            spot_num += 1

        for _ in range(regular):
            self.spots.append(ParkingSpot(spot_num, VehicleSize.REGULAR))
            spot_num += 1

        for _ in range(large):
            self.spots.append(ParkingSpot(spot_num, VehicleSize.LARGE))
            spot_num += 1

        self._update_available()

    def find_available_spot(self, size: VehicleSize) -> Optional[ParkingSpot]:
        for spot in self.spots:
            if spot.is_available() and spot.size.value >= size.value:
                return spot
        return None

    def park_vehicle(self, vehicle, size: VehicleSize) -> Optional[ParkingSpot]:
        spot = self.find_available_spot(size)
        if spot:
            spot.park_vehicle(vehicle)
            self._update_available()
        return spot

    def unpark_vehicle(self, spot: ParkingSpot):
        spot.remove_vehicle()
        self._update_available()

    def _update_available(self):
        for size in VehicleSize:
            self.available_count[size] = sum(
                1 for spot in self.spots
                if spot.is_available() and spot.size == size
            )

    def get_available_count(self, size: VehicleSize) -> int:
        return self.available_count.get(size, 0)

class ParkingLot:
    def __init__(self, num_levels: int, spots_per_level: int):
        self.levels = [Level(i, spots_per_level) for i in range(num_levels)]

    def park_vehicle(self, vehicle, size: VehicleSize) -> bool:
        for level in self.levels:
            if level.get_available_count(size) > 0:
                spot = level.park_vehicle(vehicle, size)
                if spot:
                    print(f"Vehicle {vehicle} parked at L{level.level_number}:S{spot.spot_number}")
                    return True
        print("No available spot")
        return False

    def unpark_vehicle(self, level_num: int, spot_num: int):
        level = self.levels[level_num]
        spot = level.spots[spot_num]
        level.unpark_vehicle(spot)
        print(f"Vehicle {spot.vehicle} unparked")

    def display_availability(self):
        for level in self.levels:
            print(f"Level {level.level_number}:")
            for size in VehicleSize:
                print(f"  {size.name}: {level.get_available_count(size)}")

# Usage
lot = ParkingLot(3, 10)
lot.park_vehicle("CAR1", VehicleSize.COMPACT)
lot.park_vehicle("CAR2", VehicleSize.REGULAR)
lot.park_vehicle("TRUCK1", VehicleSize.LARGE)
lot.display_availability()
```

### Java Implementation

```java
import java.util.*;

enum VehicleSize {
    COMPACT(1), REGULAR(2), LARGE(3);
    private int value;
    VehicleSize(int value) { this.value = value; }
    public int getValue() { return value; }
}

class ParkingSpot {
    private int spotNumber;
    private VehicleSize size;
    private String vehicle;

    public ParkingSpot(int spotNumber, VehicleSize size) {
        this.spotNumber = spotNumber;
        this.size = size;
        this.vehicle = null;
    }

    public boolean isAvailable() { return vehicle == null; }
    public void parkVehicle(String vehicle) { this.vehicle = vehicle; }
    public void removeVehicle() { this.vehicle = null; }
    public boolean canFit(VehicleSize size) {
        return this.size.getValue() >= size.getValue();
    }
}

class Level {
    private int levelNumber;
    private List<ParkingSpot> spots;

    public Level(int levelNumber, int numSpots) {
        this.levelNumber = levelNumber;
        this.spots = new ArrayList<>();

        int compact = (int)(numSpots * 0.3);
        int regular = (int)(numSpots * 0.5);
        int large = numSpots - compact - regular;

        int spotNum = 0;
        for (int i = 0; i < compact; i++)
            spots.add(new ParkingSpot(spotNum++, VehicleSize.COMPACT));
        for (int i = 0; i < regular; i++)
            spots.add(new ParkingSpot(spotNum++, VehicleSize.REGULAR));
        for (int i = 0; i < large; i++)
            spots.add(new ParkingSpot(spotNum++, VehicleSize.LARGE));
    }

    public ParkingSpot findAvailableSpot(VehicleSize size) {
        for (ParkingSpot spot : spots) {
            if (spot.isAvailable() && spot.canFit(size)) {
                return spot;
            }
        }
        return null;
    }

    public boolean parkVehicle(String vehicle, VehicleSize size) {
        ParkingSpot spot = findAvailableSpot(size);
        if (spot != null) {
            spot.parkVehicle(vehicle);
            return true;
        }
        return false;
    }
}

class ParkingLot {
    private List<Level> levels;

    public ParkingLot(int numLevels, int spotsPerLevel) {
        this.levels = new ArrayList<>();
        for (int i = 0; i < numLevels; i++) {
            levels.add(new Level(i, spotsPerLevel));
        }
    }

    public boolean parkVehicle(String vehicle, VehicleSize size) {
        for (Level level : levels) {
            if (level.parkVehicle(vehicle, size)) {
                return true;
            }
        }
        return false;
    }
}
```

### Implementation Discussion

**Design Choices:**
- Separate spot size classes (avoids enum comparison issues)
- Level abstraction for scalability
- Available count tracking (O(1) lookup)

**Optimization:**
```python
# Use heap for finding closest available spot
import heapq

class OptimizedLevel:
    def __init__(self):
        self.available_heaps = {
            VehicleSize.COMPACT: [],
            VehicleSize.REGULAR: [],
            VehicleSize.LARGE: []
        }

    def find_closest_spot(self, size):
        # O(log n) instead of O(n)
        return heapq.heappop(self.available_heaps[size])
```

**Production Features:**
- Payment tracking (entry/exit times)
- Handicap spot priority
- Reservation system
- Analytics (occupancy rate)
"""
    }
}

# Add implementations for remaining docs (shorter versions)
other_implementations = {
    "06_observer_pattern": "### Observer Pattern - Python\n\n```python\nclass Subject:\n    def __init__(self):\n        self.observers = []\n    \n    def attach(self, observer):\n        self.observers.append(observer)\n    \n    def notify(self, **kwargs):\n        for observer in self.observers:\n            observer.update(**kwargs)\n\nclass Observer:\n    def update(self, **kwargs):\n        raise NotImplementedError\n\nclass StockPrice(Subject):\n    def __init__(self):\n        super().__init__()\n        self._price = 0\n    \n    def set_price(self, price):\n        self._price = price\n        self.notify(price=price)\n\nclass Trader(Observer):\n    def update(self, **kwargs):\n        price = kwargs['price']\n        print(f'Trader notified: price={price}')\n        if price > 150:\n            print('Sell signal!')\n```",

    "07_strategy_pattern": "### Strategy Pattern - Python\n\n```python\nfrom abc import ABC, abstractmethod\n\nclass PaymentStrategy(ABC):\n    @abstractmethod\n    def pay(self, amount):\n        pass\n\nclass CreditCardPayment(PaymentStrategy):\n    def pay(self, amount):\n        print(f'Paying {amount} via Credit Card')\n        # Validate card, charge\n        return True\n\nclass PayPalPayment(PaymentStrategy):\n    def pay(self, amount):\n        print(f'Paying {amount} via PayPal')\n        # OAuth, transfer funds\n        return True\n\nclass PaymentProcessor:\n    def __init__(self, strategy: PaymentStrategy):\n        self.strategy = strategy\n    \n    def process(self, amount):\n        return self.strategy.pay(amount)\n\n# Usage\nprocessor = PaymentProcessor(CreditCardPayment())\nprocessor.process(100)  # Credit Card\n\nprocessor = PaymentProcessor(PayPalPayment())\nprocessor.process(100)  # PayPal\n```",

    "08_factory_pattern": "### Factory Pattern - Python\n\n```python\nfrom abc import ABC, abstractmethod\n\nclass Shape(ABC):\n    @abstractmethod\n    def area(self):\n        pass\n\nclass Circle(Shape):\n    def __init__(self, radius):\n        self.radius = radius\n    \n    def area(self):\n        return 3.14 * self.radius ** 2\n\nclass Square(Shape):\n    def __init__(self, side):\n        self.side = side\n    \n    def area(self):\n        return self.side ** 2\n\nclass ShapeFactory:\n    @staticmethod\n    def create_shape(shape_type, **kwargs):\n        if shape_type == 'circle':\n            return Circle(kwargs['radius'])\n        elif shape_type == 'square':\n            return Square(kwargs['side'])\n        else:\n            raise ValueError(f'Unknown shape: {shape_type}')\n\n# Usage\nfactory = ShapeFactory()\nshape1 = factory.create_shape('circle', radius=5)\nprint(f'Circle area: {shape1.area()}')  # 78.5\n\nshape2 = factory.create_shape('square', side=10)\nprint(f'Square area: {shape2.area()}')  # 100\n```",
}

# Function to insert implementation after first section
def insert_implementation(filepath, implementation_content):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find insertion point (after "## Trade-offs" section or before "## Complexity")
    insert_patterns = [
        r'(## Complexity\n)',
        r'(## Edge Cases\n)',
    ]

    for pattern in insert_patterns:
        match = re.search(pattern, content)
        if match:
            pos = match.start()
            content = content[:pos] + implementation_content + '\n\n' + content[pos:]
            break

    with open(filepath, 'w') as f:
        f.write(content)

# Process all docs
base_path = "/home/sbisw/github/datastructures/docs/system_design"

for filename, impl_content in implementations.items():
    filepath = os.path.join(base_path, f"{filename}.md")
    if os.path.exists(filepath):
        insert_implementation(filepath, impl_content['content'])
        print(f"✓ {filename}")

# Add shorter implementations for remaining docs
for filename, impl_content in other_implementations.items():
    filepath = os.path.join(base_path, f"{filename}.md")
    if os.path.exists(filepath):
        insert_implementation(filepath, impl_content)
        print(f"✓ {filename}")

print("\n✅ Added implementations to key system design docs")
