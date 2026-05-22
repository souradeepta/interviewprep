#!/usr/bin/env python3
"""
Enhance 30 new system design concepts with detailed content.
"""

import os
import re
import glob

base_path = "/home/sbisw/github/interviewprep/docs/system_design"

enhancements = {
    "01_consistent_hashing": {
        "arch": "Hash ring with replica placement. Nodes placed at hash(node_id). Key hashed to nearest node clockwise.",
        "diagram": "Ring with N nodes:\n  Node 1 (0°) → handles keys 0-90\n  Node 2 (90°) → handles keys 90-180\n  Node 3 (180°) → handles keys 180-270\n  Node 4 (270°) → handles keys 270-360",
        "qa": "**Q: How to handle node addition?** A: Only keys between new and previous node need remapping (~1/n).\n\n**Q: Virtual nodes?** A: Each physical node maps to 150-200 virtual nodes. Better distribution.\n\n**Q: Replication?** A: Place replicas at next k nodes clockwise. Tolerates k-1 failures.",
        "calc": "- 1000 nodes, 1B keys: remapping on node add = ~1M keys (0.1%)\n- Search: O(log n) binary search on ring + hash = 50 ops\n- Virtual nodes: 150 vnodes × 1000 = 150K ring positions",
        "choices": [
            ["Consistent hashing", "Minimal remapping on node changes", "More complex than modulo"],
            ["Modulo hashing", "Simple", "Requires remapping >50% keys on change"],
            ["Rendezvous hashing", "No virtual nodes needed", "More CPU expensive"]
        ]
    },
    "02_geohashing": {
        "arch": "Recursively subdivide map into quadrants, encode as bits. String from bits via base32.",
        "diagram": "Geohash encoding:\n  World → 32 quadrants (level 1, 5 bits)\n  Each quadrant → 32 sub-quadrants (level 2)\n  Each sub-quadrant → 32 sub-sub-quadrants (level 3)\n  \"wx4\" = precision level 3 geohash",
        "qa": "**Q: Precision levels?** A: 11 chars = 37cm accuracy. 8 chars = 38m. 6 chars = 1.2km.\n\n**Q: Spatial queries?** A: Query geohash neighbors for nearby results.\n\n**Q: Index efficiency?** A: B-tree on geohash string enables range scans.",
        "calc": "- Earth = 10 billion geohashes (level 6)\n- User location precision: level 8 = 38m (fine for most apps)\n- Neighbor queries: check up to 9 hashes (current + 8 neighbors)",
        "choices": [
            ["Geohashing", "String-based, indexable", "Proximity anomalies at boundaries"],
            ["Latitude/Longitude", "Direct coordinates", "Requires 2D spatial indexing (R-tree)"],
            ["Quadtree", "Perfect spatial locality", "More complex to implement"]
        ]
    },
    "03_trie_data_structure": {
        "arch": "Tree of characters. Each node = character, edges = next chars. Leaf = end of word.",
        "diagram": "Trie for {cat, car, card, dog}:\n      root\n     /    \\\n    c      d\n   / \\      \\\n  a   a     o\n / \\  |      \\\n t r  r      g\n |\\  |\\     (word)\n * d  d\n   *  |\\",
        "qa": "**Q: Autocomplete?** A: Start from user input chars, traverse trie, return all leaf words.\n\n**Q: Space complexity?** A: O(ALPHABET_SIZE * N) where N = total chars in all words.\n\n**Q: Prefix queries?** A: O(m) where m = prefix length, returns all matches.",
        "calc": "- English vocabulary: 170K words, avg 5 chars = 850K characters\n- Trie storage: ~10 bytes/node × 850K = 8.5MB\n- Autocomplete lookup: <1ms for typical prefixes",
        "choices": [
            ["Trie", "Efficient prefix search", "More memory than hash table"],
            ["Hash table + sort", "Simple", "O(n log n) for prefix queries"],
            ["Prefix tree + cache", "Fast with caching", "Cache invalidation complexity"]
        ]
    },
    "04_hyperloglog": {
        "arch": "Hash values to bit positions. Track max leading zeros per bucket. Estimate cardinality from max values.",
        "diagram": "HyperLogLog with 16 buckets (4 bits hash prefix):\n  Bucket 0: max zeros = 3\n  Bucket 1: max zeros = 2\n  ...\n  Bucket 15: max zeros = 4\n  Estimate cardinality from average max zeros",
        "qa": "**Q: Accuracy?** A: Standard error ~1.04/sqrt(m) where m = number of buckets. m=16 → 26% error.\n\n**Q: Merging?** A: Take max of each bucket. Combines cardinality estimates.\n\n**Q: False positives?** A: None. Standard error, not false positives.",
        "calc": "- m=16384 buckets, 14 bits per bucket = 28KB\n- 1B unique items, error = 0.8%\n- vs hash set: 1B × 8 bytes = 8GB (285× larger)",
        "choices": [
            ["HyperLogLog", "Minimal memory, fast", "Approximate, not exact"],
            ["Hash set", "Exact count", "O(n) memory"],
            ["Bitmap", "Simple, exact", "Memory = max_item / 8"]
        ]
    },
    "05_simulation_algorithms": {
        "arch": "Model system behavior via simulation. Discrete-event simulation for time progression.",
        "diagram": "DES timeline:\n  T=0: Request arrives\n  T=5: Server processing\n  T=10: Response sent\n  T=15: Next request\n  Track metrics per event",
        "qa": "**Q: Warmup period?** A: Discard first N events to stabilize. Metrics from then on.\n\n**Q: Variance reduction?** A: Use same random seed for A/B comparisons.\n\n**Q: Accuracy vs speed?** A: More iterations = more accurate but slower.",
        "calc": "- Monte Carlo sim: 100K iterations for CI = 2% error\n- Simulation 1000 events: ~10ms on modern CPU\n- 100 scenarios × 10ms = 1 second to evaluate strategy",
        "choices": [
            ["Discrete event simulation", "Natural model of queueing", "Can be slow for large scales"],
            ["Analytic model", "Fast, closed form", "Requires simplifying assumptions"],
            ["Emulation", "Realistic", "Expensive infrastructure"]
        ]
    },
    "01_proxy_pattern": {
        "arch": "Client → Proxy → Real Subject. Proxy controls access, caches, adds security.",
        "diagram": "Client → Proxy → [Cache/Auth/Logging] → RealSubject",
        "qa": "**Q: vs Decorator?** A: Proxy controls creation. Decorator wraps existing object.\n\n**Q: Use cases?** A: Lazy initialization, access control, logging, caching.",
        "calc": "- Proxy overhead: 1-2% latency for cache hits\n- Cache hit rate: 80-90% typical\n- Net benefit: 10-50% latency reduction",
        "choices": [
            ["Proxy", "Lazy loading, control", "Extra layer"],
            ["Direct access", "Simple", "No lazy loading or caching"],
            ["Facade", "Simplify interface", "Not for security/caching"]
        ]
    },
    "02_composite_pattern": {
        "arch": "Tree of objects. Leaf and Composite have same interface. Operations propagate down.",
        "diagram": "Composite\n  ├─ Leaf\n  ├─ Composite\n  │  ├─ Leaf\n  │  └─ Leaf\n  └─ Leaf",
        "qa": "**Q: vs inheritance?** A: Composition over inheritance. Flexible structure.\n\n**Q: Traversal?** A: DFS or iterator pattern.",
        "calc": "- Tree with 1M nodes, 10 levels: traversal = ~10M ops\n- Memory: 50 bytes/node = 50MB for 1M nodes",
        "choices": [
            ["Composite", "Natural hierarchy", "Extra overhead"],
            ["Flat list", "Simple", "No structure"],
            ["OOP inheritance", "Type safety", "Rigid structure"]
        ]
    },
    "03_template_method": {
        "arch": "Base class defines algorithm steps. Subclasses override specific steps.",
        "diagram": "BaseClass.templateMethod():\n  step1() [concrete]\n  step2() [abstract]\n  step3() [concrete]\nSubclass overrides step2()",
        "qa": "**Q: vs Strategy?** A: Template: inheritance, compile-time. Strategy: composition, runtime.\n\n**Q: Inversion of control?** A: Framework calls subclass methods.",
        "calc": "- Reduces code duplication: 30-50% less code\n- Performance: 0% overhead",
        "choices": [
            ["Template Method", "Code reuse, inversion of control", "Tight coupling"],
            ["Strategy pattern", "Runtime flexibility", "More classes"],
            ["Inheritance", "Simple", "Tight coupling, fragile base"]
        ]
    },
    "04_chain_of_responsibility": {
        "arch": "Handler chain. Each handler processes or forwards to next.",
        "diagram": "Request → H1 (pass) → H2 (pass) → H3 (handle) → Response",
        "qa": "**Q: vs Composite?** A: Chain: linear flow. Composite: tree structure.\n\n**Q: Order matters?** A: Yes. Chain order affects processing.",
        "calc": "- Chain length: 5-10 handlers typical\n- Latency: O(n) where n = chain length",
        "choices": [
            ["Chain of Responsibility", "Loose coupling", "Order dependency"],
            ["If-else chain", "Simple", "Tight coupling"],
            ["Visitor", "Complex traversal", "More complex"]
        ]
    },
    "05_visitor_pattern": {
        "arch": "Separates algorithm (Visitor) from object structure. Visitor implements operations.",
        "diagram": "Structure: Element (Visitor visit(Visitor))\nVisitor: Visitor (visit(ElementA), visit(ElementB))",
        "qa": "**Q: vs composite?** A: Composite: tree. Visitor: operations on elements.\n\n**Q: New operations?** A: Add new Visitor subclass without changing Element.",
        "calc": "- Element types: 10, Visitor types: 20 = 200 visit methods\n- Compile time: 2× longer due to visitor dispatch\n- Runtime: 5-10% overhead vs direct methods",
        "choices": [
            ["Visitor", "Easy to add operations", "Hard to add element types"],
            ["Element methods", "Simple", "Hard to add new operations"],
            ["Double dispatch", "Flexible", "Language dependent"]
        ]
    },
    "06_memento_pattern": {
        "arch": "Originator creates Memento (snapshot). Caretaker stores. Memento restored for undo.",
        "diagram": "Originator.createMemento() → Memento\nCaretaker.save(Memento)\nCaretaker.undo() → Originator.restore(Memento)",
        "qa": "**Q: Memory?** A: Each memento = full state snapshot. Optimize with delta/compression.\n\n**Q: Undo limit?** A: Typical: 10-100 steps. Stack-based or circular buffer.",
        "calc": "- Document state: 10MB, 50 undo levels = 500MB\n- Compression: ~30% → 350MB\n- Delta-based: ~10% original = 50MB",
        "choices": [
            ["Memento", "Clean undo/redo", "Memory intensive"],
            ["Delta storage", "Memory efficient", "Complex to implement"],
            ["Command pattern", "Reversible actions", "Depends on command impl"]
        ]
    },
    "01_btree_bplus_tree": {
        "arch": "B+ tree: all data in leaves, non-leaf nodes are routing. 100-200 keys per node.",
        "diagram": "Root [1, 5, 10, 15]\n├─ [0-1]\n├─ [1-5]\n├─ [5-10]\n└─ [10-15]",
        "qa": "**Q: Search complexity?** A: O(log n) where n = number of keys. 3-4 levels for 1B keys.\n\n**Q: Range queries?** A: Linear scan of leaf nodes. O(k + log n) for k results.",
        "calc": "- 1B keys, 200 keys/node: ~5 levels\n- Search: 5 disk reads = 50ms typical (10ms/read)\n- Insert: 5 reads + 1 write = 60ms",
        "choices": [
            ["B+ tree", "Efficient both search and range", "Complex to implement"],
            ["Binary search tree", "Simple", "O(log n) but unbalanced"],
            ["Hash table", "O(1) search", "No ordering, no range queries"]
        ]
    },
    "02_lsm_tree": {
        "arch": "In-memory MemTable → disk Levels. Compaction merges SSTables.",
        "diagram": "Writes:\n  In-memory MemTable (64MB)\n  ↓ when full\n  Level 0 (10 SSTables)\n  ↓ compaction\n  Level 1 (100MB)\n  ↓ compaction\n  Level N (TBs)",
        "qa": "**Q: Write amplification?** A: 10-50× due to compaction. O(log n) but slower constants.\n\n**Q: Read penalties?** A: Check MemTable, then L0 (may have many), then Li.",
        "calc": "- Write throughput: 100K writes/sec\n- Compaction CPU: 20-30% of total\n- Read latency: 10-50ms depending on where key is",
        "choices": [
            ["LSM tree", "Fast writes", "Slower reads, write amplification"],
            ["B+ tree", "Balanced reads/writes", "Slower writes"],
            ["Hybrid", "Tuneable", "More complex"]
        ]
    },
    "03_mvcc": {
        "arch": "Each transaction gets snapshot version. Reads from snapshot, writes create new version.",
        "diagram": "V0: key→A\nTx1 reads V0: key→A\nTx2 writes: key→B (creates V1)\nTx1 still sees V0: key→A\nTx2 commits V1",
        "qa": "**Q: No blocking?** A: Readers don't block writers. Writers create versions.\n\n**Q: GC old versions?** A: Remove versions not visible to any transaction.",
        "calc": "- 1000 concurrent transactions: 1000 versions per popular key\n- Version metadata: 100 bytes/version = 100KB per key\n- GC overhead: 10-20% of CPU",
        "choices": [
            ["MVCC", "Concurrent reads/writes", "Version overhead"],
            ["Locking", "Simple", "High contention, blocking"],
            ["Optimistic locking", "Lock-free", "Aborts on conflicts"]
        ]
    },
    "04_query_optimization": {
        "arch": "Parse → Validate → Optimize (choose indexes, join order) → Execute.",
        "diagram": "SELECT * FROM users WHERE age > 20 AND city='NYC'\n  ↓ parser\n  ↓ optimize: use age_index, filter by city\n  ↓ execute: scan index, fetch rows, filter",
        "qa": "**Q: Cost estimation?** A: Histograms of data distribution.\n\n**Q: Join order?** A: Cardinality estimation. Smaller result sets first.",
        "calc": "- Query plan options: 10! for 10 tables = 3.6M possibilities\n- Dynamic programming: O(3^n) = manageable for n≤15",
        "choices": [
            ["Cost-based optimizer", "Good plans", "Slow optimization"],
            ["Heuristic", "Fast plans", "Sometimes suboptimal"],
            ["Hints from user", "Predictable", "Requires expertise"]
        ]
    },
    "05_replication_strategies": {
        "arch": "Sync replication (all ACK), Async (one ACK), Semi-sync (majority ACK).",
        "diagram": "Sync: Master → wait ← Slaves ACK → Client ACK\nAsync: Master → Client ACK → replicate to Slaves",
        "qa": "**Q: Master failure risk?** A: Async = data loss possible. Sync = slower but safe.\n\n**Q: RPO/RTO?** A: RPO = data loss amount. RTO = recovery time.",
        "calc": "- Sync 2-slave: latency = p99(slave1, slave2) = slower\n- Async: latency = master only = faster\n- Replication lag: typically 1-100ms",
        "choices": [
            ["Async", "Fast writes", "Data loss risk"],
            ["Sync", "Safe", "Slow writes"],
            ["Semi-sync", "Balanced", "Middle ground"]
        ]
    },
    "01_instagram_scale": {
        "arch": "Photo storage: S3/HDFS. Feed: Redis cache + DB. Search: Elasticsearch.",
        "diagram": "Cameras → Storage (S3) → Cache (Redis) → Client\nSearch Index (ES) ← Photo metadata",
        "qa": "**Q: 1B+ photos?** A: Shard by user_id. Each shard = 1M photos.\n\n**Q: Feed generation?** A: Pre-compute popular, generate on-demand for tail.",
        "calc": "- 1B photos, 100KB avg: 100PB storage\n- 1M users, 1000 photos each average\n- Feed: cache 1000 latest per user = 1B entries × 100 bytes = 100GB",
        "choices": [
            ["Centralized", "Simple", "Scaling issues"],
            ["Sharded", "Scales", "Cross-shard queries harder"],
            ["Cache + DB", "Balanced", "Cache invalidation"]
        ]
    },
    "02_uber_ride_matching": {
        "arch": "User location → Redis geohash → find nearby drivers → assign via scoring.",
        "diagram": "User → geohash(location) → nearby drivers (Redis) → scorer → dispatch",
        "qa": "**Q: Cold start?** A: Few drivers available. Show all within 5km.\n\n**Q: Surge pricing?** A: Dynamic pricing based on demand/supply ratio.",
        "calc": "- 80M users, 5M drivers at peak\n- Location updates: 10M req/sec (geohashing)\n- Matching latency: <100ms p99",
        "choices": [
            ["Geohashing", "Simple spatial index", "Boundary anomalies"],
            ["Quadtree", "Better locality", "More complex"],
            ["R-tree", "Optimal", "More overhead"]
        ]
    },
    "03_netflix_streaming": {
        "arch": "Video encoding (many bitrates) → CDN (edge caches) → player (adaptive bitrate).",
        "diagram": "Upload → Transcode (1080p, 720p, 480p, ...) → CDN edge → Player",
        "qa": "**Q: Bitrate adaptation?** A: Monitor bandwidth, switch every 4-10 seconds.\n\n**Q: CDN failover?** A: Multiple CDN providers. Fallback to alternate.",
        "calc": "- 200M users, 30% watch simultaneously = 60M streams\n- Bitrate: avg 3Mbps = 180M Mbps = need 5M parallel 1Gbps connections",
        "choices": [
            ["Single CDN", "Simple", "Single point of failure"],
            ["Multi-CDN", "Resilient", "Complex routing"],
            ["Self-hosted", "Control", "Expensive at scale"]
        ]
    },
    "04_github_collaboration": {
        "arch": "Git repos → PR workflow → CI/CD → review → merge → deploy.",
        "diagram": "Dev branch → PR → CI tests → code review → main → deploy",
        "qa": "**Q: Merge conflicts?** A: Detected by Git. Manual resolution if conflicting.\n\n**Q: PR queue?** A: Risk of conflicts. Rebase/merge strategies.",
        "calc": "- 100M repos, avg 100MB each = 10EB storage\n- 10K commits/sec processing (hashing, indexing)",
        "choices": [
            ["Monorepo", "Single source of truth", "Scaling challenges"],
            ["Many repos", "Isolation", "Integration complexity"],
            ["Monolith + modules", "Balance", "Complex tooling"]
        ]
    },
    "05_airbnb_booking": {
        "arch": "Search (ES) → availability check (Redis) → booking (payment + reservation).",
        "diagram": "Search → Filter by price, dates → Check availability → Book → Payment",
        "qa": "**Q: Double booking?** A: Distributed lock on room. Atomic transaction.\n\n**Q: Cancellation?** A: Refund via payment processor. Free up room immediately.",
        "calc": "- 5M listings, 2M concurrent searches\n- Booking: <100ms from click to confirmation\n- Payment processing: ~2% decline rate",
        "choices": [
            ["Pessimistic locking", "Prevents conflicts", "Contention under load"],
            ["Optimistic + retry", "Higher throughput", "Retry overhead"],
            ["Distributed lock", "Simple", "Latency cost"]
        ]
    },
    "06_linkedin_recommendations": {
        "arch": "User profile → feature vector → nearest neighbors (ANN) → rank → serve.",
        "diagram": "User features → embedding → ANN search → Ranker → recommendations",
        "qa": "**Q: Cold start users?** A: Content-based filtering with user attributes.\n\n**Q: Freshness?** A: Update daily or weekly. Real-time for very popular.",
        "calc": "- 900M users, 5 recommendation requests/user/month = 3.75B recs/month\n- Feature vector: 256 dimensions = 256KB for 900M users = 200GB",
        "choices": [
            ["Collaborative filtering", "Captures preferences", "Cold start problem"],
            ["Content-based", "Works for cold start", "Less sophisticated"],
            ["Hybrid", "Best of both", "More complex"]
        ]
    },
    "01_collaborative_filtering": {
        "arch": "User-item matrix → matrix factorization → predict ratings → rank.",
        "diagram": "User-Item matrix:\n  User1: [5, 3, ?, 4]\n  User2: [4, ?, 2, 5]\n  Factorize: User1 ≈ [0.9, 0.1] × [[rating components]]",
        "qa": "**Q: Sparsity?** A: Users rate <1% of items. Use SVD, NMF for factorization.\n\n**Q: Scalability?** A: 1B users × 100M items = 100B matrix. Sample for training.",
        "calc": "- Matrix: 1B users × 100M items. Sparsity: 99.99%\n- Factorized: 1B × 64 + 100M × 64 = 64B floats = 256GB\n- Training: 100M interactions, SGD = hours to days",
        "choices": [
            ["User-based CF", "Intuitive", "O(n) for each recommendation"],
            ["Item-based CF", "Scalable", "Less interpretable"],
            ["Matrix factorization", "Efficient", "Model complexity"]
        ]
    },
    "02_content_based_filtering": {
        "arch": "Item features + user profile → similarity scoring → recommendations.",
        "diagram": "Item: [genre, director, year, rating]\nUser profile: [pref_genre, pref_director, ...]\nScore = similarity(item, profile)",
        "qa": "**Q: Feature engineering?** A: Manual or learned embeddings.\n\n**Q: Cold start?** A: Works well for new items (features available).",
        "calc": "- Item features: 100 per item\n- Scoring: dot product = 100 ops per item\n- 10K candidates: 1M ops = <1ms",
        "choices": [
            ["Content-based", "Cold start friendly", "Overspecialization"],
            ["Collaborative", "Serendipity", "Cold start problem"],
            ["Hybrid", "Best of both", "Higher complexity"]
        ]
    },
    "03_ranking_systems": {
        "arch": "Features extracted → ML model (LTR) → score items → sort → serve.",
        "diagram": "Item features → LTR model (LambdaMART) → score → rank → user",
        "qa": "**Q: Feature importance?** A: Analyze model weights. Top: CTR, time decay, diversity.\n\n**Q: Real-time ranking?** A: Pre-score, batch top K, fine-tune at serving.",
        "calc": "- 100 features per item\n- Model inference: 10ms for 100K items = feasible\n- Training: 100M clicks, XGBoost = hours",
        "choices": [
            ["Pointwise LTR", "Simple", "Ignores relative ranking"],
            ["Pairwise LTR", "Better", "Training slower"],
            ["Listwise LTR", "Best", "Most complex"]
        ]
    },
    "04_feature_engineering": {
        "arch": "Feature store: offline (batch) + online (cache). Transform, aggregate, serve.",
        "diagram": "Raw data → Offline: compute features → Cache → Online: serve\nLow latency access: <100ms",
        "qa": "**Q: Feature freshness?** A: Depends on use case. Hourly to daily typical.\n\n**Q: Training/serving skew?** A: Use same feature computation for both.",
        "calc": "- 1000 features × 100M users = 100B values\n- Storage: 100B × 4 bytes = 400GB (cache for active users)\n- Daily update: 100B operations = hours with MapReduce",
        "choices": [
            ["Feature store", "Centralized, consistent", "Infrastructure cost"],
            ["Inline computation", "Fresh features", "Latency cost"],
            ["Batch + cache", "Balanced", "Freshness tradeoff"]
        ]
    },
    "05_ab_testing_framework": {
        "arch": "Assign users to variants → track metrics → analyze statistics → decide.",
        "diagram": "Users split [Control: 50%, Variant A: 25%, Variant B: 25%]\nTrack: CTR, conversion, revenue → Statistical test",
        "qa": "**Q: Sample size?** A: Calculate for 80% power, 5% significance.\n\n**Q: Early stopping?** A: Risk of false positives. Run for full duration.",
        "calc": "- 1M users/day per variant\n- 2% baseline conversion, 10% lift target\n- Sample needed: 100K/variant (1 day)\n- Confidence: 95% after 7 days of control",
        "choices": [
            ["Frequentist", "Standard statistical tests", "Fixed sample size"],
            ["Bayesian", "Prior knowledge, stopping rules", "More complex"],
            ["Sequential", "Early stopping possible", "Higher false positive risk"]
        ]
    },
    "01_oauth_sso": {
        "arch": "OAuth provider → delegate auth → access token → authorize resource access.",
        "diagram": "User → App → OAuth provider → Login → Token → Access resource",
        "qa": "**Q: Security?** A: PKCE for mobile. Refresh tokens for long access.\n\n**Q: Multi-provider?** A: Use federated identity (OIDC).",
        "calc": "- Token lifespan: 1 hour access, 30 day refresh\n- Token storage: Redis, ~1KB per token\n- 100M users, 50% active daily = 50M tokens = 50GB",
        "choices": [
            ["OAuth 2.0", "Industry standard, secure", "Complex spec"],
            ["Custom JWT", "Simple", "Reinventing security"],
            ["Session cookies", "Classic", "Stateful, scaling issues"]
        ]
    },
    "02_encryption_tls": {
        "arch": "Asymmetric (TLS handshake) → symmetric (data encryption) → hash (integrity).",
        "diagram": "Client-Server TLS 1.3:\n  Encrypted handshake\n  → symmetric key agreement\n  → encrypted data with AES-256",
        "qa": "**Q: Certificate pinning?** A: App trusts only specific cert. Prevents MITM.\n\n**Q: Key rotation?** A: Monthly for symmetric. Yearly for asymmetric typical.",
        "calc": "- TLS handshake: 1.5 RTTs (TLS 1.3)\n- Encryption overhead: ~5-10% CPU for AES-NI\n- 1M connections: ~100ms each handshake",
        "choices": [
            ["TLS 1.3", "Fast, secure", "Not universally supported yet"],
            ["TLS 1.2", "Mature", "Slower handshake"],
            ["Custom encryption", "Tailored", "Security risks"]
        ]
    },
    "03_access_control": {
        "arch": "RBAC: User → Role → Permissions. ABAC: attributes + conditions.",
        "diagram": "User [admin] → Role [can_delete, can_edit]\nAttribute: department=eng → can modify own repos",
        "qa": "**Q: RBAC vs ABAC?** A: RBAC simpler. ABAC more flexible but complex.\n\n**Q: Audit trail?** A: Log all permission changes and access.",
        "calc": "- Roles: 100, Permissions: 1000, Users: 1M\n- Lookup: O(1) with caching\n- Audit storage: 1B accesses × 100 bytes = 100GB/year",
        "choices": [
            ["RBAC", "Simple, scalable", "Inflexible"],
            ["ABAC", "Flexible", "Complex rules, slow evaluation"],
            ["Hybrid", "Balanced", "More complex to implement"]
        ]
    }
}

