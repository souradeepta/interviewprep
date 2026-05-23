# Model Evaluation & Benchmarking — Measuring What Matters

Comprehensive approach to evaluating LLM and ML systems.

---

## 📊 Evaluation Frameworks

### Automatic Metrics

**BLEU, ROUGE:** Token overlap (for generation)
- Fast, reproducible
- Don't capture semantic quality well

**Exact Match, F1:** For QA tasks
- Simple but strict

**Perplexity:** Language modeling metric
- Lower is better
- Don't rely solely (can be gamed)

### Human Evaluation

```
Rubric-based: Rate quality 1-5
Preference: A vs. B, which is better?
Error analysis: Understand failure modes

Cost: Expensive but gold standard
```

---

## 🏆 Popular Benchmarks

### Academic Benchmarks

**GLUE/SuperGLUE:** Language understanding
**SQuAD:** Reading comprehension
**MMLU:** Knowledge across domains
**HumanEval:** Code generation

### LLM Leaderboards

- HuggingFace leaderboard
- LMSYS ChatBot Arena (human preference voting)
- HELM (comprehensive evaluation)

---

## 🔬 Evaluation Strategy

### Phases

1. **Automatic screening:** Quick evaluation, broad coverage
2. **Focused evaluation:** Deep dive on weak areas
3. **Human validation:** Final quality check
4. **Red teaming:** Find failure modes

### Critical Questions

```
Accuracy: Correct answers?
Latency: Response time acceptable?
Cost: Compute per query?
Fairness: Biased against groups?
Robustness: Works on edge cases?
```

---

## 🎯 Domain-Specific Benchmarks

**Medical:** USMLE, medical QA accuracy
**Law:** Bar exam questions
**Code:** HumanEval, CodeXGLUE
**Visual:** ImageNet, COCO, LAION

---

## ❓ Interview Q&A

**Q: How would you evaluate a new summarization model?**
A: Automatic: ROUGE. Human: Relevance, conciseness, factuality. Error analysis on examples. Compare against baseline.

**Q: Why not just use perplexity?**
A: Perplexity ≠ quality. Model can memorize or repeat training data. Human evaluation essential for real tasks.

**Q: How to detect overfitting to benchmarks?**
A: Evaluate on multiple benchmarks. Test on new data. Adversarial examples. Error analysis.

---

**Last updated:** 2026-05-22
