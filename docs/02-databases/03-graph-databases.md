# Graph Databases — Neo4j and Relationship Queries

Building systems optimized for relationships.

---

## 🔗 Graph Fundamentals

### Nodes & Relationships

```
Nodes: Entities (users, products, posts)
Relationships: Connections (follows, recommends, posted)

Example:
(Alice:User) --[FOLLOWS]--> (Bob:User)
(Alice:User) --[LIKES]--> (Post:Post) --[AUTHORED_BY]--> (Bob:User)
```

---

## 🎯 Use Cases

**Social Networks:** Friend connections, recommendations
**Knowledge Graphs:** Entities and relationships (Wikipedia, Google)
**Recommendations:** Path finding (people who liked this also liked...)
**Access Control:** Who has permissions to what

---

## 🔍 Graph Queries (Cypher)

### Basic Traversal

```cypher
-- Find Alice's friends
MATCH (alice:User {name: "Alice"}) -[:FOLLOWS]-> (friend:User)
RETURN friend;

-- Find friends of friends
MATCH (alice:User {name: "Alice"}) 
      -[:FOLLOWS]-> (friend1:User) 
      -[:FOLLOWS]-> (friend2:User)
RETURN friend2;

-- Shortest path between users
MATCH path = shortestPath(
  (alice:User {name: "Alice"}) -[*]- (bob:User {name: "Bob"})
)
RETURN path;
```

### Aggregation

```cypher
-- Count followers per user
MATCH (user:User) <-[:FOLLOWS]- (follower:User)
RETURN user.name, COUNT(follower) as follower_count;

-- Recommend products (similar buyers)
MATCH (user:User {id: 123}) -[:BOUGHT]-> (product)
MATCH (other:User) -[:BOUGHT]-> (product)
MATCH (other) -[:BOUGHT]-> (recommendation)
WHERE recommendation <> product
RETURN recommendation, COUNT(*) as score
ORDER BY score DESC
LIMIT 5;
```

---

## 📊 Performance Characteristics

**Strengths:**
- Relationship queries are fast (indexed)
- No JOIN overhead (relationships stored)
- Complex patterns easy to express

**Weaknesses:**
- Not good for aggregations (SUM, AVG)
- Complex filtering slower than relational
- Sharding difficult (relationships across shards)

---

## 🏛️ Design Patterns

### Hierarchies

```cypher
-- Organizational hierarchy
CREATE (ceo:Employee {name: "Alice"})
CREATE (director:Employee {name: "Bob"})
CREATE (manager:Employee {name: "Charlie"})

CREATE (ceo) -[:MANAGES]-> (director)
CREATE (director) -[:MANAGES]-> (manager)

-- Find all reports (recursive)
MATCH (ceo:Employee {name: "Alice"}) 
      -[:MANAGES*]-> (reports:Employee)
RETURN reports;
```

### Property Graphs

```cypher
-- Add properties to relationships
CREATE (alice:User {name: "Alice"})
CREATE (bob:User {name: "Bob"})
CREATE (alice) -[r:KNOWS {since: 2020, strength: 0.8}]-> (bob)
```

---

## ⚡ Index Strategies

```cypher
-- Index for fast lookups
CREATE INDEX ON :User(id);
CREATE INDEX ON :User(email);

-- Composite index (if supported)
CREATE INDEX ON :Order(user_id, date);
```

---

## ⚖️ Graph Databases vs. Relational

```
Feature          | Graph (Neo4j)    | Relational (PostgreSQL)
─────────────────|──────────────────|──────────────────────
Query: Friends   | O(1) traversal   | O(n) joins
Query: 2nd level | O(k) traversal   | O(n²) joins
Relationship ops | Native, fast     | Via joins
Complex patterns | Natural express  | Complex SQL
Aggregations     | Slower           | Optimized
Transactions     | Strong ACID      | Strong ACID
Scaling          | Single region    | Can be replicated

When Graph DB:
├─ Friend networks (Facebook, LinkedIn)
├─ Recommendation engines
├─ Social graphs (paths, communities)
├─ Knowledge graphs (semantic search)
├─ Access control (role hierarchies)
└─ Fraud detection (transaction patterns)

When Relational:
├─ Financial transactions
├─ OLAP analytics
├─ Multiple users with ACID
├─ Complex joins (3+ tables)
└─ Strong consistency required
```

