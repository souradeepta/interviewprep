# Caching & In-Memory Stores — Redis and Memcached

Fast data access patterns.

---

## 🚀 In-Memory vs. Disk

**In-Memory (Redis):**
- Microsecond latency
- Volatile (data lost on restart)
- Expensive (memory costly)

**Disk (PostgreSQL):**
- Millisecond latency
- Persistent (survives restarts)
- Cheap storage

---

## 📦 Use Cases

**Sessions:** Store user sessions
**Cache:** Cache query results
**Real-time:** Leaderboards, metrics
**Queues:** Job queues
**Pub/Sub:** Message passing

---

## 🔑 Redis Data Structures

```
Strings: "key" → "value"
Hashes: "user:1" → {name: "Alice", email: "..."}
Lists: "queue" → ["task1", "task2", "task3"]
Sets: "tags" → {"python", "javascript", "devops"}
Sorted Sets: "leaderboard" → {player1: 100, player2: 95, ...}
```

---

## 💾 Persistence

**RDB:** Snapshot every N seconds (fast, less durable)
**AOF:** Append-only file (slower, more durable)
**Hybrid:** RDB + AOF

---

## 🔄 Replication & Clustering

**Master-Slave:** Master writes, slaves read
**Sentinel:** Automatic failover
**Cluster:** Sharding across nodes

---

## 📊 Memory Management

```
Eviction policies:
- LRU: Least Recently Used
- LFU: Least Frequently Used
- TTL: Expire oldest

Monitor memory usage, set max memory limit
```

---

## ❓ Interview Q&A

**Q: Cache warm-up strategy**
A: On startup, pre-load hot data. Or lazy load on first access.

**Q: Handle cache failures gracefully**
A: Cache is optional. If miss, query DB. Don't let cache failures break app.

---

**Last updated:** 2026-05-22
