# API Pagination & Filtering

**Level:** L4-L5
**Time to read:** ~20 min

Design efficient, consistent pagination for APIs serving millions of records without degrading database performance.

---

## ⚖️ Pagination Strategy Trade-offs

| Strategy | Performance | Consistency | Seek to page | Real-time data | Best For |
|----------|-------------|-------------|---|---|---|
| **Offset/Limit** | Degrades at high offset | Poor (inserts shift pages) | Yes (page #) | No | Admin UIs, small datasets |
| **Cursor (opaque)** | O(log n) always | Good | No | Yes | Mobile feeds, APIs |
| **Keyset** | O(log n) always | Good | Partial | Yes | Sorted lists, feeds |
| **Seek** | O(log n) always | Good | Yes (with key) | Yes | Infinite scroll, search |
| **Time-based** | O(log n) | Good | Yes | Yes | Event logs, audit trails |

### Performance at Scale

```
OFFSET at different pages (10M-row table):
  Page 1    (OFFSET 0):          5ms
  Page 100  (OFFSET 990):       12ms
  Page 1K   (OFFSET 9990):      85ms
  Page 10K  (OFFSET 99990):   1200ms   ← full index scan, unusable

Keyset at any page:
  Any page:  3–8ms (index seek, constant regardless of depth)

Root cause: OFFSET must count through N rows even with an index.
```

---

## 🏗️ Pagination Patterns

### Pattern 1: Offset-Based

```sql
-- Page 3, 10 rows per page
SELECT id, title, created_at
FROM posts
ORDER BY created_at DESC
LIMIT 10 OFFSET 20;

-- Problems:
-- New post inserted → page 2 shifts → duplicates on page 3
-- OFFSET 1,000,000 scans 1M rows then returns 10
```

### Pattern 2: Cursor-Based (Opaque Token)

```
Client receives:
{
  "data": [...],
  "next_cursor": "eyJpZCI6IDEyMywgInRzIjogMTcwMDAwMH0="
}

Server decodes cursor → extracts {id: 123, ts: 1700000}
→ issues keyset query WHERE (created_at, id) < ($ts, $id)

Benefits:
  - Cursor is opaque (clients cannot manipulate internals)
  - Server can change cursor format with versioning
  - Works with any sort order
```

### Pattern 3: Keyset Pagination

```sql
-- First page
SELECT id, title, created_at FROM posts
ORDER BY created_at DESC, id DESC
LIMIT 10;
-- Last row: created_at=2024-01-15, id=500

-- Next page — pass last row values as anchor
SELECT id, title, created_at FROM posts
WHERE (created_at, id) < ('2024-01-15', 500)
ORDER BY created_at DESC, id DESC
LIMIT 10;

-- Required index: (created_at DESC, id DESC) — instant seek!
```

### Pattern 4: Bidirectional Seek

```
┌─────────────────────────────────────────────┐
│  Bidirectional Seek Pagination               │
│                                              │
│  ← prev  [anchor: created_at=T, id=400]  next →  │
│                                              │
│  Forward:  WHERE (created_at, id) < (T, 400)│
│            ORDER BY created_at DESC, id DESC│
│                                              │
│  Backward: WHERE (created_at, id) > (T, 400)│
│            ORDER BY created_at ASC, id ASC  │
│            (then reverse in application)    │
└─────────────────────────────────────────────┘
```

---

## 📊 Cursor Paginator Implementation

```python
import base64, json, time, hmac, hashlib, os
from typing import Optional, List

CURSOR_SECRET = os.environ.get("CURSOR_SECRET", "dev-secret-change-in-prod")

class CursorPaginator:
    def __init__(self, page_size: int = 20):
        self.page_size = page_size

    def encode_cursor(self, **fields) -> str:
        payload = json.dumps(fields, sort_keys=True, default=str)
        sig = hmac.new(CURSOR_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:12]
        raw = f"{payload}|{sig}"
        return base64.urlsafe_b64encode(raw.encode()).decode()

    def decode_cursor(self, cursor: str) -> dict:
        try:
            raw = base64.urlsafe_b64decode(cursor.encode()).decode()
            payload, sig = raw.rsplit("|", 1)
            expected = hmac.new(CURSOR_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:12]
            if not hmac.compare_digest(sig, expected):
                raise ValueError("Tampered cursor")
            return json.loads(payload)
        except (ValueError, json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid cursor: {e}")

    def paginate(self, items: List[dict], cursor: Optional[str] = None) -> dict:
        """In-memory demo. In production, push WHERE clause to the database."""
        sorted_items = sorted(items, key=lambda x: (x["created_at"], x["id"]), reverse=True)

        start = 0
        if cursor:
            anchor = self.decode_cursor(cursor)
            start = next(
                (i + 1 for i, item in enumerate(sorted_items)
                 if item["id"] == anchor["id"]),
                0
            )

        page = sorted_items[start: start + self.page_size]

        next_cursor = (
            self.encode_cursor(id=page[-1]["id"], created_at=page[-1]["created_at"])
            if len(page) == self.page_size else None
        )

        return {
            "data": page,
            "next_cursor": next_cursor,
            "has_more": next_cursor is not None,
            "count": len(page),
        }


# Demo
posts = [{"id": i, "title": f"Post {i}", "created_at": int(time.time()) - i * 60}
         for i in range(1, 101)]

pager = CursorPaginator(page_size=5)
p1 = pager.paginate(posts)
print("Page 1:", [p["id"] for p in p1["data"]])
p2 = pager.paginate(posts, cursor=p1["next_cursor"])
print("Page 2:", [p["id"] for p in p2["data"]])
```

---

## 🔍 Filter Design

### Safe Filter Builder

```python
from typing import Dict, Any, Tuple

ALLOWED_FILTERS = {"status", "user_id", "amount_gte", "amount_lte", "created_after"}
ALLOWED_SORTS   = {"created_at", "amount", "id"}

def build_filter_query(filters: Dict[str, Any], sort: str = "-created_at",
                       cursor_anchor: Optional[dict] = None, limit: int = 20) -> Tuple[str, list]:
    conditions, params = [], []

    for key, val in filters.items():
        if key not in ALLOWED_FILTERS:
            raise ValueError(f"Filter '{key}' not allowed")
        if key.endswith("_gte"):
            col = key[:-4]; conditions.append(f"{col} >= %s"); params.append(val)
        elif key.endswith("_lte"):
            col = key[:-4]; conditions.append(f"{col} <= %s"); params.append(val)
        elif key == "created_after":
            conditions.append("created_at > %s"); params.append(val)
        else:
            conditions.append(f"{key} = %s"); params.append(val)

    direction = "DESC" if sort.startswith("-") else "ASC"
    col = sort.lstrip("+-")
    if col not in ALLOWED_SORTS:
        raise ValueError(f"Sort '{col}' not allowed")

    if cursor_anchor:
        ts, pk = cursor_anchor["created_at"], cursor_anchor["id"]
        op = "<" if direction == "DESC" else ">"
        conditions.append(f"(created_at {op} %s OR (created_at = %s AND id {op} %s))")
        params += [ts, ts, pk]

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    return f"SELECT * FROM orders {where} ORDER BY {col} {direction}, id DESC LIMIT {limit}", params

sql, params = build_filter_query({"status": "pending", "amount_gte": 100}, sort="-created_at")
print(sql)
print(params)
```

---

## ❓ Interview Q&A

**Q1: Why is OFFSET slow at page 10,000?**

A: `OFFSET 99990 LIMIT 10` forces the DB to scan 100,000 rows, discard 99,990, and return 10. Even with an index it reads 100K entries. Keyset (`WHERE (ts, id) < ($1, $2)`) seeks directly to the anchor in O(log n), returning 10 rows immediately regardless of how deep in the table.

**Q2: User wants to jump to page 500. Cursor pagination can't do that — how do you handle it?**

A: Options:
1. **Time-based anchor**: let users seek by date, not page. "Show orders from March 15" → time cursor
2. **Hybrid**: offset pages 1–50 (safe range), cursor-only beyond that
3. **Accept the trade-off**: analytics show >95% of users never go past page 20 — restrict UI depth

**Q3: How do you paginate a feed that changes in real time without duplicates?**

A: Snapshot the feed on first load:
1. Record `snapshot_time = now()` and embed in cursor
2. All subsequent pages filter `WHERE created_at <= snapshot_time AND (ts, id) < anchor`
3. New items (after snapshot) appear via polling/SSE, not pagination
This separates "browsing history" from "live updates."

**Q4: How do you paginate across multiple sort keys efficiently?**

A: Use a composite keyset on all sort columns:
```sql
-- Sort by (amount DESC, created_at DESC, id DESC)
WHERE (amount < $1)
   OR (amount = $1 AND created_at < $2)
   OR (amount = $1 AND created_at = $2 AND id < $3)
ORDER BY amount DESC, created_at DESC, id DESC
LIMIT 20;

-- Index: (amount DESC, created_at DESC, id DESC)
```
The composite condition maintains sort order while seeking.

**Q5: How do you prevent cursor tampering?**

A: HMAC-sign the cursor payload:
```python
sig = hmac.new(SECRET, payload, sha256).hexdigest()[:12]
cursor = base64(f"{payload}|{sig}")
# On decode: verify sig before trusting payload values
```
A tampered cursor fails HMAC verification → 400 Bad Request.

---

## 🧪 Practical Exercises

### Exercise 1: Rewrite Offset to Keyset (Easy)

**Problem:** Legacy endpoint `GET /orders?page=N&per_page=20`. Add cursor support while keeping `page` working for pages 1–50.

```python
def handle_request(params: dict) -> dict:
    cursor   = params.get("cursor")
    page     = int(params.get("page", 1))
    per_page = int(params.get("per_page", 20))

    if cursor:
        anchor = decode_cursor(cursor)
        rows = query_db(keyset_anchor=anchor, limit=per_page)
    else:
        if page > 50:
            return {"error": "Page > 50 not supported. Use cursor."}
        rows = query_db(offset=(page - 1) * per_page, limit=per_page)

    return {
        "data": rows,
        "next_cursor": encode_cursor(rows[-1]) if len(rows) == per_page else None,
        "deprecated_page_support": page <= 50,
    }
```

---

### Exercise 2: Pagination with Total Count (Medium)

**Problem:** UI needs total count for progress indicator. Counting is expensive. Design efficient approach.

```python
import functools, time

class PaginatorWithCount:
    """Cache the total count separately with a longer TTL."""

    def __init__(self, count_ttl_secs: int = 60):
        self._count_cache: dict = {}
        self.count_ttl = count_ttl_secs

    def get_count(self, query_fingerprint: str, count_fn) -> int:
        cached = self._count_cache.get(query_fingerprint)
        if cached and time.time() - cached["ts"] < self.count_ttl:
            return cached["count"]
        count = count_fn()
        self._count_cache[query_fingerprint] = {"count": count, "ts": time.time()}
        return count

    def paginate(self, items: list, filters: dict, cursor=None, per_page=20) -> dict:
        fingerprint = str(sorted(filters.items()))
        # Approximate count (cached 60 sec) — good enough for "~10,000 results"
        total = self.get_count(fingerprint, lambda: len(items))
        page_data = items[:per_page]
        return {
            "data": page_data,
            "total_approx": total,
            "next_cursor": page_data[-1]["id"] if len(page_data) == per_page else None,
        }

pager = PaginatorWithCount()
items = [{"id": i} for i in range(1000)]
result = pager.paginate(items, {"status": "active"})
print(f"Total (approx): {result['total_approx']}, page size: {len(result['data'])}")
```

---

### Exercise 3: Keyset Pagination on Sharded DB (Hard)

**Problem:** Table is sharded across 4 nodes by `user_id`. Paginate across shards without reading all data.

```python
from typing import List
import heapq

class ShardedPaginator:
    """Fan-out to all shards, merge by cursor key using a min-heap."""

    def __init__(self, shards: List['Shard'], page_size: int = 20):
        self.shards = shards
        self.page_size = page_size

    def get_page(self, cursor: Optional[dict] = None) -> dict:
        # Fetch page_size+1 from each shard (to detect has_more)
        shard_results = []
        for shard in self.shards:
            rows = shard.query(cursor=cursor, limit=self.page_size + 1)
            shard_results.append(rows)

        # Merge using min-heap on (created_at DESC, id DESC)
        heap = []
        for shard_id, rows in enumerate(shard_results):
            for row in rows:
                # Negate for max-heap behaviour (heapq is min-heap)
                heapq.heappush(heap, (-row["created_at"], -row["id"], shard_id, row))

        merged = []
        while heap and len(merged) < self.page_size:
            _, _, _, row = heapq.heappop(heap)
            merged.append(row)

        next_cursor = (
            {"created_at": merged[-1]["created_at"], "id": merged[-1]["id"]}
            if len(merged) == self.page_size else None
        )
        return {"data": merged, "next_cursor": next_cursor}

class Shard:
    def __init__(self, data: list):
        self.data = sorted(data, key=lambda r: (r["created_at"], r["id"]), reverse=True)

    def query(self, cursor=None, limit=20) -> list:
        rows = self.data
        if cursor:
            rows = [r for r in rows if (r["created_at"], r["id"]) < (cursor["created_at"], cursor["id"])]
        return rows[:limit]

# Setup 4 shards
import random, time as t
shards = [
    Shard([{"id": i, "created_at": t.time() - random.randint(0, 1000)} for i in range(j, 100, 4)])
    for j in range(4)
]
pager = ShardedPaginator(shards, page_size=5)
p1 = pager.get_page()
print("Page 1 IDs:", [r["id"] for r in p1["data"]])
p2 = pager.get_page(cursor=p1["next_cursor"])
print("Page 2 IDs:", [r["id"] for r in p2["data"]])
```

---

**Last updated:** 2026-05-22
