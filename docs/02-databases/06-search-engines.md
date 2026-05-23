# Search Engines & Full-Text Search

Building fast, ranked search systems for documents, products, and content.

---

## 🔍 Inverted Index Fundamentals

### How Inverted Indexes Work

```
Document Collection:
Doc 1: "The quick brown fox"
Doc 2: "The lazy dog"
Doc 3: "A quick fox"

Traditional Forward Index:
Doc 1 → ["The", "quick", "brown", "fox"]
Doc 2 → ["The", "lazy", "dog"]
Doc 3 → ["A", "quick", "fox"]

Inverted Index (Word → Documents):
"the" → [Doc1, Doc2]          (DF=2, IDF=low)
"quick" → [Doc1, Doc3]        (DF=2, IDF=low)
"brown" → [Doc1]              (DF=1, IDF=high)
"fox" → [Doc1, Doc3]          (DF=2, IDF=low)
"lazy" → [Doc2]               (DF=1, IDF=high)
"dog" → [Doc2]                (DF=1, IDF=high)
"a" → [Doc3]                  (DF=1, IDF=high, stop word removed)

Query: "quick fox"
└─ Lookup: quick → [Doc1, Doc3]
           fox → [Doc1, Doc3]
└─ Intersection: [Doc1, Doc3]
└─ Rank by BM25
```

### Inverted Index Storage

```
Posting List Structure:
Word: "quick"
├─ Posting: [(doc_id=1, positions=[1], freq=1),
             (doc_id=3, positions=[1], freq=1)]

Compression (for large indexes):
├─ Delta encoding: Store differences (doc_id gap)
│  Original: [1, 3, 47, 89]
│  Delta: [1, 2, 44, 42]
│  Stored as VInt (variable-length integers)
├─ Bit-packing: Store multiple postings per byte
└─ Result: 100x compression of posting lists
```

---

## ⚖️ Search Systems Comparison

```
System          | Latency | Scale    | Setup | Features     | Cost
────────────────|─────────|──────────|───────|──────────────|──────
Elasticsearch   | 50-200ms| 1B docs  | Medium| Rich, complex| Medium
Solr            | 50-200ms| 1B docs  | Hard  | Apache std   | Low
Meilisearch     | <100ms  | 100M docs| Easy  | Simple, fast | Medium
Algolia         | <100ms  | 100M docs| None  | Managed      | High
OpenSearch      | 50-200ms| 1B docs  | Medium| AWS managed  | Medium

When Elasticsearch:
├─ Complex queries needed
├─ Analytics + search
├─ 1B+ documents
├─ Team familiar with ELK
└─ Enterprise requirements

When Meilisearch:
├─ Simple product search
├─ Fast typo tolerance
├─ < 100M documents
├─ Minimal configuration
└─ Low operational overhead

When Algolia:
├─ SaaS preferred
├─ Don't want to manage infrastructure
├─ Real-time indexing needed
└─ Budget not constrained
```

---

## 🎯 Ranking Algorithms

### TF-IDF (Term Frequency-Inverse Document Frequency)

```
Score(doc, query) = Σ TF(term, doc) × IDF(term)

TF (Term Frequency): How often term appears in doc
├─ Raw count: "quick" appears 3 times → TF = 3
├─ Log normalized: TF = 1 + log(count)
├─ Boolean: TF = 1 if present, 0 otherwise

IDF (Inverse Document Frequency): How rare across corpus
├─ N = total documents = 1 million
├─ DF = documents containing term = 10000
├─ IDF = log(N / DF) = log(1M / 10K) = 4.6

Limitations:
├─ Doesn't consider term position
├─ Doesn't handle phrase queries well
├─ Doesn't account for document length
└─ Older algorithm (before BM25)
```

### BM25 (Best Match 25) - Industry Standard

```
Score(doc, q) = Σ IDF(qi) × (f(qi,D) × (k1 + 1)) / 
                (f(qi,D) + k1 × (1 - b + b × |D|/avgdl))

f(qi, D) = frequency of query term in document
|D| = document length
avgdl = average document length
k1 = saturation parameter (default 1.2)
b = length normalization (default 0.75)

Example Calculation:
doc = "quick brown fox jumps over lazy dog"
query = "quick fox"

Score = IDF("quick") × contribution("quick", doc) +
        IDF("fox") × contribution("fox", doc)
      = 3.0 × (1/(1+1.2)) + 2.5 × (1/(1+1.2))
      = 3.0 × 0.45 + 2.5 × 0.45
      = 2.48

Advantages over TF-IDF:
├─ Handles term frequency saturation
├─ Accounts for document length
├─ Better phrase matching
└─ Industry standard (Elasticsearch default)
```

### Custom Scoring

