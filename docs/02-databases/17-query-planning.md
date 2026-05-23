# Query Planning & Optimization

Understand how databases execute queries and optimize slow queries through better plans, indexes, and statistics.

---

## ⚖️ Query Execution Trade-offs

### Join Order Impact

| Join Order | Rows Processed | Time | Best For |
|-----------|---------------|------|----------|
| **Worst** | 1M × 1M | 15 seconds | Never |
| **Seq scan all** | 1M + 1M | 2 seconds | Small tables |
| **Index-based** | 10K matched | 100ms | Large skewed data |
| **Cost-based optimal** | 10K matched | 50ms | Modern DBs |

### Statistics Quality Impact

```
Accurate statistics:
  ├─ Cardinality estimates correct
  ├─ Optimizer chooses best plan
  ├─ Query time: 100ms
  
Stale statistics (not updated in 1 month):
  ├─ Wrong cardinality estimates
  ├─ Optimizer chooses bad plan
  └─ Query time: 10 seconds (100x worse!)
```

---

## 🏗️ Query Execution Plans

### Plan 1: Full Table Scan

```
SELECT * FROM orders WHERE amount > 1000

Table Scan: orders
  ├─ Read all rows (1M rows)
  ├─ Check condition (amount > 1000)
  ├─ Return 50K matching rows
  └─ Time: 5 seconds
  
Use when: No index available, or many rows match
Cost: O(n) - read all rows
```

### Plan 2: Index Scan + Lookup

```
CREATE INDEX idx_orders_amount ON orders(amount);

SELECT * FROM orders WHERE amount > 1000

Index Scan: idx_orders_amount
  ├─ Seek to amount = 1000 (binary search, O(log n))
  ├─ Read index: 50K keys (scan, O(n'))
  ├─ Row lookup: 50K times (random access)
  └─ Time: 500ms
  
Use when: Small result set
Cost: O(log n + k*log n) where k = result size
```

### Plan 3: Index Only Scan

```
CREATE INDEX idx_orders_amount_total ON orders(amount, total);

SELECT amount, total FROM orders WHERE amount > 1000

Index Only Scan: idx_orders_amount_total
  ├─ Seek to amount = 1000
  ├─ Read index: 50K rows (covers query)
  ├─ No table lookup needed!
  └─ Time: 100ms (5x faster!)
  
Use when: Index contains all needed columns
Cost: O(log n + k) - much better
```

### Plan 4: Nested Loop Join

```
SELECT o.id, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.date > '2024-01-01'

Nested Loop:
  ├─ Seq scan orders (1M rows)
  ├─ For each order:
  │   └─ Seek customer (index lookup)
  ├─ Total lookups: 1M × O(log n) = 20M operations
  └─ Time: 10 seconds
  
Use when: Small inner table or index available
```

### Plan 5: Hash Join

```
Hash Join:
  ├─ Build hash table of customers (1M rows) in memory
  ├─ Scan orders (1M rows)
  ├─ For each order, lookup customer in hash table O(1)
  └─ Time: 2 seconds (5x faster than nested loop)
  
Use when: Enough memory for hash table
Limitation: Memory = table size
```

---

## 📊 Query Optimization

### EXPLAIN Analysis

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'pending' AND amount > 1000;

Seq Scan on orders  (cost=0.00..35000.00 rows=10000)
  Filter: ((status = 'pending') AND (amount > 1000))
  Rows: 1000000 → 10000 (10% filter selectivity)
  Actual time: 2000.00ms

Problem: Seq scan of 1M rows takes 2 seconds
Solution: Add index on (status, amount)
```

### Index Selection Strategy

```
Query: WHERE status = 'pending' AND amount > 1000 AND date > '2024-01-01'

Option 1: Single index on status
  ├─ Filter status (100K matches)
  ├─ Check amount condition (10K matches)
  ├─ Check date condition (5K matches)
  └─ Cost: Scan 100K rows

Option 2: Composite index (status, amount, date)
  ├─ Filter status + amount + date in index
  ├─ Result: 5K matches (no table access!)
  └─ Cost: 5K index scans (much better)
  
