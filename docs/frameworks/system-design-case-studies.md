# System Design Case Studies: Deep Dives into Real Problems

Master system design through detailed case studies of common interview problems.

---

## URL Shortener (TinyURL)

### Requirements
- Shorten long URLs
- Forward short URLs (redirect)
- Analytics (view count, clicks)
- 1M DAU, 100K QPS read, 5K QPS write

### Architecture

```
Client → Load Balancer → API Servers
                      → Redis Cache
                      → MySQL (URLs + Analytics)
                      → Kafka (Analytics events)
```

### Key Design Decisions

1. **Primary Key Strategy**
   - Random base62: 6 chars = 62^6 ≈ 56 billion combinations ✓
   - Sequential: easier to guess URLs ✗
   - Hash: consistent but collision-prone ✗

2. **Read Heavy (100:1)**
   - Cache layer critical (95% cache hit target)
   - Duplicate reads go to cache, not DB
   - Use CDN for redirects across regions

3. **Sharding Strategy**
   - Shard by hash(short_url) for even distribution
   - Avoid single hotspot

4. **Analytics**
   - Asynchronous (queue events, batch update)
   - Approximate counts acceptable

### Challenges

**Collisions:** Hash(long_url) == Hash(long_url)
- Solution: Use 8 chars instead of 6, check collision on insert

**Hot URLs:** Some short codes get 1M requests/day
- Solution: Partition heavy hitters, multi-replica cache

---

## Video Streaming System (YouTube)

### Requirements
- Upload videos (1GB avg)
- Stream videos (1M concurrent users)
- 100M DAU, 1M QPS read
- P99 latency < 2 seconds

### Architecture

```
Upload → Transcoding → CDN
                    → Database (metadata)
Stream  → CDN → Player
```

### Key Design Decisions

1. **Transcoding**
   - Multiple qualities (144p, 360p, 720p, 1080p)
   - Asynchronous (upload completes after transcoding)
   - Queue heavy videos overnight

2. **Streaming**
   - CDN for geographic distribution (1000ms+ latency reduced to 10ms)
   - Adaptive bitrate (DASH) based on bandwidth
   - P2P for peer assistance (reduce CDN load)

3. **Storage**
   - Blob store (S3, GCS) for video data
   - Distributed, replicated for durability

### Challenges

**Storage cost:** 1PB per day at scale
- Solution: Compression, old video deletion, tiered storage

**Transcoding queue:** Millions of videos daily
- Solution: Auto-scale workers, prioritize popular uploads

---

## Chat System (WhatsApp-like)

### Requirements
- Send/receive messages
- 1M DAU, 100K concurrent users
- P99 latency < 500ms
- Message persistence

### Architecture

```
Client → WebSocket Servers (stateful) → Message Queue (Kafka)
                                     → Database (persistence)
                                     → Redis (recent messages cache)
```

### Key Design Decisions

1. **Real-time Delivery**
   - WebSocket for bidirectional communication
   - Horizontal scale: each server handles 10K concurrent
   - Service discovery for routing

2. **Ordering**
   - Monotonic sequence number per conversation
   - Client reorders on receive if out of order

3. **Offline Messages**
   - Queue messages for offline users
   - Deliver on reconnect
   - Delete after 30 days

4. **Acknowledgments**
   - Sent: server receives from client
   - Delivered: server delivers to recipient (or queues)
   - Read: recipient opens message

### Challenges

**Duplicate delivery:** Network retries cause duplicate sends
- Solution: Idempotency key (UUID per message)

**Out-of-order delivery:** Messages arrive out of sequence
- Solution: Sequence number + client reordering

---

## Recommendation System (Netflix-like)

### Requirements
- Personalized recommendations
- 10M DAU, 1K QPS read
- Latency < 200ms

### Architecture

```
User behavior → Feature extraction → ML Model → Redis Cache
                                              → Suggestions API
```

### Key Design Decisions

1. **Data Collection**
   - Views, clicks, ratings → event stream (Kafka)
   - Update user features hourly/daily

2. **Recommendation Model**
   - Collaborative filtering: "Users like you also liked..."
   - Content-based: "Similar to what you watched"
   - Hybrid: Combine both

3. **Caching**
   - Pre-compute top-N for each user daily
   - Cache recommendations for 1 hour
   - Handle cold-start users (popular items)

4. **Latency**
   - Return cached if available (< 10ms)
   - Compute online if cache miss (< 200ms timeout)

### Challenges

**Cold-start:** New user with no history
- Solution: Popular items, content-based (metadata only)

**Stale recommendations:** Yesterday's popular items
- Solution: Update daily, mix recent + popular

---

## Case Study Comparison

| System | Main Challenge | Solution |
|--------|---|---|
| URL Shortener | Unique keys, high read | Cache, CDN, efficient encoding |
| Video Streaming | Storage, bandwidth | CDN, transcoding, compression |
| Chat | Real-time ordering, offline | WebSocket, sequence #, queues |
| Recommendation | Latency, accuracy | Caching, offline computation |
| Payment | Exactly-once, consistency | Idempotency, saga, strong consistency |
| Search | Indexing, ranking | Inverted index, TF-IDF, ML |

---

## System Design Lessons

1. **Know your bottleneck** — Measure before optimizing
2. **Cache everything** — But invalidate carefully
3. **Async everything** — Reduce latency with queues
4. **Shard early** — Scale from day 1 (don't migrate later)
5. **Monitor** — Can't optimize what you don't measure
6. **Start simple** — Add complexity only if needed

