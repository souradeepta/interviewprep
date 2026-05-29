# Recommendation Engine

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Users on a platform with millions of items (videos, products, articles, songs) cannot browse
exhaustively. A recommendation engine surfaces items that a specific user is most likely to engage
with, increasing session length, conversion, and retention. Without personalized recommendations,
users see generic popular content, churn rates are higher, and long-tail items are never discovered.

The core challenge is predicting relevance for 100M users × 10M items = 1 quadrillion pairs —
making an exhaustive approach impossible. The solution is a multi-stage funnel: retrieval (narrow
100M items to 1K candidates), ranking (score 1K candidates with a heavy model), and post-processing
(business rules, diversity, freshness injection).

## Functional Requirements

- Recommend top-K items per user on homepage load (online serving, < 200 ms)
- Update recommendations as users interact (click, watch, purchase, skip)
- Handle new users with no history (cold-start problem)
- Handle new items with no interaction data (item cold-start)
- Support A/B testing of different recommendation models

## Non-Functional Requirements

- **Scale:** 100M DAU, 10M items, 1B interactions/day (clicks, views, purchases)
- **Latency:** P99 < 200 ms for top-20 recommendations (online serving)
- **Availability:** 99.9%; degrade gracefully to popularity-based recs if model is unavailable
- **Consistency:** Eventual — personalized recs updated every few minutes; not real-time

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Users:               100M DAU
Items:               10M (products, videos, etc.)
Interactions/day:    1B clicks + views + purchases  = 11,574/sec
Model training:      Daily batch on 1B interactions
Embedding size:      128 dimensions, float32 = 512 bytes per user/item embedding
User embeddings:     100M * 512 bytes             = 51 GB (fits in RAM on large nodes)
Item embeddings:     10M  * 512 bytes             = 5.1 GB (easily fits in RAM)
ANN index size:      10M items, HNSW index        = ~500 MB additional (adjacency graph)

Serving latency budget (P99 200 ms):
  Feature lookup (user profile, context):   20 ms
  Candidate retrieval (ANN search, 1K):     10 ms
  Ranking model inference (1K items):      120 ms  ← dominant
  Post-processing (dedup, rules):            5 ms
  Total:                                   155 ms  (45 ms margin)
```

### Architecture Diagram

```
  User Request: "homepage for user_id=42"
        |
  +-----v-----------+
  | Rec API Server  |  ← orchestrates the pipeline
  +-----+-----------+
        |
  +-----v-----------+        +------------------+
  | Feature Store   |        | User Embeddings  |  ← precomputed nightly
  | (user profile,  |        | (Redis / FAISS)  |
  |  recent clicks) |        +--------+---------+
  +-----+-----------+                 |
        |          Retrieval Stage    |
        +----------+------------------+
                   |
         +---------v---------+
         | ANN Index (FAISS/ |  ← find top 1K items nearest to user embedding
         | ScaNN / Annoy)    |
         +---------+---------+
                   |  1K candidates
         +---------v---------+
         | Ranking Model     |  ← deep neural net (DNN), scores 1K candidates
         | (TensorFlow Serve)|
         +---------+---------+
                   |  ranked top-20
         +---------v---------+
         | Post-processor    |  ← deduplicate, inject fresh/diverse items, business rules
         +---------+---------+
                   |
              Response: top-20 items

Offline Training Pipeline:
  Kafka (interactions) → Spark batch job → Train CF/DNN model → Export embeddings
  → Update FAISS index → Update Feature Store
```

### Data Model

```sql
-- User-item interactions (source of truth for training)
CREATE TABLE interactions (
    interaction_id  BIGINT PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    item_id         BIGINT NOT NULL,
    interaction_type ENUM('view','click','purchase','skip','like') NOT NULL,
    weight          FLOAT NOT NULL,  -- view=0.1, click=0.5, purchase=1.0, skip=-0.2
    context_json    JSON,            -- device, session_id, position_shown
    created_at      TIMESTAMP NOT NULL,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_item_created (item_id, created_at)
);

