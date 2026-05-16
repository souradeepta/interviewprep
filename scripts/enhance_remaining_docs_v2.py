#!/usr/bin/env python3
"""
Enhance system design docs (14-39) with detailed content.
Maps to actual filenames.
"""

import os
import re

# Enhanced content - using actual filenames as keys
docs_content = {
    "14_news_feed": ("News Feed",
        "┌──────────────────────────────────────────┐\n│      News Feed Service                   │\n│  ┌──────────────────────────────────────┐  │\n│  │ User Request: getFeed(userId)        │  │\n│  │                                      │  │\n│  │ 1. Get followed users (Redis)        │  │\n│  │ 2. Fetch posts from cache/DB         │  │\n│  │ 3. Rank by timestamp/engagement      │  │\n│  │ 4. Return top 20 posts               │  │\n│  └──────────────────────────────────────┘  │\n└──────────────────────────────────────────────┘",
        "**Q: Why multi-layer caching?** A: L1 (Redis): hot data, 1hr. L2 (Memcached): warm data. L3 (DB): persistent. Reduces load.\n\n**Q: Feed freshness?** A: TTL 1hr + event-based invalidation on post. Trade: cache hit vs freshness.\n\n**Q: Ranking complexity?** A: Timestamp (simple), engagement score (time-decay), ML ranking. Simple fast, ML better UX.\n\n**Q: Scaling to billions?** A: Shard by userId. Each shard manages subset feeds. Replicate for HA. Cache miss hits only shard.",
        "1B users, 1K friends avg, 10 posts/day: 10K posts/user/day. Cache 90% hit rate: 5ms latency. Storage: 1B users × 100KB = 100TB distributed.",
        [["Pull model", "Fresh data, simple", "O(followers) latency"],
         ["Push model", "Fast O(1)", "Complex, high storage"],
         ["Hybrid", "Balances both", "More complex"]],
        "1. Real-time feed updates (WebSocket)? 2. Millions of followers handling? 3. Trending topics in feed? 4. Cache invalidation bottleneck at 10x. 5. High-value content prioritization?"
    ),
    "15_ecommerce": ("E-commerce",
        "┌───────────────────────────────────────┐\n│   E-commerce Platform                 │\n│  ┌───────────────────────────────────┐  │\n│  │ Product Catalog (Elasticsearch)   │  │\n│  │ - 100M products, <100ms search    │  │\n│  │ Shopping Cart (Redis, 24hr TTL)   │  │\n│  │ - <10ms read/write                │  │\n│  │ Order Processing                  │  │\n│  │ - Inventory, Payment, Fulfill     │  │\n│  └───────────────────────────────────┘  │\n└───────────────────────────────────────────┘",
        "**Q: Inventory consistency?** A: Pessimistic lock or optimistic versioning. Use saga pattern for order flow.\n\n**Q: Cart timeout?** A: TTL 24hr, notify before expiry. Recover from backup.\n\n**Q: Product search scaling?** A: Elasticsearch cluster, shard by product_id, cache popular.\n\n**Q: Payment failure recovery?** A: Retry + exponential backoff, webhook from gateway, saga rollback.",
        "10M SKUs, 1M concurrent users, 1K orders/sec. Cart: 1M × 500B = 500GB Redis. Search: 100K QPS ES cluster. Payment: 1K req/sec (3-4 gateways).",
        [["Monolithic", "Simple, consistent", "Poor scaling"],
         ["Microservices", "Scalable, independent", "Complex coordination"],
         ["Event-driven", "Decoupled, responsive", "Harder to debug"]],
        "1. Flash sales (millions orders/sec)? 2. Real-time inventory across regions? 3. Fraud detection in payments? 4. Payment gateway bottleneck. 5. Return/refund workflow?"
    ),
    "19_database_sharding": ("Database Sharding",
        "┌──────────────────────────────────────┐\n│   Sharded Database Architecture      │\n│  ┌──────────────────────────────────┐  │\n│  │ Sharding Key: user_id            │  │\n│  │ Shard 1: user_id % 4 == 0        │  │\n│  │ Shard 2: user_id % 4 == 1        │  │\n│  │ Shard 3: user_id % 4 == 2        │  │\n│  │ Shard 4: user_id % 4 == 3        │  │\n│  │                                  │  │\n│  │ Directory: user_id → shard_id    │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Shard key selection?** A: Choose high-cardinality (user_id good, gender bad). Enables even distribution.\n\n**Q: Hot shard problem?** A: Uneven distribution if key skewed (celebrities). Solution: split hot shard, re-shard.\n\n**Q: Cross-shard queries?** A: Expensive, scatter-gather to all shards. Avoid if possible.\n\n**Q: Re-sharding complexity?** A: Double shards: migrate half of each to new shards. Zero-downtime hard, plan carefully.",
        "1B users, 4 shards: 250M per shard. Each shard: single master + replicas. Queries: shard_id = hash(user_id) % 4. Cross-shard: 4x latency.",
        [["Range sharding", "Easy range queries", "Uneven distribution"],
         ["Hash sharding", "Even distribution", "Range queries hard"],
         ["Directory-based", "Flexible, dynamic", "Extra lookup latency"]],
        "1. Dynamic re-sharding without downtime? 2. Handling growth (1B → 10B)? 3. Cross-shard transactions? 4. Load imbalance detection? 5. Disaster recovery per shard?"
    ),
    "20_message_queue": ("Message Queue",
        "┌──────────────────────────────────────┐\n│   Message Broker (Kafka-like)        │\n│  ┌──────────────────────────────────┐  │\n│  │ Topics: partitioned by key        │  │\n│  │ Producers: send messages          │  │\n│  │ Consumers: read at own pace       │  │\n│  │ Brokers: replicate, persist       │  │\n│  │ Offset: consumer position         │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Durability vs latency?** A: Sync write: all replicas ack (slow, safe). Async: leader only (fast, risky).\n\n**Q: Consumer group rebalancing?** A: When consumer joins/leaves, re-partition across group. Brief pause.\n\n**Q: Dead letter queue?** A: Messages fail N times → separate DLQ for manual review.\n\n**Q: Message ordering guarantee?** A: Per-partition ordered. Multi-partition: no global order.",
        "1M msg/sec, 10 partitions (10x parallelism). Storage: 1M × 1KB = 1GB/sec = 86TB/day. Retention: 7 days = 600TB cluster.",
        [["Queue (RabbitMQ)", "Simple per-consumer", "No persistence usually"],
         ["Log (Kafka)", "Durable, replay-able", "More complex"],
         ["Pub-Sub (Redis)", "Real-time, in-memory", "No persistence"]],
        "1. Exactly-once delivery semantics? 2. Consumer lag monitoring? 3. Broker failover recovery? 4. Throughput bottleneck at 10x? 5. Schema evolution/versioning?"
    ),
    "21_search_engine": ("Search Engine",
        "┌──────────────────────────────────────┐\n│   Full-Text Search Index             │\n│  ┌──────────────────────────────────┐  │\n│  │ Inverted Index                   │  │\n│  │ term → [doc_id, position, freq]  │  │\n│  │ Query: lookup term, get docs     │  │\n│  │ Rank: BM25 + engagement          │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Inverted index structure?** A: Map term → doc list. Query: O(log n) index lookup, retrieve ranked docs. Supports phrase, boolean.\n\n**Q: Crawling frequency?** A: Periodic (monthly full, weekly delta) + event-based (sitemap ping).\n\n**Q: Ranking algorithm?** A: TF-IDF (simple), BM25 (better), neural (ML, slow). Use BM25 + signals.\n\n**Q: Privacy?** A: Don't log queries, anonymize IPs, differential privacy for aggregates.",
        "10B pages, 5KB avg = 50TB. Inverted index: 100M terms × 8B + refs = 100GB. Query: 1-5ms search, 5-10ms total.",
        [["Full inverted index", "Fast O(log n)", "Large storage"],
         ["Trie-based", "Prefix matching", "Complex"],
         ["Bloom filters", "Space efficient", "False positives"]],
        "1. Typo/spell correction? 2. Personalized search (user interests)? 3. Spam/malicious content detection? 4. Index size bottleneck. 5. Auto-complete suggestions?"
    ),
    "22_recommendation_engine": ("Recommendation Engine",
        "┌──────────────────────────────────────┐\n│   ML-based Recommendations          │\n│  ┌──────────────────────────────────┐  │\n│  │ Collaborative Filtering          │  │\n│  │ - User-item matrix (sparse)      │  │\n│  │ - Matrix factorization           │  │\n│  │ - KNN similar users              │  │\n│  │ Content-based + Hybrid           │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Cold start problem?** A: New user: popular items. New item: content match. Explore-exploit (bandit).\n\n**Q: Recommendation staleness?** A: Batch daily + cache hot, compute cold on-demand.\n\n**Q: Sparsity handling?** A: Matrix factorization, implicit feedback, regularization.\n\n**Q: Diversity?** A: Lambda ranking penalty. 10% exploration for serendipity.",
        "100M users, 1M items, 1% sparsity. Matrix factorization: 100M × 100 factors × 4B = 40GB. Latency: 10-50ms KNN.",
        [["Collaborative filtering", "Works for all items", "Cold start, sparsity"],
         ["Content-based", "Handles cold start", "Needs features"],
         ["Hybrid", "Balances both", "More complex"]],
        "1. Detect recommendation gaming? 2. Explainability (why recommend)? 3. Context-aware (time, location)? 4. A/B testing safely? 5. Real-time vs batch?"
    ),
    "26_followers_system": ("Followers System",
        "┌──────────────────────────────────────┐\n│   Social Graph (Followers)           │\n│  ┌──────────────────────────────────┐  │\n│  │ Following Graph                  │  │\n│  │ - user → [follower_ids] (Redis)  │  │\n│  │ - O(1) add/remove follower       │  │\n│  │ Follower Graph                   │  │\n│  │ - user → [following_ids]         │  │\n│  │ - Bidirectional relationship     │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Graph consistency?** A: Keep both directions in sync. Atomic update or eventual consistency?\n\n**Q: Large follower lists?** A: Pagination (fetch first 1000). Truncate in feed (show top K).\n\n**Q: Block/mute user?** A: Add to blocklist, filter from feed/notifications.\n\n**Q: Mutual follow detection?** A: Check if A in B's followers AND B in A's followers.",
        "1B users, avg 500 followers. Storage: 500B avg followers per user = 500GB Redis. Queries: is_follower O(1), get_followers O(n).",
        [["In-memory (Redis)", "Fast, simple", "Memory cost"],
         ["Graph DB (Neo4j)", "Complex queries", "Slower"],
         ["Materialized view", "Pre-computed", "Update lag"]],
        "1. Handle celebrity (10M followers) efficiently? 2. Viral following (growth spike)? 3. Follow suggestion algorithm? 4. Privacy (hide followers)? 5. Analytics (who unfollowed)?"
    ),
    "27_notifications": ("Notifications",
        "┌──────────────────────────────────────┐\n│   Notification Service               │\n│  ┌──────────────────────────────────┐  │\n│  │ Events: like, follow, mention    │  │\n│  │ Channels: push, email, SMS       │  │\n│  │ Delivery: queue-based (Kafka)    │  │\n│  │ Preferences: user opt-in/out     │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Notification delivery reliability?** A: Persistent queue, retry exponential backoff, dead letter queue.\n\n**Q: Thundering herd (all wake at once)?** A: Stagger notifications across time window, use jitter.\n\n**Q: Preference system?** A: Per notification type opt-in. Don't spam = healthy user experience.\n\n**Q: Real-time vs digest?** A: Real-time for critical (comment reply), digest for daily summary.",
        "1B users, 10 notifications/day avg. Throughput: 100K notif/sec. Delivery: 1% hard bounce rate. Cost: $0.01 per push, $10M/month at scale.",
        [["Real-time push", "Immediate, engaging", "Battery drain, spam"],
         ["Digest email", "Non-intrusive", "Lower engagement"],
         ["Hybrid", "Balances both", "More complex"]],
        "1. Handle notification fatigue (user unsubscribes)? 2. Personalization (frequency, time)? 3. Multi-device synchronization? 4. Delivery channel failure (fall back)? 5. Cost optimization?"
    ),
    "28_api_gateway": ("API Gateway",
        "┌──────────────────────────────────────┐\n│   API Gateway (Nginx/Kong)           │\n│  ┌──────────────────────────────────┐  │\n│  │ Request Routing                  │  │\n│  │ - Path → service mapping         │  │\n│  │ - Load balancing                 │  │\n│  │ Authentication                   │  │\n│  │ - JWT validation, OAuth          │  │\n│  │ Rate limiting, circuit breaking  │  │\n│  │ Request/response transformation  │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Single point of failure?** A: HA gateway cluster (active-active), stateless design, health checks.\n\n**Q: Authentication caching?** A: Cache JWT validation (10min TTL) to reduce auth service load.\n\n**Q: Request timeout tuning?** A: Per-route timeouts. Read timeout > write timeout. Don't timeout indefinitely.\n\n**Q: Versioning (v1, v2)?** A: Header-based or URL path. Deprecate old versions with notice.",
        "1M req/sec, 100ms avg latency budget. Gateway: <5ms overhead ideal. RPS per gateway: 100K-200K. Need 5-10 gateways.",
        [["Simple proxy", "Low overhead", "No auth/rate-limit"],
         ["Full gateway", "Feature-rich", "More complex"],
         ["Service mesh (Istio)", "Decentralized", "Operational overhead"]],
        "1. Blue-green deployment (zero downtime)? 2. Service discovery integration? 3. Request logging/tracing? 4. Scale beyond 10 gateways? 5. Cost optimization?"
    ),
    "29_websocket_server": ("WebSocket Server",
        "┌──────────────────────────────────────┐\n│   WebSocket Server (Real-time)       │\n│  ┌──────────────────────────────────┐  │\n│  │ Connection Pool                  │  │\n│  │ - 1M concurrent WebSocket conns  │  │\n│  │ - 10KB per connection (memory)   │  │\n│  │ Message Broadcast                │  │\n│  │ - Room/channel abstraction       │  │\n│  │ - Efficient fan-out              │  │\n│  │ Graceful Disconnection           │  │\n│  │ - Heartbeat ping-pong            │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: WebSocket scalability?** A: Single server: ~10-50K connections (memory limited). Horizontal scale: use Redis pub-sub for cross-server messaging.\n\n**Q: Connection state management?** A: Store in Redis, allow failover to another server.\n\n**Q: Heartbeat mechanism?** A: Ping every 30s. Timeout after 3 missed pongs. Detects dead connections.\n\n**Q: Message ordering?** A: Order preserved within single connection. Multi-server: eventual order (acceptable).",
        "1M concurrent WebSocket connections. Memory: 1M × 10KB = 10GB per server. Throughput: 10K msg/sec broadcast = fan-out to 1M = 10M msg/sec.",
        [["Raw WebSocket", "Low latency", "Stateful, harder scale"],
         ["With Redis", "Scales horizontally", "Extra hop latency"],
         ["Message queue", "Decoupled, durable", "Higher latency"]],
        "1. Handle connection storms (users spike)? 2. Message compression? 3. Binary vs text protocol? 4. Reconnection logic? 5. Security (auth on upgrade)?"
    ),
    "33_photo_sharing": ("Photo Sharing",
        "┌──────────────────────────────────────┐\n│   Photo Sharing Platform             │\n│  ┌──────────────────────────────────┐  │\n│  │ Upload Pipeline                  │  │\n│  │ - Multipart form (resumable)     │  │\n│  │ - Virus scan, EXIF strip         │  │\n│  │ - Compression (multiple sizes)   │  │\n│  │ Storage & CDN                    │  │\n│  │ - S3 + CloudFront               │  │\n│  │ Metadata (ElasticSearch)         │  │\n│  │ - Search by tags, location       │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Image resizing—when?** A: On-demand first, cache. Pre-resize for popular (expensive). Background worker for bulk.\n\n**Q: Storage cost—how to optimize?** A: Compress lossy (JPEG 75%), delete old/unused, archive to cold storage.\n\n**Q: EXIF data—privacy?** A: Strip location data (privacy), keep upload timestamp/camera (non-sensitive).\n\n**Q: DRM for photos?** A: Watermarking, view-only, disable save. Trade UX vs protection.",
        "1B photos, 2MB avg = 2EB. Resizing: thumbnail (100KB), medium (500KB), original. CDN: 10M req/day, 99% hit rate.",
        [["On-demand resize", "Saves storage", "Slower first load"],
         ["Pre-resize all", "Fast load", "Storage overhead"],
         ["Tiered sizing", "Balance both", "More complex"]],
        "1. Handle massive upload spike? 2. Copyright detection (similar photos)? 3. Privacy (make private/public)? 4. Analytics (hot photos)? 5. Cost per user?"
    ),
    "36_like_comment_system": ("Like/Comment System",
        "┌──────────────────────────────────────┐\n│   Like/Comment Engine                │\n│  ┌──────────────────────────────────┐  │\n│  │ Like Counter                     │  │\n│  │ - Redis atomic increment         │  │\n│  │ - Persist to DB (async)          │  │\n│  │ Comments                         │  │\n│  │ - Threaded (parent_id)           │  │\n│  │ - Sorted by time/score           │  │\n│  │ Notification on engagement       │  │\n│  │ - Publish event (Kafka)          │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Double-like prevention?** A: Check if user already liked (set membership). If yes, unlike. If no, add to set.\n\n**Q: Like count accuracy vs speed?** A: Cache in Redis (fast but stale), sync to DB hourly (accurate). Acceptable lag.\n\n**Q: Comment moderation?** A: ML classifier (toxicity), manual review for borderline. Hide pending review.\n\n**Q: Comment ordering—best first?** A: By score (likes - reports). Time-decay: recent higher. Controversial (mixed opinions) interesting.",
        "1B items, 1K likes avg = 1T likes. Like updates: 10 req/sec per item = 100K global. Cache 1B items × 4B = 4GB Redis.",
        [["Count-only", "Simple, fast", "No like history"],
         ["Set-based (track users)", "De-duplicate, per-user prefs", "Higher memory"],
         ["Sorted set (scored)", "Complex ranking", "More storage"]],
        "1. Spam like detection? 2. Sort comments optimally? 3. Like propagation (friend feed update)? 4. Sensitivity (hide counts)? 5. Verification (real accounts)?"
    ),
    "37_auction_system": ("Auction System",
        "┌──────────────────────────────────────┐\n│   Auction/Bidding System             │\n│  ┌──────────────────────────────────┐  │\n│  │ Auction State Machine            │  │\n│  │ - Open, Active, Closed, Settled  │  │\n│  │ Current Bid Tracking             │  │\n│  │ - Redis sorted set (price)       │  │\n│  │ Bid Validation                   │  │\n│  │ - > current, min increment       │  │\n│  │ Winner Determination             │  │\n│  │ - Highest bid at close time      │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Bid race condition—same bid twice?** A: Use versioning or CAS (compare-and-swap). Increment version on bid.\n\n**Q: Auction end-time manipulation?** A: Record exact close time in DB. If bid arrives within 5s of close, extend by 5s (prevent sniping).\n\n**Q: Automatic bidding (proxy bid)?** A: Store max bid, auto-bid up to that. Reveal gradually to encourage competition.\n\n**Q: Payment guarantee?** A: Escrow: winner pays into escrow, seller ships, then escrow releases. Reduces fraud.",
        "eBay: 10M concurrent auctions, 100K bids/sec. Bid validation O(1). State transition O(1). Close processing: batch hourly, 100K winners.",
        [["Simple highest-bid", "Easy, fast", "No auto-bidding"],
         ["Proxy bid auction", "Fair, encourages bidding", "More state"],
         ["Dutch auction", "Price decreases", "Different mechanics"]],
        "1. Shill bidding detection (fake bids)? 2. Reserve price (hidden minimum)? 3. Multiple winners (buy-it-now)? 4. Dispute resolution? 5. International (currency conversion)?"
    ),
    "38_transaction_ledger": ("Transaction Ledger",
        "┌──────────────────────────────────────┐\n│   Immutable Transaction Log          │\n│  ┌──────────────────────────────────┐  │\n│  │ Append-Only Log                  │  │\n│  │ - Never update/delete            │  │\n│  │ - Hash chain (blockchain-like)   │  │\n│  │ Snapshots (for fast restart)     │  │\n│  │ - Hourly checkpoint              │  │\n│  │ Balance Derivation               │  │\n│  │ - Replay log = current balance   │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Why append-only?** A: Immutable audit trail. Corruption detectable (hash breaks). Replaying gives any point-in-time state.\n\n**Q: Ledger bloat—retention?** A: Archive old entries (S3), keep recent (hot DB). Snapshots reduce replay time.\n\n**Q: Balance query performance?** A: Materialized view (balance table), updated via ledger replay. Or cache at query time.\n\n**Q: Reconciliation audits?** A: Periodic: replay ledger, compare balance snapshot. Detects bugs or data corruption.",
        "1M users, 10 txns/day avg = 10M ledger entries/day. Storage: 10M × 200B = 2GB/day = 730GB/year. Snapshot: hourly.",
        [["Append-only log", "Immutable, auditable", "Slower queries"],
         ["Update-in-place", "Fast, simple", "Loses history, harder audit"],
         ["Event sourcing", "Full history, replay", "Complex, large storage"]],
        "1. Query balance at specific timestamp? 2. Exporting ledger for tax/audit? 3. Compliance (GDPR retention)? 4. Corruption detection? 5. Performance at scale?"
    ),
    "39_consensus_algorithm": ("Consensus Algorithm",
        "┌──────────────────────────────────────┐\n│   Distributed Consensus (Raft)       │\n│  ┌──────────────────────────────────┐  │\n│  │ Leader Election                  │\n│  │ - Followers vote for leader      │  │\n│  │ - Majority wins                  │  │\n│  │ Log Replication                  │  │\n│  │ - Leader appends entries         │  │\n│  │ - Followers replicate            │  │\n│  │ Safety                           │  │\n│  │ - Majority ack = committed       │  │\n│  └──────────────────────────────────┘  │\n└──────────────────────────────────────────┘",
        "**Q: Leader election timeout tuning?** A: Too short: election flaps. Too long: recovery slow. Typical: 150-300ms.\n\n**Q: Partition tolerance—split brain?** A: Minority partition can't elect leader (needs majority). Minority read-only until merge.\n\n**Q: Log compaction?** A: Snapshot at intervals, discard old log. Speeds up recovery.\n\n**Q: Performance impact?** A: Write latency = wait for majority replication (synchronous). Read faster (leader only). Throughput limited by leader.",
        "ZooKeeper: 5-node cluster, 1000 txn/sec. Election: 150-300ms. Replication: 10-20ms per node × 3 = 30-60ms total latency impact.",
        [["Raft", "Simple, understandable", "Slower writes"],
         ["Paxos", "More complex, faster", "Harder to implement"],
         ["Eventual consistency", "Fast, no consensus", "Inconsistent state possible"]],
        "1. Add node to cluster dynamically? 2. Remove node safely (no data loss)? 3. Cross-datacenter replication? 4. Linearizability guarantee? 5. Performance at 1000s of nodes?"
    ),
}

