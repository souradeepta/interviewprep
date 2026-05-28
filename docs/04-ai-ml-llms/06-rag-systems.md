# RAG Systems — Retrieval-Augmented Generation

**Level:** L4-L5
**Time to read:** ~20 min

Combining LLMs with knowledge bases for better answers.

---

## 🎯 The Problem

LLMs have knowledge cutoff and can't access proprietary/real-time data.

```
User: "What is the current weather in San Francisco?"
LLM: "I don't know, my knowledge cuts off at April 2024."

Better: Retrieve current weather data, include in prompt.
```

---

## 🏗️ RAG Architecture

### Simple RAG Pipeline

```
1. User Query: "How do I reset my password?"

2. Retrieval:
   - Search knowledge base (docs, FAQs, etc.)
   - Find: "Password reset guide.pdf", "FAQ #42"
   - Return top K relevant documents

3. Augmentation:
   - Combine: query + retrieved documents

4. Generation:
   - LLM reads augmented prompt
   - Generate answer based on documents
```

### Core Components

**1. Knowledge Base/Corpus**
- Documents, PDFs, web pages, databases
- Could be: 1000 documents to 1B documents

**2. Indexing**
- Extract text from documents
- Create searchable index
- Example: Vector database (Pinecone, Weaviate)

**3. Retrieval**
- Search index for relevant documents
- Return top K most similar to query

**4. Augmentation**
- Combine query + retrieved docs into prompt

**5. Generation**
- LLM generates answer using augmented context

---

## 🔍 Retrieval Methods

### Dense Retrieval (Vector Search)

```
1. Embed query: "password reset"
   → vector: [0.2, 0.8, -0.1, ...]  (768-dim)

2. Embed documents:
   "How to reset password" → [0.15, 0.82, -0.05, ...]
   "Account settings guide" → [0.1, 0.3, 0.5, ...]
   
3. Similarity: Cosine similarity of vectors
   Query vs Doc1: 0.99 (very similar)
   Query vs Doc2: 0.45 (less similar)

4. Return: Top-K documents (e.g., K=3)
```

**Advantages:**
- Semantic matching (understands meaning)
- Works across languages
- Single vector database handles billions

**Disadvantages:**
- Requires embedding model
- Vector similarity ≠ exact matching
- "Not in docs" harder to detect

### Sparse Retrieval (Keyword Search)

```
1. Index: BM25 or TF-IDF
   
2. Query: "password reset"
   → Search for documents containing keywords

3. Rank by: TF-IDF score or BM25

4. Return: Top-K documents
```

**Advantages:**
- Simple, interpretable
- Good for exact/keyword matches
- No embedding model needed

**Disadvantages:**
- No semantic understanding
- Misses synonyms ("password reset" vs "PIN change")

### Hybrid Approach

Combine dense + sparse:

```
Results = 0.7 × dense_results + 0.3 × sparse_results

Benefits: Semantic + keyword matching, more robust
```

---

## 🎯 Practical Considerations

### Chunking Documents

Documents too long to fit in context. Split into chunks:

```
Document: "A 10,000 word policy document"

Chunking strategy:
- Size: 256-1024 tokens
- Overlap: 50-100 tokens (preserve context)

Naive: Split at fixed boundaries
  ❌ Breaks mid-sentence

Better: Semantic chunking
  ✅ Split at paragraph/section boundaries
  ✅ Keeps related information together
```

### Reranking

Initial retrieval might return 100 results. Rerank to keep best K:

```
1. Dense retrieval: Get top 100 documents
2. Reranker model: More expensive but accurate
3. Keep top K: Return top 5-10

Why: Balances speed and accuracy
```

### Context Window Management

```
Query + Documents must fit in context:

Available tokens = 4096 (assume)
- System prompt: 500 tokens
- User query: 50 tokens
- Documents: 2000 tokens
- Response: 1500 tokens
- Safety margin: ~46 tokens

Fit documents to context window
```

---

## 🔧 Building a RAG System

### Step 1: Prepare Documents

