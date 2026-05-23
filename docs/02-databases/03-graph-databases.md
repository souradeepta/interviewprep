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

## ❓ Interview Q&A

**Q: Design graph DB for LinkedIn (people connections)**
A: Nodes: User, Company, Post. Relationships: FOLLOWS, WORKS_AT, AUTHORED. Indexes on user_id.

**Q: Find mutual friends between users**
```cypher
MATCH (user1:User {id: 1}) -[:FOLLOWS]-> (mutual) <-[:FOLLOWS]- (user2:User {id: 2})
RETURN mutual;
```

**Q: Why graphs are better for recommendations than relational**
A: No joins needed. Traversals are fast. Complex patterns express naturally. Relationship queries are core strength.

---

**Last updated:** 2026-05-22
