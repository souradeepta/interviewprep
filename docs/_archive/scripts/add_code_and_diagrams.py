#!/usr/bin/env python3
"""
Add code implementations and UML diagrams to all system design docs.
"""

import os
import re
import glob

base_path = "/home/sbisw/github/interviewprep/docs/system_design"

# Implementation templates by concept type
implementations = {
    # Caching
    "lru_cache": {
        "python": """```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```""",
        "java": """```java
class LRUCache {
    private final int capacity;
    private final java.util.LinkedHashMap<Integer, Integer> cache;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new java.util.LinkedHashMap<Integer, Integer>(capacity, 0.75f, true) {
            protected boolean removeEldestEntry(java.util.Map.Entry eldest) {
                return size() > LRUCache.this.capacity;
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
```"""
    },
    "rate_limiter": {
        "python": """```python
import time
from collections import deque

class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def allow_request(self) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity,
                         self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```""",
        "java": """```java
class TokenBucketLimiter {
    private double tokens;
    private final double capacity;
    private final double refillRate;
    private long lastRefill;

    public TokenBucketLimiter(double capacity, double refillRate) {
        this.capacity = capacity;
        this.tokens = capacity;
        this.refillRate = refillRate;
        this.lastRefill = System.currentTimeMillis();
    }

    public synchronized boolean allowRequest() {
        long now = System.currentTimeMillis();
        long elapsed = now - lastRefill;
        tokens = Math.min(capacity, tokens + (elapsed * refillRate / 1000));
        lastRefill = now;

        if (tokens >= 1) {
            tokens -= 1;
            return true;
        }
        return false;
    }
}
```"""
    },
    "url_shortener": {
        "python": """```python
class URLShortener:
    def __init__(self):
        self.mapping = {}
        self.reverse_mapping = {}
        self.counter = 0

    def encode(self, url: str) -> str:
        if url in self.reverse_mapping:
            return self.reverse_mapping[url]

        encoded = self._to_base62(self.counter)
        self.counter += 1
        self.mapping[encoded] = url
        self.reverse_mapping[url] = encoded
        return encoded

    def decode(self, code: str) -> str:
        return self.mapping.get(code, "")

    def _to_base62(self, num: int) -> str:
        chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if num == 0:
            return chars[0]
        result = ""
        while num > 0:
            result = chars[num % 62] + result
            num //= 62
        return result
```""",
        "java": """```java
class URLShortener {
    private java.util.Map<String, String> mapping = new java.util.HashMap<>();
    private java.util.Map<String, String> reverse = new java.util.HashMap<>();
    private long counter = 0;

    public String encode(String url) {
        if (reverse.containsKey(url)) {
            return reverse.get(url);
        }
        String encoded = toBase62(counter++);
        mapping.put(encoded, url);
        reverse.put(url, encoded);
        return encoded;
    }

    public String decode(String code) {
        return mapping.getOrDefault(code, "");
    }

    private String toBase62(long num) {
        String chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
        if (num == 0) return "0";
        StringBuilder sb = new StringBuilder();
        while (num > 0) {
            sb.insert(0, chars.charAt((int)(num % 62)));
            num /= 62;
        }
        return sb.toString();
    }
}
```"""
    },
    "auction_system": {
        "python": """```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import time

class AuctionStatus(Enum):
    OPEN = "open"
    ACTIVE = "active"
    CLOSED = "closed"
    SETTLED = "settled"

@dataclass
class Bid:
    user_id: int
    amount: float
    timestamp: float

class AuctionSystem:
    def __init__(self):
        self.auctions = {}
        self.bids = {}

    def create_auction(self, auction_id: int, item: str, start_price: float, end_time: float):
        self.auctions[auction_id] = {
            'item': item,
            'start_price': start_price,
            'end_time': end_time,
            'status': AuctionStatus.OPEN,
            'highest_bid': start_price
        }
        self.bids[auction_id] = []

    def place_bid(self, auction_id: int, user_id: int, amount: float) -> bool:
        auction = self.auctions.get(auction_id)
        if not auction or time.time() > auction['end_time']:
            return False

        if amount <= auction['highest_bid']:
            return False

        auction['highest_bid'] = amount
        self.bids[auction_id].append(Bid(user_id, amount, time.time()))
        return True

    def get_highest_bid(self, auction_id: int) -> Optional[float]:
        return self.auctions.get(auction_id, {}).get('highest_bid')

    def finalize_auction(self, auction_id: int) -> Optional[int]:
        bids = sorted(self.bids[auction_id], key=lambda b: b.amount, reverse=True)
        if bids:
            winner = bids[0].user_id
            self.auctions[auction_id]['status'] = AuctionStatus.SETTLED
            return winner
        return None
```""",
        "java": """```java
class AuctionSystem {
    enum AuctionStatus { OPEN, ACTIVE, CLOSED, SETTLED }

    static class Bid {
        int userId;
        double amount;
        long timestamp;

        Bid(int userId, double amount, long timestamp) {
            this.userId = userId;
            this.amount = amount;
            this.timestamp = timestamp;
        }
    }

    static class Auction {
        String item;
        double highestBid;
        long endTime;
        AuctionStatus status;
        java.util.List<Bid> bids;
    }

    private java.util.Map<Integer, Auction> auctions = new java.util.HashMap<>();

    public void createAuction(int id, String item, double startPrice, long endTime) {
        Auction a = new Auction();
        a.item = item;
        a.highestBid = startPrice;
        a.endTime = endTime;
        a.status = AuctionStatus.OPEN;
        a.bids = new java.util.ArrayList<>();
        auctions.put(id, a);
    }

    public boolean placeBid(int auctionId, int userId, double amount) {
        Auction a = auctions.get(auctionId);
        if (a == null || System.currentTimeMillis() > a.endTime) return false;
        if (amount <= a.highestBid) return false;

        a.highestBid = amount;
        a.bids.add(new Bid(userId, amount, System.currentTimeMillis()));
        return true;
    }

    public Integer finalizeAuction(int auctionId) {
        Auction a = auctions.get(auctionId);
        if (a == null || a.bids.isEmpty()) return null;

        a.bids.sort((b1, b2) -> Double.compare(b2.amount, b1.amount));
        a.status = AuctionStatus.SETTLED;
        return a.bids.get(0).userId;
    }
}
```"""
    }
}

