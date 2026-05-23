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

## ❓ Interview Q&A

**Q: MongoDB vs. PostgreSQL, when use each?**
A: MongoDB: Flexible schema, scale horizontally, rapid iteration. PostgreSQL: Strong consistency, complex queries, ACID.

**Q: Design DynamoDB schema for user activity**
A: Partition Key: user_id. Sort Key: timestamp. GSI for reverse lookups (activity_id → user).

**Q: Handle 1B documents, design sharding**
A: Shard by user_id (or another high-cardinality field). Monitor hotspots. Use consistent hashing if rebalancing needed.

---

**Last updated:** 2026-05-22
