# NoSQL Comprehensive Guide — MongoDB, DynamoDB, and Beyond

Building scalable document and key-value systems.

---

## 📄 Document Databases (MongoDB)

### Data Model

```javascript
// Document = JSON-like object
{
  _id: ObjectId("..."),
  name: "Alice",
  email: "alice@example.com",
  orders: [
    { id: 1, total: 50, date: ISODate("2024-01-15") },
    { id: 2, total: 30, date: ISODate("2024-01-20") }
  ],
  address: {
    street: "123 Main St",
    city: "NYC",
    zip: "10001"
  }
}
```

**Pros:**
- Flexible schema (evolve over time)
- Nested data (no joins needed)
- Array support (embedded one-to-many)

**Cons:**
- Larger document size (duplication)
- No ACID across documents (MongoDB 4.0+ supports)
- Indexing harder (nested fields)

---

### Indexing Strategies

```javascript
// Simple index
db.users.createIndex({ email: 1 });

// Compound index (for AND queries)
db.orders.createIndex({ user_id: 1, date: -1 });

// Partial index (subset of documents)
db.users.createIndex({ email: 1 }, { sparse: true });

// Text index (full-text search)
db.articles.createIndex({ content: "text" });
```

---

### Aggregation Pipeline

```javascript
// Complex data processing
db.orders.aggregate([
  { $match: { user_id: 123 } },          // Filter
  { $group: { _id: "$user_id", total: { $sum: "$amount" } } },  // Group
  { $sort: { total: -1 } },              // Sort
  { $limit: 10 }                         // Limit
]);
```

---

## 🔑 Key-Value Databases (DynamoDB)

### Table Design

```
Table: Orders
Partition Key: user_id
Sort Key: order_date

Access pattern:
- Get all orders for user_id: Fast (partition key)
- Get orders in date range: Fast (sort key range)
```

**Single table design:**
```
GSI (Global Secondary Index):
Partition Key: order_id
Sort Key: user_id

Enables: Get orders by order_id
```

---

### Consistency Models

**Strong Consistency:** Read latest (slower)
**Eventual Consistency:** May be stale (faster)

```javascript
// DynamoDB read
const result = await dynamodb.get({
  TableName: 'Orders',
  Key: { user_id: '123', order_date: '2024-01-15' },
  ConsistentRead: true  // Strong consistency
});
```

---

## 🌍 Horizontal Scaling

### Sharding Strategy

```
User IDs: 1-1000000
Shard by user_id % 10:

Shard 0: users 0, 10, 20, ...
Shard 1: users 1, 11, 21, ...
...
Shard 9: users 9, 19, 29, ...

Each shard: separate database instance
```

**Challenges:**
- Hotspots (some shards busier)
- Rebalancing (when add shards)
- Cross-shard queries (slow)

### Replication

```
Primary: Handles writes
Replica 1: Read-only copy
Replica 2: Read-only copy

Write: Primary only
Read: Primary or any replica

If primary fails: Promote replica
```

---

## 🔄 Consistency Models

### Eventual Consistency

```
Write to primary → Returns immediately
Replicates to secondaries → 100ms delay

Risk: Read from secondary gets stale data
Solution: Read from primary for critical data
```

### Read Your Writes Consistency

```
After writing, subsequent reads see your write
Application tracks write version
```

---

## 💾 Transactions

**MongoDB 4.0+:** Multi-document transactions
```javascript
const session = db.getMongo().startSession();
session.startTransaction();
try {
  db.users.updateOne({ _id: 1 }, { $set: { balance: balance - 100 } }, { session });
  db.users.updateOne({ _id: 2 }, { $set: { balance: balance + 100 } }, { session });
  session.commitTransaction();
} catch (error) {
  session.abortTransaction();
}
```

**DynamoDB:** Single-item transactions

---

## ⚖️ MongoDB vs. PostgreSQL Trade-offs

