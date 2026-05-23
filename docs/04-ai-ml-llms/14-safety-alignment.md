# Safety & Alignment — Building Trustworthy AI

Ensuring AI systems behave safely and align with human values.

---

## 🛡️ Core Concepts

### Alignment Problem

```
Goal: Make AI systems do what humans want
Challenge: Difficult to specify all constraints
Example: "Be helpful" → Literal interpretation problems
```

### Specification Gaming

```
Agent optimizes stated objective, ignores intent
Example: RL agent maximizing score → exploits bug instead of playing well
Solution: Better reward design, constraints
```

---

## 🚨 Common Harms

**Bias:** Discriminatory outputs
- Mitigated by: Balanced training data, fairness metrics, audits

**Hallucination:** False confident statements
- Mitigated by: Fine-tuning, RAG, uncertainty estimation

**Jailbreaking:** Tricking system into unsafe behavior
- Mitigated by: Robust adversarial training, safety layers

**Privacy:** Leaking training data
- Mitigated by: DP training, data sanitization, access controls

---

## 🎯 Safety Techniques

### Constitutional AI

Define principles, have model critique itself:
```
1. Write response
2. Evaluate against principles
3. Revise based on critique
```

### RLHF (Refined from Honest Feedback)

Train reward model on human preferences, optimize for alignment.

### Adversarial Training

Find failure cases, train to handle them.

### Uncertainty Quantification

Report confidence: "I'm unsure" vs. confident predictions.

---

## 📊 Benchmarking Safety

**Toxicity:** TOXIGEN, RealToxicityPrompts
**Bias:** Gender bias, racial bias metrics
**Factuality:** Fact-checking datasets
**Hallucination:** F1 on knowledge tasks
**Robustness:** Adversarial examples

---

## 🔍 Interpretability & Explainability

### Why Needed

```
Black box models hard to debug
Safety decisions require understanding
Regulatory requirements (EU AI Act, etc.)
```

### Techniques

**Attention visualization:** What does model attend to?
**Feature importance:** Which inputs matter most?
**Probing:** Extract internal representations
**Mechanistic interpretability:** Understand internal circuits

---

## ❓ Interview Q&A

**Q: How would you audit an LLM for bias?**
A: Test on bias benchmarks (gender, race, religion). Compare outputs for different demographics. Quantify with metrics. Fine-tune to address gaps.

**Q: What's constitutional AI?**
A: Have model self-critique against principles. Iteratively improve responses. More scalable than manual feedback.

**Q: How to detect hallucinations?**
A: Compare against knowledge base (RAG). Cross-check facts. Model uncertainty. Combine with retrieval.

---

**Last updated:** 2026-05-22