---

## 🏗️ Graph Architecture Patterns

### Pattern 1: Social Network
```
(User) -[FOLLOWS]-> (User)
   |        |
   |        v
   +----> (Post)
          ^  |
          |  v
       (Comment) -[BY]-> (User)

Query: Find friends who liked my post
MATCH (me:User {id: 1})
      -[:FOLLOWS]->(friend:User)
      -[:LIKES]->(post:Post {author_id: 1})
RETURN friend, post;
```

### Pattern 2: Recommendation Engine
```
(User) -[BOUGHT]-> (Product)
  ^                    |
  |                    |
  +----[SIMILARITY]----+

Query: Products similar users bought
MATCH (user:User {id: 123}) -[:BOUGHT]-> (product1)
MATCH (similar:User) -[:BOUGHT]-> (product1)
MATCH (similar) -[:BOUGHT]-> (recommendation)
WHERE recommendation <> product1
RETURN recommendation, COUNT(*) as score ORDER BY score DESC;
```

### Pattern 3: Hierarchical Roles
```
(CEO) -[MANAGES]-> (VP) -[MANAGES]-> (Manager) -[MANAGES]-> (Employee)
                     ^                                             |
                     |___________    ____________[REPORTS_TO]_____|

Query: All reports under VP
MATCH (vp:Employee {title: "VP"}) -[:MANAGES*]-> (reports)
RETURN reports;
```

---

## 📊 Performance Characteristics

### Query Time Comparison
```
Query: "Find all friends of user 123 who also bought product 456"

PostgreSQL (with indexes):
├─ users → user_id=123
├─ user_friends → user_id=123  (JOIN)
├─ purchase_history → product_id=456 (JOIN)
├─ Execution: Multiple JOINs on large tables
└─ Time: 1000ms

Neo4j (Graph):
├─ User node → index lookup O(log n)
├─ FOLLOWS relationships → direct access O(k) where k=friend count
├─ BOUGHT relationships → direct access O(m)
├─ Execution: Pure traversal
└─ Time: 10ms (100x faster!)
```

### Scaling Characteristics
```
        Nodes/Rels
↑
│                PostgreSQL (joins slow down)
│              ╱
│           ╱
│        ╱       Neo4j (constant traversal time)
│      ╱
│    ╱────────────────────────────────
│ ╱
└────────────────────────────→ Million/Billion
```

---

## 🔍 Index Strategies

### Node Indexes
```cypher
-- Fast lookups on node properties
CREATE INDEX idx_user_id ON :User(id);
CREATE INDEX idx_user_email ON :User(email);

-- Query plan: Uses index
EXPLAIN MATCH (u:User {email: "alice@example.com"}) RETURN u;
```

### Relationship Indexes
```cypher
-- Index outgoing relationships (less common)
CREATE INDEX ON :KNOWS(since);

-- Query with relationship property
MATCH (user:User) -[r:KNOWS {since: 2020}]-> (friend)
RETURN user, friend;
```

### Compound Indexes
```cypher
-- Not directly supported in Neo4j, but:
-- Create combined node property
CREATE (u:User {id: 1, email_domain: "example.com"})
CREATE INDEX ON :User(email_domain);

-- Query uses index on domain
MATCH (u:User {email_domain: "example.com"})
WHERE u.email CONTAINS "alice"
RETURN u;
```

---

## ❓ Comprehensive Interview Q&A

**Q: Design graph database for LinkedIn (500M users)**