```
                 PostgreSQL          MongoDB
                 ──────────────────────────────────
Schema           Rigid               Flexible
Transactions     Strong ACID         Multi-doc (v4.0+)
Consistency      Immediate           Eventual (default)
Scaling          Vertical            Horizontal
Joins            Required            Not needed (embedded)
Normalization    Yes (3NF)           No (denormalized)
Complexity       Higher              Lower
Analytics        Better (joins)      Worse (aggregation pipeline)

When PostgreSQL:
├─ Complex relationships between data
├─ Strong consistency required
├─ ACID transactions critical
├─ Data correctness > scale
└─ Structured data (financial, healthcare)

When MongoDB:
├─ Rapid iteration (schema changes)
├─ Flexible document structure
├─ Scale to billions of documents
├─ High write throughput needed
└─ JSON-like data (logs, events)
```

---

## 🏗️ Document Design Patterns

### Pattern 1: Embedding (One-to-Few)
```javascript
// Good for: Static relationships
// Example: User with orders (10-100 orders max)

db.users.insertOne({
  _id: 1,
  name: "Alice",
  email: "alice@example.com",
  orders: [
    { order_id: 101, total: 50, date: ISODate("2024-01-15") },
    { order_id: 102, total: 30, date: ISODate("2024-01-20") }
  ]
});

// Query: Get user with all orders
db.users.findOne({ _id: 1 });

// Trade-off:
// ✓ Single query to get user + orders
// ✗ Document grows as orders added
// ✗ Hard to query across users
```

### Pattern 2: Referencing (One-to-Many)
```javascript
// Good for: Growing relationships
// Example: User with thousands of orders

db.users.insertOne({
  _id: 1,
  name: "Alice",
  email: "alice@example.com"
});

db.orders.insertOne({
  _id: 101,
  user_id: 1,
  total: 50,
  date: ISODate("2024-01-15")
});

// Query: Get user and their orders
db.users.findOne({ _id: 1 });  // Get user
db.orders.find({ user_id: 1 }); // Get orders (2 queries, needs join logic)

// Trade-off:
// ✓ Flexible (orders grow independently)
// ✗ Requires 2 queries (N+1 problem)
// ✗ No join support (app-level joining)
```

### Pattern 3: Hybrid (Embedding + Referencing)
```javascript
// Good for: Balancing performance and flexibility

db.users.insertOne({
  _id: 1,
  name: "Alice",
  order_summary: {
    total_spent: 1000,
    total_orders: 25,
    last_order_date: ISODate("2024-01-20")
  }
});

db.orders.find({ user_id: 1 });  // Get full orders

// Trade-off:
// ✓ Denormalized summary for fast access
// ✓ Full details in separate collection
// ✗ Must keep summary and orders in sync
```

---

## 🔑 DynamoDB Design Deep Dive

### Access Pattern Modeling
```
Use Case: User activity tracking

Requirement:
- Get all activities for user (user_id, date range)
- Get activity by activity_id
- Get activity summary by date

Schema Design:

Table: Activity
PK: user_id
SK: activity_id#timestamp

GSI 1 (for date-based queries):
PK: date
SK: user_id#activity_id

GSI 2 (activity lookup):
PK: activity_id
SK: timestamp

Query patterns:
1. Get activities for user on date:
   user_id = '123' AND activity_id BEGINS_WITH 'ACT#2024-01-15'

2. Get by activity_id:
   Query GSI 2: activity_id = 'ACT456'

3. Get by date:
   Query GSI 1: date = '2024-01-15'
```

### Hot Partition Problem
```
Design Issue:
Activity: user_id = 'system' (all events go here)
└─ All writes to same partition
└─ Throttling if > 40KB/sec

Solutions:
1. Partition key: random_id + ':' + user_id
   Access: Query with random_id values (0-9)

2. Write sharding: user_id + '#' + (timestamp % 10)
   Access: Query all 10 partitions

3. DynamoDB Streams + Lambda:
   Write to fast table, distribute via Lambda

Best: Partition key with high cardinality
```

---

## 📊 Consistency Models Comparison

