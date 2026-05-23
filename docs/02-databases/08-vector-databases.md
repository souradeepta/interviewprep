# Vector Databases — Semantic Search and Embeddings

Finding similar items using vector similarity and approximate nearest neighbor search.

---

## 🔢 Vector Embeddings Fundamentals

### Embedding Concept

```
Text → Embedding Model → Dense Vector

"Hello world" 
  ↓ (sentence-transformers)
[0.2, 0.5, -0.3, 0.1, 0.7, -0.2, ..., -0.1]  (1536 dimensions)

"Hi everyone"
  ↓ (same model)
[0.21, 0.48, -0.32, 0.09, 0.68, -0.21, ..., -0.08]  (similar!)

"Goodbye"
  ↓ (same model)
[0.8, 0.1, 0.6, -0.2, 0.1, 0.5, ..., 0.9]  (different)
```

### Similarity Metrics

```
Cosine Similarity (most common):
cos(A, B) = (A · B) / (||A|| × ||B||)
Range: -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite)

Example:
A = [1, 0, 0]
B = [0.9, 0.43, 0]
cos(A, B) = (0.9) / (1 × 1.04) = 0.86  (very similar!)

Euclidean Distance (alternative):
d(A, B) = √((a1-b1)² + (a2-b2)² + ...)
Range: 0 to ∞ (0 = identical)

Manhattan Distance:
d(A, B) = |a1-b1| + |a2-b2| + ...

Dot Product:
A · B (optimized version, requires normalized vectors)
```

---

## ⚖️ Embedding Model Selection

```
Model        | Dimension | Speed  | Quality | Use Case
─────────────|───────────|────────|─────────|──────────────────
all-MiniLM   | 384       | Fast   | Good    | Speed-critical
all-mpnet    | 768       | Medium | Very Good| Balanced
bge-base     | 768       | Fast   | Excellent| Semantic search
OpenAI ada   | 1536      | Medium | Excellent| Cloud (expensive)
local-llama  | 4096      | Slow   | High    | On-premise, low cost

Trade-offs:
├─ Dimension: Higher = more expressive, slower, more storage
├─ Quality: Better models = better similarity matching
├─ Cost: Cloud APIs expensive, local models free
└─ Latency: Embedding time + vector search time

Recommendation:
├─ Start: all-mpnet-base-v2 (384-768 dim, balanced)
├─ Production: bge-large-v1.5 (1024 dim, excellent quality)
├─ Cost-sensitive: OpenAI ada (already have embeddings)
```

---

## 🔍 Indexing Methods Comparison

### Flat Index (Brute Force)
```
Method: Linear scan all vectors
Complexity: O(n×d) where n=vectors, d=dimensions

Pros:
├─ Exact results (100% recall)
├─ Simple implementation
└─ Good for small scale (<100K vectors)

Cons:
├─ Slow for large scale
├─ 100 QPS for 1M vectors is difficult
└─ Not practical for 1B+ vectors

When: Development, <100K vectors
```

### HNSW (Hierarchical Navigable Small World)
```
Method: Graph-based navigation in hierarchical layers

Structure:
Layer 0 (top): Few nodes
Layer 1: More nodes
Layer 2: Even more
Layer 3 (bottom): All vectors

Search: Start top, navigate down

Complexity: O(log n) approximately

Pros:
├─ Very fast (100-1000s QPS)
├─ Good recall (95-99%)
├─ Simple to implement
└─ Popular choice

Cons:
├─ High memory (graph pointers)
├─ Slower inserts (graph maintenance)
└─ Approximate (not 100% accurate)

When: Most use cases (default choice)
```

### IVF (Inverted File)
```
Method: Partition vectors into clusters, search relevant clusters

Structure:
├─ K clusters (centroids)
├─ Each vector assigned to nearest centroid
├─ Search: Only search nearby clusters

Complexity: O(n/k) with k clusters

Pros:
├─ Memory efficient
├─ Can search subset of clusters
├─ Fast with small k
└─ Parallelizable

Cons:
├─ Clustering overhead
├─ Recall drops if k too small
├─ Approximate only

When: Memory-constrained, 1M+ vectors
```

### PQ (Product Quantization)
```
Method: Compress vectors to smaller size

Process:
1. Split vector into m subvectors
2. Quantize each subvector independently
3. Store compressed version

Example:
Original: 768 dimensions × 4 bytes = 3KB per vector
Compressed: 768/16 quantized to 1 byte = 48 bytes per vector
Compression: 64x!

Pros:
├─ Extreme memory efficiency
├─ Fast distance computation
├─ 1B vectors becomes manageable
└─ Can combine with HNSW

Cons:
├─ Information loss
├─ Lower recall (~85%)
└─ More complex

When: Scale to billions, memory critical
```