```python
documents = load_documents("docs/")
# Returns: List[Document] with id, text, metadata

# Split into chunks
chunks = []
for doc in documents:
    doc_chunks = chunk_document(doc, chunk_size=512)
    chunks.extend(doc_chunks)
# Returns: 10,000 chunks from 100 documents
```

### Step 2: Create Index

```python
from pinecone import Pinecone

pc = Pinecone(api_key="...")
index = pc.Index("rag-index")

# Embed and index chunks
embeddings = embed_model.encode(chunks)  # (10k, 768)
index.upsert(vectors=[
    (chunk_id, embedding, {"text": chunk_text})
    for chunk_id, embedding, chunk_text in zip(range(10k), embeddings, chunks)
])
```

### Step 3: Query

```python
query = "How do I reset my password?"
query_embedding = embed_model.encode(query)

# Retrieve
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)

# Results: List of (score, doc_id, metadata)
# score: Similarity (0-1), higher is better
```

### Step 4: Augment Prompt

```python
# Combine retrieved docs with query
retrieved_docs = "\n".join([
    result['metadata']['text'] 
    for result in results
])

augmented_prompt = f"""
Based on the following documents:

{retrieved_docs}

Answer this question: {query}
"""

# Generate
response = llm.generate(augmented_prompt)
```

---

## ⚡ Optimization Strategies

### Compression

```
Context: documents + query may be 3000+ tokens

Solution: Compress documents
- LLMCompress: Use LLM to summarize
- Tokens compressed: 3000 → 500 tokens
- Trade-off: May lose details
```

### Metadata Filtering

```
# Index includes metadata
{
  "id": "doc_123",
  "text": "password reset guide",
  "source": "help.pdf",
  "date": "2024-03-15",
  "category": "account-management"
}

# Query with filters
results = index.query(
    vector=query_embedding,
    top_k=5,
    filter={"category": "account-management"}  # Only relevant docs
)
```

### Caching

```python
# Cache retrieved documents for same query
cache = {}

def retrieve(query):
    if query in cache:
        return cache[query]
    
    results = index.query(query_embedding, top_k=5)
    cache[query] = results
    return results
```

---

## 📊 Evaluation

### Retrieval Quality

```
Metric: Precision@K
- Did we retrieve relevant documents?
- P@5: % of top-5 that are relevant

Metric: Recall@K  
- Did we retrieve most relevant documents?
- R@5: Of all relevant docs, did top-5 capture them?
```

### Generation Quality

```
Compare LLM response to ground truth:

BLEU: Overlap of tokens/n-grams
ROUGE: Recall of overlapping units
Human evaluation: Most reliable for open-ended tasks
```

### End-to-End

```
Did RAG system give correct answer to user query?

Examples:
✅ Retrieves: "Password reset: Click Settings > Security > Reset"
✅ Generates: "Click Settings, go to Security tab, click Reset"
```

---

## ❓ Interview Q&A

**Q: Why use RAG instead of fine-tuning?**
A: RAG is faster to implement (hours), cheaper, works with updated knowledge. Fine-tuning requires retraining (expensive), knowledge gets stale.

**Q: What's the difference between dense and sparse retrieval?**
A: Dense: Semantic similarity, handles synonyms. Sparse: Keyword matching, exact. Hybrid combines both.

**Q: How do you handle very large document collections?**
A: Use distributed vector DBs (Pinecone scales to billions), implement hierarchical retrieval, use approximate nearest neighbor search.

**Q: What happens if the answer isn't in your documents?**
A: LLM may hallucinate or admit "not found". Mitigate: Confidence scores, "Not in knowledge base" in prompt, metrics monitoring.

---

## ✅ Checklist

- [ ] Understand RAG architecture and why it matters
- [ ] Know dense vs. sparse retrieval trade-offs
- [ ] Understand document chunking strategies
- [ ] Know how to build a RAG system (index → query → augment)
- [ ] Understand reranking and context management
- [ ] Know evaluation metrics (retrieval, generation)
- [ ] Understand caching and optimization
- [ ] Know when to use RAG vs. fine-tuning vs. prompt engineering

---

**Last updated:** 2026-05-22