Rule: First filter column most selective, then others
```

### Query Rewrite

```sql
-- SLOW: Using function in WHERE
SELECT * FROM users WHERE YEAR(created_at) = 2024;
  ├─ Cannot use index on created_at
  └─ Full table scan: 1000ms

-- FAST: Range query instead
SELECT * FROM users 
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
  ├─ Can use index on created_at
  └─ Index scan: 10ms (100x faster!)
```

---

## ❓ Interview Q&A

**Q1: Query takes 10 seconds - how to debug?**

A:
1. Run EXPLAIN ANALYZE to see actual plan
2. Identify bottleneck:
   - Seq Scan with 1M rows? → Add index
   - Nested loop with high cost? → Use hash join
   - Wrong cardinality estimate? → Update statistics
3. Add appropriate indexes
4. If index doesn't help, rewrite query

**Q2: Index on column but still slow - why?**

A:
- Index exists but not used because:
  1. Query uses function: YEAR(date) → Date range query instead
  2. Type mismatch: INT vs. VARCHAR comparison → Cast correctly
  3. Composite index wrong order → Reorder columns
  4. Optimizer chose seq scan (table is small) → Force index if needed
  
- Check: Verify index is actually used in EXPLAIN ANALYZE

**Q3: Adding index made query slower, how?**

A:
- Possible causes:
  1. Random I/O from index lookup > Seq scan cost
     → Use in memory cache or columnar format
  2. Index stats wrong → Recalculate statistics
  3. Index fragmentation → Rebuild index
  4. Covering index not used → Verify index columns include all needed
  
- Solution: Analyze before/after plans

**Q4: Hash join needs 50GB RAM but database only has 10GB - solution?**

A:
- Problem: Hash table doesn't fit in memory
- Solutions:
  1. Reduce table size: Add WHERE clause to filter
  2. Batch processing: Process in chunks
  3. Nested loop: Falls back to slower join
  4. Sort-merge join: Sort both tables, then merge (slower)
  5. Add more RAM or split to separate machines

**Q5: Database scans wrong index - how to force correct one?**

A:
- Database picked wrong index → Manually hint:
  ```sql
  -- MySQL: use index hint
  SELECT * FROM orders USE INDEX (idx_amount) 
  WHERE amount > 1000;
  
  -- PostgreSQL: set enable_*=off to force
  SET enable_seqscan = off;
  
  -- But better: Update statistics
  ANALYZE orders;
  ```

---

## 🧪 Practical Exercises

### Exercise 1: Query Plan Analysis (Easy)

**Problem:** Identify slow query from EXPLAIN output. Determine optimal index.

**Solution:**

```python
class QueryPlanAnalyzer:
    def __init__(self):
        self.plans = {}
    
    def parse_explain(self, query_id, explain_output):
        """Parse EXPLAIN ANALYZE output"""
        plan = {
            'query_id': query_id,
            'nodes': []
        }
        
        # Parse nodes
        for line in explain_output.split('\n'):
            if 'Seq Scan' in line:
                plan['nodes'].append({
                    'type': 'SeqScan',
                    'cost': 35000,
                    'rows': 1000000
                })
            elif 'Index Scan' in line:
                plan['nodes'].append({
                    'type': 'IndexScan',
                    'cost': 100,
                    'rows': 10000
                })
        
        return plan
    
    def identify_bottleneck(self, plan):
        """Find slowest operation"""
        slowest = max(plan['nodes'], key=lambda n: n['cost'])
        return slowest
    
    def recommend_index(self, bottleneck, columns):
        """Recommend index based on bottleneck"""
        if bottleneck['type'] == 'SeqScan' and bottleneck['rows'] > 100000:
            return f"CREATE INDEX idx_{columns} ON table({columns})"
        return None

# Test
analyzer = QueryPlanAnalyzer()

explain = """
Seq Scan on orders  (cost=0.00..35000.00 rows=1000000)
  Filter: (status = 'pending' AND amount > 1000)
  Rows: 1000000
  Actual time: 2000ms
"""

plan = analyzer.parse_explain('q1', explain)
bottleneck = analyzer.identify_bottleneck(plan)

print(f"Bottleneck: {bottleneck['type']} (cost={bottleneck['cost']})")
print(f"Recommendation: CREATE INDEX idx_status_amount ON orders(status, amount)")
```

---

### Exercise 2: Join Order Optimization (Medium)

**Problem:** Complex 3-table join is slow. Determine optimal join order.

**Solution:**

```python
from itertools import permutations

