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

### Scaling Deep Dives

**Database Bottleneck:** MySQL becomes single point of failure at 10K+ QPS

```
Phase 1 (1-5K QPS): Single MySQL with read replicas
  - Read replicas for analytics queries
  - Write replicas for failover

Phase 2 (5K-50K QPS): Sharded MySQL
  - Shard by hash(short_url) % num_shards
  - 4-8 shards initially, each with replicas
  - Resharding needed at 10x growth

Phase 3 (50K+ QPS): NoSQL (Cassandra)
  - Better write throughput (no ACID needed)
  - Append-only log for immutability
```

**Cache Invalidation:** What if URL content changes?

```
Option 1: TTL-based (simple)
  - Cache for 1 day, expire automatically
  - Problem: stale data up to 24 hours
  
Option 2: Event-based (better)
  - URL update publishes event to Kafka
  - Cache layer subscribes, invalidates immediately
  - Problem: complexity, infrastructure overhead
  
Choice: TTL + on-demand invalidation
  - Users can request refresh (clears cache for their URL)
  - Default TTL = 24 hours
  - Balances simplicity and freshness
```

### Interview Follow-up Questions

**Q: What if someone tries to create the same short URL twice?**
- Check if exists before insert
- Return same short URL (idempotent)
- Prevents duplicates, good for retries

**Q: How do you handle malicious URLs?**
- Scan against known malware DB
- Rate limit creation (10/user/hour)
- Quarantine suspicious URLs (manual review)

**Q: How do you measure analytics accuracy?**
- Approximate counts acceptable (80-99% accurate)
- Use probabilistic counters (HyperLogLog)
- Batch updates (reduce DB writes by 100x)

### Challenges

**Collisions:** Hash(long_url) == Hash(long_url)
- Solution: Use 8 chars instead of 6, check collision on insert

**Hot URLs:** Some short codes get 1M requests/day
- Solution: Partition heavy hitters, multi-replica cache
- Pre-warm cache for top 1K URLs

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

### Scaling Strategies

**Transcoding Bottleneck:** Transcoding 1M videos/day with 30-min avg processing

```
Real numbers:
- 1M uploads × 30 min = 30M CPU-minutes/day
- 1 worker (1 CPU) = 1440 minutes/day
- Need: 30M / 1440 = 20,833 workers minimum

Auto-scaling:
- Start with 1000 workers
- Monitor queue depth: if > 1M videos waiting, scale up by 10%
- Maximum 50,000 workers (cost limit)
- Scale down: idle 5 minutes → remove 10%
```

**CDN Distribution:** Where to place caches globally?

```
Strategy: Geo-distributed edge caches
- Place caches in major cities (NYC, London, Tokyo, etc.)
- Videos are huge (multi-GB), so cache fewer total videos
- Prioritize caching popular videos (80/20 rule)

Example:
- Top 1% videos = 80% of views
- Cache only top 1% in every edge location
- Long-tail videos: only in regional cache
```

### Interview Follow-up Questions

**Q: How do you handle video re-encoding if user requests aren't predicted?**
- Cache miss → request lowest quality immediately (stream starts fast)
- Spawn background job to transcode higher qualities
- User can upgrade quality as encoding completes

**Q: How do you prevent bandwidth waste from crawlers?**
- Rate limit by IP/user (10 requests/second)
- Require authentication for streaming API
- Detect automated patterns, block bots

**Q: How do you handle video corruption or incomplete uploads?**
- Checksum every chunk (SHA256)
- Verify after transcoding, re-transcode if fails
- Alert to user if final transcoding fails

### Challenges

**Storage cost:** 1PB per day at scale = $50K+/month
- Solution: Compression (H.265 saves 50% space vs H.264)
- Delete old videos after 12 months
- Tiered storage (SSD for hot, HDD for cold, archive for rare)

**Transcoding queue:** Millions of videos daily
- Solution: Auto-scale workers, prioritize popular uploads
- Queue backlog causes user frustration → critical KPI

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

### High Availability & Failure Modes

**Server Failure:** WebSocket server crashes with 10K connected users

```
Recovery:
1. Load balancer detects server is down (health check fails)
2. Stops routing new connections to dead server
3. Existing 10K connections drop (client reconnects)
4. Client reconnects, queries: "what messages did I miss?"
5. Server returns messages from last_seq_number received

Problem: 10K simultaneous reconnections = thundering herd
Solution: Add randomized exponential backoff (1s + random 0-10s)
         Rate-limit reconnections (100/second)
```