-- Item feature store
CREATE TABLE items (
    item_id         BIGINT PRIMARY KEY,
    title           VARCHAR(512),
    category        VARCHAR(128),
    tags            JSON,            -- ["electronics", "laptop", "gaming"]
    price_cents     INT,
    embedding       BLOB,            -- 128-dim float32, updated nightly
    popularity_7d   FLOAT,           -- rolling 7-day interaction count (normalized)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User feature store (hot features for online inference)
-- Stored in Redis as JSON, TTL = 1 hour
-- Key: user_features:{user_id}
-- Value: { age_group, top_categories, recent_item_ids: [last 20], device_type }
```

### API Design

```
# Recommendation API
GET /recommendations/{user_id}?context=homepage&limit=20
  Response: 200 {
    user_id: 42,
    recommendations: [
      { item_id, title, score, explanation: "because you viewed X" },
      ...
    ],
    model_version: "dnn_v23",
    generated_at: "2024-01-15T12:00:00Z"
  }

# Interaction feedback (real-time signal)
POST /interactions
  Body: { user_id, item_id, type: "click", context: { page: "homepage", position: 3 } }
  Response: 202 { recorded: true }

# Item similarity (item-to-item, for "customers also viewed")
GET /items/{item_id}/similar?limit=10
  Response: 200 { similar_items: [{ item_id, similarity_score }, ...] }

# Cold-start: onboarding preferences (new user)
POST /users/{user_id}/preferences
  Body: { categories: ["electronics", "books"], skip_categories: ["fashion"] }
  Response: 200 { initial_recommendations: [...] }
```

### Basic Scaling

- **Offline training:** Daily Spark/Flink batch job trains matrix factorization or DNN on prior
  day interactions; export user/item embeddings to Feature Store and FAISS index
- **Candidate retrieval:** ANN (approximate nearest neighbor) search with FAISS finds top-1K item
  candidates nearest to user embedding in < 10 ms; avoids scoring all 10M items
- **Ranking:** Lightweight DNN (2-3 layers, 100 ms inference) scores 1K candidates using user
  features + item features; deployed via TF Serving or Triton
- **Cold-start fallback:** New users get popularity-based recommendations (top-100 items by
  interaction_count_7d) until ≥ 10 interactions collected

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Feature Store (Redis Cluster):
  User features: 100M users * 500 bytes = 50 GB (fits in 3-node Redis cluster, 32 GB/node)
  Item features: 10M items * 1 KB = 10 GB (easily fits)
  Read QPS: 100M DAU * 5 homepage loads/day / 86400 = 5,800 reads/sec → Redis trivially handles

FAISS Index (item embeddings, 10M items, 128-dim):
  IVF_HNSW index: ~500 MB in RAM per ANN server node
  Search: top-1K from 10M in ~5 ms (tested on single node)
  Replicas: 3 read replicas for 10K QPS * 5800/3 ≈ 1,933 QPS/node (well within limits)

Ranking Model Server:
  Model size: DNN 3-layer MLP ≈ 10 MB (small, fast inference)
  Batch inference: 1K items in 50 ms on 4-core CPU; 10 ms on A10G GPU
  Throughput: at 5,800 req/sec, each scoring 1K items: 5.8B item-score computations/sec
  GPU nodes: 10× A10G (24 GB VRAM) → handles 20K req/sec with batching (batch_size=32)

Training cluster:
  Daily: process 1B interactions (1 TB compressed); Spark on 20× m5.4xlarge (16 vCPU each)
  Training time: 2-4 hours for collaborative filtering; 4-8 hours for DNN with features
  Schedule: start at 02:00 UTC, complete by 06:00 UTC (before peak traffic)
```

### Failure Modes

```
FAILURE: FAISS index node down
  Detection:  Health check every 5 sec; load balancer marks node unhealthy
  Mitigation: Route to remaining replicas (2 of 3 still up → no degradation)
  Full outage: Fall back to pre-computed popular items per category (stored in Redis)
  Recovery:   New node fetches FAISS index from S3 snapshot (5 min to load 500 MB)

FAILURE: Ranking model server OOM or crash
  Detection:  HTTP 5xx rate > 1% on model server; alert fires in 30 sec
  Mitigation: Circuit breaker trips → fall back to ANN score (cosine similarity) as rank
              Cosine rank is 20-30% worse in CTR but prevents complete failure
  Model rollback: Canary deployment → new model gets 10% traffic; if p99 latency degrades
                  or CTR drops > 5% vs control, auto-rollback to prior model version

FAILURE: Feature store stale (Redis primary fails, replica promoted)
  Window:     30-60 sec promotion time; during window, feature reads fail
  Mitigation: Use locally cached features (in-process LRU, TTL 5 min) on recommendation server
              Fallback: use item popularity features only (no personalization)

FAILURE: Model trained on biased data (feedback loop — popular items get more clicks → trained
         to recommend more popular items → other items starved)
  Detection:  Monitor long-tail item impression rate; alert if < 5% of impressions are long-tail
  Mitigation: Exploration injection: 10% of recommendations are randomly sampled from long-tail
              (epsilon-greedy or Thompson Sampling); ensures diverse training signal
```

### Consistency Boundaries

```
INTERACTION → TRAINING: Batch (daily)
  1B interactions collected in Kafka; batch-processed by Spark nightly
  Model reflects interactions from T-1 day; not real-time
  Acceptable: user preference changes slowly; daily update sufficient for most cases

REAL-TIME SIGNAL (session-level personalization):
  Within a session: track last 20 items clicked in Redis (TTL = session)
  Retrieval stage uses current session items to boost similar candidates
  This creates within-session personalization without retraining the model

A/B TEST CONSISTENCY:
  User bucketed by hash(user_id + experiment_id) % 100
  Bucket assignment is deterministic: same user always in same experiment
  Models A and B deployed simultaneously; traffic split at API gateway layer
  Experiment metrics logged to data warehouse; significance test after 1 week

MODEL VERSIONING:
  Each model version tagged: model_dnn_v23, model_dnn_v24
  Feature store schema versioned separately; model and feature schema must match
  Blue-green deploy: v24 deployed to shadow traffic → validated → promoted
```

### Cost Model

```
Infrastructure (AWS, us-east-1):
  GPU ranking servers: 10× p3.2xlarge ($3.06/hr): 10 * $3.06 * 8760 = $268K/yr
  FAISS ANN servers:  3× r6i.4xlarge ($1.02/hr): 3 * $1.02 * 8760  = $27K/yr
  Feature store:      Redis r6g.4xlarge 3-node cluster: 3 * $0.97 * 8760 = $25K/yr
  Training cluster:   20× m5.4xlarge 4 hr/day (Spot): 20 * $0.27 * 4 * 365 = $8K/yr
  Storage (S3):       1 TB/day interactions * 30 days = 30 TB * $0.023/GB = $690/mo = $8K/yr
  Total:                                                                    = $336K/yr

Per-user per-month: $336K / (100M * 12) = $0.00028/user/month

Optimization levers:
  1. Spot GPU instances for ranking (interruptible): 70% savings → $188K saved
  2. Distill large DNN to small model: 4× faster inference → 4× fewer GPU nodes
  3. Batching: group homepage requests within 10ms window → GPU utilization 80%+
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Collaborative filtering (matrix factorization) | Captures latent user taste; works with implicit feedback; explainable | Cold-start for new users/items; requires dense interaction data; offline only | Mature platforms with rich interaction history |
| Content-based filtering | Works for new items (uses item features); no cold-start for items | User preference profile must be built from scratch; no "serendipity" | News, documents, niche domains with rich item metadata |
| Hybrid (CF + content + context) | Best accuracy; handles cold-start; adapts to context | High complexity; expensive to train and serve; A/B testing harder | Large platforms (Netflix, Spotify, Amazon) |
| Two-tower DNN (query tower + item tower) | Scalable: item embeddings precomputed; serves with ANN; joint training | Training complexity; requires labeled data; GPU expensive | Modern large-scale rec systems; enables ANN retrieval |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is the cold-start problem and how do you handle it?
   → New users have no interaction history, so collaborative filtering cannot compute
   personalized embeddings. Solutions: (a) Onboarding flow: ask users to pick interests;
   (b) Popularity-based fallback: show top trending items; (c) Content-based: recommend
   items matching user's stated demographics or context (device, location).

2. **(L3)** What is the difference between collaborative filtering and content-based filtering?
   → CF: "users similar to you liked item X" — learns from interaction patterns, ignores item
   content. Content-based: "item X is similar to items you liked, based on item features" —
   uses item metadata, no interaction needed. Hybrid combines both signals.

3. **(L4)** How does ANN (approximate nearest neighbor) search speed up candidate retrieval?
   → Exact nearest neighbor in 10M items * 128 dims = 1.28B dot products per query — too slow
   (50-100 ms). ANN (FAISS HNSW or IVF) builds a graph/cluster index that finds 95%+ of true
   nearest neighbors in < 10 ms by only examining a small fraction of items. The "approximate"
   trade-off costs 2-5% recall but saves 10× latency.

4. **(L4)** How do you measure recommendation quality offline and online?
   → Offline: Precision@K, Recall@K, NDCG (normalized discounted cumulative gain), AUC.
   Online (A/B test): CTR (click-through rate), CVR (conversion rate), session length, revenue
   per user, long-term retention. Offline metrics correlate ~60-70% with online metrics;
   always validate with A/B test before full rollout.

5. **(L5)** Describe the two-tower model architecture and why it's preferred at scale.
   → Two-tower: Query tower encodes user + context into an embedding; Item tower encodes item
   features into an embedding. Dot product of both embeddings predicts interaction probability.
   Scalability: item tower outputs precomputed and cached (10M items * 512 bytes ≈ 5 GB);
   at serving time, compute user embedding online, then ANN search precomputed item embeddings.
   Training: contrastive loss (positive interactions vs sampled negatives).

6. **(L5)** How would you run an A/B test to validate a new recommendation model?
   → Bucket users deterministically: hash(user_id + experiment_id) % 100 < 10 → treatment,
   else control. Measure primary metric (CTR or CVR) and guardrail metrics (latency, diversity).
   Run for ≥ 1 week (avoids day-of-week effects), ≥ 10K users per arm for statistical power
   (two-sample t-test, p < 0.05). Analyze novelty bias: new model always wins short-term
   due to "novelty" — measure long-term retention after 2 weeks.

7. **(L5+)** How do you use real-time Flink to update user features without model retraining?
   → Flink consumes Kafka interaction stream; maintains rolling aggregations: category affinity
   scores, recent items, session velocity. Writes updated feature vectors to Feature Store
   (Redis) every minute. Ranking model reads fresh features at inference time — no retraining
   needed. Model sees up-to-date user context; only embeddings (from offline training) are
   stale. This is "online feature engineering" (not model retraining).

## Anti-patterns / Things NOT to Say

- **"Train the model in real-time on every interaction"** — Gradient descent on a large DNN
  requires mini-batches, GPU clusters, hours of training. True real-time model updates
  (online learning) are possible only for simple linear models; DNNs need batch training.
  Instead, update features in real-time; retrain models on a schedule.
- **"Score all 10M items per user at serving time"** — 10M items * DNN inference = impossible
  in < 200 ms. Always use a two-stage funnel: ANN retrieval (get 1K candidates in ms) then
  ranking (score 1K items in 100 ms).
- **"Use accuracy as the offline evaluation metric"** — Recommendation is a ranking problem,
  not classification. Use ranking metrics: NDCG@K, MRR, Recall@K. Accuracy (overall correct
  predictions) is dominated by true negatives (user didn't click 99.9% of items) and is
  misleadingly high.
- **"Only recommend popular items to avoid risk"** — Popularity bias reduces serendipity,
  starves long-tail creators, and creates a feedback loop where popular items get more data
  and stay popular forever. Inject exploration (10% random from long-tail) to maintain
  catalog coverage.
- **"Same model for all contexts (homepage, email, push)"** — Context matters enormously.
  A user browsing homepage on desktop expects different recommendations than a quick mobile
  check. Train context-specific models or include context as a feature.

## Python Implementation (sketch)

```python
import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserProfile:
    user_id: int
    embedding: np.ndarray       # 128-dim float32
    recent_item_ids: list[int]

@dataclass
class Item:
    item_id: int
    embedding: np.ndarray       # 128-dim float32
    popularity_score: float

class TwoStageRecommender:
    """Two-stage: ANN retrieval → cosine similarity ranking."""

    def __init__(self, items: list[Item]):
        self._items = {it.item_id: it for it in items}
        # Build item matrix for batch cosine similarity
        self._item_ids = np.array([it.item_id for it in items])
        raw = np.stack([it.embedding for it in items])         # (N, 128)
        self._item_matrix = raw / (np.linalg.norm(raw, axis=1, keepdims=True) + 1e-9)

    def _retrieve_candidates(
        self, user_embedding: np.ndarray, top_k: int = 100
    ) -> list[int]:
        """ANN approximation: in production, use FAISS HNSW."""
        u = user_embedding / (np.linalg.norm(user_embedding) + 1e-9)
        scores = self._item_matrix @ u          # (N,)
        top_indices = np.argpartition(scores, -top_k)[-top_k:]
        return self._item_ids[top_indices].tolist()

    def _rank_candidates(
        self,
        user: UserProfile,
        candidate_ids: list[int],
        top_k: int = 20,
    ) -> list[tuple[float, int]]:
        """Score candidates with cosine similarity + popularity boost."""
        u = user.embedding / (np.linalg.norm(user.embedding) + 1e-9)
        scored: list[tuple[float, int]] = []
        for item_id in candidate_ids:
            if item_id in user.recent_item_ids:
                continue  # already seen — skip
            item = self._items[item_id]
            v = item.embedding / (np.linalg.norm(item.embedding) + 1e-9)
            cosine = float(np.dot(u, v))
            # Blend relevance + popularity (tunable alpha)
            score = 0.8 * cosine + 0.2 * item.popularity_score
            scored.append((score, item_id))
        scored.sort(reverse=True)
        return scored[:top_k]

    def recommend(self, user: UserProfile, top_k: int = 20) -> list[int]:
        candidates = self._retrieve_candidates(user.embedding, top_k=200)
        ranked = self._rank_candidates(user, candidates, top_k=top_k)
        return [item_id for _, item_id in ranked]


# Usage
np.random.seed(42)
items = [Item(item_id=i, embedding=np.random.randn(128), popularity_score=np.random.random())
         for i in range(10_000)]

rec = TwoStageRecommender(items)
user = UserProfile(user_id=42, embedding=np.random.randn(128), recent_item_ids=[0, 1, 2])
recommendations = rec.recommend(user, top_k=20)
print(f"Top-20 for user 42: {recommendations[:5]}...")
```