class JoinOptimizer:
    def __init__(self):
        self.tables = {
            'orders': {'rows': 1000000, 'indexed': True},
            'customers': {'rows': 100000, 'indexed': True},
            'products': {'rows': 50000, 'indexed': True}
        }
    
    def estimate_cost(self, join_sequence):
        """Estimate cost for join order"""
        cost = 0
        rows = self.tables[join_sequence[0]]['rows']
        
        for i in range(1, len(join_sequence)):
            next_table = join_sequence[i]
            next_rows = self.tables[next_table]['rows']
            
            if self.tables[next_table]['indexed']:
                # Index join: O(rows * log(next_rows))
                join_cost = rows * 10  # Simplified
            else:
                # Hash join: O(rows + next_rows)
                join_cost = rows + next_rows
            
            cost += join_cost
            rows = int(rows * next_rows / 1000000)  # Estimate output rows
        
        return cost, rows
    
    def find_optimal_order(self):
        """Find best join order"""
        table_names = list(self.tables.keys())
        best_cost = float('inf')
        best_order = None
        
        for perm in permutations(table_names):
            cost, output_rows = self.estimate_cost(perm)
            
            if cost < best_cost:
                best_cost = cost
                best_order = perm
        
        return best_order, best_cost

# Test
optimizer = JoinOptimizer()
order, cost = optimizer.find_optimal_order()

print(f"Optimal join order: {' → '.join(order)}")
print(f"Estimated cost: {cost}")
```

---

### Exercise 3: Index Selection for Multiple Conditions (Hard)

**Problem:** Query has 5 WHERE conditions. Design optimal index strategy.

**Solution:**

```python
class IndexDesigner:
    def __init__(self):
        self.table = 'users'
        self.row_count = 10000000
        self.columns = {
            'status': {'cardinality': 10, 'selectivity': 0.1},
            'country': {'cardinality': 200, 'selectivity': 0.005},
            'age': {'cardinality': 100, 'selectivity': 0.01},
            'verified': {'cardinality': 2, 'selectivity': 0.5},
            'created_at': {'cardinality': 3650, 'selectivity': 0.001}
        }
    
    def estimate_rows_after_filter(self, columns_filtered):
        """Estimate rows remaining after filters"""
        rows = self.row_count
        for col in columns_filtered:
            rows *= self.columns[col]['selectivity']
        return int(rows)
    
    def design_indexes(self, conditions):
        """Design indexes for given conditions"""
        # Sort by selectivity (most selective first)
        sorted_cols = sorted(
            conditions,
            key=lambda c: self.columns[c]['selectivity']
        )
        
        # Composite index on most selective columns
        index_cols = sorted_cols[:3]  # Limit to 3 columns
        
        # Covering index: add remaining columns needed for SELECT
        covering_cols = sorted_cols[3:]
        
        return index_cols, covering_cols
    
    def estimate_improvement(self, conditions):
        """Estimate query improvement"""
        # Seq scan
        rows_seq_scan = self.estimate_rows_after_filter(conditions)
        cost_seq_scan = self.row_count  # Read all rows
        
        # Optimized with index
        rows_index = rows_seq_scan
        cost_index = len(conditions) * 10 + rows_seq_scan  # Index lookup + result scan
        
        improvement = cost_seq_scan / cost_index
        
        return improvement

# Test
designer = IndexDesigner()

conditions = ['status', 'country', 'age', 'verified', 'created_at']
index_cols, covering_cols = designer.design_indexes(conditions)

print(f"Query: SELECT * FROM users WHERE")
for i, col in enumerate(conditions):
    print(f"  {col} = ? {('AND' if i < len(conditions)-1 else '')}")

print(f"\nOptimal index: CREATE INDEX idx_users_{', '.join(index_cols)}")
print(f"  ON users({', '.join(index_cols)})")

if covering_cols:
    print(f"  INCLUDE ({', '.join(covering_cols)})")

improvement = designer.estimate_improvement(conditions)
print(f"\nEstimated improvement: {improvement:.0f}x faster")
```

---

**Last updated:** 2026-05-22
