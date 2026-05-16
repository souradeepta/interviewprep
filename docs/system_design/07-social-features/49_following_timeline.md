# Following Timeline Feed

## Problem Statement

### Functional Requirements
- Show posts from followed users only
- Chronological or algorithmic ordering
- Support filtering by content type
- Enable muting and unfollowing
- Display engagement metrics

### Non-Functional Requirements
- Latency: Load timeline < 500ms p99
- Freshness: New posts visible within 5 seconds
- Ranking: Personalized feed relevance
- Throughput: 100K+ timeline requests/second
- Scalability: Support 1B+ concurrent users

## System Overview

**Scale Metrics:**
- Throughput: Millions of operations per second
- Latency: Milliseconds to seconds depending on operation
- Data volume: Terabytes to Petabytes
- Concurrent users: Millions to billions
- Availability: 99.99% to 99.999% uptime SLA

**Key Components:**
- User-facing API endpoints
- Data persistence layer
- Caching and optimization
- Real-time messaging
- Analytics and monitoring

## Architecture Diagrams

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1["Web Client"]
        C2["Mobile App"]
        C3["API Clients"]
    end

    subgraph "API Layer"
        A1["API Gateway"]
        A2["Load Balancer"]
    end

    subgraph "Service Layer"
        S1["Feature Service 1"]
        S2["Feature Service 2"]
        S3["Feature Service N"]
    end

    subgraph "Data Layer"
        D1["Primary DB"]
        D2["Cache Layer"]
        D3["Message Queue"]
    end

    C1 --> A1
    C2 --> A1
    C3 --> A1
    A1 --> A2
    A2 --> S1
    A2 --> S2
    A2 --> S3
    S1 --> D1
    S2 --> D2
    S3 --> D3

    style C1 fill:#e1f5ff
    style A1 fill:#f3e5f5
    style S1 fill:#fff3e0
    style D1 fill:#e8f5e9
```

### Request Flow

```mermaid
graph LR
    A["User Request"] --> B["Validate"]
    B --> C["Authenticate"]
    C --> D["Process"]
    D --> E["Cache"]
    E --> F["Response"]

    style A fill:#c8e6c9
    style C fill:#ffccbc
    style D fill:#bbdefb
    style F fill:#fff9c4
```

### Scalability Architecture

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        H1["Add Service Replicas"]
        H2["Database Sharding"]
        H3["Cache Replication"]
    end

    subgraph "Vertical Scaling"
        V1["Upgrade CPU"]
        V2["Increase Memory"]
        V3["Faster Storage"]
    end

    subgraph "Optimization"
        O1["Batch Operations"]
        O2["Async Processing"]
        O3["Connection Pooling"]
    end

    H1 --> H2
    H2 --> H3
    V1 --> V2
    V2 --> V3

    style H1 fill:#bbdefb
    style V1 fill:#f8bbd0
    style O1 fill:#fff9c4
```

### Real-Time Updates

```mermaid
graph TB
    A["User Action"] --> B["Process"]
    B --> C["Notify"]
    C --> D["Update Cache"]
    D --> E["Broadcast"]
    E --> F["Client Update"]

    style B fill:#ffccbc
    style C fill:#c8e6c9
    style E fill:#bbdefb
```

### Error Handling

```mermaid
graph TB
    A["Request"] --> B["Execute"]
    B --> C["Success"]
    C -->|Yes| D["Return Result"]
    C -->|No| E["Retry"]
    E --> F["Retries Exceeded"]
    F -->|Yes| G["Return Error"]
    F -->|No| E

    style D fill:#c8e6c9
    style G fill:#ffcdd2
```

## Data Flow Scenarios

### Scenario 1: Normal Operation
1. User sends request through API
2. Authenticate and authorize user
3. Validate input parameters
4. Process business logic
5. Update database and cache
6. Send response to user
7. Broadcast real-time updates

### Scenario 2: High Traffic Spike
1. Rate limiter detects surge
2. Queue requests if necessary
3. Load balance across servers
4. Serve from cache when possible
5. Gracefully degrade non-critical features
6. Queue background tasks

### Scenario 3: Data Inconsistency
1. Detect stale cache entry
2. Invalidate cache
3. Fetch fresh data from database
4. Update cache with fresh data
5. Send updated data to client
6. Log for monitoring

## Performance Optimization

### Caching Strategy
- **Write-through**: Cache and DB always in sync
- **Write-back**: Async cache writes, higher throughput
- **TTL-based**: Automatic invalidation after time

### Database Optimization
- **Indexing**: Fast lookups on frequently queried columns
- **Sharding**: Distribute data for parallel processing
- **Replication**: Read scaling and high availability

