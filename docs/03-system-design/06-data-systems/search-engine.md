# Search Engine

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Users expect to type a few words and get back the most relevant results from a corpus of billions
of documents in under 200 milliseconds. Full-table SQL LIKE queries are unusable at this scale —
scanning 1B rows takes minutes. A search engine pre-processes documents at index time to build an
inverted index: a mapping from each term to the list of documents containing it. At query time,
terms are looked up in microseconds and result lists are intersected, ranked, and paginated.

The design challenges are: keeping the index up-to-date with document changes (write path), serving
10K queries per second with sub-100ms P99 latency (read path), handling typos and synonyms, and
distributing the index across machines when a single node can't hold it all.

## Functional Requirements

- Index documents (title, body, metadata) and make them searchable within seconds
- Return top-K ranked results for a multi-term query with pagination
- Support phrase queries, boolean operators (AND/OR/NOT), and filters (date, category)
- Handle typos (edit distance ≤ 2) and synonyms
- Delete or update documents without a full index rebuild

## Non-Functional Requirements

- **Scale:** 1B documents indexed; 10K QPS search; 1K document updates/sec
- **Latency:** P99 < 100 ms for top-10 results; P50 < 20 ms
- **Availability:** 99.9% (8.7 hr downtime/year); read availability prioritized over index freshness
- **Consistency:** Eventual — new documents visible within 5-10 seconds of indexing

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Documents:          1B docs, avg 10 KB each = 10 TB raw text
Index size:         Inverted index ≈ 20-30% of raw text = 2-3 TB
Postings list size: avg term appears in 10K docs; 1B docs * 100 terms/doc = 100B term-doc pairs
                    Each pair: 4B doc_id + 4B position = 8 bytes → 800 GB postings data
RAM per shard:      Hot index fits in 64-128 GB RAM (frequently accessed terms)
Shards:             3 TB index / 500 GB usable RAM per node = 6 shards minimum → 10 with headroom
QPS per shard:      10K QPS / 10 shards = 1K QPS per shard (easily handled by Lucene)
Update rate:        1K doc/sec * 10 KB = 10 MB/sec ingest
Segment merge:      Lucene segments merge every 10-30 min; temp disk 2× segment size
```

### Architecture Diagram

```
  User Query: "coffee shops near me"
        |
  +-----v------+
  | Query API  |  ← REST gateway, query parsing, spelling correction
  +-----+------+
        |
  +-----v---------+
  | Query Planner |  ← tokenize, expand synonyms, build query tree
  +-----+---------+
        |  fan-out to all shards
  +-----v--+  +--------+  +--------+
  | Shard 0|  | Shard 1|  | Shard 9|   ← each holds 100M docs
  | Lucene |  | Lucene |  | Lucene |
  +--+-----+  +----+---+  +---+----+
     |              |          |
  +--v--------------v----------v---+
  |       Result Merger / Ranker   |  ← merge top-K per shard, global re-rank
  +----------------+---------------+
                   |
            +------v------+
            | Result Cache|  ← Redis, TTL 60s, key = normalized query hash
            +------+------+
                   |
              Response to User

Write Path:
  Document → Indexer Service → Kafka topic "doc.updates"
           → Index Workers (one per shard) → Lucene segment flush → segment merge
```

### Data Model

```
# Inverted Index (conceptual — Lucene manages actual storage)
term          →  postings_list
"coffee"      →  [(doc_id=101, freq=3, positions=[2,15,42]),
                  (doc_id=504, freq=1, positions=[7]), ...]
"machine"     →  [(doc_id=12,  freq=5, positions=[1,3,8,11,22]), ...]

# Document store (forward index — for snippet generation)
doc_id: 101
  title:       "Best Coffee Machines 2024"
  body:        "..."   (stored compressed, retrieved for snippet)
  url:         "https://..."
  indexed_at:  2024-01-15T12:00:00Z
  category:    "shopping"
  boost:       1.2     (editorial boost for high-quality sources)

# Schema (Elasticsearch-style mapping)
{
  "mappings": {
    "properties": {
      "title":      { "type": "text", "analyzer": "english" },
      "body":       { "type": "text", "analyzer": "english", "store": false },
      "url":        { "type": "keyword" },
      "indexed_at": { "type": "date" },
      "category":   { "type": "keyword" },
      "boost":      { "type": "float" }
    }
  }
}
```

### API Design

```
# Search API
GET /search?q=coffee+machine&page=0&size=10&category=shopping&sort=relevance
  Response: 200 {
    total_hits: 1_240_000,
    took_ms: 18,
    results: [
      { doc_id, title, url, snippet, score, indexed_at },
      ...
    ],
    next_page_token: "base64-encoded-search-after"
  }

