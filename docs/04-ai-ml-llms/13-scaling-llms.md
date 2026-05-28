# Scaling LLMs — From Millions to Billions of Parameters

**Level:** L5
**Time to read:** ~20 min

Practical strategies for training and deploying large language models: scaling laws, parallelism strategies, memory optimization, and compute budgeting.

---

## ⚖️ Parallelism Strategy Trade-offs

| Strategy | Memory Saving | Comm Overhead | Max Model Size | Best For |
|----------|--------------|---------------|----------------|---------|
| **Data Parallelism** | None | Low (gradients) | Single GPU | Small models, large batches |
| **Tensor Parallelism** | Per-GPU | High (all-reduce each layer) | 8-16× GPU | Single large model |
| **Pipeline Parallelism** | Per-stage | Medium (activations) | Any | Very large models |
| **ZeRO-3** | 12× | High (parameter sharding) | GPU × N | Training any size |
| **FSDP** | 4–16× | Medium | GPU × N | PyTorch native |
| **Expert Parallelism (MoE)** | Sparse | Medium (routing) | Unlimited | Sparse models |

### Scaling Laws Summary

```
Chinchilla (DeepMind 2022):
  Optimal tokens = 20 × parameters

  Model       Params    Optimal Tokens    Compute (PF-days)
  ────────────────────────────────────────────────────────
  LLaMA-7B    7B        140B              1.5k
  LLaMA-13B   13B       260B              2.8k
  LLaMA-70B   70B       1.4T              15k
  GPT-4       ~1.8T     36T              ~380k (est.)
  
Power law: Loss ∝ N^-0.076 × D^-0.095
  (N = params, D = training tokens)
```

---

## 🏗️ Architecture Patterns

### Pattern 1: 3D Parallelism (Megatron-LM)

```
Combine tensor (TP), pipeline (PP), and data (DP) parallelism:

                         DP group (gradient sync)
                    ┌────────────────────────────┐
                    │  Node 1          Node 2    │
  PP stage 1 ─────► │  [TP=0][TP=1]  [TP=0][TP=1]│
  PP stage 2 ─────► │  [TP=0][TP=1]  [TP=0][TP=1]│
  PP stage 3 ─────► │  [TP=0][TP=1]  [TP=0][TP=1]│
                    └────────────────────────────┘
  
GPT-3 (175B): TP=8, PP=8, DP=64 = 4096 GPUs
Throughput: ~150 TFLOP/s per GPU (50% MFU)
```

### Pattern 2: ZeRO Optimizer States

```
ZeRO Stage 1: Partition optimizer states (Adam: m, v, fp32 weights)
  Each GPU holds 1/N of optimizer states
  Memory: 4× reduction (for 4-GPU setup)

ZeRO Stage 2: + Partition gradients
  Each GPU accumulates only its share of gradients
  Memory: 8× reduction (combined)

ZeRO Stage 3: + Partition model parameters
  Each GPU holds 1/N of parameters, gathers on demand
  Memory: 12× reduction (combined)
  Tradeoff: Higher communication overhead

Practical: ZeRO-2 is most common (good savings, low comm overhead)
```

### Pattern 3: Mixture of Experts (MoE)

```
Standard transformer:
  All 175B parameters activated per token

MoE transformer (Mixtral 8×7B):
  8 expert FFN layers (7B each = 56B total)
  Router selects top-2 experts per token
  Only 2 × 7B = 14B parameters activated
  
  Input token → Router → Expert 1 (25%), Expert 5 (75%)
                       → Weighted sum of outputs
  
Cost: 56B param model runs at speed of 14B model
Load balancing loss prevents routing collapse
```

---

## 📊 Training Cost Calculator

