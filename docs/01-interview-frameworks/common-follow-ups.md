# Common System Design Follow-ups

Likely interviewer questions for each system design in this repo. Study these patterns.

---

## Social Feed System

**Initial focuses on:** Feed generation, caching strategy, ranking algorithm

**Likely follow-ups:**

1. **Scaling:** "How do you handle a user with 100M followers?"
   - Answer: "Fan-out writes for normal users (queue write to follower feeds). For celebrity accounts, fan-out on read instead."

2. **Real-time:** "Posts take 30 seconds to appear in follower feeds. How do you improve?"
   - Answer: "Cache invalidation on post creation via message queue. Or: push updates to online users via WebSocket."

3. **Consistency:** "What if my feed is stale?"
   - Answer: "Feed cache has 1-hour TTL. On cache miss, recomputed from DB. User can explicitly refresh."

4. **Failure:** "One cache server went down. What happens?"
   - Answer: "Requests bypass cache to DB, which might spike load. Mitigation: cache cluster replication or circuit breaker."

---

## Payment System

**Initial focuses on:** Transaction safety, idempotency, payment gateway integration

**Likely follow-ups:**

1. **Exactly-once:** "How do you ensure a payment isn't processed twice?"
   - Answer: "Idempotency key (unique ID per transaction). Payment gateway detects duplicates using this key."

2. **Failure mode:** "Payment service is down. How do you handle new payments?"
   - Answer: "Queue payment requests to message queue. Process asynchronously when service recovers. Timeout after 24 hours."

3. **Refunds:** "How do you handle refunds?"
   - Answer: "Refund is a reverse transaction. Record in audit log, call payment gateway refund API, update user balance."

---

## Chat System

**Initial focuses on:** Message persistence, real-time delivery, conversation ordering

**Likely follow-ups:**

1. **Real-time:** "How do you push messages to both users simultaneously?"
   - Answer: "WebSocket connection for each user. On message send, push to recipient's open connections. If offline, store in DB."

2. **Ordering:** "Messages arrive out of order sometimes."
   - Answer: "Assign monotonic sequence number per conversation. Message includes sequence number. Client reorders on receive."

3. **Scalability:** "100K concurrent users. One server max is 10K connections. How do you scale?"
   - Answer: "WebSocket servers scale horizontally. Message broker (Kafka) coordinates delivery. No shared state on servers."

---

## Notification System

**Initial focuses on:** Delivery reliability, channel management (email, SMS, push)

**Likely follow-ups:**

1. **Delivery:** "How do you ensure a notification is delivered despite failures?"
   - Answer: "Queue notifications. Retry with exponential backoff (3x). Dead-letter queue for failures after 3 attempts."

2. **Deduplication:** "User receives same notification twice in 2 minutes."
   - Answer: "Deduplication key (notification_type + user_id + time_window). Check before queuing. Discard duplicates."

3. **Throttling:** "Users complain about notification spam."
   - Answer: "Rate limiting: max 10 notifications per user per hour. Priority queue for urgent. User preferences."

---

## E-commerce System

**Initial focuses on:** Inventory management, order processing, consistency

**Likely follow-ups:**

1. **Inventory:** "How do you prevent overselling when multiple users buy simultaneously?"
   - Answer: "Pessimistic locking (reserve inventory before payment). Or: optimistic with versioning. Check against version on update."

2. **Order state:** "Order status updates don't propagate to user dashboard immediately."
   - Answer: "Event sourcing: order status changes trigger events. Dashboard subscribes to events. Cache with TTL for eventual consistency."

3. **Scaling writes:** "Checkout throughput maxes out. How do you scale?"
   - Answer: "Partition orders by time (hourly table). Or: sharding by user_id. Separate read replicas for dashboard queries."

---

## Rate Limiter

**Initial focuses on:** Bucketing algorithm, distributed tracking, quota management

**Likely follow-ups:**

1. **Distributed:** "How do you enforce rate limits across multiple servers?"
   - Answer: "Centralized counter in Redis. Each server queries Redis before allowing request. Or: token bucket with sync."

2. **Burst handling:** "User constantly hits rate limit boundary."
   - Answer: "Use sliding window instead of fixed window. Or: offer burst capacity (allow 10x for 1 second, then throttle)."

3. **Reset behavior:** "Rate limit resets unpredictably."
   - Answer: "Use sliding window with timestamps, not fixed windows. For fixed windows, specify clear reset policy (UTC midnight, etc.)."

---

## Load Balancer

**Initial focuses on:** Routing algorithm, health checking, session persistence

**Likely follow-ups:**

1. **Sticky sessions:** "User session lost after request routed to different server."
   - Answer: "Consistent hashing (same user → same server). Or: session store (Redis). Trade-off: former less resilient to server failure."

2. **Uneven load:** "Some servers get 10x more traffic than others."
   - Answer: "Health-aware routing: check server metrics, route away from overloaded. Or: use weighted round-robin based on capacity."

3. **Failover:** "Server goes down during sticky session. How do you handle?"
   - Answer: "If using consistent hashing: client detects timeout, retries (hash to next server). If using session store: session served from backup."

---

## Search Engine

**Initial focuses on:** Indexing strategy, relevance ranking, query processing

**Likely follow-ups:**

1. **Latency:** "Search query takes 5 seconds. How do you optimize?"
   - Answer: "Cache popular queries. Use approximate search (BIT). Shard index by term range. Reduce ranking complexity."

2. **Freshness:** "New documents don't appear in search immediately."
   - Answer: "Near real-time indexing (seconds to minutes). Or: accept eventual consistency. Add invalidation queue for urgent updates."

3. **Relevance:** "Search results don't match user intent."
   - Answer: "Use ML ranking model. Consider user history, context. A/B test ranking changes. User feedback loop for learning."

---

## Recommendation Engine

**Initial focuses on:** Personalization algorithm, feature computation, caching

**Likely follow-ups:**

1. **Latency:** "Recommendation generation takes too long."
   - Answer: "Pre-compute recommendations offline (batch). Cache results. Use approximation algorithms. Hybrid: online refinement of cached batch."

2. **Cold start:** "New user has no history. What recommendations do you show?"
   - Answer: "Popular items globally. Ask user for interests. Collaborative filtering on similar users. A/B test cold-start strategies."

3. **Diversity:** "All recommendations are similar (echo chamber)."
   - Answer: "Inject diversity: penalize similar recommendations. Use content-based + collaborative hybrid. Serendipity ranking."

---

**Pattern for your answers:**
1. Restate the question
2. Identify the concern
3. Propose a solution
4. Discuss trade-offs
5. Ask clarifying questions if needed

See [System Design Guide](system-design-interview-guide.md) for comprehensive framework.
