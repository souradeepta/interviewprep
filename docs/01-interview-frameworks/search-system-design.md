# Search System Design: Building Fast, Relevant Search

Master search system architecture from indexing to ranking.

---

## Full-Text Search Components

### 1. Indexing

```
Document collection
    ↓
Tokenize (break into words)
    ↓
Remove stopwords (the, a, an)
    ↓
Normalize (lowercase, stemming)
    ↓
Create inverted index

Inverted Index:
"database" → [doc1, doc5, doc8]
"search" → [doc2, doc3, doc8]
"system" → [doc1, doc4, doc5]
```

### 2. Querying

```
User query: "database search system"
    ↓
Tokenize: ["database", "search", "system"]
    ↓
Look up each in inverted index
    ↓
Combine results: [doc1, doc2, doc3, doc4, doc5, doc8]
    ↓
Rank by relevance
    ↓
Return top-K
```

### 3. Ranking

**TF-IDF (Term Frequency - Inverse Document Frequency)**

```
Score = TF(term, doc) * IDF(term)

TF: How often term appears in doc (frequent = higher score)
IDF: How rare term is across all docs (rare = higher score)

"the database" in doc about databases:
- TF("the") = high (appears often), IDF("the") = low (common word)
- TF("database") = high, IDF("database") = high (specific word)
```

---

## Search System Architecture

### Small Scale (< 1M documents)

```
Users
  ↓
API Server
  ↓
Elasticsearch (indexing + querying)
  ↓
Database
```

### Large Scale (> 100M documents)

```
Users
  ↓
API Gateway
  ↓
Query Service (parse query, ranking logic)
  ↓
├─ Index Searcher (lookup inverted index)
│  └─ Elasticsearch (distributed)
├─ Ranker (TF-IDF, ML model, signals)
├─ Filter (category, date, price)
└─ Cache (popular queries)
```

---

## Search Technologies

### Elasticsearch

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['localhost:9200'])

# Index a document
doc = {
    'title': 'Introduction to Machine Learning',
    'content': 'Machine learning is a field of study...',
    'author': 'John Doe',
    'date': '2024-01-15'
}
es.index(index='articles', doc_type='_doc', body=doc)

# Search
results = es.search(
    index='articles',
    body={
        'query': {
            'multi_match': {
                'query': 'machine learning',
                'fields': ['title', 'content']
            }
        },
        'size': 10
    }
)
```

### Inverted Index Implementation

```python
class InvertedIndex:
    def __init__(self):
        self.index = {}  # word → set of doc_ids
    
    def add_document(self, doc_id, text):
        words = self.tokenize(text)
        for word in words:
            if word not in self.index:
                self.index[word] = set()
            self.index[word].add(doc_id)
    
    def search(self, query):
        words = self.tokenize(query)
        result = None
        for word in words:
            docs = self.index.get(word, set())
            if result is None:
                result = docs
            else:
                result &= docs  # AND: intersection
        return result or set()
    
    def tokenize(self, text):
        return text.lower().split()
```

---

## Advanced Search Features

### Auto-complete

```
Prefix-based search using Trie or Redis
User types: "dat"
Suggestions: ["database", "data science", "data analytics"]

Implementation: Trie for O(k) where k = suggestion length
```

### Spell Correction

```
User types: "dtabase"
Did you mean: "database"

Implementation: Edit distance or probabilistic
```

### Faceted Search

```
Results: 1000 documents about "programming"
Facets:
- Language: Python (300), Java (200), ...
- Level: Beginner (400), Advanced (600)
- Topic: Web (250), Mobile (180), ...
```

---

## Ranking Signals

**Beyond TF-IDF:**

```
Score = TF-IDF + Signals

Signals:
- Freshness: Recent docs ranked higher
- Popularity: Popular docs (more clicks) ranked higher
- Authority: From trusted sources
- User history: Docs similar to user's past searches
- Personalization: User preferences
- Click-through rate (CTR): If available
- Dwell time: How long user stayed on result
```

---

## Search System Checklist

- ✓ Inverted index for fast lookup
- ✓ Tokenization and normalization
- ✓ TF-IDF or similar ranking
- ✓ Distributed indexing (sharded by doc_id)
- ✓ Query caching (popular queries)
- ✓ Real-time or near-real-time indexing
- ✓ Relevance tuning (human evaluation)
- ✓ Spell correction
- ✓ Auto-complete suggestions
- ✓ Faceted search options
- ✓ Analytics on search queries
- ✓ A/B testing ranking algorithms