```python
import math

def estimate_training_cost(
    params_billions: float,
    tokens_billions: float,
    num_gpus: int,
    gpu_tflops: float = 312.0,     # A100 theoretical
    mfu: float = 0.45,             # Model flop utilization (typical)
    gpu_cost_per_hour: float = 3.0,  # $/hr for A100
) -> dict:
    """
    Estimate training compute cost.
    FLOPs ≈ 6 × params × tokens (standard approximation)
    """
    params = params_billions * 1e9
    tokens = tokens_billions * 1e9
    
    # Total training FLOPs
    total_flops = 6 * params * tokens
    
    # Effective throughput per GPU
    effective_tflops = gpu_tflops * mfu
    
    # GPU-hours needed
    total_tflops = total_flops / 1e12
    gpu_hours = total_tflops / effective_tflops
    
    # Wall-clock time
    wall_hours = gpu_hours / num_gpus
    wall_days = wall_hours / 24
    
    # Cost
    total_cost = gpu_hours * gpu_cost_per_hour
    
    return {
        "total_flops": f"{total_flops:.2e}",
        "gpu_hours": round(gpu_hours),
        "wall_clock_days": round(wall_days, 1),
        "estimated_cost_usd": f"${total_cost:,.0f}",
        "optimal_tokens": f"{params_billions * 20:.0f}B (Chinchilla)",
        "is_compute_optimal": abs(tokens_billions - params_billions * 20) / (params_billions * 20) < 0.2,
    }


# Examples
configs = [
    (7, 140, 128, "LLaMA-2 7B"),
    (70, 1400, 512, "LLaMA-2 70B"),
    (175, 300, 1024, "GPT-3 (original)"),
]

for params, tokens, gpus, name in configs:
    est = estimate_training_cost(params, tokens, gpus)
    print(f"\n{name}:")
    print(f"  FLOPs: {est['total_flops']}")
    print(f"  Wall clock: {est['wall_clock_days']} days on {gpus} A100s")
    print(f"  Cost: {est['estimated_cost_usd']}")
    print(f"  Compute optimal: {est['is_compute_optimal']}")
    print(f"  Optimal tokens: {est['optimal_tokens']}")


def memory_per_gpu(
    params_billions: float,
    precision: str = "bf16",
    optimizer: str = "adam",
    batch_size: int = 1,
    seq_len: int = 2048,
) -> dict:
    """Estimate GPU memory requirements."""
    bytes_per_param = {"fp32": 4, "fp16": 2, "bf16": 2, "int8": 1, "int4": 0.5}[precision]
    params = params_billions * 1e9
    
    # Weights
    weights_gb = params * bytes_per_param / 1e9
    
    # Optimizer states (Adam: m, v, fp32 copy)
    optimizer_gb = 0.0
    if optimizer == "adam":
        optimizer_gb = params * 12 / 1e9  # 3× fp32 (m, v, master weights)
    
    # Activations (approximate: seq_len × batch × hidden × layers)
    hidden = int(math.sqrt(params_billions / 0.012) * 1024)  # rough estimate
    layers = max(12, int(params_billions * 2))
    activation_gb = batch_size * seq_len * hidden * layers * 2 / 1e9  # bf16
    
    total_gb = weights_gb + optimizer_gb + activation_gb
    
    return {
        "weights_gb": round(weights_gb, 1),
        "optimizer_gb": round(optimizer_gb, 1),
        "activation_gb": round(activation_gb, 1),
        "total_gb": round(total_gb, 1),
        "a100_80gb_needed": math.ceil(total_gb / 80),
    }


print("\n\nMemory Requirements:")
for params in [7, 13, 70]:
    mem = memory_per_gpu(params, precision="bf16", optimizer="adam")
    print(f"  {params}B model: {mem['total_gb']} GB total → {mem['a100_80gb_needed']} A100-80GB")
```

---

## ❓ Interview Q&A

**Q1: How do you choose between tensor parallelism and pipeline parallelism?**

A: 
- **Tensor parallelism (TP)**: Split each layer across GPUs; requires all-reduce after every layer; needs fast interconnect (NVLink, ~600 GB/s). Best within a single server. TP=2-8 is common.
- **Pipeline parallelism (PP)**: Split model by layers; activations pass between stages; has pipeline bubble overhead (K/K+1 efficiency). Best across nodes. PP=8-128.
- **Rule**: Use TP within a node (fast interconnect), PP across nodes (slower interconnect). Combine both + DP for largest models.

**Q2: What are scaling laws and what do they tell us?**

A: Empirical power laws relating loss to compute, parameters, and data:
- `Loss ∝ N^-0.076` (double params → 5% loss reduction)
- Chinchilla finding: for a given compute budget C, allocate equally between params and tokens. GPT-3 (175B, 300B tokens) was undertrained — same compute on 66B params with 1.4T tokens gives better loss.
- Practical: most practitioners now use 20 tokens/param as rule of thumb. LLaMA models were trained with this insight.

**Q3: Why does gradient checkpointing trade time for memory?**

A: Forward pass stores all activations (needed for backward pass gradients). For 70B model: activations consume >100 GB. Gradient checkpointing keeps only 1 in √n activation checkpoints; recomputes the rest during backward. Memory: O(√n) instead of O(n). Time cost: +20-30% (one extra forward pass per checkpoint interval). Almost always worth it for large models.

**Q4: How does ZeRO-3 differ from naive data parallelism?**

A: Naive DP: each GPU holds full model copy + full optimizer states. Memory: 16 bytes/param (bf16 weights + Adam states). For 70B model: 70B × 16 = 1,120 GB → need 14 A100-80GB just for optimizer.

ZeRO-3: Shard parameters, gradients, and optimizer states across N GPUs. Each GPU holds 1/N of each. Memory: 16 bytes × 70B / 128 GPUs = 8.75 GB per GPU — fits on one A100! Trade-off: Must gather parameters on-demand (all-gather before each layer, reduce-scatter after). Communication volume: 3 × param_bytes per iteration vs. 2 × grad_bytes for naive DP.

---

## 🧪 Practical Exercises

### Exercise 1: Compute Budget Allocator (Easy)

```python
def optimal_model_given_compute(
    compute_flops: float,  # total FLOPs budget
    min_params_b: float = 1.0,
    max_params_b: float = 1000.0,
) -> dict:
    """
    Given compute budget C, find optimal (N, D) per Chinchilla:
    N = sqrt(C / (6 × 20)) = params
    D = C / (6 × N)        = tokens
    """
    # Chinchilla: N_opt ≈ √(C / 120), D_opt ≈ 20 × N_opt
    n_opt = math.sqrt(compute_flops / 120)
    d_opt = 20 * n_opt
    
    return {
        "optimal_params_B": round(n_opt / 1e9, 1),
        "optimal_tokens_B": round(d_opt / 1e9, 0),
        "compute_flops": f"{compute_flops:.2e}",
        "efficiency_note": "Per Chinchilla scaling — N and D should scale equally",
    }


budgets = [1e22, 1e23, 1e24]  # FLOPs
for c in budgets:
    print(optimal_model_given_compute(c))
```

---

**Last updated:** 2026-05-22
