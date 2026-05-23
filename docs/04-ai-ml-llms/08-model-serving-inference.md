# Model Serving & Inference Optimization — Getting Models to Production

How to deploy models efficiently at scale.

---

## 🎯 Inference Challenges

LLM inference is different from training:

```
Training: Limited runs, ample time
- Run once per day, takes 24 hours, fine

Inference: Continuous requests, tight latency
- 1000 concurrent users
- <100ms latency required  
- Cost-sensitive

This is the hard problem!
```

---

## ⚡ Optimization Techniques

### Quantization

Reduce precision to use less memory/compute:

```
Full Precision (fp32): 1 float = 4 bytes
- 7B model = 28GB memory

Half Precision (fp16): 1 float = 2 bytes
- 7B model = 14GB memory
- 2x faster, barely any quality loss

8-bit Quantization: ~1 byte per parameter
- 7B model = 7GB memory
- 4x memory savings
- Small quality loss (usually acceptable)

4-bit Quantization: 0.5 byte per parameter
- 7B model = 3.5GB memory
- Reasonable quality with tiny GPU
```

### Batching

Process multiple requests together:

```
Single request: Process immediately
- Latency: 100ms
- Throughput: 10 req/sec

Batch of 8: Wait, then process together
- Latency: 150ms (30ms + batch overhead)
- Throughput: 80 req/sec (8x improvement!)

Trade-off: Add 50ms latency, get 8x throughput
Good for backend batch jobs, less good for interactive.
```

### KV Cache

Reuse computation during generation:

```
Generate token 1: Attend to position 1 (compute K,V)
Generate token 2: Attend to positions 1,2 (reuse K,V from 1)
Generate token 3: Attend to positions 1,2,3 (reuse K,V from 1,2)

Without KV cache: Recompute everything
With KV cache: Reuse previous attention values
Result: 2-3x speedup
Memory tradeoff: Store K,V for all positions
```

### Flash Attention

Optimized attention implementation:

```
Standard attention:
- O(n²) memory for attention matrix
- Slow GPU memory access patterns

Flash Attention:
- Cache-aware algorithm
- 3-4x faster
- Same quality
- Standard in production

Just use modern libraries (transformers, vLLM)
```

### Speculative Decoding

Generate multiple tokens speculatively:

```
1. Small model (fast): Generate 3 tokens speculatively
2. Large model (slow): Verify tokens are correct
3. Accept all or some: Keep if large model agrees

Trade-off: Some wasted small model compute,
but large model is bottleneck so overall faster
```

---

## 🏗️ Serving Architecture

### Single GPU Approach

```
Request → GPU Queue → Model → Generate → Response

Pros: Simple, low cost
Cons: Limited concurrency (process 1 at a time)
Use when: <100 QPS with higher latency acceptable
```

### Batched Serving

```
Request 1 ──┐
Request 2 ──┼→ Queue → Batch → GPU → Unbatch → Response 1,2,3,4
Request 3 ──┤
Request 4 ──┘

Pros: Higher throughput
Cons: Increased latency due to batching
Use when: 100-1000 QPS, some latency acceptable
```

### Distributed Tensor Parallelism

```
Model too large for single GPU:

GPU 1: attention_head_0,1,2,3
GPU 2: attention_head_4,5,6,7

Requires: Fast interconnect (NVLink, InfiniBand)
Use when: Model > single GPU memory
```

### Pipeline Parallelism

```
Split model across devices:

GPU 1: Layers 1-10   → GPU 2: Layers 11-20 → GPU 3: Layers 21-32

Trade-off: GPU idle time when pipelining (GPU 1 waits for GPU 2)
```

---

## 📊 Production Patterns

### Load Balancing

```
Request → Load Balancer → [Server 1: 100/100 loaded]
                         → [Server 2: 80/100 loaded] ← route here
                         → [Server 3: 50/100 loaded]

Strategies:
- Round robin: Alternate servers
- Least loaded: Send to least busy
- Latency-aware: Consider latency history
```

### Caching

```
Cache generations to avoid recomputation:

User 1: "Summarize document X"
  → Generate summary, cache result

User 2: "Summarize document X"
  → Return cached result immediately
  → No generation needed, instant response

Cache invalidation: Depends on use case
```

### Model Serving Frameworks

```
vLLM: Popular, optimized for LLM inference
- Auto batching
- Efficient memory management
- Easy distributed setup

TensorRT-LLM: NVIDIA, compiled optimization
- Better than vLLM for some models
- More complex to set up

Ray Serve: General framework
- More flexible
- Less optimized for LLMs

Ollama: Easy local deployment
- Simple CLI
- Good for prototyping
```

---

## 💰 Cost Optimization

### Latency vs. Throughput Trade-off

```
Target: Process 1000 users/day

Option 1: High latency, high throughput
- 2 GPUs, batch size 32
- Latency: 200ms
- Throughput: 1000 QPS
- Cost: 2 GPUs × $0.50/h = $12/day

Option 2: Low latency, low throughput  
- 10 GPUs, batch size 1
- Latency: 50ms
- Throughput: 1000 QPS
- Cost: 10 GPUs × $0.50/h = $60/day

Choose based on user tolerance!
```

### Model Size Selection

```
7B model (good quality, fast):
- Inference: 20ms
- Cost per 1M tokens: $0.05

70B model (better quality, slow):
- Inference: 200ms
- Cost per 1M tokens: $0.50

Question: Does 3.5x better quality justify 10x higher cost?
Answer: Depends on your users!
```

---

## 🔍 Monitoring & Observability

### Key Metrics

```
Latency (p50, p99): How fast are responses?
- p50: Median response time
- p99: 99th percentile (tail latencies)
- Aim: p50 < 100ms, p99 < 500ms

Throughput: Requests per second
- Aim: Full GPU utilization

Token throughput: Tokens generated per second
- More meaningful than request throughput
- Aim: 100-300 tokens/sec per GPU

Cost per request: $/request
- Important business metric
```

### Alerting

```
Alert if:
- Latency p99 > 500ms (user experience)
- GPU memory error (memory leak)
- Generation timeout (stuck model)
- Error rate > 0.1% (production issue)
```

---

## ❓ Interview Q&A

**Q: How would you optimize LLM inference for low latency?**
A: Use quantization (4-bit), KV caching, batching, modern optimized frameworks (vLLM), and request batching within latency limits.

**Q: What's the trade-off between latency and throughput?**
A: Higher batch sizes → more throughput but higher latency. Choose based on user tolerance. Real-time apps need low latency, batch jobs can tolerate higher.

**Q: How do you serve a 70B model on limited GPUs?**
A: Quantize (4-bit), use tensor parallelism, cache KV, use optimized kernels. May need 2-4 GPUs instead of 6+.

**Q: What's the cost of generating 1M tokens?**
A: Depends on model and hardware. Rule of thumb: $0.01-0.10 per 1M tokens depending on size.

---

## ✅ Checklist

- [ ] Understand quantization trade-offs
- [ ] Know batching strategies and trade-offs
- [ ] Understand KV caching and its benefits
- [ ] Know different serving architectures
- [ ] Understand tensor and pipeline parallelism
- [ ] Know production patterns (load balancing, caching)
- [ ] Understand cost vs. latency trade-offs
- [ ] Know key metrics to monitor

---

**Last updated:** 2026-05-22
