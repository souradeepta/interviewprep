# Advanced Patterns

## Segment Tree
**When to use:** Range queries with updates, efficient interval operations

**Best DS:** Binary tree structure (array representation)

**Key Algorithms:** Build O(n), range query O(log n), point update O(log n), lazy propagation for ranges

**Example Problems:**
1. "Range sum query with update" → Segment tree with lazy propagation. Your repo: `python/advanced/segment_tree.py`. Time: O(log n) per op

---

## Fenwick Tree (BIT)
**When to use:** Prefix sums with updates, 2D prefix sum, inversion count

**Best DS:** Array (implicitly represents tree via index manipulation)

**Key Algorithms:** Update: add to current index, jump via index + (index & -index). Query: accumulate via index, jump via index - (index & -index)

**Example Problems:**
1. "Count inversion in array" → Coordinate compression + Fenwick tree. Your repo: `python/advanced/fenwick_tree.py`. Time: O(n log n)

---

## Heavy-Light Decomposition
**When to use:** Tree path queries/updates, LCA with aggregation

**Best DS:** Tree, Segment tree or Fenwick tree per chain

**Key Algorithms:** Decompose tree into heavy/light edges, maintain segment tree per heavy chain

**Example Problems:**
1. "Tree path sum query/update" → Heavy-light decomposition + segment tree. Time: O(log² n)

---

## AC Automaton
**When to use:** Multiple pattern matching, dictionary search

**Best DS:** Trie with failure links (KMP-like)

**Key Algorithms:** Build Trie, compute failure function, scan text with failure link fallback

**Example Problems:**
1. "Word filter: match all patterns in text" → AC Automaton for multi-pattern matching. Time: O(n + m + z)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
