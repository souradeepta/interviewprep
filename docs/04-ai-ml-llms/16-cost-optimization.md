# Cost Optimization for ML — Reducing Spend Without Sacrificing Quality

Practical strategies for cost-effective ML systems.

---

## 💰 Cost Breakdown

```
Training: One-time, amortized over all requests
Inference: Per-query, scales with usage

Typical for LLM API:
- Input: $0.001-0.05 per 1K tokens
- Output: $0.003-0.15 per 1K tokens
```

---

## 🎯 Optimization Strategies

### Model Selection

**Smaller models:**
- 3B model: 10x cheaper than 30B
- 20% accuracy loss typical
- Good for cost-sensitive applications

**Distillation:** Train small model to mimic large
- Large model as teacher
- Small student learns outputs
- 5-10x speedup, minimal quality loss

### Inference Optimization

**Quantization:** 8-bit or 4-bit
- 4x memory reduction
- 2-3x faster inference
- <5% accuracy loss

**Batching:** Process multiple requests together
- Amortize latency
- Better GPU utilization
- Higher throughput

**Caching:** Reuse computations
- Cache embeddings, pre-computed responses
- Instant response for repeated queries

---

## 🔄 Data Efficiency

**Few-shot learning:** Reduce training data needs
**Transfer learning:** Leverage pre-training
**Active learning:** Select most informative examples
**Data augmentation:** Synthetic data generation

---

## 🏗️ System-Level Optimization

**Use cheaper regions:** Different cloud costs
**Reserved instances:** Long-term commitment discounts
**Spot instances:** Interruptible, 70-90% cheaper
**Self-host:** Own infra, long-term ROI

---

## ❓ Interview Q&A

**Q: How would you cut inference costs 10x?**
A: Quantization (4x), batching (3x), caching (2x), smaller model (5x). Combine: 10-30x savings.

**Q: Trade-offs of distillation?**
A: Expensive to train (need teacher). Performance gap (5-20%). But huge inference savings. Worth for deployed systems.

**Q: When to self-host vs. API?**
A: API: <100k QPS, easy setup. Self-host: >1M QPS, long-term ROI. Hybrid: Peak load → API, steady → self-hosted.

---

**Last updated:** 2026-05-22
