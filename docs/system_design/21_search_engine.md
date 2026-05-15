# Search Engine

## Problem Statement
Design a full-text search engine with ranking and relevance.

**Requirements:**
- Index documents
- Full-text search
- Ranking by relevance
- Handle typos/suggestions

## Design

### Inverted Index

```
Word → [doc_id, position, frequency]
Enables fast search
Compressed for storage
```

### Ranking Algorithm

```
TF-IDF: Term frequency × Inverse document frequency
BM25: Enhanced TF-IDF
PageRank: Link-based importance
Combined score
```

### Distributed Search

```
Index sharding by document ID
Query all shards
Merge and rank results
```

### Suggestion/Autocomplete

```
Trie for prefix matching
N-gram indexing
Edit distance for typos
```

## Complexity

| Operation | Time |
|-----------|------|
| Index document | O(d) where d=doc length |
| Search | O(log n + k) |
| Rank | O(k log k) |
