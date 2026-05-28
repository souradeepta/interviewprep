# Indexing Deep Dive

**Level:** L4-L5
**Time to read:** ~30 min

Master index data structures and design optimal indexes for fast lookups, range queries, and analytics.

---

## ⚖️ Index Type Trade-offs

### Index Structure Comparison

| Index Type | Lookup | Range | Scan | Memory | Updates | Best For |
|-----------|--------|-------|------|--------|---------|----------|
| **B-tree** | O(log n) | O(log n + k) | Slow | Medium | Fast | General purpose |
| **Hash** | O(1) | No | No | Medium | Medium | Exact lookups |
| **LSM** | O(log n) | O(log n + k) | Fast | Low | Very fast | Write-heavy |
| **Bitmap** | N/A | N/A | Fast | Low | Slow | Boolean columns |
| **Inverted** | N/A | N/A | Fast | Low | Slow | Full-text search |

### When to Use Each

```
B-tree (PostgreSQL, MySQL):
  ├─ Most queries (lookups, ranges)
  ├─ Balanced read/write workload
  └─ Default choice

Hash (Redis, Memcached):
  ├─ Key-value stores (exact lookups)
  ├─ Fast point queries
  └─ No range queries needed

LSM (RocksDB, Cassandra):
  ├─ Write-heavy workloads
  ├─ Time-series data
  └─ Fast sequential writes

Bitmap (Data warehouses):
  ├─ Low cardinality columns (status, type)
  ├─ Aggregation queries
  └─ Analytical queries
```

---

## 🏗️ Index Data Structures

### B-tree (Balanced Tree)

```
                    [50]
                   /    \
              [25]        [75]
             /    \      /    \
           [10]  [30]  [60]  [85]
          /  \   / \   /  \   / \
        [5][15][27][35][55][65][80][90]

Properties:
  - All leaves at same depth
  - Balanced: log(n) height
  - Range queries work (in order)
  - Updates maintain balance (expensive)

Operations:
  - Search: O(log n)
  - Insert: O(log n)
  - Range query: O(log n + k)
```

### Hash Index

```
Hash Table:
  
  user_id → hash → bucket → [data]
  
  123 → hash → 5 → [user_record]
  456 → hash → 2 → [user_record]
  789 → hash → 5 → [user_record] (collision)

Properties:
  - Exact lookups: O(1)
  - No range queries (unordered)
  - Good for point queries
  - Bad for <, >, BETWEEN

Operations:
  - Search: O(1) average
  - Insert: O(1) average
  - Range query: Not possible
```

### LSM Tree (Log-Structured Merge)

```
Writes come here first:
  
  MemTable (in-memory) [0-100MB]
  When full, flush to disk:
    ↓
  L0 (newer) [100MB SSTables]
    ↓ (background compaction)
  L1 [10GB]
    ↓
  L2 [100GB]

Properties:
  - Fast sequential writes
  - Reads check multiple levels
  - Background compaction merges levels
  - Great for write-heavy workloads
```

---

## 📊 Index Design Patterns

### Pattern 1: Single Column Index

```sql
-- Query: WHERE user_id = 123
CREATE INDEX idx_user_id ON users(user_id);

B-tree on user_id:
  [50]
  /  \
[25] [75]

Lookup: 123 → traverse tree → O(log n)
```

### Pattern 2: Composite Index

```sql
-- Query: WHERE status = 'active' AND country = 'US' AND age > 18
CREATE INDEX idx_composite ON users(status, country, age);

Tree structure groups by:
  ├─ active
  │   ├─ US
  │   │   ├─ age 18-25
  │   │   ├─ age 25-40
  │   │   └─ age 40+
  │   └─ CA
  └─ inactive

Search:
  1. Find 'active' (fast, first key)
  2. Find 'US' (fast, second key)
  3. Find age > 18 (range scan)
  
Time: O(log n + k) where k = matching records
```

### Pattern 3: Covering Index

