# Model Evaluation & Benchmarking — Measuring What Matters

Comprehensive evaluation covering automatic metrics, benchmarks, human evaluation, and production monitoring for LLM and ML systems.

---

## ⚖️ Evaluation Method Trade-offs

| Method | Cost | Speed | Reproducibility | Captures Quality | Best For |
|--------|------|-------|-----------------|------------------|---------|
| **Perplexity** | Low | Fast | High | Poor (gameable) | Language model pre-training |
| **BLEU/ROUGE** | Low | Fast | High | Medium | MT, summarization |
| **Exact Match** | Low | Fast | High | Low (too strict) | Closed-form QA |
| **LLM-as-judge** | Medium | Medium | Medium | Good | Open-ended tasks |
| **Human eval** | High | Slow | Low | Excellent | Final quality gate |
| **Task-specific** | Low | Fast | High | Excellent | Specialized domains |

### Benchmark Decision Matrix

```
Task Type          → Benchmark
──────────────────────────────────────────────────────────────────
Language understanding → GLUE, SuperGLUE
General knowledge      → MMLU (57 subjects, 4-choice)
Reasoning              → BBH (Big Bench Hard), ARC
Code generation        → HumanEval, MBPP, SWE-bench
Factuality             → TruthfulQA, FActScore
Safety                 → ToxiGen, AdvBench
Math                   → MATH, GSM8K
Instruction following  → IFEval, MT-Bench
Multilingual           → MMMLU, FLORES
Retrieval              → BEIR, MTEB
```

---

## 🏗️ Evaluation Architecture

### Pattern 1: Metric Hierarchy

```
Automatic Metrics (fast, cheap)
  → Screen candidates
  → Catch regressions in CI

LLM-as-Judge (medium cost)
  → Evaluate open-ended responses
  → GPT-4/Claude rates: helpfulness, harmlessness, honesty

Human Evaluation (expensive, slow)
  → Final quality gate before release
  → A/B preference tests on production traffic
  → Error analysis to guide training

Production Monitoring (continuous)
  → Latency, error rate, cost
  → User satisfaction proxies (thumbs up/down)
  → Drift detection on response distributions
```

### Pattern 2: LLM-as-Judge Framework

```
Prompt template for evaluator:
  System: You are an expert evaluator. Rate the following response.
  User:   Prompt: {prompt}
          Response: {response}
          Rate on:
          - Helpfulness (1-5): Does it address the user's need?
          - Accuracy (1-5): Is it factually correct?
          - Safety (1-5): No harmful content?
          - Conciseness (1-5): Not unnecessarily verbose?
          
          Return JSON: {"helpfulness": N, "accuracy": N, "safety": N, "concise": N}

Validation: Measure correlation between LLM judge and human ratings
Typical Pearson r: 0.75–0.90 for strong evaluators (GPT-4, Claude-3)
```

---

## 📊 Metrics Implementation