base_path = "/home/sbisw/github/interviewprep/docs/system_design"

# Process each doc
for filename, (name, arch, qa, calc, comparison, followups) in docs_content.items():
    file_path = os.path.join(base_path, f"{filename}.md")

    if not os.path.exists(file_path):
        print(f"⚠ {filename}.md not found, skipping")
        continue

    with open(file_path, 'r') as f:
        content = f.read()

    # Replace sections
    content = re.sub(
        r"## Architecture Diagram\n\n```\n\[Visual representation[^\]]*\]\n```",
        f"## Architecture Diagram\n\n```\n{arch}\n```",
        content
    )

    # Replace Q&A section
    content = re.sub(
        r"\*\*Q: Key design decision\?\*\*\nA: \[Answer[^\n]*\]\n\n\*\*Q: When[^\n]*\*\*\nA: \[Use case[^\n]*\]\n\n\*\*Q: What are the trade[^\n]*\*\*\nA: \[Trade[^\n]*\]\n\n\*\*Q: How does this scale\?\*\*\nA: \[Scalability[^\n]*\]",
        qa,
        content
    )

    # Replace calculations
    content = re.sub(
        r"For typical scenario \(adjust numbers\):\n- Storage: \[calculation\][^\n]*\n- Throughput: \[req/sec[^\n]*\n- Latency: \[p99[^\n]*\n- Bandwidth: \[calculation\]",
        calc,
        content
    )

    # Replace comparison table
    comp_text = "\n".join([f"| {row[0]} | {row[1]} | {row[2]} |" for row in comparison])
    content = re.sub(
        r"\| Option A \| \[pros\] \| \[cons\] \|\n\| Option B \| \[pros\] \| \[cons\] \|",
        comp_text,
        content
    )

    # Replace followup questions
    content = re.sub(
        r"1\. How would you handle \[scale/failure/change\]\?\n2\. What if requirements change to \[different constraint\]\?\n3\. How to monitor \[key metric\]\?\n4\. What's the bottleneck at 10x scale\?\n5\. How would you optimize for \[specific scenario\]\?",
        followups,
        content
    )

    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✓ Updated {filename}")

print("\n✅ All remaining docs enhanced")