```sql
-- Query: SELECT user_id, email FROM users WHERE status = 'active'
CREATE INDEX idx_covering ON users(status) INCLUDE (user_id, email);

Without covering:
  ├─ Index lookup: Find 'active' (100K matches)
  ├─ Table lookup: 100K random disk reads (slow!)
  └─ Total: 500ms

With covering:
  ├─ Index lookup: Find 'active' (100K matches)
  ├─ Index contains (user_id, email) - no table access!
  └─ Total: 50ms (10x faster)
```

### Pattern 4: Partial Index

```sql
-- Query: SELECT * FROM users WHERE status = 'active' AND created_at > now() - interval 1 year
-- Only 10% of users are active AND recent

CREATE INDEX idx_active_recent ON users(status, created_at)
WHERE status = 'active' AND created_at > now() - interval 1 year;

Benefits:
  ├─ Smaller index (10% of data)
  ├─ Faster to maintain
  ├─ Fits in memory
  └─ Cost: Saves 90% of index space
```

---

## ❓ Interview Q&A

**Q1: Index created but query still slow - why?**

A:
- Check if index is actually used:
  1. Run EXPLAIN ANALYZE
  2. If Seq Scan instead of Index Scan → index not used
  
- Why not used?
  1. Query uses function: WHERE YEAR(date) = 2024
     → Change to range: WHERE date >= '2024-01-01'
  
  2. Wrong index type: Need composite index (col1, col2)
     → But index is (col2, col1)
  
  3. Index selectivity poor: All rows are status = 'active'
     → Index doesn't help, seq scan cheaper
  
  4. Optimizer chose seq scan: Table small, seq scan = index scan
     → Add FORCE INDEX hint if needed

**Q2: Composite index - what order for columns?**

A:
- Order matters! Example: WHERE status = 'active' AND created_date > '2024-01-01'
  
  Option 1: CREATE INDEX (status, created_date)
  - Filter by status first (equality)
  - Then range scan created_date
  - Good: Uses both columns
  
  Option 2: CREATE INDEX (created_date, status)
  - Inefficient: Can't use created_date for range after equality
  
- Rule: Equality columns first, then range columns
  - status = X (equality first)
  - date > Y (range second)

**Q3: Index consumes 500GB of storage - how to reduce?**

A:
- Current: One index per query
  
- Optimization strategies:
  1. Consolidate indexes:
     - Have 10 similar indexes? Combine with 1 composite
     - Each index adds 50GB → Combine 10 = 50GB instead of 500GB
  
  2. Partial index:
     - Only index recent data: WHERE created_at > now() - interval 1 year
     - 90% of queries use recent data
     - Saves 90% space
  
  3. Drop unused indexes:
     - Find indexes with 0 reads
     - Monitor with pg_stat_user_indexes
     - Drop if not used in 1 month
  
  4. Compression:
     - Use different column order to improve compression
     - Compress index pages

**Q4: Write latency increased 50% after adding index - solution?**

A:
- Problem: Every write updates all indexes
  ```
  1 INSERT → Update table + 5 indexes = 5x slower
  ```
  
- Solutions:
  1. Drop unused indexes:
     - Do all 5 indexes help queries?
     - If only 3 are used, drop 2 indexes
  
  2. Batch writes:
     - INSERT 1000 rows → Update indexes once
     - Faster than 1000 individual inserts
  
  3. Async index updates (if supported):
     - Update index in background
     - Query sees stale index temporarily
  
  4. Use LSM tree:
     - RocksDB has fast writes
     - Trade: Reads slower (check multiple levels)

**Q5: Full table scan vs. index - when to use each?**

A:
- Full table scan faster if:
  - Querying 50%+ of rows: Sequential read > random index lookup
  - Index selectivity poor: Matches many rows anyway
  - Small table (< 1M rows): Fits in memory
  
- Index faster if:
  - Querying < 10% of rows
  - Index is selective
  - Large table (> 100M rows)
  
