# Interpretability & Explainability — Understanding Model Decisions

Make AI models transparent: explain individual predictions, audit internal representations, detect shortcuts, and satisfy regulatory requirements.

---

## ⚖️ Interpretability Method Trade-offs

| Method | Fidelity | Speed | Model-Agnostic | Complexity | Best For |
|--------|---------|-------|----------------|------------|---------|
| **LIME** | Medium | Fast | Yes | Low | Local explanations, any model |
| **SHAP** | High | Slow | Yes | Medium | Feature attribution, tabular data |
| **Attention viz** | Low (debate) | Fast | No (transformers) | Low | Debugging, intuition |
| **Saliency maps** | Medium | Fast | No (gradient) | Low | Image models |
| **Probing** | High | Medium | No | Medium | Representation analysis |
| **Mechanistic** | Very High | Very Slow | No | Very High | Research, circuit discovery |

### When to Use Each

```
Task                               Method
────────────────────────────────────────────────────────────
"Why did model predict X?"         SHAP (tabular), LIME, saliency (images)
"What does this neuron detect?"    Mechanistic interpretability, activation maximization
"Is model using feature F?"        Probing, ablation study
"Why is model biased toward X?"    SHAP grouped by group, counterfactual analysis
"EU AI Act compliance?"            SHAP + audit report, model cards
"Debug performance regression?"    Attention visualization, activation comparison
```

---

## 🏗️ Architecture Patterns

### Pattern 1: LIME (Local Interpretable Model-Agnostic Explanations)

```
Original prediction: Review → "Positive" (p=0.92)

LIME process:
  1. Perturb input: Remove words one-by-one
  2. Get model predictions for each perturbation
  3. Weight by distance to original
  4. Fit linear model: prediction ≈ a₀ + a₁·"excellent" + a₂·"waste" + ...
  5. Report coefficients as feature importance

Positive contributions:  "excellent" (+0.3), "loved" (+0.25), "great" (+0.2)
Negative contributions:  "waste" (-0.1), "but" (-0.05)
```

### Pattern 2: SHAP (SHapley Additive exPlanations)

```
Game theory foundation:
  Each feature is a "player" in a cooperative game
  Shapley value = average marginal contribution across all subsets

For prediction f(age=30, income=80K) = "Approved":
  SHAP(age=30)    = E[f | age=30] - E[f]     ≈ +0.15
  SHAP(income=80K)= E[f | income=80K] - E[f] ≈ +0.32
  SHAP(credit=720)= ...                        ≈ +0.28

Total: base_value + 0.15 + 0.32 + 0.28 = 0.92 (approved)

Properties: Completeness (sum = f(x) - f(baseline)), Symmetry, Dummy, Additivity
```

### Pattern 3: Probing Classifiers

```
Do BERT representations encode part-of-speech?

  Text: "The cat sat"
  BERT layer 4 hidden states: h₁, h₂, h₃
  
  Probing classifier: Linear(h → POS_tag)
  Train on 1000 sentences with POS labels
  
  Accuracy: 95% → Layer 4 strongly encodes POS
  Accuracy: 55% → Layer 4 doesn't encode POS (near chance)
  
  Key insight: Probe accuracy ≈ how much information is linearly encoded
  Limitation: High accuracy could mean probe itself learned, not representation
```

---

## 📊 Implementation Examples

