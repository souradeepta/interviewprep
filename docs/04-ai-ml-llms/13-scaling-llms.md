# Scaling LLMs — From Millions to Billions of Parameters

Practical strategies for training large models.

---

## 📈 Scaling Laws

**Empirical relationships discovered by OpenAI, DeepMind:**

```
Loss = E / N^α

Where:
- E = compute budget (FLOPs)
- N = number of parameters
- α ≈ 0.07 (for parameters)

Doubling parameters → ~5% loss improvement
Doubling compute → ~5% loss improvement
Doubling data → ~5% loss improvement
```

### Chinchilla Scaling

Optimal allocation:
```
Compute = C
Optimal: 20 tokens per parameter

Example:
- 7B parameters → 140B tokens
- 70B parameters → 1.4T tokens
```

---

## 🏗️ Distributed Training

### Data Parallelism

```
Model on each GPU
Different data on each GPU
Gradients aggregated via AllReduce

Pros: Simple, good scaling
Cons: Model size limited by GPU memory
```

### Tensor Parallelism

```
Model split across GPUs
Each GPU processes different part of computation

Example (split attention):
GPU1: heads [1-16]
GPU2: heads [17-32]

Requires fast interconnect (NVLink)
```

### Pipeline Parallelism

```
Split model by layers
GPU1: Layers 1-10
GPU2: Layers 11-20
GPU3: Layers 21-32

Challenges: GPU idle time, bubble overhead
```

### Expert Parallelism (Mixture of Experts)

```
Multiple expert modules
Router selects which experts for each token

Pros: Sparse activation (faster)
Cons: Load balancing, training complexity
```

---

## 💾 Memory Optimization

### Gradient Checkpointing

```
Forward: Compute, discard intermediate values
Backward: Recompute when needed

Trade-off: Save memory, slower (recomputation)
Often worth it: 3-4x memory savings for 20% slowdown
```

### Activation Checkpointing

Only store subset of activations, recompute others.

### ZeRO (Zero Redundancy Optimizer)

```
Stage 1: Partition optimizer states (4x memory savings)
Stage 2: Partition gradients (2x more savings)
Stage 3: Partition model parameters (3x more savings)

Total: Up to 12x memory reduction!
```

---

## 🔧 Training Tricks

### Learning Rate Scheduling

```
Warmup: Low → high (stabilize training)
Decay: High → low (convergence)

Cosine annealing: Smooth decay over time
```

### Gradient Clipping

```
Cap gradient norm to prevent explosion
norm = ||g||
if norm > threshold:
    g = g * threshold / norm
```

### Loss Scaling (for mixed precision)

```
FP16 has smaller range than FP32
Multiply loss by large number before backward
Then divide gradients by same number

Prevents gradient underflow
```

---

## 🎯 Practical Considerations

### Compute Budget

```
3 passes through data = 6 PetaFLOPs
- 1 pass: Pretraining
- 2 more passes: Instruction tuning + RLHF
```

### Token Budget

```
Typical: 300B - 2T tokens
Rule of thumb: Equal to parameters

7B model: 140B tokens
70B model: 1.4T tokens
```

### Infrastructure

```
100 GPUs (A100): ~$5M
8 weeks training: ~$2-5M compute cost
Total: ~$10M for state-of-art model
```

---

## ❓ Interview Q&A

**Q: How would you scale a 7B to 70B model?**
A: Use scaling laws to guide compute allocation. Implement tensor parallelism, gradient checkpointing, ZeRO. Monitor loss curves to detect issues.

**Q: Data parallelism vs. tensor parallelism?**
A: Data parallelism: Simple, limited by single GPU memory. Tensor parallelism: Complex, enables larger models, needs fast interconnect.

**Q: Why gradient checkpointing?**
A: Save memory (recompute vs. store). Enable larger batch sizes. 3-4x memory savings typically worth 20% slowdown.

---

**Last updated:** 2026-05-22