- Example: Status = 'active' (90% of users)
  - Index lookup 90% of rows
  - Sequential scan also reads 90% of rows
  - Seq scan may be faster (no random I/O)
  
  → Optimizer may choose seq scan correctly

---

## 🧪 Practical Exercises

### Exercise 1: B-tree Index Operations (Easy)

**Problem:** Implement B-tree operations (insert, search, range query).

**Solution:**

```python
class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf
    
    def search(self, key):
        """Search for key in subtree"""
        i = 0
        while i < len(self.keys) and key > self.keys[i]:
            i += 1
        
        if i < len(self.keys) and key == self.keys[i]:
            return True
        
        if self.leaf:
            return False
        
        return self.children[i].search(key)

class BTree:
    def __init__(self, degree=3):
        self.root = BTreeNode()
        self.degree = degree  # Max keys = 2*degree - 1
    
    def insert(self, key):
        """Insert key into B-tree"""
        if len(self.root.keys) >= 2 * self.degree - 1:
            self._split_root()
        
        self._insert_non_full(self.root, key)
    
    def _insert_non_full(self, node, key):
        """Insert into non-full node"""
        i = len(node.keys) - 1
        
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if len(node.children[i].keys) >= 2 * self.degree - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key)
    
    def search(self, key):
        """Search for key"""
        return self._search_helper(self.root, key)
    
    def _search_helper(self, node, key):
        """Helper to search"""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            return True
        
        if node.leaf:
            return False
        
        return self._search_helper(node.children[i], key)
    
    def range_query(self, min_key, max_key):
        """Find all keys in range [min_key, max_key]"""
        result = []
        self._range_helper(self.root, min_key, max_key, result)
        return sorted(result)
    
    def _range_helper(self, node, min_key, max_key, result):
        """Helper for range query"""
        i = 0
        while i < len(node.keys):
            if node.keys[i] >= min_key:
                break
            i += 1
        
        while i < len(node.keys) and node.keys[i] <= max_key:
            if node.keys[i] >= min_key:
                result.append(node.keys[i])
            i += 1
        
        if not node.leaf:
            for child in node.children:
                self._range_helper(child, min_key, max_key, result)

# Test
btree = BTree(degree=3)

# Insert values
for key in [10, 20, 5, 6, 12, 30, 7, 17]:
    btree.insert(key)

print("Inserted: 10, 20, 5, 6, 12, 30, 7, 17")

# Search
print(f"\nSearch 12: {btree.search(12)}")
print(f"Search 25: {btree.search(25)}")

# Range query
result = btree.range_query(5, 20)
print(f"\nRange [5, 20]: {result}")
```

---

### Exercise 2: Index Selection for Multiple Queries (Medium)

**Problem:** Database has 5 queries. Design minimal indexes to cover all.

**Solution:**

```python
class IndexPlanner:
    def __init__(self, table_name):
        self.table = table_name
        self.queries = []
        self.indexes = []
    
    def add_query(self, query_id, where_columns, select_columns):
        """Add query to plan"""
        self.queries.append({
            'id': query_id,
            'where': where_columns,  # ORDER matters for composite
            'select': select_columns,
            'frequency': 0  # Will estimate
        })
    
    def design_indexes(self):
        """Design minimal indexes"""
        # Group queries by where columns
        column_sets = {}
        for query in self.queries:
            where_key = tuple(query['where'])
            if where_key not in column_sets:
                column_sets[where_key] = []
            column_sets[where_key].append(query)
        
        # For each column set, create covering index
        for where_cols, queries in column_sets.items():
            # Collect all selected columns
            all_selected = set()
            for q in queries:
                all_selected.update(q['select'])
            
            # Remove where columns from covering
            covering = list(all_selected - set(where_cols))
            
            index_name = f"idx_{self.table}_{','.join(where_cols)}"
            if covering:
                index_name += f"_covering"
            
            self.indexes.append({
                'name': index_name,
                'columns': list(where_cols),
                'covering': covering
            })
        
        return self.indexes

# Test
planner = IndexPlanner('users')

# Add queries
planner.add_query('q1', ['status'], ['id', 'email', 'name'])
planner.add_query('q2', ['status'], ['id', 'phone'])
planner.add_query('q3', ['country', 'age'], ['id', 'name'])
planner.add_query('q4', ['country', 'age'], ['id', 'email'])
planner.add_query('q5', ['created_at'], ['id', 'status'])

indexes = planner.design_indexes()

print("Designed indexes:")
for idx in indexes:
    create_sql = f"CREATE INDEX {idx['name']} ON {planner.table}({','.join(idx['columns'])})"
    if idx['covering']:
        create_sql += f"\nINCLUDE ({','.join(idx['covering'])})"
    print(f"\n{create_sql}")
```