```python
import math
import random
from typing import Callable, List, Optional, Dict

# ── LIME for Text Classification ──────────────────────────────────────────────

class TextLIME:
    """
    Local Interpretable Model-Agnostic Explanations for text.
    Perturbs text, collects predictions, fits local linear model.
    """

    def __init__(self, model_fn: Callable[[str], float], n_samples: int = 100):
        self.model_fn = model_fn
        self.n_samples = n_samples

    def _perturb(self, tokens: List[str]) -> tuple:
        """Randomly mask tokens (set to empty)."""
        mask = [random.choice([True, False]) for _ in tokens]
        perturbed = " ".join(t if keep else "" for t, keep in zip(tokens, mask))
        return perturbed.strip(), mask

    def _distance_weight(self, mask: List[bool], original_mask: List[bool] = None) -> float:
        """Cosine distance-based weight (simulated)."""
        if original_mask is None:
            return 1.0
        shared = sum(a == b for a, b in zip(mask, original_mask))
        return shared / len(mask)

    def explain(self, text: str, top_k: int = 5) -> List[tuple]:
        """Returns top_k (token, importance) pairs."""
        tokens = text.split()
        if not tokens:
            return []

        # Collect perturbed predictions
        samples = []
        for _ in range(self.n_samples):
            perturbed, mask = self._perturb(tokens)
            pred = self.model_fn(perturbed)
            weight = self._distance_weight(mask)
            samples.append((mask, pred, weight))

        # Fit weighted linear regression per token (coefficient = importance)
        importances = []
        for i, token in enumerate(tokens):
            # Correlation between token[i] presence and prediction
            with_token    = [p * w for m, p, w in samples if m[i]]
            without_token = [p * w for m, p, w in samples if not m[i]]
            avg_with    = sum(with_token) / max(len(with_token), 1)
            avg_without = sum(without_token) / max(len(without_token), 1)
            importance = avg_with - avg_without
            importances.append((token, importance))

        # Sort by absolute importance
        importances.sort(key=lambda x: abs(x[1]), reverse=True)
        return importances[:top_k]


# ── SHAP Values (Simplified) ──────────────────────────────────────────────────

class SimpleSHAP:
    """
    SHAP values via sampling (KernelSHAP approximation).
    Real SHAP: TreeSHAP (tree models), DeepSHAP (neural nets), KernelSHAP (any).
    """

    def __init__(self, model_fn: Callable, baseline_fn: Callable, n_samples: int = 200):
        self.model_fn = model_fn
        self.baseline_fn = baseline_fn  # Returns baseline input
        self.n_samples = n_samples

    def shap_values(self, x: List[float]) -> List[float]:
        """Compute SHAP value for each feature in x."""
        n_features = len(x)
        shapley = [0.0] * n_features

        baseline = self.baseline_fn()

        for _ in range(self.n_samples):
            # Random coalition (subset of features)
            perm = list(range(n_features))
            random.shuffle(perm)

            # Build input with and without each feature (marginal contribution)
            current = list(baseline)
            for i, feat_idx in enumerate(perm):
                # Without feature feat_idx
                val_without = self.model_fn(current)
                # With feature feat_idx
                current[feat_idx] = x[feat_idx]
                val_with = self.model_fn(current)
                # Marginal contribution
                shapley[feat_idx] += val_with - val_without

        return [s / self.n_samples for s in shapley]


# ── Saliency Map (Gradient-based) ─────────────────────────────────────────────

class SaliencyMap:
    """
    Gradient-based input attribution.
    Saliency = |∂output/∂input| — high = input influences output.
    """

    def compute(
        self,
        input_vec: List[float],
        model_fn: Callable[[List[float]], float],
        epsilon: float = 1e-4,
    ) -> List[float]:
        """Finite differences approximation of gradient."""
        base_output = model_fn(input_vec)
        saliency = []

        for i in range(len(input_vec)):
            perturbed = list(input_vec)
            perturbed[i] += epsilon
            perturbed_output = model_fn(perturbed)
            gradient = (perturbed_output - base_output) / epsilon
            saliency.append(abs(gradient))

        # Normalize
        max_sal = max(saliency) or 1
        return [s / max_sal for s in saliency]


# Demo

# Simulated sentiment model: count positive words - negative words
POSITIVE_WORDS = {"excellent", "great", "loved", "amazing", "perfect"}
NEGATIVE_WORDS = {"terrible", "awful", "waste", "disappointing", "broken"}

def sentiment_model(text: str) -> float:
    words = set(text.lower().split())
    score = sum(1 for w in words if w in POSITIVE_WORDS)
    score -= sum(1 for w in words if w in NEGATIVE_WORDS)
    return max(0.0, min(1.0, 0.5 + score * 0.2))

print("=== LIME Text Explanation ===")
explainer = TextLIME(sentiment_model, n_samples=200)
review = "This product is excellent and I loved every aspect of it but the packaging was terrible"
result = sentiment_model(review)
print(f"Review: '{review[:60]}...'")
print(f"Model prediction: {result:.2f} (positive)")
explanation = explainer.explain(review, top_k=5)
for token, importance in explanation:
    direction = "+" if importance > 0 else "-"
    print(f"  {direction} {token:15} {importance:+.3f}")

print("\n=== SHAP Values (Tabular) ===")
# Loan approval model: sum of normalized features
def loan_model(x: List[float]) -> float:
    weights = [0.4, 0.35, 0.25]  # age, income, credit_score weights
    return sum(w * v for w, v in zip(weights, x))

shap = SimpleSHAP(
    model_fn=loan_model,
    baseline_fn=lambda: [0.5, 0.5, 0.5],  # Average applicant
    n_samples=100,
)
applicant = [0.7, 0.9, 0.8]  # Normalized: age=0.7, income=0.9, credit=0.8
values = shap.shap_values(applicant)
features = ["age", "income", "credit_score"]
print(f"Prediction: {loan_model(applicant):.3f} (baseline: {loan_model([0.5]*3):.3f})")
for feat, val in zip(features, values):
    print(f"  {feat:15}: SHAP = {val:+.3f}")
```