```
System                Read Your Writes    Monotonic Reads    Transaction
──────────────────────────────────────────────────────────────────────
PostgreSQL            ✓ Strong           ✓ Strong           ✓ Multi-document
MongoDB               ✗ Eventual default ✗ Eventual default ✓ Multi-doc (v4.0+)
DynamoDB              ✓ If strong read   ✗ Eventual copy    ✗ Single item only
Cassandra             ✗ Eventual         ✗ Eventual         ✗ Single row only
Elasticsearch         ✗ Eventual         ✗ Eventual         ✗ No transactions

Legend:
✓ Supported, ✗ Not supported (default behavior)

Trade-off visualization:
Consistency ←──────────────────→ Availability
PostgreSQL    ←─ Strong ─→    High ✓
MongoDB       ← Eventual → High ✓
DynamoDB      ← Tunable → High ✓
Cassandra     → Eventual ← Very High ✓
```

---

## 🌍 Sharding Strategies Comparison

```
Strategy 1: Range-Based Sharding
├─ Shard Key: user_id
├─ Shard 0: user_id 0-999999
├─ Shard 1: user_id 1000000-1999999
├─ Shard 2: user_id 2000000-2999999
├─ Pros: Simple, sequential access fast
└─ Cons: Hot spots (uneven distribution)

Strategy 2: Hash-Based Sharding
├─ Shard Key: hash(user_id) % 10
├─ Shard 0: users 0, 10, 20, ...
├─ Shard 1: users 1, 11, 21, ...
├─ Pros: Even distribution, balanced
└─ Cons: Range queries require all shards

Strategy 3: Directory-Based Sharding
├─ Lookup table: user_id → shard_id
├─ All queries: Find shard first, then query
├─ Pros: Flexible, rebalancing easy
└─ Cons: Extra lookup overhead, SPOF

Strategy 4: Consistent Hashing (Ring)
├─ Nodes arranged in hash ring (0-360°)
├─ New node: rebalance only ~1/N data
├─ Pros: Minimal rebalancing on add/remove
└─ Cons: Complex to implement, hot spots possible
```

---

## 💾 Transaction Support Comparison

```
Database    Single Item    Multi-Item    Atomicity    Rollback
────────────────────────────────────────────────────────────────
PostgreSQL  ✓✓ Fast       ✓✓ Full       ✓ Full       ✓ Yes
MongoDB     ✓✓ Fast       ✓ Limited     ✓ Full       ✓ Yes
DynamoDB    ✓ Supported   ✗ No          ✗ Single     ✗ No
Cassandra   ✓ Supported   ✗ No          ✗ None       ✗ No
Redis       ✓✓ Fast       ✓ Limited     ✓ Full       ✓ Yes (MULTI/EXEC)

Multi-Item Transaction Pattern (Saga):
Step 1: Deduct from account A (MongoDB update)
Step 2: Add to account B (MongoDB update)
If step 2 fails: Compensate step 1 (deduct back)
```

---

## ❓ Comprehensive Interview Q&A

**Q: MongoDB vs. PostgreSQL, when use each?**

A:
```
PostgreSQL when:
✓ Complex joins (multiple tables)
✓ Strong ACID needed (financial)
✓ Schema is stable
✓ You need transaction guarantees
✓ Analytics/reporting (better for joins)

MongoDB when:
✓ Schema evolves rapidly
✓ Document structure varies
✓ Scale to billions (horizontal)
✓ High write throughput
✓ JSON-like data (logs, events)
✓ Rapid prototyping

Example decision:
→ Banking: PostgreSQL (ACID, accuracy)
→ User events: MongoDB (scale, flexibility)
→ E-commerce: Both (Orders in PostgreSQL, activity in MongoDB)
```

**Q: Design DynamoDB schema for user activity (100M events/day)**

A:
```
Requirements:
- Get user activities in date range (most common)
- Get activity by activity_id (less common)
- Aggregate by date for dashboard

Schema:

Table: UserActivity
├─ PK (Partition): user_id
├─ SK (Sort): date#activity_id
├─ Data: event_type, timestamp, details
├─ TTL: 90 days (auto-delete old data)

Global Secondary Index 1 (Date queries):
├─ PK: date
├─ SK: user_id#activity_id

Global Secondary Index 2 (Activity lookup):
├─ PK: activity_id
├─ SK: timestamp

Query Examples:
1. Get user activities on specific date (most common):
   Query PK=user_id, SK BETWEEN 'date#' AND 'date#Z'
   
2. Get by activity_id:
   Query GSI2 with activity_id
   
3. Get activity summary (pre-aggregated):
   Use Lambda on DynamoDB Streams to update 
   ActivitySummary table as events come in

Capacity:
- Read: 100M events = 1.15M writes/sec (peak)
- Setup: On-demand or auto-scaling
```