def enhance_concept(category, concept_id, content):
    """Enhance a single concept file."""
    filepath = f"{base_path}/{category}/{concept_id}.md"

    try:
        with open(filepath, 'r') as f:
            doc = f.read()

        # Replace sections
        doc = doc.replace(
            "Core Mechanism:\n- How this system works\n- Key components and interactions\n- Data flow and processing",
            content['arch']
        )

        doc = doc.replace(
            "[Visual system components and interactions]",
            content['diagram']
        )

        doc = doc.replace(
            "**Q: When to use this approach?**\nA: [Specific use cases and scenarios where this is beneficial]\n\n**Q: What are the key trade-offs?**\nA: [Pros and cons of this approach vs alternatives]\n\n**Q: How does this handle failures?**\nA: [Failure scenarios and recovery mechanisms]\n\n**Q: How to scale this?**\nA: [Scaling strategies and bottlenecks]",
            content['qa']
        )

        doc = doc.replace(
            "For typical distributed system scenario:\n- Performance metrics\n- Scalability limits\n- Resource requirements\n- Typical deployment sizes",
            content['calc']
        )

        table_rows = "\n".join([f"| {row[0]} | {row[1]} | {row[2]} |" for row in content['choices']])
        doc = doc.replace(
            "| Option A | [Advantages] | [Disadvantages] |\n| Option B | [Advantages] | [Disadvantages] |\n| Option C | [Advantages] | [Disadvantages] |",
            table_rows
        )

        with open(filepath, 'w') as f:
            f.write(doc)

        return True
    except Exception as e:
        print(f"Error: {filepath}: {str(e)}")
        return False

# Enhance all files
total = 0
for category_path in glob.glob(f"{base_path}/1[0-5]-*"):
    category = os.path.basename(category_path)

    for concept_file in glob.glob(f"{category_path}/*.md"):
        concept_id = os.path.basename(concept_file).replace(".md", "")

        for key, content in enhancements.items():
            if key in concept_id:
                if enhance_concept(category, concept_id, content):
                    total += 1
                    print(f"✓ Enhanced {category}/{concept_id}")
                break

print(f"\n✅ Enhanced {total} new concepts with detailed content")
