# Recommendation Engine

## Problem Statement
Design a system recommending content to users based on preferences.

**Approaches:**
- Content-based: Similar to liked items
- Collaborative filtering: Similar users' preferences
- Hybrid: Combine both

## Design

### Collaborative Filtering

```
User-item matrix (sparse)
Find similar users (cosine similarity)
Recommend items liked by similar users
```

### Content-based

```
Item features (genre, tags, etc.)
User preference vector
Rank items by similarity
```

### Cold Start Problem

```
New user: Popularity-based recommendations
New item: Content-based (feature similarity)
Hybrid approach: Mix strategies
```

### Personalization Pipeline

```
Batch: Precompute recommendations
Online: Real-time re-ranking by context
A/B test: Measure engagement
```

## Complexity

| Operation | Time |
|-----------|------|
| User similarity | O(u) |
| Recommendations | O(u*i) precomputed |
| Re-ranking | O(k log k) |
