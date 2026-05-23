# Search Engines & Full-Text Search

Building fast search systems.

---

## 🔍 Full-Text Search

### Inverted Index

Traditional index:
```
Doc 1: "The quick brown fox"
Doc 2: "The lazy dog"
```

Inverted index:
```
"the" → [Doc 1, Doc 2]
"quick" → [Doc 1]
"brown" → [Doc 1]
"fox" → [Doc 1]
"lazy" → [Doc 2]
"dog" → [Doc 2]
```

Query "quick fox" → Doc 1 (contains both)

---

## 📚 Search Engines

**Elasticsearch:** Distributed search, analytics
**Solr:** Java-based search
**Meilisearch:** Fast, minimal config
**Algolia:** Cloud search API

---

## 🎯 Ranking

```
Score = TF-IDF * BM25 * Custom

TF-IDF:
  TF: How often term appears in doc
  IDF: How rare term is across docs
  
BM25: Improved TF-IDF (industry standard)

Custom: Boost popular/recent docs
```

---

## 🔤 Text Processing

```
"The Quick Brown Fox!"
→ Lowercase: "the quick brown fox!"
→ Tokenize: ["the", "quick", "brown", "fox"]
→ Stop words: ["quick", "brown", "fox"]
→ Stemming: ["quick", "brown", "fox"]
(Already stemmed in this example)
```

---

## 🏷️ Faceted Search

```
Query: "laptop"
Filters:
  - Brand: [Apple, Dell, HP]
  - Price: $500-$2000
  - Rating: 4+ stars

Results grouped by facets
```

---

## ❓ Interview Q&A

**Q: Design search for e-commerce (10M products)**
A: Elasticsearch cluster. Index product fields. BM25 ranking. Facets for filtering.

**Q: Autocomplete for search box (1M suggestions)**
A: Trie or prefix tree in memory. Or Elasticsearch with prefix query.

---

**Last updated:** 2026-05-22
