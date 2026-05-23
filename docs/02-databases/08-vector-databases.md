# Vector Databases — Semantic Search and Embeddings

Finding similar items using vector similarity.

---

## 🔢 Vector Embeddings

Convert data to vectors (embeddings):

```
"Hello world" → [0.2, 0.5, -0.3, 0.1, ...]  (1536-dim)
"Hi everyone" → [0.21, 0.48, -0.32, 0.09, ...] (similar)
"Goodbye" → [0.8, 0.1, 0.6, -0.2, ...]  (different)

Similarity = cosine(v1, v2)
```

---

## 📚 Use Cases

**RAG:** Retrieve relevant documents for LLM
**Product Recommendations:** Find similar items
**Image Search:** Find visually similar images
**Semantic Search:** Find documents by meaning (not keywords)

---

## 🏗️ Architecture

```
1. Embed documents into vectors
2. Index vectors (special data structure)
3. Query: Embed query, find nearest neighbors
4. Return top-K similar items
```

---

## 🔍 Indexing Methods

**Flat:** Brute force, all vectors (slow for 1B items)
**HNSW:** Hierarchical navigation (fast)
**IVF:** Inverted file (approximate)
**PQ:** Product quantization (memory efficient)

---

## 🏆 Popular Systems

**Pinecone:** Managed vector DB
**Weaviate:** Open-source, full-featured
**Milvus:** Scalable, many index types
**Qdrant:** Modern, Rust-based

---

## 💡 RAG Pipeline

```
1. Document chunks → Embed → Store in vector DB
2. User query → Embed
3. Search vector DB for top-K similar chunks
4. Pass chunks + query to LLM
5. LLM generates answer based on context
```

---

## ❓ Interview Q&A

**Q: Design semantic search for 10M documents**
A: Chunk documents, embed, store in vector DB. Query embedding, top-K retrieval.

**Q: Embedding dimension selection**
A: 384 (small, fast), 768 (common), 1536 (high quality). Trade latency vs. accuracy.

---

**Last updated:** 2026-05-22