A:
```
Data Model:
Nodes:
├─ User (500M) properties: id, name, email, profile_url
├─ Company (5M) properties: id, name, industry
├─ School (1M) properties: id, name
├─ Skill (50K) properties: skill_name
└─ Post (10B) properties: id, content, timestamp

Relationships:
├─ User -[FOLLOWS]-> User (user follows another)
├─ User -[WORKS_AT]-> Company {start_date, end_date}
├─ User -[STUDIED_AT]-> School {graduation_year}
├─ User -[HAS_SKILL]-> Skill {endorsements}
├─ User -[AUTHORED]-> Post
├─ Post -[LIKED_BY]-> User
└─ Post -[COMMENTED_ON_BY]-> User

Indexes:
CREATE INDEX idx_user_id ON :User(id);
CREATE INDEX idx_user_email ON :User(email);
CREATE INDEX idx_post_timestamp ON :Post(timestamp);
CREATE INDEX idx_company_id ON :Company(id);

Key Queries:
1. User's feed (posts from followers):
   MATCH (user:User {id: 123})
   -[:FOLLOWS]->(follower:User)
   -[:AUTHORED]->(post:Post)
   RETURN post ORDER BY post.timestamp DESC LIMIT 10;

2. People you may know:
   MATCH (user:User {id: 123})
   -[:FOLLOWS]->(friend:User)
   -[:FOLLOWS]->(connection:User)
   WHERE NOT (user)-[:FOLLOWS]->(connection)
   RETURN connection, COUNT(*) as mutual_friends
   ORDER BY mutual_friends DESC LIMIT 10;

3. Skill-based search:
   MATCH (user:User)-[r:HAS_SKILL]->(skill:Skill {skill_name: "Python"})
   WHERE r.endorsements > 10
   RETURN user ORDER BY r.endorsements DESC LIMIT 20;

Scaling Strategy:
├─ Sharding by user_id (each shard has subgraph)
├─ Cache hot paths (your feed, recommendations)
├─ Async updates (endorsements, skill changes)
└─ Analytics cluster (separate for reporting)
```

**Q: Find mutual friends between user1 and user2**

A:
```cypher
-- Direct mutual friends (both follow each other)
MATCH (user1:User {id: 1})
-[:FOLLOWS]->(mutual:User)
<-[:FOLLOWS]-(user2:User {id: 2})
RETURN mutual;

-- Mutual connections (both follow common user, but not each other)
MATCH (user1:User {id: 1})
-[:FOLLOWS]->(connection:User)
<-[:FOLLOWS]-(user2:User {id: 2})
WHERE NOT (user1)-[:FOLLOWS]->(user2)
RETURN connection, COUNT(*) as shared_connections
ORDER BY shared_connections DESC;

-- All paths between users (degrees of separation)
MATCH path = shortestPath(
  (user1:User {id: 1})
  -[:FOLLOWS*]-(user2:User {id: 2})
)
RETURN path, LENGTH(path) as degrees;

Performance:
├─ Direct mutual: O(k) where k = avg followers
├─ Path finding: O(2^depth) worst case
└─ Optimization: Use apoc.algo.shortestPath (bidirectional)
```

**Q: Recommendation engine: "People who bought X also bought Y"**

A:
```cypher
-- Find products
MATCH (target_user:User {id: 123})
-[:BOUGHT]->(product:Product)
-[:SIMILAR_TO]->(recommendation:Product)
RETURN recommendation, COUNT(*) as score
ORDER BY score DESC LIMIT 5;

-- Alternative (collaborative filtering)
MATCH (target_user:User {id: 123})
-[:BOUGHT]->(product:Product)
<-[:BOUGHT]-(similar_user:User)
-[:BOUGHT]->(recommendation:Product)
WHERE recommendation <> product
RETURN recommendation, COUNT(*) as similar_users
ORDER BY similar_users DESC
LIMIT 5;

Optimization:
├─ Pre-compute similarity edges (batch job)
├─ Cache popular recommendations
├─ Use apoc.algo.cosineDistance for scoring
└─ Partition by user segment for faster traversal
```