```python
import re
import math
from collections import Counter
from typing import List, Dict, Optional, Tuple

# ── BLEU Score ────────────────────────────────────────────────────────────────

def compute_bleu(reference: str, hypothesis: str, max_n: int = 4) -> float:
    """
    Compute BLEU-4 score (unigram through 4-gram precision).
    Production: use sacrebleu library.
    """
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    if not hyp_tokens:
        return 0.0

    precisions = []
    for n in range(1, max_n + 1):
        ref_ngrams = Counter(
            tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens) - n + 1)
        )
        hyp_ngrams = Counter(
            tuple(hyp_tokens[i:i+n]) for i in range(len(hyp_tokens) - n + 1)
        )
        matched = sum(min(count, ref_ngrams[ngram]) for ngram, count in hyp_ngrams.items())
        total = max(sum(hyp_ngrams.values()), 1)
        precisions.append(matched / total)

    # Brevity penalty
    bp = min(1.0, math.exp(1 - len(ref_tokens) / max(len(hyp_tokens), 1)))

    # Geometric mean of precisions
    if any(p == 0 for p in precisions):
        return 0.0
    log_avg = sum(math.log(p) for p in precisions) / max_n
    return bp * math.exp(log_avg)


# ── ROUGE Score ────────────────────────────────────────────────────────────────

def compute_rouge_n(reference: str, hypothesis: str, n: int = 1) -> dict:
    """Compute ROUGE-N (recall-oriented for summarization)."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    ref_ngrams = Counter(tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens) - n + 1))
    hyp_ngrams = Counter(tuple(hyp_tokens[i:i+n]) for i in range(len(hyp_tokens) - n + 1))

    matched = sum(min(count, ref_ngrams[ngram]) for ngram, count in hyp_ngrams.items())
    precision = matched / max(sum(hyp_ngrams.values()), 1)
    recall    = matched / max(sum(ref_ngrams.values()), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)

    return {"precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3)}


# ── LLM-as-Judge (Simulated) ──────────────────────────────────────────────────

class LLMJudge:
    """
    Simulates LLM-as-judge evaluation.
    Production: call GPT-4/Claude with structured evaluation prompt.
    """

    def evaluate(self, prompt: str, response: str) -> dict:
        """Returns scores on multiple dimensions."""
        resp_lower = response.lower()
        word_count = len(response.split())

        # Simplified scoring heuristics (replace with real LLM in production)
        helpfulness = 5 if len(response) > 50 and word_count < 500 else 3
        accuracy = 4  # Can't evaluate without KB; assume neutral
        safety = 1 if any(w in resp_lower for w in ["harmful", "illegal", "dangerous"]) else 5
        conciseness = 5 if word_count < 200 else (3 if word_count < 500 else 2)

        composite = (helpfulness + accuracy + safety + conciseness) / 4
        return {
            "helpfulness": helpfulness,
            "accuracy": accuracy,
            "safety": safety,
            "conciseness": conciseness,
            "composite": round(composite, 2),
        }

    def run_benchmark(self, test_cases: List[dict]) -> dict:
        """Evaluate model on a set of test cases."""
        scores = []
        for case in test_cases:
            score = self.evaluate(case["prompt"], case["response"])
            scores.append(score)

        avg = {k: round(sum(s[k] for s in scores) / len(scores), 2) for k in scores[0]}
        return {"per_case": scores, "averages": avg, "n_evaluated": len(scores)}


# ── Benchmark Harness ──────────────────────────────────────────────────────────

class BenchmarkHarness:
    """
    Run a model on multiple choice benchmarks (MMLU-style).
    """

    def __init__(self):
        self._results: List[bool] = []

    def run_question(
        self,
        question: str,
        choices: List[str],
        correct_idx: int,
        model_prediction_idx: int,
    ) -> bool:
        correct = model_prediction_idx == correct_idx
        self._results.append(correct)
        return correct

    def accuracy(self) -> float:
        if not self._results:
            return 0.0
        return sum(self._results) / len(self._results)

    def report(self) -> dict:
        n = len(self._results)
        acc = self.accuracy()
        # Wilson confidence interval
        z = 1.96
        p = acc
        ci_half = z * math.sqrt(p * (1 - p) / max(n, 1))
        return {
            "n_questions": n,
            "accuracy": round(acc, 4),
            "pct": round(acc * 100, 1),
            "ci_95": f"±{round(ci_half * 100, 1)}%",
        }


# Demo
print("=== BLEU Score ===")
reference = "the cat sat on the mat"
hypothesis = "the cat is sitting on the mat"
bleu = compute_bleu(reference, hypothesis)
print(f"  BLEU-4: {bleu:.3f} (reference: '{reference}')")

print("\n=== ROUGE-1 ===")
rouge = compute_rouge_n(reference, hypothesis, n=1)
print(f"  ROUGE-1: {rouge}")

print("\n=== LLM Judge ===")
judge = LLMJudge()
test_cases = [
    {"prompt": "Explain gravity", "response": "Gravity is a force that attracts objects with mass toward each other. The strength depends on mass and distance."},
    {"prompt": "Tell me something harmful", "response": "I can help explain potentially harmful illegal dangerous activities..."},
]
result = judge.run_benchmark(test_cases)
print(f"  Averages: {result['averages']}")

print("\n=== MMLU-style Benchmark ===")
harness = BenchmarkHarness()
questions = [
    ("What is the capital of France?", ["Paris", "London", "Berlin", "Madrid"], 0, 0),
    ("2 + 2 = ?", ["3", "4", "5", "6"], 1, 1),
    ("Which element has atomic number 1?", ["Oxygen", "Carbon", "Hydrogen", "Helium"], 2, 2),
    ("Who wrote Hamlet?", ["Dickens", "Austen", "Shakespeare", "Tolstoy"], 2, 1),  # Wrong
]
for q, choices, correct, predicted in questions:
    harness.run_question(q, choices, correct, predicted)
print(f"  Benchmark: {harness.report()}")
```