### Comparison Matrix

```
Index    | Recall | Speed   | Memory | Inserts | Scale     | Complexity
─────────|--------|---------|--------|---------|-----------|────────
Flat     | 100%   | Slow    | High   | Fast    | <100K     | Simple
HNSW     | 95-99% | Fast    | Medium | Medium  | <100M     | Medium
IVF      | 90-98% | Medium  | Low    | Medium  | <1B       | Medium
PQ       | 85-95% | Fast    | Very Low| Fast   | <1B       | Complex
HNSW+PQ  | 90-98% | Very Fast| Very Low| Medium | 1B+      | Complex

Recommendation:
├─ <1M vectors: HNSW
├─ 1M-100M: HNSW with PQ
├─ 100M+: IVF + PQ
└─ If unsure: Start HNSW, scale to HNSW+PQ
```

---

## 🏗️ RAG (Retrieval-Augmented Generation) Pipeline

### Full Workflow

```
Phase 1: Indexing (Offline)
├─ Documents → Chunk (500 tokens each)
├─ Chunk → Embed (all-mpnet model)
├─ Store: {id, chunk_text, embedding, metadata}
├─ Index: HNSW over embeddings
└─ Time: ~10 tokens/sec per doc

Phase 2: Query (Online)
├─ User query: "How does photosynthesis work?"
├─ Embed query (same model)
├─ Search vector DB: Find top-K (e.g., 5) similar chunks
├─ LLM context: Query + top 5 chunks
├─ LLM response: Answer based on chunks
└─ Time: <500ms for end-to-end

Example Implementation:
```python
from sentence_transformers import SentenceTransformer
import pinecone

# Initialize
model = SentenceTransformer('all-mpnet-base-v2')
pinecone.init(api_key="xxx")
index = pinecone.Index("documents")

# Indexing
documents = load_documents()
for i, doc in enumerate(documents):
    chunks = chunk_text(doc, size=500)
    for j, chunk in enumerate(chunks):
        embedding = model.encode(chunk)
        index.upsert((f"{i}_{j}", embedding, {"text": chunk}))

# Querying
query = "How does photosynthesis work?"
query_embedding = model.encode(query)
results = index.query(query_embedding, top_k=5)
context = "\n".join([r['metadata']['text'] for r in results])
answer = llm.complete(f"{query}\n\nContext:\n{context}")
```
```

### Chunking Strategy

```
Chunk Size (tokens):
├─ 256: Too small (not enough context)
├─ 512: Good balance (most common)
├─ 1024: Better context (more overlap needed)
└─ 2048: Large (fewer chunks, less granular)

Overlapping:
├─ No overlap: Chunks isolated, may miss context
├─ 50 tokens: Smooth transitions
├─ 100 tokens: Safe overlaps
└─ Rule: overlap = chunk_size / 4

Example:
Chunk 1: tokens 0-512
Chunk 2: tokens 256-768 (50% overlap)
Chunk 3: tokens 512-1024 (50% overlap)
```

---

## 💾 Vector Database Comparison

```
System      | Type    | Scale   | Latency | Cost      | Setup
────────────|─────────|─────────|─────────|───────────|────────
Pinecone    | Managed | 1B      | <100ms  | $$$$      | Easiest
Weaviate    | OSS     | 100M    | 50-200ms| $         | Medium
Milvus      | OSS     | 1B      | 50-200ms| $         | Hard
Qdrant      | OSS     | 1B      | 50-100ms| $         | Medium
PgVector    | OSS     | 10M     | 100-500ms| $        | Easy (PG)

When Pinecone (Managed):
├─ Don't want operations overhead
├─ Budget allows cloud cost
├─ Need <100ms latency globally
└─ 1B+ vectors

When Open-Source (Weaviate/Milvus):
├─ Cost-sensitive
├─ Control infrastructure
├─ Self-host in Kubernetes
└─ 100M-1B vectors
```

---

## ❓ Comprehensive Interview Q&A

**Q: Design semantic search for 10M documents (product search)**