uml_diagrams = {
    "auction_system": """## UML Diagram

```
┌──────────────────┐
│    Auction       │
├──────────────────┤
│- id: int         │
│- item: String    │
│- status: Enum    │
│- endTime: long   │
├──────────────────┤
│+ placeBid()      │
│+ finalize()      │
│+ getWinner()     │
└──────────────────┘
         │
         │ contains
         ↓
┌──────────────────┐
│      Bid         │
├──────────────────┤
│- userId: int     │
│- amount: double  │
│- timestamp: long │
└──────────────────┘

┌──────────────────┐
│  AuctionSystem   │
├──────────────────┤
│- auctions: Map   │
│- bids: Map       │
├──────────────────┤
│+ createAuction() │
│+ placeBid()      │
│+ finalize()      │
└──────────────────┘
```"""
}

def find_and_replace_implementation(filepath, concept_name):
    """Find and replace placeholder implementations with real code."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if we have implementations for this concept
    for key, impl in implementations.items():
        if key in concept_name.lower() or key in filepath.lower():
            # Replace Python implementation
            python_pattern = r"```python\n# Working implementation with key mechanisms[^`]*```"
            content = re.sub(python_pattern, impl['python'], content, flags=re.DOTALL)

            # Replace Java implementation
            java_pattern = r"```java\n// Object-oriented implementation[^`]*```"
            content = re.sub(java_pattern, impl['java'], content, flags=re.DOTALL)
            break

    with open(filepath, 'w') as f:
        f.write(content)

    return True

def add_uml_diagram(filepath, concept_name):
    """Add UML diagram if applicable."""
    for key, diagram in uml_diagrams.items():
        if key in concept_name.lower() or key in filepath.lower():
            with open(filepath, 'r') as f:
                content = f.read()

            # Add UML before Implementation section
            if "## Implementation" in content and diagram not in content:
                content = content.replace("## Implementation", diagram + "\n\n## Implementation")
                with open(filepath, 'w') as f:
                    f.write(content)
            break

# Process all markdown files
updated_count = 0
for filepath in glob.glob(f"{base_path}/*/*_*.md"):
    try:
        filename = os.path.basename(filepath)
        find_and_replace_implementation(filepath, filename)
        add_uml_diagram(filepath, filename)
        updated_count += 1
        if updated_count % 10 == 0:
            print(f"✓ Processed {updated_count} files")
    except Exception as e:
        print(f"⚠ {filepath}: {str(e)}")

print(f"\n✅ Enhanced {updated_count} system design documents with code and diagrams")