### Async Processing
- **Message Queue**: Decouple services
- **Background Jobs**: Process expensive operations
- **Webhooks**: Event-driven updates

## Back-of-Envelope Calculations

### User Base and Traffic
```
Daily Active Users: 500M
Requests per user per day: 100
Daily total requests: 50B
Requests per second: 50B / 86400 ≈ 578K RPS
Peak hour (10x): 5.78M RPS
```

### Storage Requirements
```
Data per user: 100 KB (profile, preferences, settings)
Total user data: 500M × 100 KB = 50 TB
Cache hit rate: 90%
Cache miss storage: 50 TB × 10% = 5 TB
Database storage with replication: 50 TB × 3 = 150 TB
```

### Compute Resources
```
CPU per RPS: 1 core for 10K RPS
CPUs needed for peak: 5.78M / 10K = 578 cores
Servers (32 cores each): 578 / 32 ≈ 18 servers
Redundancy (3x): 54 servers per region
Global (10 regions): 540 servers
```

### Network Bandwidth
```
Average request size: 5 KB
Average response size: 20 KB
Inbound bandwidth: 578K RPS × 5 KB = 2.89 GB/s
Outbound bandwidth: 578K RPS × 20 KB = 11.56 GB/s
Total peak: 14.45 GB/s ≈ 116 Tbps
```

## Interview Questions & Answers

### Q1: Design a social feed for 500M users

**Answer:**
1. **Clarify**: Content types, update frequency, ranking
2. **High-level design**: Feed service, user graph, ranking engine
3. **Scalability**: Sharding by user ID, cache recent feeds
4. **Ranking**: Engagement score = likes × 2 + comments × 3 + shares × 5
5. **Challenges**: Feed staleness, thundering herd during viral posts
6. **Trade-offs**: Consistency vs freshness, cost vs latency

### Q2: Handle 10M concurrent users

**Answer:**
- **Load balancing**: Distribute across regions/zones
- **Horizontal scaling**: Stateless services with replicas
- **Caching**: Cache hot data (trending, recent posts)
- **Database**: Read replicas for scaling reads
- **Async**: Background jobs for non-critical tasks
- **Circuit breaker**: Prevent cascade failures

### Q3: What about real-time updates?

**Answer:**
- **WebSockets**: Long-lived connections for real-time
- **Message Queue**: Decouple publishers from subscribers
- **Fan-out**: Broadcast updates to followers efficiently
- **Rate limiting**: Prevent overwhelming clients
- **Batching**: Group updates to reduce network traffic

### Q4: How do you handle notifications?

**Answer:**
- **Queue**: Decouple notification generation from delivery
- **Multi-channel**: Email, push, SMS, in-app
- **Deduplication**: Avoid duplicate notifications
- **User preferences**: Respect notification settings
- **Retry**: Exponential backoff for failed deliveries

### Q5: Design comment system for massive scale

**Answer:**
1. **Hierarchy**: Tree structure for nested comments
2. **Storage**: Store in database with B-tree indexing
3. **Caching**: Cache top comments per post
4. **Pagination**: Load comments in batches
5. **Real-time**: Websocket for new comments
6. **Scalability**: Shard by post ID

### Q6: How to prevent abuse and moderation at scale?

**Answer:**
- **Detection**: Pattern matching on spam/abuse indicators
- **Rate limiting**: Prevent spam posting
- **User reporting**: Crowdsource moderation signals
- **ML models**: Train on reported content
- **Action queue**: Process reports efficiently
- **Appeal process**: Allow user appeals

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| API Gateway | Nginx, Envoy | Load balancing, request routing |
| Services | Node.js, Java, Go | High concurrency, low latency |
| Database | PostgreSQL, MongoDB | ACID, flexible schema options |
| Cache | Redis, Memcached | Sub-millisecond access |
| Message Queue | Kafka, RabbitMQ | Reliable async processing |
| Real-time | WebSocket, Server-Sent Events | Live updates to clients |
| Monitoring | Prometheus, DataDog | Performance and error tracking |

## Lessons Learned

1. **Start simple**: Basic implementation handles more than you'd expect
2. **Measure everything**: Instrument before optimizing
3. **Cache is critical**: 10-100x latency improvement
4. **Async is essential**: Decouple services for scalability
5. **Real-time is hard**: Trade-offs between latency and cost

## Related Topics

- Load balancing and API gateway design
- Database sharding and partitioning
- Caching strategies and invalidation
- Message queue and pub/sub systems
- WebSocket and real-time communication
- User authentication and authorization
- Rate limiting and throttling
- Monitoring and alerting systems


## Code Implementation