**Message Loss:** What if Kafka broker crashes before persisting?

```
Durability settings:
- acks=all: wait for all replicas to persist (slow but safe)
- acks=leader: wait for leader only (faster, acceptable for chat)
- Use acks=leader, rely on Kafka replication (3 copies minimum)

Risk: message lost if all 3 replicas down simultaneously
      Acceptable: probability < 0.001%, business can tolerate
```

### Interview Follow-up Questions

**Q: How do you handle large media (images, videos) in messages?**
- Don't store in message queue (too big)
- Upload to blob store (S3), put reference in message
- Message: {"text": "...", "image_url": "s3://bucket/id.jpg"}

**Q: How do you ensure message ordering in distributed system?**
- Single partition per conversation (all messages for chat go to same partition)
- Consumer reads in order, client reorders if needed (just in case)
- Sequence numbers: client sees gaps → request missing messages

**Q: How do you handle user typing indicators ("Alice is typing...")?**
- Ephemeral messages (not persisted, TTL = 5 seconds)
- Send separately from chat messages (lower priority)
- Broadcast to all users in conversation

### Challenges

**Duplicate delivery:** Network retries cause duplicate sends
- Solution: Idempotency key (UUID per message)
- Server deduplicates within 1-hour window

**Out-of-order delivery:** Messages arrive out of sequence
- Solution: Sequence number + client reordering
- Server-side: single partition enforces order

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

### Recommendation Algorithms Deep Dive

**Collaborative Filtering:** "Users like you also liked..."

```python
# Simplified: find similar users, recommend their likes
def recommend_collaborative(user_id, n=5):
    user_profile = get_user_profile(user_id)  # Movies they liked
    
    # Find similar users (cosine similarity)
    similar_users = find_similar_users(user_profile, top=100)
    
    # Collect recommendations
    liked_by_similar = {}
    for similar_user in similar_users:
        for movie in get_likes(similar_user):
            if movie not in user_profile:
                liked_by_similar[movie] += similarity_score
    
    return sorted(liked_by_similar, key=lambda x: x[1], reverse=True)[:n]

# Problem: Slow for 10M users (matrix is 10M × 1M)
# Solution: Pre-compute user clusters, only compare within cluster
```

**Cold-Start Problem:** New user with no history

```
Strategy 1: Popular items
- If no history, recommend global top-100 items
- Works for ~50% of new users

Strategy 2: Content-based filtering
- Use metadata only: genre, director, actors
- Recommend movies similar to profiles user watched before
- Works for ~30% of new users (migrating from competitor)

Strategy 3: Demographic
- Infer from IP location, device type, etc.
- Works for ~20% of new users

Hybrid: Combine all three, let user rate 5 movies, retrain
```

### Interview Follow-up Questions

**Q: How do you handle diversity vs. accuracy in recommendations?**

```
Problem: Model predicts "users like action movies" → recommend 100 action movies
Reality: User wants variety (20% drama, 30% comedy, 50% action)

Solution:
- Diversity penalty: reduce score if recommending similar genre
- Enable user control: filter by genre preference
- A/B test: 70% optimized, 30% diverse/serendipitous
```

**Q: How do you prevent recommendation bias?**

```
Bias: System only recommends popular items
     Women recommended romance, men recommended action (unfair)
     Recommendations reinforce existing preferences (filter bubble)

Mitigation:
1. Track diversity metrics (% new items, % from underrep'd creators)
2. Diversity as part of ranking (favor fresh content 10%)
3. Explicit fairness: ensure minorities well-represented
4. A/B test: measure user satisfaction vs. diversity
```

**Q: How do you handle feedback loops?**

```
Loop: System recommends action → user watches → data shows user likes action
      → system recommends more action (reinforces bias)
      → user might actually like romance but never sees it

Prevention:
- Mix exploration vs. exploitation (80% best match, 20% explore)
- Thompson Sampling: show diverse options, learn from clicks
- Cold-start all users weekly (show variety, gather data)
```

### Challenges

**Cold-start:** New user with no history
- Solution: Popular items, content-based (metadata only)
- A/B test to see what works best

**Stale recommendations:** Yesterday's popular items
- Solution: Update daily, mix recent + popular
- Weigh recent events higher (last 7 days = 40% weight)

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