**Q: Design MongoDB for 1B documents, handle sharding**

A:
```
Schema:
db.orders.insertOne({
  _id: ObjectId(),
  user_id: 1000,
  product_id: 5000,
  order_date: ISODate("2024-01-15"),
  total: 100,
  items: [...]
});

Sharding Key: user_id (high cardinality)
└─ Cardinality: Billions of unique values ✓
└─ Even distribution: Yes (large range) ✓
└─ Monotonic: No (but acceptable) ✓

Shard Cluster:
├─ Config Servers (3): Metadata, consistent
├─ Shard 0: user_id 0-1M (200M docs)
├─ Shard 1: user_id 1M-2M (200M docs)
├─ Shard 2: user_id 2M-3M (200M docs)
├─ Shard 3: user_id 3M-4M (200M docs)
├─ Shard 4: user_id 4M-5B (300M docs)
└─ Mongos (Router): Directs queries to correct shard

Handling hot spots:
1. Monitor distribution: sh.status()
2. If uneven: Split chunks, rebalance
3. Alternative: Compound key user_id + product_id

Writes/performance:
- 100K writes/sec per shard = 500K total
- Replication: Each shard has replica (3 total)
- All shards write in parallel → linear scaling
```

**Q: Handle failures in distributed database**

A:
```
Scenario 1: Replica fails
├─ Replication lag detected
├─ Primary continues serving
├─ Replica rebuilt from primary
├─ No user impact (read replicas have backups)

Scenario 2: Primary fails
├─ Heartbeat missed
├─ Replica promoted to primary
├─ Writes now go to new primary
├─ Recovery Time: ~10-30 seconds
├─ Data loss: None (replicated before write ack)

Scenario 3: Network partition
├─ DynamoDB: Uses quorum, continues serving
├─ MongoDB: May elect new primary
├─ PostgreSQL: Stops writes (prevent split-brain)
├─ Strategy: Prefer availability (CRDT) or consistency (2PC)

Scenario 4: Data corruption
├─ Backup recovery
├─ Point-in-time restore
├─ Consider: pg_filedump, mongodump for analysis
```

**Q: When to use embedding vs. referencing in MongoDB?**

A:
```
Embedding (Embed the related document):
✓ When: One-to-few relationships
✓ When: Static data (won't change often)
✓ When: Frequently access together
✓ Size: Document < 16MB MongoDB limit
✗ Not when: Relationship grows unbounded

Example: User + Settings (user has 1-3 settings)
db.users.insertOne({
  _id: 1,
  name: "Alice",
  settings: { theme: "dark", language: "en" }
});

Referencing (Store ID reference):
✓ When: One-to-many relationships
✓ When: Data grows unbounded
✓ When: Data updated independently
✓ Size: Document would exceed 16MB
✗ Not when: Always need both together

Example: User + Orders (user has thousands)
db.users.insertOne({ _id: 1, name: "Alice" });
db.orders.insertOne({ _id: 101, user_id: 1, total: 100 });

Decision tree:
├─ Do you always need both together?
│  ├─ Yes: Embedding (if size permits)
│  └─ No: Referencing
├─ Size check:
│  ├─ < 16MB with all related data: Embedding possible
│  └─ > 16MB or unbounded growth: Referencing
└─ Query pattern:
   ├─ Mostly together: Embedding
   └─ Separate queries: Referencing
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Design MongoDB schema" → Do you understand embedding vs. referencing?
- "Handle 1B documents" → Do you know sharding, partition keys, cardinality?
- "Consistency models" → Do you balance consistency vs. availability?
- "Failures" → Do you understand replication, quorum, failover?

**How to answer:**
1. **Clarify requirements:** Read/write ratio, consistency needs, scale
2. **Simple design first:** Single table, no sharding
3. **Add sharding:** If > 1 million documents
4. **Handle failures:** Replication, quorum, monitoring
5. **Optimize:** Indexing, caching, denormalization

---

**Last updated:** 2026-05-22
