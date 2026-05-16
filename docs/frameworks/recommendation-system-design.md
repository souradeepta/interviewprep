# Recommendation System Design: Building Personalized Experiences

Master recommendation algorithms and system architecture.

---

## Recommendation Approaches

### 1. Collaborative Filtering

**Idea:** "Users who liked what you liked also liked X"

```
User-Item Matrix:
        Movie A  Movie B  Movie C
User 1    5        4        ?     (predict rating)
User 2    4        3        5
User 3    5        5        4

Find users similar to User 1 (cosine similarity)
User 1 ≈ User 2 (both like A, B)
User 2 rated C=5, so recommend C to User 1
```

**Implementation:**

```python
def collaborative_filtering(user_ratings, target_user_id):
    # Find similar users (cosine similarity)
    target_ratings = user_ratings[target_user_id]
    similarities = {}
    
    for other_user_id, other_ratings in user_ratings.items():
        if other_user_id == target_user_id:
            continue
        # Cosine similarity
        similarity = cosine_similarity(target_ratings, other_ratings)
        similarities[other_user_id] = similarity
    
    # Get recommendations from similar users
    recommendations = {}
    for other_user_id, similarity in sorted(similarities.items(), reverse=True)[:10]:
        for item_id, rating in user_ratings[other_user_id].items():
            if item_id not in target_ratings:
                recommendations[item_id] = recommendations.get(item_id, 0) + rating * similarity
    
    return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
```

**Pros:** Simple, captures user preferences
**Cons:** Cold-start (new users), sparsity (ratings matrix sparse)

### 2. Content-Based Filtering

**Idea:** "You liked movies with these features, here are similar ones"

```
Movie A: [Comedy, Adventure, Family]
Movie B: [Comedy, Family]
Movie C: [Drama, Thriller]

User 1 likes: [Movie A, Movie B]
Features: [Comedy, Family]
Recommend: Movie X if it has [Comedy, Family]
```

**Pros:** Works for new items
**Cons:** Doesn't capture user preferences across different content types

### 3. Hybrid (Collaborative + Content)

```
Score = 0.7 * Collaborative_Score + 0.3 * Content_Score
Best of both worlds
```

---

## Recommendation System Architecture

### Small Scale (< 1M users, < 10K items)

```
Users
  ↓
API Server
  ↓
Compute recommendations daily (batch)
Store in Redis/cache
  ↓
Serve cached recommendations
```

### Large Scale (> 100M users, > 1M items)

```
User Events (views, clicks, purchases)
  ↓
Feature Store (user features, item features)
  ↓
ML Model (trains offline)
  ↓
Ranking Service (score candidates)
  ↓
Cache (hot recommendations)
  ↓
API Gateway → Users
```

---

## Algorithm Comparison

| Algorithm | Latency | Accuracy | Scalability |
|-----------|---------|----------|-----------|
| **Popularity** | < 1ms | Low | ✓ |
| **Content-based** | 10-100ms | Medium | ✓ |
| **Collaborative** | 100-1000ms | High | ✗ for large scale |
| **Matrix Factorization** | 100-1000ms | High | ✗ for large scale |
| **Deep Learning** | 10-100ms (cached) | Very High | ✓ with infrastructure |
| **Hybrid** | 100-1000ms | Very High | ✓ |

---

## Cold-Start Problem

### New User
```
Problem: No rating history
Solution:
1. Popular items (trending, most downloaded)
2. Content-based (from profile info, demographics)
3. Random exploration (let user rate a few items)
4. Hybrid approach
```

### New Item
```
Problem: No ratings yet
Solution:
1. Content-based (similar to rated items)
2. Hybrid with user features
3. Gradual rollout (show to small % of users first)
```

---

## Ranking & Personalization

```
Candidates (1000 potential recommendations)
  ↓
Scoring (Collaborative/Content model)
  ↓
Diversity (don't recommend all same genre)
  ↓
Freshness (mix new and old items)
  ↓
A/B Testing (test different algorithms)
  ↓
Top-K (return 10 recommendations)
```

---

## Key Metrics

| Metric | Meaning | Target |
|--------|---------|--------|
| **CTR** | Click-through rate | > 1% |
| **Conversion** | % who purchase after recommendation | > 0.5% |
| **NDCG** | Normalized discounted cumulative gain | > 0.6 |
| **Diversity** | % recommendations in different categories | > 40% |
| **Coverage** | % of items recommended at least once | > 80% |

---

## Recommendation System Checklist

- ✓ Identified recommendation approach (collaborative/content/hybrid)
- ✓ Training data pipeline (user events, features)
- ✓ Batch or online training strategy
- ✓ Model evaluation (NDCG, coverage)
- ✓ Cold-start handling (new users/items)
- ✓ Ranking and diversification
- ✓ Caching strategy (popular recommendations)
- ✓ A/B testing for algorithms
- ✓ Monitoring: CTR, conversion, diversity
- ✓ Feedback loop (user interactions improve future models)