---

## ❓ Interview Q&A

**Q1: Why is attention not always a faithful explanation?**

A: Attention weights show what the model "looks at" but not necessarily what drives predictions. Studies (Jain & Wallace, 2019) showed alternative attention distributions produce identical predictions — attention can be shuffled without changing outputs. Gradient-based methods (integrated gradients, saliency) are more faithful because they directly measure input→output sensitivity. Attention is useful for intuition and debugging but shouldn't be cited as causal explanation.

**Q2: When would you use LIME vs. SHAP?**

A: 
- **LIME**: Need fast local explanation, model-agnostic, explain to non-technical stakeholders. Weakness: unstable (re-running gives different results), superpixel assumptions for images
- **SHAP**: Need theoretically grounded attributions, consistent explanations, global feature importance across all predictions. Weakness: slow for large feature counts (KernelSHAP), TreeSHAP fast but model-specific

Rule of thumb: SHAP for tabular/tree models (fast via TreeSHAP), LIME for text/arbitrary models when consistency < speed matters.

**Q3: How do you detect if a model is using a spurious correlation?**

A: Five approaches:
1. **Probing**: Train probe on spurious feature (background color, gender words); if high accuracy, model likely uses it
2. **Ablation**: Remove spurious feature from test set; if performance drops significantly, model relied on it
3. **Counterfactual**: Change only the spurious feature; if prediction changes, model is sensitive to it
4. **SHAP audit**: Compute SHAP for spurious feature across many samples; high mean |SHAP| = model relies on it
5. **Out-of-distribution test**: Test on data where spurious correlation is broken; performance should drop if shortcut was used

**Q4: What is mechanistic interpretability and why is it hard?**

A: Mechanistic interp: reverse-engineer the exact computation a neural network performs. Example: Anthropic's finding that induction heads implement in-context learning by searching for previous occurrences of tokens.

Why hard:
1. **Superposition**: Single neuron represents multiple features (polysemanticity)
2. **Distributed representations**: Concepts spread across thousands of neurons
3. **Feature geometry**: Features may be encoded in non-orthogonal directions
4. **Scale**: GPT-4 has ~1.8T parameters — verifying circuit hypotheses at scale is infeasible

Approach: Start with tiny models (1-2 layer transformers), find circuits, verify with activation patching, scale hypothesis.

---

## 🧪 Practical Exercises

### Exercise 1: Counterfactual Explanation Generator (Easy)

```python
def generate_counterfactual(
    x: List[float],
    model_fn: Callable[[List[float]], float],
    target_class: int,   # 0 or 1
    feature_names: List[str],
    step_size: float = 0.05,
    max_steps: int = 100,
) -> dict:
    """
    Find minimum feature changes to flip prediction.
    Greedy: change most impactful feature each step.
    """
    current = list(x)
    original_pred = model_fn(x)
    original_class = 1 if original_pred >= 0.5 else 0

    if original_class == target_class:
        return {"message": "Already in target class", "changes": {}}

    changes = {}
    for step in range(max_steps):
        pred = model_fn(current)
        if (1 if pred >= 0.5 else 0) == target_class:
            break

        # Try changing each feature ±step_size
        best_improvement = 0
        best_feat = None
        best_direction = 0

        for i in range(len(current)):
            for direction in [+1, -1]:
                test = list(current)
                test[i] = max(0, min(1, test[i] + direction * step_size))
                new_pred = model_fn(test)
                improvement = abs(new_pred - 0.5) if target_class == 1 else abs(0.5 - new_pred)
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_feat = i
                    best_direction = direction

        if best_feat is None:
            break

        current[best_feat] = max(0, min(1, current[best_feat] + best_direction * step_size))
        changes[feature_names[best_feat]] = round(current[best_feat] - x[best_feat], 3)

    final_pred = model_fn(current)
    return {
        "original_pred": round(original_pred, 3),
        "counterfactual_pred": round(final_pred, 3),
        "changes": changes,
        "flipped": (1 if final_pred >= 0.5 else 0) == target_class,
    }


# Test: loan denied (0) → find changes to get approved (1)
result = generate_counterfactual(
    x=[0.3, 0.4, 0.5],  # Low scores → denied
    model_fn=loan_model,
    target_class=1,   # Want approved
    feature_names=["age", "income", "credit_score"],
)
print("Counterfactual to get loan approved:")
for feature, change in result["changes"].items():
    print(f"  {feature}: change by {change:+.3f}")
print(f"  Prediction: {result['original_pred']} → {result['counterfactual_pred']}")
print(f"  Flipped: {result['flipped']}")