### Python
```python
import redis
import time
from dataclasses import dataclass, field
from typing import Optional

r = redis.Redis(decode_responses=True)

@dataclass
class Post:
    post_id: str
    author_id: str
    content: str
    timestamp: float = field(default_factory=time.time)

class FeedService:
    """Hybrid push-pull feed: push for regular users, pull for celebrities."""
    CELEBRITY_THRESHOLD = 1_000_000   # followers

    def publish_post(self, post: Post, follower_count: int) -> None:
        """Push post to follower feeds (fanout on write for small accounts)."""
        post_data = f"{post.post_id}:{post.timestamp}"
        # Store post metadata
        r.hset(f"post:{post.post_id}", mapping={
            "content": post.content,
            "author": post.author_id,
            "ts": post.timestamp,
        })
        if follower_count < self.CELEBRITY_THRESHOLD:
            # Push to each follower's feed sorted set (score = timestamp)
            followers = r.smembers(f"followers:{post.author_id}")
            pipe = r.pipeline()
            for follower_id in followers:
                pipe.zadd(f"feed:{follower_id}", {post.post_id: post.timestamp})
                pipe.zremrangebyrank(f"feed:{follower_id}", 0, -1001)  # cap at 1000
            pipe.execute()

    def get_feed(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get merged feed: own feed (pushed) + celebrity followings (pulled)."""
        post_ids = r.zrevrange(f"feed:{user_id}", 0, limit - 1, withscores=False)
        return [r.hgetall(f"post:{pid}") for pid in post_ids]
```

### Java
```java
import redis.clients.jedis.*;
import java.util.*;

public class FeedService {
    private static final int CELEBRITY_THRESHOLD = 1_000_000;
    private final JedisPool jedisPool;

    public FeedService(JedisPool jedisPool) { this.jedisPool = jedisPool; }

    public void publishPost(String postId, String authorId, String content,
                             long followerCount) {
        try (Jedis jedis = jedisPool.getResource()) {
            double timestamp = System.currentTimeMillis() / 1000.0;
            // Store post metadata
            jedis.hset("post:" + postId, Map.of(
                "content", content, "author", authorId, "ts", String.valueOf(timestamp)
            ));
            if (followerCount < CELEBRITY_THRESHOLD) {
                // Fanout on write — push to each follower's feed
                Set<String> followers = jedis.smembers("followers:" + authorId);
                Pipeline pipe = jedis.pipelined();
                for (String followerId : followers) {
                    pipe.zadd("feed:" + followerId, timestamp, postId);
                    pipe.zremrangeByRank("feed:" + followerId, 0, -1001); // keep 1000
                }
                pipe.sync();
            }
        }
    }

    public List<Map<String, String>> getFeed(String userId, int limit) {
        try (Jedis jedis = jedisPool.getResource()) {
            List<String> postIds = new ArrayList<>(
                jedis.zrevrangeByScore("feed:" + userId, "+inf", "-inf",
                                       0, limit));
            List<Map<String, String>> posts = new ArrayList<>();
            for (String pid : postIds) posts.add(jedis.hgetAll("post:" + pid));
            return posts;
        }
    }
}
```

## Back-of-the-Envelope Calculations

**System Load Estimation:**
- 1M daily active users × 10 requests/day = 10M requests/day
- Peak QPS = 10M / 86400 × 3 (peak factor) ≈ 350 QPS
- API server capacity: 1000 QPS/server → 1 server sufficient at peak
- With 2x redundancy: 2 servers minimum

**Storage Estimation:**
- 1M users × 10KB average data = 10GB structured data
- Annual growth: 10GB × 365 = 3.65TB/year
- With 3x replication: 11TB/year
- SSD cost ($0.10/GB): $1,100/year

**Bandwidth:**
- 350 QPS × 10KB response = 3.5MB/sec outbound
- Monthly egress: 3.5MB × 86400 × 30 = 9TB/month
## Follow-up Questions

1. **How would you handle this at 10x the scale described?**
   - What breaks first? (typically: single DB, single cache node, single region)
   - What architectural changes are required?

2. **What are the consistency vs. availability trade-offs in your design?**
   - Where did you accept eventual consistency?
   - Which operations require strong consistency and why?

3. **How would you debug a sudden latency spike in production?**
   - What metrics would you look at first?
   - What's your runbook for the top 3 likely causes?

4. **How does your design handle partial failures?**
   - What happens if one component is slow (not down)?
   - How do you prevent cascading failures?

5. **What would you change if you had to build this in one week vs. six months?**
   - What corners can safely be cut initially?
   - What must be right from day one?

6. **How would you migrate from the current design to a better one without downtime?**
   - What's the strangler-fig or blue-green strategy here?
   - How do you validate correctness during migration?