**Q: Why graph DB better for recommendations than SQL?**

A:
```
SQL approach:
SELECT r.product_id, COUNT(*) as score
FROM users u1
JOIN purchases p1 ON u1.id = p1.user_id
JOIN purchases p2 ON p1.product_id = p2.product_id
JOIN users u2 ON p2.user_id = u2.id
JOIN purchases p3 ON u2.id = p3.user_id
JOIN products r ON p3.product_id = r.id
WHERE u1.id = 123
AND r.product_id != p1.product_id
GROUP BY r.product_id
ORDER BY score DESC;

Issues:
├─ Multiple JOINs (expensive)
├─ Large intermediate results
├─ Difficult to understand
└─ Hard to add more hops (friends of friends)

Graph approach:
MATCH (user:User {id: 123})
-[:BOUGHT]->(product)
<-[:BOUGHT]-(similar_user)
-[:BOUGHT]->(recommendation)
RETURN recommendation, COUNT(*) as score
ORDER BY score DESC;

Benefits:
├─ Clear intent (human-readable)
├─ Native relationship support
├─ Easy to extend (add more hops)
├─ Relationship traversal O(k) not O(n²)
└─ Can add weights to relationships
```

**Q: Design fraud detection using graph**

A:
```
Data Model:
Nodes:
├─ Account
├─ Transaction
├─ Device (IP, browser fingerprint)
├─ Merchant

Relationships:
├─ Account -[INITIATED]-> Transaction
├─ Transaction -[FROM_DEVICE]-> Device
├─ Device -[USED_BY]-> Account
├─ Account -[MERCHANT]-> Merchant

Patterns indicating fraud:
1. Device jumping (same device, different countries in short time):
   MATCH (a1:Account)-[:INITIATED]->(t1:Transaction)-[:FROM_DEVICE]->(d:Device)
   MATCH (a2:Account)-[:INITIATED]->(t2:Transaction)-[:FROM_DEVICE]->(d)
   WHERE a1 <> a2 AND t1.timestamp < t2.timestamp < t1.timestamp + 3600
   AND distance(t1.location, t2.location) > 1000km
   RETURN a1, a2, d as suspicious_device;

2. Money mule pattern (account receives money, immediately sends):
   MATCH (a:Account)-[:RECEIVES]->(t1:Transaction)
   MATCH (a)-[:INITIATES]->(t2:Transaction)
   WHERE t1.timestamp < t2.timestamp < t1.timestamp + 600
   AND t1.amount > 1000
   RETURN a as suspicious_account;

3. Structuring (multiple small transactions from same device):
   MATCH (d:Device)<-[:FROM_DEVICE]-(t:Transaction)-[:INITIATED_BY]->(a:Account)
   WHERE t.timestamp > now() - duration("P1D")
   AND t.amount < 10000
   WITH a, COUNT(*) as tx_count, SUM(t.amount) as total_amount
   WHERE tx_count > 5 AND total_amount > 50000
   RETURN a, tx_count, total_amount as suspicious_structuring;
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Design graph DB" → Do you understand nodes, relationships, indexes?
- "Find mutual friends" → Do you know traversal depth, N+1 problem?
- "Why graph over SQL" → Do you understand join complexity?
- "Fraud detection" → Do you recognize anomaly patterns?

**How to answer:**
1. **Clarify:** Relationship types, traversal depth, expected scale
2. **Model:** Nodes first, then relationships
3. **Query:** Show Cypher with EXPLAIN plans
4. **Scale:** Discuss sharding, caching, performance
5. **Optimize:** Indexes, relationship direction (outgoing for traversals)

---

**Last updated:** 2026-05-22