```
Elasticsearch Query:
{
  "query": {
    "bool": {
      "must": [
        {"match": {"title": "quick fox"}}
      ]
    }
  },
  "rescore": {
    "window_size": 50,
    "query": {
      "rescore_query": {
        "match": {
          "title": {
            "query": "quick fox",
            "boost": 2.0
          }
        }
      },
      "query_weight": 0.7,
      "rescore_query_weight": 1.2
    }
  }
}

Scoring boosters:
├─ Title match: +1.0 (higher weight)
├─ Popularity: +log(num_views)
├─ Recency: +exp(-days_old / 30)
├─ Quality: +rating / 5.0
└─ Combined: BM25 + (boost factors)
```

---

## 🔤 Text Processing Pipeline

```
Input: "The Quick Brown Fox!"

1. Lowercasing:
   "the quick brown fox!"

2. Tokenization (Splitting):
   ["the", "quick", "brown", "fox"]

3. Stop Word Removal:
   ["quick", "brown", "fox"]
   (Removed: "the", punctuation)

4. Stemming/Lemmatization:
   ["quick", "brown", "fox"]
   (In English, already stemmed)
   
   Examples:
   ├─ running, runs, runner → "run"
   ├─ playing, plays, player → "play"
   └─ walked, walks, walking → "walk"

5. Custom Filters (Language-dependent):
   ├─ Synonyms: "quick" → ["quick", "fast"]
   ├─ Phrase handling: "new york" → single token
   └─ Normalization: "naïve" → "naive"

6. Index:
   Inverted index with processed tokens
```

---

## 🏷️ Faceted Search (Filtering)

### Implementation

```
Query: "laptop"

Aggregations:
{
  "brand_facet": {
    "terms": {
      "field": "brand.keyword",
      "size": 10
    }
  },
  "price_ranges": {
    "range": {
      "field": "price",
      "ranges": [
        {"to": 500},
        {"from": 500, "to": 1000},
        {"from": 1000, "to": 2000},
        {"from": 2000}
      ]
    }
  },
  "rating": {
    "range": {
      "field": "rating",
      "ranges": [
        {"from": 4.0}
      ]
    }
  }
}

Results:
{
  "aggregations": {
    "brand_facet": {
      "buckets": [
        {"key": "Apple", "doc_count": 1250},
        {"key": "Dell", "doc_count": 890},
        {"key": "HP", "doc_count": 750},
        ...
      ]
    },
    "price_ranges": {
      "buckets": [
        {"key": "*-500", "doc_count": 150},
        {"key": "500-1000", "doc_count": 800},
        {"key": "1000-2000", "doc_count": 950},
        {"key": "2000-*", "doc_count": 100}
      ]
    }
  }
}
```

### Filtering with Facets

```
User interaction:
1. Search for "laptop"
2. Click facet: Brand = Apple
3. Click facet: Price 1000-2000

Query becomes:
{
  "query": {
    "bool": {
      "must": [
        {"match": {"title": "laptop"}}
      ],
      "filter": [
        {"term": {"brand.keyword": "Apple"}},
        {"range": {"price": {"gte": 1000, "lte": 2000}}}
      ]
    }
  }
}
```

---

## 🔍 Query Types & Use Cases

### Full-Text Search
```
Query: "fast laptop for programming"

Tokenized: ["fast", "laptop", "programming"]
Matches documents containing all or some terms
Score: BM25 relevance
```

### Phrase Search
```
Query: "machine learning"

Must match exact phrase (words adjacent)
Elasticsearch: {"match_phrase": {"content": "machine learning"}}
More restrictive than full-text
```

### Prefix/Autocomplete
```
Query: "quic" (user typing)

Matches words starting with "quic":
├─ quick
├─ quicker
├─ quickly
└─ quicksand

Implementation:
├─ Trie (in-memory, < 1M suggestions)
├─ Prefix query (Elasticsearch)
├─ N-gram tokenization (flexible)
```

### Fuzzy Search (Typo Tolerance)
```
Query: "quik" (typo for "quick")

Edit distance ≤ 1:
├─ quick (1 substitution)
├─ quit (1 deletion)
└─ quill (1 substitution)

Elasticsearch: {"match": {"field": {"query": "quik", "fuzziness": "AUTO"}}}
```

---

## ❓ Comprehensive Interview Q&A

**Q: Design search for e-commerce (10M products, 1M/day searches)**