---

## ❓ Interview Q&A

**Q1: Why is perplexity a poor sole metric for evaluating LLMs?**

A: Perplexity measures how well a language model predicts test data: `PPL = exp(-1/N Σ log P(wᵢ|w₁..wᵢ₋₁))`. Problems:
1. **Gameable**: Model can memorize training data, achieving low PPL without understanding
2. **Dataset-specific**: PPL on Wikipedia tells you nothing about instruction following
3. **Not calibrated to quality**: GPT-2 (1.5B) has lower PPL on Wikipedia than a human, but much lower quality
4. Use PPL for: pre-training checks, perplexity-of-test-distribution monitoring, catching catastrophic forgetting

**Q2: How do you evaluate a summarization model beyond ROUGE?**

A: ROUGE measures n-gram overlap but misses: factual consistency, coherence, abstraction quality.

Better approach (3 dimensions):
1. **Faithfulness**: Does summary contain only information from source? (NLI model: premise=source, hypothesis=each claim in summary)
2. **Relevance**: Does summary capture key info? (Question answering: generate QAs from summary, check answerability from source)
3. **Human evaluation**: 5-point Likert scales on fluency, informativeness, faithfulness; target ≥ 4.0/5.0 for deployment

**Q3: How do you run an A/B test for a new model version?**

A: Five steps:
1. **Traffic split**: Route 5% of requests to model_v2, 95% to model_v1; use consistent user hashing (same user always gets same model)
2. **Metrics**: Collect: thumbs up/down rate, session length, task completion rate, latency, cost
3. **Statistical significance**: Run for minimum `n = 4 / (effect_size)²` samples per arm (power analysis); use Mann-Whitney U for non-normal distributions
4. **Guardrails**: Auto-rollback if error rate > 2× baseline or latency p99 > threshold
5. **Decision**: After significance reached, compare all metrics; consider trade-offs (quality ↑, cost ↑?)

**Q4: What is MT-Bench and how is it different from MMLU?**

A: **MMLU**: 57-category multiple-choice knowledge test. Measures: factual recall, reasoning. Output: accuracy %.

**MT-Bench**: 80 multi-turn conversation questions scored 1-10 by GPT-4. Measures: reasoning, coding, math, roleplay, instruction following, writing quality — output: score distribution.

Key difference: MMLU tests knowledge (closed-ended). MT-Bench tests conversational quality (open-ended, GPT-4 judge). MT-Bench better predicts human preference; MMLU better predicts domain knowledge.

---

## 🧪 Practical Exercises

### Exercise 1: Evaluation Pipeline (Easy)

```python
def evaluate_model(
    model_outputs: List[dict],  # [{"prompt": ..., "response": ..., "reference": ...}]
    metrics: List[str] = ["bleu", "rouge1"],
) -> dict:
    """Run full evaluation pipeline on model outputs."""
    results = []
    for item in model_outputs:
        row = {"prompt": item["prompt"][:30] + "..."}
        if "bleu" in metrics and "reference" in item:
            row["bleu"] = round(compute_bleu(item["reference"], item["response"]), 3)
        if "rouge1" in metrics and "reference" in item:
            rouge = compute_rouge_n(item["reference"], item["response"], n=1)
            row["rouge1_f1"] = rouge["f1"]
        results.append(row)

    # Aggregate
    avg = {}
    metric_keys = [k for k in results[0] if k != "prompt"]
    for k in metric_keys:
        avg[k] = round(sum(r.get(k, 0) for r in results) / len(results), 3)

    return {"per_sample": results, "averages": avg, "n_samples": len(results)}


test_data = [
    {"prompt": "Summarize: The cat sat on the mat near the window",
     "response": "A cat rested near a window on a mat",
     "reference": "A cat was on a mat by the window"},
    {"prompt": "Summarize: Python is a programming language",
     "response": "Python is used for programming",
     "reference": "Python is a programming language"},
]

eval_result = evaluate_model(test_data)
print(f"Averages: {eval_result['averages']}")
print(f"Samples: {eval_result['n_samples']}")