A:
```
Requirements:
├─ 10M documents (medium scale)
├─ Sub-500ms latency
├─ 100 QPS peak
├─ 95%+ recall

Architecture:

Indexing:
├─ Documents → Chunks (500 tokens)
├─ Chunks: 10M docs × 2 chunks = 20M chunks
├─ Embed: all-mpnet-base-v2 (768 dim)
├─ Storage: 20M × 768 × 4 bytes = 60GB
└─ Index: HNSW with M=16, efConstruction=200

Vector DB:
├─ Milvus or Weaviate (OSS)
├─ Cluster: 3 nodes × 30GB RAM = 90GB total
├─ Replication: 2x (HA)
├─ Partitioning: By product category

Query Path:
1. User search: "best wireless headphones"
2. Embed query: [768-dim vector]
3. HNSW search: O(log 20M) ≈ 100 comparisons
4. Return top-5 chunks
5. Display results
Latency: ~50ms

Optimization:
├─ Cache: Top 1000 queries (80/20 rule)
├─ Batch: Multiple queries if needed
├─ Approximate: Use lower efSearch for speed
└─ Monitoring: Recall, latency, QPS
```

**Q: Embedding dimension selection (384 vs. 768 vs. 1536)**

A:
```
Trade-off Analysis:

384 Dimensions (all-MiniLM):
├─ Vector size: 384 × 4 = 1.5KB
├─ Storage for 1M: 1.5GB
├─ Speed: 100 embeddings/sec
├─ Quality: 80% of full model
├─ Latency: <10ms query

768 Dimensions (all-mpnet):
├─ Vector size: 768 × 4 = 3KB
├─ Storage for 1M: 3GB
├─ Speed: 50 embeddings/sec
├─ Quality: 90-95% of full model
├─ Latency: ~20ms query

1536 Dimensions (OpenAI ada):
├─ Vector size: 1536 × 4 = 6KB
├─ Storage for 1M: 6GB
├─ Speed: Via API (100-500ms)
├─ Quality: 95-99% (very good)
├─ Latency: ~100ms query + API

Decision Framework:
├─ If <1M vectors: Use 768 (quality matters)
├─ If 10M+ vectors: Use 384 (storage matters)
├─ If cost-critical: Use 384 (cheap)
├─ If accuracy-critical: Use 768 (balanced)
├─ If have OpenAI: Use 1536 (already embedded)

Recommendation for most cases:
├─ Start: 768 (all-mpnet)
├─ Scale: 384 (if storage becomes issue)
├─ Premium: 1536 (if accuracy critical)
```

**Q: How to handle out-of-domain queries?**

A:
```
Scenario: User searches for something not in corpus

Example:
Corpus: Product catalog (electronics)
Query: "How do I get to the moon?"

Solutions:

1. Threshold-based (Reject low similarity):
   ├─ min_similarity = 0.5
   ├─ If top result < 0.5, return "No results"
   ├─ Simple, effective
   └─ Threshold tuning (0.4-0.7 typical)

2. Semantic clustering (Detect out-of-domain):
   ├─ Embed all documents
   ├─ Compute density in vector space
   ├─ Sparse areas = out-of-domain
   ├─ Return "No results" for sparse
   └─ More sophisticated

3. Hybrid (Similarity + diversity):
   ├─ Top-K results
   ├─ Ensure diversity (not all similar)
   ├─ If all from one cluster = likely out-of-domain
   └─ Return results OR "No results"

Implementation:
```python
def search_with_threshold(query, top_k=5, min_similarity=0.5):
    query_vec = embed(query)
    results = index.query(query_vec, top_k=top_k)
    
    # Filter by similarity threshold
    filtered = [r for r in results if r['score'] > min_similarity]
    
    if not filtered:
        return {"status": "no_results", "message": "No relevant documents"}
    
    return {"status": "success", "results": filtered}
```

Tuning:
├─ For aggressive filtering: threshold = 0.6-0.7
├─ For lenient: threshold = 0.4-0.5
├─ Monitor: False negatives (rejecting valid queries)
└─ A/B test threshold values
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Design semantic search" → Do you know chunking, embeddings, indexing?
- "Dimension selection" → Do you understand quality vs. scale trade-off?
- "1B vectors" → Do you know PQ, IVF, clustering?
- "Out-of-domain" → Do you think about threshold, edge cases?

**How to answer:**
1. **Clarify:** Scale, latency SLA, recall target
2. **Chunking:** Size (512 tokens), overlapping (50 tokens)
3. **Embedding:** Model selection (all-mpnet) and dimension trade-offs
4. **Indexing:** HNSW for scale <100M, HNSW+PQ for 1B+
5. **Latency:** Cache, approximate search, monitoring
6. **Edge cases:** Out-of-domain, diversity, threshold tuning

---

**Last updated:** 2026-05-22
