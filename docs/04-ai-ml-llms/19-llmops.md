# LLMOps — Operational Excellence for LLM Systems

Managing LLM systems in production at scale.

---

## 📊 Deployment Patterns

### Self-Hosted

```
Own infrastructure (on-prem or cloud VMs)
Pros: Full control, cost-effective at scale
Cons: Ops burden, maintenance

Stack: vLLM, TensorRT, Ray Serve
```

### API-Based

```
Use provider API (OpenAI, Anthropic, etc.)
Pros: Simple, no ops, latest models
Cons: Cost, vendor lock-in, latency

Trade-offs: Easy but expensive
```

### Hybrid

```
Self-host internal models
Use APIs for specialized/large models
Balance cost and convenience
```

---

## 🎯 Monitoring & Observability

### Metrics

**Latency:** p50, p99 response times
**Throughput:** Requests per second
**Token throughput:** Tokens/sec
**Cost per request:** $ per query
**Cache hit rate:** Reuse efficiency

### Alerting

```
Alert if:
- Latency p99 > 1s
- Error rate > 1%
- Token cost > budget
- Memory usage > threshold
```

---

## 🔄 Model Management

### Versioning

```
v1.0: Initial deployment
v1.1: Fine-tuned on domain data
v2.0: New pre-trained model

Rollback: v2.0 → v1.1 if issues
Shadow deploy: Test v2.0 in parallel
```

### A/B Testing

```
% traffic to v1.0: 50%
% traffic to v2.0: 50%

Compare: Latency, cost, quality
Winner: Gradually increase % to better model
```

### Gradual Rollout

```
Day 1: 5% traffic → v2.0
Day 3: 25% → v2.0
Day 7: 100% → v2.0

Catch issues early with small % impact
```

---

## 💰 Cost Management

**Reserved capacity:** Cheaper long-term
**Spot instances:** 70-90% discount, interruptions
**Caching:** Avoid recomputation
**Quantization:** Smaller models, cheaper
**Right-sizing:** Match compute to needs

---

## 🔐 Security & Compliance

**Input validation:** Reject malicious inputs
**Output filtering:** Block harmful outputs
**PII masking:** Remove sensitive data
**Audit logging:** Track all requests
**Access control:** Limit who can use API

---

## ❓ Interview Q&A

**Q: How would you deploy a new LLM model safely?**
A: Shadow deploy (parallel, small %), monitor metrics, A/B test, gradual rollout. Rollback plan ready.

**Q: How to reduce inference latency?**
A: Quantization, caching, batching, better hardware, model distillation. Profile to find bottleneck.

**Q: How to monitor for hallucination in production?**
A: Compare output to knowledge base. User feedback. Automated fact-checking. Alert on low confidence.

---

**Last updated:** 2026-05-22