A:
```
Requirements:
├─ 10M products (medium scale)
├─ 1M searches/day (~10/sec peak)
├─ Faceted search (brand, price, rating)
├─ Autocomplete on search box
├─ Typo tolerance

Architecture:

Elasticsearch Cluster:
├─ 3 nodes (HA setup)
├─ Primary + 2 replicas
├─ Index per product type (optional)

Indexing:

CREATE INDEX products {
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "name": {
        "type": "text",
        "analyzer": "standard"
      },
      "description": {"type": "text"},
      "brand": {"type": "keyword"},
      "category": {"type": "keyword"},
      "price": {"type": "float"},
      "rating": {"type": "float"},
      "popularity": {"type": "integer"}
    }
  }
}

Search Query:

{
  "size": 20,
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "gaming laptop",
            "fields": ["name^2", "description"]
          }
        }
      ],
      "filter": [
        {"term": {"brand.keyword": "Apple"}},
        {"range": {"price": {"gte": 1000, "lte": 2000}}},
        {"range": {"rating": {"gte": 4.0}}}
      ]
    }
  },
  "aggs": {
    "brands": {"terms": {"field": "brand.keyword"}},
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          {"to": 500},
          {"from": 500, "to": 1000},
          {"from": 1000, "to": 2000},
          {"from": 2000}
        ]
      }
    }
  }
}

Autocomplete:

Separate index for suggestions:
├─ Suggestions: ["gaming laptop", "gaming laptop stand", ...]
├─ Using completion type
├─ Fast prefix queries
├─ Weight by popularity

Query Autocomplete:
{
  "suggest": {
    "product-suggest": {
      "prefix": "gam",
      "completion": {
        "field": "suggestion",
        "size": 5
      }
    }
  }
}

Performance:
├─ Search: ~50ms (BM25 scoring)
├─ Facets: ~20ms (aggregations)
├─ Autocomplete: <10ms (completion index)
└─ Total: ~80ms user-facing latency
```

**Q: Autocomplete for search box (1M suggestions, <100ms latency)**

A:
```
Approach 1: In-Memory Trie (Simplest)
├─ Size: 1M suggestions × 50 bytes = 50MB
├─ Lookup: O(m) where m = prefix length
├─ Build: O(m log n) for insertion
├─ Latency: <1ms
├─ Limitation: Single machine, memory-bound

Approach 2: Elasticsearch Completion Index (Scalable)
├─ Data structure: FST (Finite State Transducer)
├─ Size: Compressed, ~100MB
├─ Lookup: O(log n)
├─ Latency: <10ms distributed
├─ Scalable: Multiple machines

Approach 3: Dedicated Service (Redis)
├─ Sorted set with score = popularity
├─ Data: ZADD suggestions "gaming laptop" 1000
├─ Query: ZRANGE suggestions 0 gam* (prefix)
├─ Latency: <5ms
├─ Memory: ~50-100MB
├─ Limitation: Limited prefix matching

Implementation (Elasticsearch):

Product Doc:
{
  "name": "gaming laptop",
  "suggestion": {
    "input": ["gaming laptop", "laptop gaming"],
    "weight": 100  (popularity score)
  }
}

Query:
{
  "suggest": {
    "my-suggest": {
      "prefix": "gam",
      "completion": {
        "field": "suggestion",
        "size": 10,
        "skip_duplicates": true
      }
    }
  }
}

Response: ["gaming laptop", "gaming desktop", ...]
```

**Q: Design full-text search with typo tolerance**

A:
```
Requirements:
├─ Find "quik" → "quick"
├─ Find "lpatop" → "laptop"
├─ Latency: <200ms

Approach: Elasticsearch with Fuzziness

Query:
{
  "query": {
    "match": {
      "name": {
        "query": "quik laptop",
        "fuzziness": "AUTO",
        "prefix_length": 0  (typo at start)
      }
    }
  }
}

Fuzziness levels:
├─ "AUTO": Adjust based on term length
│  ├─ Length 1-2: exact match
│  ├─ Length 3-5: 1 edit
│  └─ Length 6+: 2 edits
├─ "1": Allow 1 edit distance
├─ "2": Allow 2 edits

Edit Distance Definition:
├─ Substitution: "quik" → "quick"
├─ Insertion: "lapto" → "laptop"
├─ Deletion: "quickk" → "quick"

Performance Tuning:
├─ prefix_length: Skip exact prefix match (faster)
├─ max_expansions: Limit candidates (100-1000)
└─ boost exact match: {"match": {"name": {"query": "quick", "boost": 2}}}
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Design search for X" → Do you know inverted indexes, BM25, facets?
- "Typo tolerance" → Do you understand fuzzy matching, edit distance?
- "Autocomplete" → Do you know completion indexes, prefix queries?
- "1M searches/day" → Do you know scaling (sharding, replicas)?

**How to answer:**
1. **Understand search type:** Full-text, phrase, faceted, autocomplete
2. **Index design:** Schema, analyzers, tokenization
3. **Query design:** Match type, filters, aggregations
4. **Ranking:** BM25 fundamentals, custom boosting
5. **Scale:** Sharding strategy, replica count
6. **Optimize:** Latency targets, facet cardinality

---

**Last updated:** 2026-05-22