# Document indexing API
POST /documents
  Body: { doc_id, title, body, url, category, boost }
  Response: 202 { status: "accepted", estimated_visible_in_seconds: 10 }

PUT  /documents/{doc_id}
  Body: { title, body, ... }
  Response: 202 { status: "accepted" }

DELETE /documents/{doc_id}
  Response: 202 { status: "accepted" }   -- soft-delete; removed on next segment merge

# Suggest API (autocomplete)
GET /suggest?prefix=coffe&limit=10
  Response: 200 { suggestions: ["coffee", "coffee machine", "coffee beans", ...] }
```

### Basic Scaling

- **Sharding:** Divide document corpus across N shards; each shard is a complete Lucene index for
  its partition; search fans out to all shards, merges results (scatter-gather)
- **Replicas:** 2 replicas per shard for read throughput and HA; replicas serve searches while
  primary ingests writes
- **Result cache:** Cache top-100 most frequent queries in Redis (TTL 60s); cache key = normalized
  query + filters; 80% of QPS typically served from cache for popular terms
- **Segment merging:** Background merge consolidates many small segments into fewer large ones,
  improving read performance; do not merge during peak hours (schedule merges nightly)

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Search node sizing (Elasticsearch data node):
  CPU:    32 vCPUs; query parsing + BM25 scoring is CPU-intensive
          At 1K QPS/shard and 20ms avg per query: 1000 * 0.020 = 20 CPU-seconds/sec → 20 vCPUs
  RAM:    256 GB: 128 GB heap (Lucene field data/doc values) + 128 GB OS page cache for segments
          Target: entire "hot" index fits in page cache (cache miss → disk read → 10× slower)
  Disk:   4 TB NVMe per node; 300 GB/shard index * 10 shards * 1.5 (merge temp space) ≈ 4.5 TB
  Net:    10 Gbps; per query result payload ~100 KB * 1K QPS = 100 MB/sec well within limit

Indexer (write path) node:
  1K doc/sec * 10 KB/doc = 10 MB/sec parsing + tokenization: 4 vCPUs sufficient
  Segment flush: every 1 sec (near real-time); merge every 5 min (background)
  Kafka consumer: one indexer per shard partition

Query latency breakdown (P99 budget = 100 ms):
  Network (client → gateway):         5 ms
  Query parsing + synonym expansion:  2 ms
  Fan-out to 10 shards (parallel):   40 ms  ← dominant: disk seek if page cache miss
  Merge + re-rank top-10:             3 ms
  Network (gateway → client):         5 ms
  Total:                             55 ms   (45 ms headroom for cache misses)
```

### Failure Modes

```
FAILURE: Search shard node goes down
  Detection:    Cluster health check every 5 sec; node marked DEAD after 2 missed heartbeats
  Mitigation:   Traffic routed to replica automatically; shard re-allocated to new node
                Re-allocation copies segment files from another node: ~10 min for 300 GB shard
  Query impact: Queries to that shard fail → partial results (show results from 9/10 shards)
                Decision: return partial results with warning vs. return error
                Prefer partial: better UX for most queries

FAILURE: Indexer falls behind (high document update rate spike)
  Detection:    Kafka consumer lag > 100K messages (> 100 sec at 1K/sec)
  Mitigation:   Scale out indexer instances (they consume from separate partitions)
                Throttle index merges (defer expensive merges)
  Risk:         Stale index — users don't see recent documents until lag clears
  SLO:          Index freshness SLO = 95% of docs visible within 10 sec

FAILURE: Inverted index corruption (disk failure during write)
  Prevention:   Lucene uses write-ahead log (translog) before segment commit
  Recovery:     Replay translog on node restart; data since last commit recovered
  Mitigation:   Replicas on separate nodes ensure corruption on one doesn't lose data

FAILURE: Query amplification (one term matches 500M docs — e.g., "the")
  Detection:    Postings list size > threshold (100M entries)
  Mitigation:   Stop-word list filters common terms from index
                max_clause_count limit on boolean query fan-out
                TermFrequency threshold: skip terms with IDF near zero
```

### Consistency Boundaries