---

### Exercise 3: Index Maintenance & Fragmentation (Hard)

**Problem:** Index fragmentation causes 50% performance degradation. Design maintenance strategy.

**Solution:**

```python
class IndexMaintenance:
    def __init__(self):
        self.indexes = {}
    
    def create_index(self, name, size_mb=100):
        """Create index"""
        self.indexes[name] = {
            'size_mb': size_mb,
            'fragmentation': 0,
            'last_rebuild': 0,
            'reads': 0,
            'writes': 0
        }
    
    def simulate_operations(self, num_operations):
        """Simulate reads/writes causing fragmentation"""
        for idx_name in self.indexes:
            idx = self.indexes[idx_name]
            idx['writes'] += num_operations
            # Fragmentation increases with writes
            idx['fragmentation'] = min(95, idx['writes'] / 1000)
    
    def estimate_performance_impact(self, fragmentation):
        """Estimate impact on query speed"""
        if fragmentation < 10:
            return 1.0  # No impact
        elif fragmentation < 30:
            return 1.2  # 20% slower
        elif fragmentation < 50:
            return 1.8  # 80% slower
        else:
            return 3.0  # 3x slower
    
    def should_rebuild(self, name):
        """Determine if index needs rebuild"""
        idx = self.indexes[name]
        if idx['fragmentation'] > 30:
            return True
        if idx['writes'] > 1000000 and idx['fragmentation'] > 10:
            return True
        return False
    
    def rebuild_index(self, name):
        """Rebuild index to eliminate fragmentation"""
        idx = self.indexes[name]
        idx['fragmentation'] = 0
        idx['writes'] = 0
        idx['last_rebuild'] = 0
        print(f"Rebuilt {name}: fragmentation → 0%")
    
    def recommend_maintenance(self):
        """Recommend maintenance actions"""
        recommendations = []
        
        for name, idx in self.indexes.items():
            impact = self.estimate_performance_impact(idx['fragmentation'])
            
            if self.should_rebuild(name):
                recommendations.append({
                    'action': 'rebuild',
                    'index': name,
                    'fragmentation': idx['fragmentation'],
                    'impact': f"{impact}x slower"
                })
            elif idx['fragmentation'] > 50:
                recommendations.append({
                    'action': 'reorganize',
                    'index': name,
                    'fragmentation': idx['fragmentation'],
                    'impact': f"{impact}x slower"
                })
        
        return recommendations

# Test
maintenance = IndexMaintenance()

maintenance.create_index('idx_users_status')
maintenance.create_index('idx_users_email')
maintenance.create_index('idx_orders_date')

# Simulate heavy write load
print("Simulating 50M write operations...")
maintenance.simulate_operations(50000)

# Check recommendations
recs = maintenance.recommend_maintenance()
print(f"\nMaintenance recommendations:")
for rec in recs:
    print(f"  {rec['index']}: {rec['action'].upper()}")
    print(f"    Fragmentation: {rec['fragmentation']:.0f}%")
    print(f"    Performance impact: {rec['impact']}")

# Rebuild
print(f"\nRebuilding fragmented indexes...")
for rec in recs:
    if rec['action'] == 'rebuild':
        maintenance.rebuild_index(rec['index'])
```

---

**Last updated:** 2026-05-22
