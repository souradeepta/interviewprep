# Interpretability & Explainability — Understanding Model Decisions

Why and how to make AI systems transparent.

---

## 🔍 Core Concepts

### Interpretability vs. Explainability

**Interpretability:** Understand how model works
**Explainability:** Explain specific prediction

### Why It Matters

```
Debugging: Find failure modes
Trust: Understand model logic
Regulatory: Required for high-stakes (medical, legal)
Science: Learn about data and patterns
```

---

## 🛠️ Interpretation Techniques

### Attention Visualization

```
Transformer: Visualize which tokens model attends to
Example: For each output token, show attention weights
Shows which inputs influence output
```

### Feature Importance

```
SHAP values: How much each input contributes
Permutation: Remove feature, measure impact
Gradient: Sensitivity to input changes
```

### Probing

```
Extract model's internal representations
Train classifier on them: Do representations encode concepts?
Example: Internal representations encode gender (bias indicator)
```

---

## 📊 Explainability Methods

### LIME (Local Interpretable Model-agnostic Explanations)

```
Approximate model locally with simple model
Perturb input, observe output changes
Identify important features for this prediction
```

### SHAP (SHapley Additive exPlanations)

```
Coalition game theory approach
Fair contribution of each feature
Explains exact prediction
```

### Saliency Maps

```
Compute gradient of output w.r.t. input
High gradient = input influences output
Visualize as heatmap
```

---

## 🚨 Common Issues

**Shortcuts:** Model uses spurious correlations
**Bias:** Disproportionate impact on groups
**Inconsistency:** Similar inputs get different explanations

---

## ❓ Interview Q&A

**Q: How would you check if model is using features you intended?**
A: Attention visualization, feature importance analysis, gradient-based saliency, probing. Adversarial examples to test robustness.

**Q: What's SHAP and why use it?**
A: Fair attribution of each feature to prediction. Theoretically grounded (Shapley values). Slower but interpretable.

**Q: How to detect bias in model explanations?**
A: Explanations differ for demographic groups. Counterfactual analysis. Fairness probes on representations.

---

**Last updated:** 2026-05-22