```
WRITE → VISIBLE LATENCY:
  Document indexed → Lucene segment flushed (every 1 sec, NRT) → visible on primary shard
  Primary → Replica replication: 1-5 sec additional
  Total: 2-10 sec from ingest to searchable (eventual consistency)

DELETE CONSISTENCY:
  Deleted docs are marked with a "live docs" bitset (soft delete)
  Still returned by index scan until segment merge expunges them
  Hard expunge: forced merge (expensive) or wait for next scheduled merge
  Risk: deleted doc appears in results briefly after deletion API returns 202

RANKING CONSISTENCY:
  Different replicas may have slightly different segment states → same query may return
  different scores on different replicas (read repair not applicable to search)
  Acceptable: ranking differences are < 1% in practice; deterministic for same replica
```

### Cost Model

```
10 shards, 2 replicas each = 30 nodes total (10 primary, 20 replica)
Node: m6i.8xlarge (32 vCPU, 128 GB RAM, 4 TB NVMe): $1.50/hr

Compute: 30 * $1.50 * 8760                      = $394K/yr
Storage: 30 * 4 TB * $0.10/GB/month * 12        = $144K/yr (NVMe-backed EBS)
Network: 10K QPS * 100 KB response * ~5% cross-AZ = 50 MB/sec * $0.01/GB * 31.5M sec
                                                = $16K/yr
Total:                                          = $554K/yr

Per-query cost: $554K / (10K QPS * 31.5M sec)  = $0.0000018/query ($1.76/million queries)

Optimization levers:
  1. Query result cache (Redis): 80% cache hit rate → effective cost = $0.35/million queries
  2. Tiered replicas: hot shards on NVMe, cold shards on gp3 EBS → 40% storage savings
  3. Spot instances for read replicas: 70% discount → $276K/yr for replica compute
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Elasticsearch (Lucene-based) | Feature-rich; distributed; near real-time; large ecosystem | JVM tuning; GC pauses at scale; complex cluster ops; expensive RAM | General-purpose full-text search, log search, autocomplete |
| Apache Solr (Lucene-based) | Battle-tested; strong faceting; SolrCloud for distribution | Similar JVM issues; slower innovation vs Elasticsearch | Enterprise search, faceted navigation in e-commerce |
| Custom inverted index (PostgreSQL GIN) | No extra infrastructure; ACID on document updates | Slow for large corpora; no horizontal sharding; limited ranking | Small datasets (<10M docs), when full-text is one feature among many |
| Typesense / Meilisearch | Simple ops; typo-tolerance built-in; fast setup | Less mature for PB-scale; fewer enterprise features | Startups, product search, smaller corpora (<100M docs) |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is an inverted index and why does it make search fast?
   → An inverted index maps each term to the list of documents containing it (postings list).
   At query time, we look up the query terms (O(1) hash lookup) and intersect postings lists
   instead of scanning every document. Intersection of two 1M-entry lists takes milliseconds
   vs. minutes for a full-table scan.

2. **(L3)** What is TF-IDF and why does "the" rank lower than "coffee"?
   → TF (term frequency) rewards terms that appear many times in a document. IDF (inverse
   document frequency) penalizes terms that appear in many documents. "The" appears in almost
   all documents → near-zero IDF → low score. "Coffee" is rare → high IDF → high score. BM25
   is a modern improvement on TF-IDF with saturation and field-length normalization.

3. **(L4)** How do you handle index updates without downtime?
   → Lucene uses immutable segments. Updates are: (1) soft-delete old document (mark in live
   docs bitset), (2) append new document to a new segment. Background merge consolidates
   segments and physically removes deleted docs. This allows continuous writes without locking
   the entire index.

4. **(L4)** How would you implement typo correction (did you mean)?
   → Build a dictionary of known terms. For a misspelled query term, compute edit distance
   (Levenshtein) against dictionary terms with distance ≤ 2. At scale, use BK-trees or
   SymSpell for fast nearest-neighbor lookup in the dictionary (O(log N) vs. O(N) brute force).

5. **(L5)** How does scatter-gather work across 10 shards and what is the query latency impact?
   → Each query is broadcast to all 10 shards simultaneously. Each shard returns its local top-K
   results with scores. The coordinator merges all responses (up to 10×K results), globally
   re-ranks by score, and returns the final top-K. Latency is bounded by the slowest shard
   (P99 of max of 10 independent P99s ≈ much worse than single-shard P99). Mitigation: timeout
   slow shards and return partial results.

6. **(L5)** How would you design incremental index updates vs. full rebuild? When does each apply?
   → Incremental: consume document change events from Kafka; update affected posting lists in
   real time. Works for ongoing updates but postings lists become fragmented over time.
   Full rebuild: periodically re-index entire corpus (e.g., nightly) from scratch for a clean
   index; blue-green swap (build new index, atomically switch traffic). Use incremental for
   freshness SLO < 10 sec; full rebuild for schema changes or corruption recovery.

7. **(L5+)** How do you distribute the index when total index size exceeds RAM of all nodes?
   → Horizontal sharding by document range (time-based, hash-based, or alphabetical by URL).
   Each shard is a complete self-contained Lucene index. Hot shards (frequently accessed
   partitions, e.g., recent documents) get more RAM/replicas. Cold shards use tiered storage
   (cheaper HDD nodes or S3-backed). Routing: scatter to all shards for recall; for filtered
   queries (e.g., date range), route only to relevant shards.

## Anti-patterns / Things NOT to Say

- **"Use LIKE '%keyword%' in SQL"** — Full-table scan; unusable beyond 1M rows; no ranking;
  no typo tolerance. Always use a purpose-built inverted index for user-facing search.
- **"Rebuild the full index on every document update"** — At 1K updates/sec, a full rebuild
  would never complete. Use incremental updates via segment append + background merge.
- **"Store the entire index in RAM"** — 3 TB index doesn't fit in RAM. Use OS page cache
  intelligently: frequently accessed segments stay hot in page cache; cold segments read from
  SSD. Tune heap allocation to leave at least 50% of RAM for page cache.
- **"Elasticsearch handles everything — just use it as your primary DB"** — Elasticsearch
  is not a primary database: no ACID transactions, eventual consistency, hard to do point
  lookups efficiently, operational complexity. Use Postgres/MySQL as the source of truth;
  sync to Elasticsearch for search.
- **"One shard per index is fine for 1B documents"** — A single Lucene shard is limited to
  ~2B documents (Integer.MAX_VALUE doc IDs) and practically to a few hundred GB. At 1B
  documents and 3 TB index size, you need multiple shards for memory, throughput, and fault
  isolation.

## Python Implementation (sketch)

```python
import re
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterator

@dataclass
class Document:
    doc_id: int
    title: str
    body: str

@dataclass
class Posting:
    doc_id: int
    term_freq: int
    positions: list[int] = field(default_factory=list)

class InvertedIndex:
    """Minimal in-memory inverted index with BM25 ranking."""

    K1 = 1.5   # BM25 term saturation
    B  = 0.75  # BM25 field-length normalization

    def __init__(self):
        self._index: dict[str, list[Posting]] = defaultdict(list)
        self._doc_store: dict[int, Document] = {}
        self._doc_lengths: dict[int, int] = {}
        self._total_docs = 0
        self._total_terms = 0

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'\w+', text.lower())

    def add_document(self, doc: Document) -> None:
        tokens = self._tokenize(f"{doc.title} {doc.body}")
        self._doc_store[doc.doc_id] = doc
        self._doc_lengths[doc.doc_id] = len(tokens)
        self._total_docs += 1
        self._total_terms += len(tokens)

        freq_map: dict[str, list[int]] = defaultdict(list)
        for pos, token in enumerate(tokens):
            freq_map[token].append(pos)

        for term, positions in freq_map.items():
            self._index[term].append(Posting(doc.doc_id, len(positions), positions))

    def _avg_doc_length(self) -> float:
        return self._total_terms / max(self._total_docs, 1)

    def _bm25_score(self, tf: int, df: int, dl: int) -> float:
        idf = math.log((self._total_docs - df + 0.5) / (df + 0.5) + 1)
        norm_tf = (tf * (self.K1 + 1)) / (
            tf + self.K1 * (1 - self.B + self.B * dl / self._avg_doc_length())
        )
        return idf * norm_tf

    def search(self, query: str, top_k: int = 10) -> list[tuple[float, Document]]:
        terms = self._tokenize(query)
        scores: dict[int, float] = defaultdict(float)

        for term in terms:
            postings = self._index.get(term, [])
            df = len(postings)
            for p in postings:
                dl = self._doc_lengths[p.doc_id]
                scores[p.doc_id] += self._bm25_score(p.term_freq, df, dl)

        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        return [(score, self._doc_store[doc_id]) for doc_id, score in ranked]


# Usage
idx = InvertedIndex()
for doc in [
    Document(1, "Best Coffee Machines 2024", "Review of top espresso and drip machines"),
    Document(2, "Coffee Beans Guide", "Arabica vs Robusta: which bean to buy"),
    Document(3, "Tea vs Coffee", "Comparing caffeine and health benefits"),
]:
    idx.add_document(doc)

results = idx.search("coffee machine", top_k=3)
for score, doc in results:
    print(f"{score:.3f}  [{doc.doc_id}] {doc.title}")
# 1.234  [1] Best Coffee Machines 2024
# 0.987  [2] Coffee Beans Guide
# 0.543  [3] Tea vs Coffee
```
