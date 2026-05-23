# NLP Advanced Topics — Beyond Language Models

Specialized NLP techniques and applications.

---

## 📚 Named Entity Recognition (NER)

Identify and classify named entities: person, location, organization, date.

```
"Apple Inc. was founded by Steve Jobs in 1976"
 ^^^^^^      ^^^^^^^^^^^       ^^^^^^^^^^  ^^^^
  ORG        PERSON             PERSON    DATE
```

### Approaches

**Sequence tagging:**
- Tag each token: B-PER, I-PER, B-ORG, O (outside)
- Use LSTM/CRF or Transformer
- Can use pre-trained models (spaCy, BERT)

---

## 🔗 Relation Extraction

Identify relationships between entities.

```
Text: "Microsoft CEO Satya Nadella announced..."
Entities: [Microsoft (ORG), Satya Nadella (PER)]
Relation: "is_CEO_of"
Result: Satya_Nadella --[is_CEO_of]--> Microsoft
```

### Methods

- Rule-based: Pattern matching
- Supervised: Train classifier on labeled pairs
- Distant supervision: Use knowledge base to generate labels

---

## 🗣️ Sentiment Analysis

Determine emotional tone: positive, negative, neutral.

```
"I love this product!" → positive
"Terrible experience" → negative
"It's okay" → neutral

Aspect-based: "Good camera but bad battery" 
→ camera (positive), battery (negative)
```

### Techniques

**Lexicon-based:** Dictionary of words + sentiment scores
**Supervised:** Train on labeled reviews
**Transformers:** Fine-tune BERT on your domain

---

## 🔍 Information Retrieval

Find relevant documents for query.

### Key Concepts

**TF-IDF:** Relevance score
```
TF: How often term appears in document
IDF: How rare term is across documents
TF-IDF = TF × IDF
```

**BM25:** Improved TF-IDF variant
- Accounts for document length
- Saturation (diminishing returns for term frequency)

**Vector embeddings:** Dense vector similarity
- FastText, Word2Vec for words
- BERT, sentence-transformers for sentences

---

## 🎯 Question Answering

Answer questions given context.

### Types

**Extractive:** Answer is span in context
- BERT-based: Find start and end positions
- High accuracy on SQuAD dataset

**Generative:** Generate answer from scratch
- Seq2seq model
- More flexible, harder to train

---

## 🔄 Machine Translation

Translate text between languages.

### Architecture

```
Encoder: Process source language
Decoder: Generate target language
Attention: Focus on relevant source words
```

### Metrics

**BLEU:** Overlap of n-grams with reference
- 0-100, higher is better
- Imperfect metric (synonyms not captured)

**METEOR, CIDEr:** Better alternatives

---

## 📊 Topic Modeling

Discover latent topics in documents.

### LDA (Latent Dirichlet Allocation)

```
Documents → Mix of topics
Topics → Mix of words

Example:
Document 1: [0.7 Tech, 0.3 Sports]
Tech topic: {0.3 AI, 0.2 software, 0.1 computer...}
```

### Application

- Organize documents by topic
- Content recommendation
- Understanding corpus themes

---

## ❓ Interview Q&A

**Q: How would you build NER system?**
A: Sequence tagging approach: LSTM/Transformer over word embeddings. Output probability per NER tag. Use BIO tagging scheme. Fine-tune pre-trained BERT if possible.

**Q: TF-IDF vs. embeddings for search?**
A: TF-IDF: Fast, interpretable, good for lexical match. Embeddings: Better semantic understanding, slower. Hybrid often best.

**Q: How to evaluate question answering system?**
A: Exact match (answer matches exactly), F1 (overlap with reference). Human evaluation for quality.

---

**Last updated:** 2026-05-22
