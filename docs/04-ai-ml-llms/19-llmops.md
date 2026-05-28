# LLMOps — Operational Excellence for LLM Systems

**Level:** L5-L5+
**Time to read:** ~30 min

Production lifecycle management for LLM-powered applications: deployment, monitoring, cost control, and reliability at scale.

---

## ⚖️ Deployment Strategy Trade-offs

| Strategy | Latency | Cost | Control | Reliability | Best For |
|----------|---------|------|---------|-------------|---------|
| **Managed API** (OpenAI/Anthropic) | 200-2000ms | High ($0.01-$0.06/1K tokens) | Low | 99.9% SLA | Prototyping, variable load |
| **Self-hosted** (vLLM + A100) | 50-500ms | Low ($0.001/1K tokens at scale) | Full | Your burden | 1M+ req/day, regulated data |
| **Serverless** (Replicate/Modal) | 500-5000ms (cold start) | Medium | Medium | 99% | Bursty, infrequent workloads |
| **Hybrid** | Mixed | Optimized | Mixed | Mixed | Cost optimization with fallback |

### Self-Hosted Cost Model (70B model)

```
Hardware:    4× A100 80GB = $12/hr (cloud) or $40K purchase
Throughput:  ~500 tokens/sec (vLLM, FP16, 4 GPUs)
             = 1.8M tokens/hour

At $0.002/1K tokens (self-hosted effective cost):
  Revenue break-even vs. OpenAI ($0.01/1K):   200M tokens/month
  That's ~6,600 tokens/minute sustained load

Rule: self-host when you exceed $10K/month in API costs
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Production LLM Gateway

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LLM Gateway Architecture                         │
│                                                                      │
│  Clients                                                             │
│  [Web App]  [Mobile]  [Internal Tools]                               │
│       │           │           │                                      │
│       └───────────┴───────────┘                                      │
│                   │                                                   │
│          ┌────────▼────────┐                                         │
│          │   API Gateway   │  Rate limiting, auth, routing           │
│          └────────┬────────┘                                         │
│                   │                                                   │
│     ┌─────────────┼─────────────┐                                   │
│     ▼             ▼             ▼                                    │
│  ┌──────┐     ┌──────┐     ┌──────┐                                 │
│  │Prompt│     │Cache │     │Guard │  Input validation               │
│  │Mgmt  │     │Layer │     │Rails │  PII detection                  │
│  └──┬───┘     └──┬───┘     └──┬───┘ Prompt injection filter        │
│     └────────────┴────────────┘                                      │
│                   │                                                   │
│     ┌─────────────┼─────────────┐                                   │
│     ▼             ▼             ▼                                    │
│ ┌────────┐  ┌──────────┐  ┌──────────┐                              │
│ │OpenAI  │  │Anthropic │  │Self-host │  Model routing               │
│ │GPT-4   │  │Claude    │  │LLaMA-3   │  (cost/latency/quality)     │
│ └────────┘  └──────────┘  └──────────┘                              │
│                   │                                                   │
│          ┌────────▼────────┐                                         │
│          │  Observability  │  Logs, traces, metrics                  │
│          └─────────────────┘                                         │
└─────────────────────────────────────────────────────────────────────┘

Open-source options: LiteLLM (routing + fallback), Portkey, HelixML
```

### Pattern 2: vLLM Self-Hosted Inference Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                    vLLM Production Stack                             │
│                                                                      │
│  Load Balancer (nginx / Envoy)                                       │
│       ├── vLLM instance 1 (GPU 0,1)  ─── Llama-3-70B               │
│       ├── vLLM instance 2 (GPU 2,3)  ─── Llama-3-70B               │
│       └── vLLM instance 3 (GPU 4,5)  ─── Mistral-7B (cheap tasks)  │
│                                                                      │
│  Key vLLM features:                                                  │
│  ┌──────────────────────────────────────────────────┐               │
│  │  PagedAttention: KV cache managed like OS pages  │               │
│  │  → 24x more throughput than HuggingFace TGI      │               │
│  │  → 0% memory waste (vs 60% waste in naive KV)    │               │
│  │                                                   │               │
│  │  Continuous batching: Add requests to in-flight  │               │
│  │  → Eliminates idle GPU time between requests     │               │
│  │  → 3-5x throughput vs static batching           │               │
│  │                                                   │               │
│  │  Tensor parallelism: Split model across GPUs     │               │
│  │  → 70B model requires 2-4× A100 80GB GPUs       │               │
│  └──────────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────┘

Launch command:
  python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-70b-instruct \
    --tensor-parallel-size 4 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.90 \
    --port 8000

Throughput: ~500 output tokens/sec on 4× A100
```

### Pattern 3: Semantic Cache Layer

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Semantic Cache Architecture                        │
│                                                                      │
│  Request: "What is the capital of France?"                          │
│       │                                                              │
│       ▼                                                              │
│  Embed query → [0.23, -0.45, ..., 0.78]  (768-dim)                 │
│       │                                                              │
│       ▼                                                              │
│  FAISS / Redis Vector Search                                         │
│       │                                                              │
│       ├── Cache HIT (cosine sim > 0.95)                             │
│       │   "What's France's capital?" → "Paris"                      │
│       │   → Return cached response (0ms + embedding cost)           │
│       │                                                              │
│       └── Cache MISS (sim < 0.95)                                   │
│           → Forward to LLM                                           │
│           → Store (query embedding, response) in cache              │
│                                                                      │
│  Results at 10K QPS:                                                 │
│    Cache hit rate: 40-60% for FAQ-style workloads                   │
│    Cost savings:   40-60% API cost reduction                        │
│    Latency:        HIT: <5ms,  MISS: 200-2000ms                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Pattern 4: Safe Deployment (Blue-Green + Canary)

```
Production Traffic
       │
       ▼
  Load Balancer
       │
       ├── 95% ──► Blue (v1.0, stable)
       │
       └──  5% ──► Green (v2.0, canary)
                        │
                    Monitor:
                    - Error rate
                    - Latency p99
                    - Output quality score
                    - User satisfaction
                        │
                   ┌────┴────┐
                 Pass?      Fail?
                   │          │
                   ▼          ▼
              Increment     Rollback
              to 25%→50%    100% → Blue
              →100%
```

---

## 📊 Key Metrics & SLOs

### Performance SLOs

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| TTFT (time-to-first-token) | < 500ms | 500ms–2s | > 2s |
| Total latency (p99) | < 5s | 5–10s | > 10s |
| Throughput | > 100 req/min | 50–100 | < 50 |
| Error rate | < 0.1% | 0.1–1% | > 1% |
| Token cost/request | < $0.01 | $0.01–0.05 | > $0.05 |

### Quality Metrics

| Metric | What It Measures | Tool |
|--------|-----------------|------|
| **Hallucination rate** | Factual accuracy | LLM-as-judge, FactScore |
| **Relevance** | Answer matches query | BERTScore, ROUGE |
| **Toxicity** | Harmful content | Perspective API, LlamaGuard |
| **Prompt injection** | Security attacks | Custom classifiers |
| **User satisfaction** | Business outcome | Thumbs up/down, CSAT |

---

## 🔧 Key Implementation Patterns

### Semantic Cache with GPTCache

```python
from gptcache import cache
from gptcache.adapter import openai
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

def init_semantic_cache(similarity_threshold: float = 0.95):
    """
    Initialize semantic cache for LLM responses.
    Reduces API calls by 40-60% for FAQ-heavy workloads.
    """
    onnx = Onnx()  # Fast embedding model (~50ms)
    
    data_manager = get_data_manager(
        CacheBase("sqlite"),              # Store responses
        VectorBase("faiss", dimension=onnx.dimension)  # Store embeddings
    )
    
    cache.init(
        embedding_func=onnx.to_embeddings,
        data_manager=data_manager,
        similarity_evaluation=SearchDistanceEvaluation(),
    )
    cache.set_openai_key()

# With cache initialized, use OpenAI as normal — cache is transparent
def cached_completion(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
    # First call: ~1500ms (API + cache store)
    # Subsequent similar queries: ~50ms (cache hit)
```

### LLM Observability with Langfuse

```python
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from anthropic import Anthropic

langfuse = Langfuse(
    public_key="pk-...",
    secret_key="sk-...",
    host="https://cloud.langfuse.com"
)
client = Anthropic()

@observe()  # Automatically traces this function
def rag_pipeline(query: str, user_id: str) -> str:
    """Full RAG pipeline with automatic observability."""
    # Set metadata for filtering in dashboard
    langfuse_context.update_current_trace(
        user_id=user_id,
        session_id=f"session-{user_id}",
        tags=["rag", "production"]
    )
    
    # Retrieval step
    with langfuse_context.trace("retrieval"):
        docs = retrieve_documents(query)
        langfuse_context.update_current_observation(
            input=query,
            output={"num_docs": len(docs)},
        )
    
    # Generation step
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Context: {docs}\n\nQuestion: {query}"
        }]
    )
    
    answer = response.content[0].text
    
    # Log quality score (can be updated later with user feedback)
    langfuse_context.update_current_trace(
        output=answer,
        metadata={"tokens": response.usage.input_tokens + response.usage.output_tokens}
    )
    
    return answer

# Dashboard shows: latency, cost, error rate, user satisfaction per query
```

### Model Router (Cost-Optimized)

```python
from enum import Enum
from anthropic import Anthropic

class Complexity(Enum):
    SIMPLE = "simple"    # factual, short
    MEDIUM = "medium"    # reasoning required
    COMPLEX = "complex"  # multi-step, creative

client = Anthropic()

def classify_query_complexity(query: str) -> Complexity:
    """Route to appropriate model tier based on query complexity."""
    # Simple heuristics (replace with a classifier in production)
    query_lower = query.lower()
    
    simple_patterns = ["what is", "who is", "when did", "define", "list"]
    complex_patterns = ["analyze", "compare", "design", "explain why", "write code"]
    
    if any(p in query_lower for p in simple_patterns) and len(query) < 100:
        return Complexity.SIMPLE
    elif any(p in query_lower for p in complex_patterns):
        return Complexity.COMPLEX
    return Complexity.MEDIUM

# Model cost mapping (per 1M tokens, as of 2026)
MODEL_CONFIG = {
    Complexity.SIMPLE:  {"model": "claude-haiku-4-5-20251001", "cost_per_1m": 0.80},
    Complexity.MEDIUM:  {"model": "claude-sonnet-4-6",         "cost_per_1m": 3.00},
    Complexity.COMPLEX: {"model": "claude-opus-4-7",           "cost_per_1m": 15.00},
}

def routed_completion(query: str) -> tuple[str, str, float]:
    """Route to cheapest model that can handle this query."""
    complexity = classify_query_complexity(query)
    config = MODEL_CONFIG[complexity]
    
    response = client.messages.create(
        model=config["model"],
        max_tokens=1000,
        messages=[{"role": "user", "content": query}]
    )
    
    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    cost = tokens_used * config["cost_per_1m"] / 1_000_000
    
    return response.content[0].text, config["model"], cost

# Cost savings:
# Without routing: All queries → Opus = $15/1M tokens
# With routing (60% simple, 30% medium, 10% complex):
#   Effective cost = 0.6×$0.80 + 0.3×$3.00 + 0.1×$15.00 = $3.00/1M
#   Savings: 80% cost reduction
```

### Production-Ready Rate Limiter

```python
import time
import redis
from functools import wraps

redis_client = redis.Redis(host="localhost", decode_responses=True)

class LLMRateLimiter:
    """
    Token bucket rate limiter for LLM API calls.
    Limits both requests/min and tokens/min per user.
    """
    def __init__(self, requests_per_min: int = 60, tokens_per_min: int = 100_000):
        self.rpm_limit = requests_per_min
        self.tpm_limit = tokens_per_min
    
    def check_and_consume(self, user_id: str, estimated_tokens: int = 500) -> bool:
        """Returns True if request allowed, False if rate limited."""
        pipe = redis_client.pipeline()
        now = time.time()
        window = 60  # 1 minute sliding window
        
        rpm_key = f"rate:rpm:{user_id}"
        tpm_key = f"rate:tpm:{user_id}"
        
        # Remove old entries outside window
        pipe.zremrangebyscore(rpm_key, 0, now - window)
        pipe.zremrangebyscore(tpm_key, 0, now - window)
        
        # Count current usage
        pipe.zcard(rpm_key)
        pipe.zrange(tpm_key, 0, -1, withscores=True)
        
        results = pipe.execute()
        current_rpm = results[2]
        token_entries = results[3]
        current_tpm = sum(score for _, score in token_entries)
        
        if current_rpm >= self.rpm_limit:
            return False  # Rate limited: too many requests
        if current_tpm + estimated_tokens > self.tpm_limit:
            return False  # Rate limited: too many tokens
        
        # Consume quota
        pipe = redis_client.pipeline()
        pipe.zadd(rpm_key, {str(now): now})
        pipe.zadd(tpm_key, {str(now): estimated_tokens})
        pipe.expire(rpm_key, 120)
        pipe.expire(tpm_key, 120)
        pipe.execute()
        
        return True

limiter = LLMRateLimiter(requests_per_min=60, tokens_per_min=100_000)

def rate_limited_completion(user_id: str, prompt: str) -> str:
    if not limiter.check_and_consume(user_id):
        raise Exception("Rate limit exceeded. Retry after 60 seconds.")
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

---

## 🔐 Security Patterns

### Prompt Injection Detection

```python
import re
from anthropic import Anthropic

client = Anthropic()

# Common injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(?:previous|all|above)\s+instructions",
    r"you\s+are\s+now\s+(?:in\s+)?(?:developer|jailbreak|dan)\s+mode",
    r"disregard\s+(?:your|all)\s+(?:previous|prior|training)",
    r"system\s+prompt\s*:",
    r"\[system\]",
    r"<\|im_start\|>",
]

def detect_prompt_injection(user_input: str) -> tuple[bool, str]:
    """Returns (is_injection, reason) for logging."""
    user_lower = user_input.lower()
    
    # Pattern-based detection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_lower):
            return True, f"Matched injection pattern: {pattern}"
    
    # LLM-based detection (for sophisticated attacks)
    if len(user_input) > 500:  # Only for longer inputs (cost optimization)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Cheap model for detection
            max_tokens=10,
            system="Respond only 'SAFE' or 'INJECTION'",
            messages=[{
                "role": "user",
                "content": f"Is this prompt injection? '{user_input[:500]}'"
            }]
        )
        if "INJECTION" in response.content[0].text:
            return True, "LLM classifier flagged as injection"
    
    return False, ""

def safe_completion(user_id: str, user_input: str, system_prompt: str) -> str:
    is_injection, reason = detect_prompt_injection(user_input)
    if is_injection:
        # Log for security review
        log_security_event(user_id, user_input, reason)
        return "I cannot process that request."
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}]
    )
    return response.content[0].text
```

---

## ❓ Interview Q&A

**Q: How would you deploy a new LLM model safely?**
A: Four-stage rollout: (1) Shadow deploy — run new model in parallel with zero user impact, log outputs for comparison; (2) Canary — route 1-5% of traffic, monitor error rate/latency/quality; (3) Progressive rollout — 10% → 25% → 50% → 100% with automated rollback triggers; (4) Full cutover — keep old model warm for instant rollback if issues surface. Key metrics to gate each stage: p99 latency, error rate, LLM-as-judge quality score.

**Q: How to reduce inference latency by 50% without changing the model?**
A: Profile first, then: (1) **Quantization** — FP16→INT8 gives ~1.5x speedup, INT4 gives 2x with ~5% quality loss; (2) **Speculative decoding** — use small draft model (7B) to propose tokens, verify with large model; can achieve 3x speedup; (3) **KV cache** — PagedAttention (vLLM) eliminates 60% memory waste, enabling 2-3x more concurrent requests; (4) **Prefix caching** — cache the KV for your system prompt; saves 30-50% time for long prompts; (5) **Continuous batching** — eliminates idle GPU time, 3x throughput improvement.

**Q: How do you monitor for hallucinations in production?**
A: Three-layer approach: (1) **Automated fact-checking** — retrieve relevant documents, ask LLM if the answer is grounded in them, flag low-confidence responses; (2) **Consistency sampling** — generate 5 responses, flag if they contradict each other (high variance = likely hallucinating); (3) **User signals** — thumbs down, correction requests, follow-up questions are leading indicators. Build a feedback loop: flag → human review → fine-tuning or RAG knowledge update.

**Q: You're spending $50K/month on OpenAI API. How do you reduce costs?**
A: Structured approach:
```
1. Audit call patterns (15 min):
   - What % of calls are "simple" (factual, <200 tokens output)?
   - What % repeat similar prompts?
   - What's average token count?

2. Quick wins (30-50% savings):
   - Model routing: Use Haiku/Sonnet for 70% of calls, GPT-4 for 30%
   - Semantic caching: 40-60% hit rate for FAQ workloads
   - Prompt compression: Remove padding, use fewer examples → 20% token reduction

3. Medium-term (50-80% savings):
   - Fine-tune smaller model on your data → match GPT-4 quality at Haiku price
   - Self-host for high-volume use cases (>$10K/month = self-host wins)

4. Measure impact: A/B test quality before cutting, not after
```

**Q: How do you handle LLM API outages in production?**
A: Multi-provider fallback: route primary to Anthropic, automatic failover to OpenAI, then self-hosted. Use a circuit breaker — after 3 failures in 30 seconds, open the circuit and redirect traffic. Implement retry with exponential backoff (1s, 2s, 4s) for transient errors. Cache responses so repeat queries survive outages. Always have a graceful degradation path — show cached/deterministic responses vs. crashing.

**Q: Design an observability stack for a 100K req/day LLM application.**
A:
```
Tracing:  LangSmith or Langfuse — trace every request (input, output, 
          latency, cost, model version). Sample 100% of errors, 10% of 
          successes for cost efficiency.

Metrics:  Prometheus + Grafana
          - TTFT p50/p99 (alert > 2s)
          - Token cost per request (alert if 2x above baseline)
          - Error rate (alert > 0.5%)
          - Cache hit rate (alert if drops below 30%)

Quality:  LLM-as-judge pipeline (async, not blocking)
          - Sample 5% of responses, score 1-5 on relevance
          - Aggregate daily, alert if drops 10% week-over-week

Logs:     Structured JSON to ElasticSearch
          - All inputs/outputs (with PII masking)
          - Retain 30 days for debugging, 1 year for compliance

Cost:     FinOps dashboard: cost per user, per feature, per model
```

**Q: What is speculative decoding and when should you use it?**
A: A draft model (7B) proposes K tokens ahead, and the main model (70B) verifies all K in parallel (one forward pass). If the draft's tokens match the main model's distribution, accept them — otherwise fall back. Net result: 2-4x throughput improvement with zero quality loss. Best for: large models (70B+), low-latency requirements, hardware where the draft model fits in cache. Avoid: if draft and main are architecturally dissimilar (different families), or if the workload is already compute-saturated.

---

## 🧪 Practical Exercises

### Exercise 1 (Easy) — Cost Dashboard

Build a simple cost tracker that logs and reports LLM API expenses.

```python
import sqlite3
from datetime import datetime, timedelta
from anthropic import Anthropic

client = Anthropic()

# Cost per 1M tokens (as of 2026)
MODEL_COSTS = {
    "claude-haiku-4-5-20251001":  {"input": 0.80,  "output": 4.00},
    "claude-sonnet-4-6":          {"input": 3.00,  "output": 15.00},
    "claude-opus-4-7":            {"input": 15.00, "output": 75.00},
}

def init_db():
    conn = sqlite3.connect("llm_costs.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_calls (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            model TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost_usd REAL,
            feature TEXT
        )
    """)
    conn.commit()
    return conn

def tracked_completion(prompt: str, feature: str = "default") -> str:
    model = "claude-sonnet-4-6"
    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Calculate cost
    costs = MODEL_COSTS[model]
    cost = (response.usage.input_tokens * costs["input"] +
            response.usage.output_tokens * costs["output"]) / 1_000_000
    
    # Log to DB
    conn = init_db()
    conn.execute("""
        INSERT INTO api_calls VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (None, datetime.now().isoformat(), model,
          response.usage.input_tokens, response.usage.output_tokens,
          cost, feature))
    conn.commit()
    
    return response.content[0].text

def cost_report(days: int = 7) -> dict:
    conn = init_db()
    since = (datetime.now() - timedelta(days=days)).isoformat()
    
    rows = conn.execute("""
        SELECT feature, model, SUM(cost_usd) as total_cost,
               COUNT(*) as calls, SUM(input_tokens + output_tokens) as tokens
        FROM api_calls WHERE timestamp > ?
        GROUP BY feature, model
        ORDER BY total_cost DESC
    """, (since,)).fetchall()
    
    return {
        "period_days": days,
        "breakdown": [
            {"feature": r[0], "model": r[1], "cost": r[2], "calls": r[3], "tokens": r[4]}
            for r in rows
        ],
        "total": sum(r[2] for r in rows)
    }

# Usage
tracked_completion("Summarize this document...", feature="summarization")
report = cost_report(7)
print(f"7-day spend: ${report['total']:.2f}")
```

---

### Exercise 2 (Medium) — A/B Testing Framework

```python
import random
import sqlite3
from datetime import datetime
from anthropic import Anthropic

client = Anthropic()

class LLMABTest:
    """
    A/B test two model configs: different models, prompts, or parameters.
    Collects implicit feedback (user_satisfied flag) to determine winner.
    """
    def __init__(self, experiment_name: str, variant_a: dict, variant_b: dict, traffic_split: float = 0.5):
        """
        variant_a/b: {"model": ..., "system_prompt": ..., "temperature": ...}
        traffic_split: fraction of traffic to variant A (0.5 = 50/50)
        """
        self.name = experiment_name
        self.variant_a = variant_a
        self.variant_b = variant_b
        self.split = traffic_split
        self.db = sqlite3.connect(f"ab_test_{experiment_name}.db")
        self._init_db()
    
    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                variant TEXT,
                prompt_hash TEXT,
                latency_ms REAL,
                tokens INTEGER,
                cost_usd REAL,
                user_satisfied INTEGER  -- 1=yes, 0=no, NULL=unknown
            )
        """)
        self.db.commit()
    
    def complete(self, user_id: str, prompt: str) -> tuple[str, str]:
        """Returns (response, experiment_id) for later feedback."""
        # Deterministic assignment (same user always gets same variant)
        variant_name = "A" if hash(user_id) % 100 < self.split * 100 else "B"
        config = self.variant_a if variant_name == "A" else self.variant_b
        
        start = datetime.now()
        response = client.messages.create(
            model=config["model"],
            max_tokens=500,
            system=config.get("system_prompt", ""),
            temperature=config.get("temperature", 1.0),
            messages=[{"role": "user", "content": prompt}]
        )
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        
        cost = response.usage.output_tokens * 0.000015  # Simplified
        exp_id = f"{variant_name}_{datetime.now().timestamp()}"
        
        self.db.execute("""
            INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
        """, (None, datetime.now().isoformat(), variant_name,
              str(hash(prompt)), latency_ms,
              response.usage.input_tokens + response.usage.output_tokens,
              cost))
        self.db.commit()
        
        return response.content[0].text, exp_id
    
    def record_feedback(self, exp_id: str, satisfied: bool):
        """Called when user gives thumbs up/down."""
        variant = exp_id.split("_")[0]
        self.db.execute("""
            UPDATE results SET user_satisfied = ?
            WHERE variant = ? ORDER BY timestamp DESC LIMIT 1
        """, (1 if satisfied else 0, variant))
        self.db.commit()
    
    def results(self) -> dict:
        """Statistical summary of the experiment."""
        for variant in ["A", "B"]:
            row = self.db.execute("""
                SELECT COUNT(*), AVG(latency_ms), AVG(cost_usd),
                       AVG(user_satisfied), COUNT(user_satisfied)
                FROM results WHERE variant = ?
            """, (variant,)).fetchone()
            print(f"Variant {variant}: {row[0]} calls, "
                  f"{row[1]:.0f}ms avg, ${row[2]:.4f}/call, "
                  f"{row[3]*100:.1f}% satisfaction ({row[4]} rated)")

# Usage
test = LLMABTest(
    "system_prompt_test",
    variant_a={"model": "claude-sonnet-4-6", "system_prompt": "You are a helpful assistant."},
    variant_b={"model": "claude-sonnet-4-6", "system_prompt": "You are a concise expert."},
)
response, exp_id = test.complete("user-123", "Explain transformers")
test.record_feedback(exp_id, satisfied=True)
test.results()
```

---

### Exercise 3 (Hard) — Self-Healing LLM Pipeline

```python
"""
Production pipeline with circuit breaker, fallback, retry, and alerting.
Handles: API outages, rate limits, model degradation, budget exhaustion.
"""
import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from anthropic import Anthropic, APIStatusError, RateLimitError

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: int = 30  # seconds
    _failures: int = 0
    _last_failure_time: float = 0
    _state: CircuitState = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit half-open, testing recovery")
            else:
                raise Exception(f"Circuit OPEN. Retry in {self.recovery_timeout}s")
        
        try:
            result = func(*args, **kwargs)
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failures = 0
                logger.info("Circuit closed (recovered)")
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure_time = time.time()
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.error(f"Circuit OPENED after {self._failures} failures")
            raise

PRIMARY_MODEL = "claude-opus-4-7"
FALLBACK_MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5-20251001"]

circuit_breakers = {model: CircuitBreaker() for model in [PRIMARY_MODEL] + FALLBACK_MODELS}

def resilient_completion(
    prompt: str,
    max_retries: int = 3,
    budget_limit_usd: float = 0.10
) -> dict:
    """
    Attempt primary model → fallback → degrade gracefully.
    Returns: {"response": str, "model_used": str, "cost": float, "degraded": bool}
    """
    client = Anthropic()
    models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
    
    for model in models_to_try:
        breaker = circuit_breakers[model]
        
        for attempt in range(max_retries):
            try:
                def _call():
                    return client.messages.create(
                        model=model,
                        max_tokens=500,
                        messages=[{"role": "user", "content": prompt}]
                    )
                
                response = breaker.call(_call)
                
                # Estimate cost
                cost = response.usage.output_tokens * 0.000015  # rough
                if cost > budget_limit_usd:
                    logger.warning(f"Request cost ${cost:.4f} exceeds limit ${budget_limit_usd}")
                
                return {
                    "response": response.content[0].text,
                    "model_used": model,
                    "cost": cost,
                    "degraded": model != PRIMARY_MODEL
                }
            
            except RateLimitError:
                wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                logger.warning(f"Rate limited on {model}, waiting {wait}s")
                time.sleep(wait)
            
            except (APIStatusError, Exception) as e:
                logger.error(f"Error on {model} attempt {attempt+1}: {e}")
                if attempt == max_retries - 1:
                    break  # Try next model
    
    # All models failed — return degraded response
    logger.critical("All models failed, returning degraded response")
    return {
        "response": "Service temporarily unavailable. Please try again shortly.",
        "model_used": None,
        "cost": 0,
        "degraded": True
    }

# Test
result = resilient_completion("Explain quantum computing")
print(f"Used: {result['model_used']}, Degraded: {result['degraded']}")
```

---

### Exercise 4 (Hard) — Automated Evaluation Pipeline

```python
"""
LLM-as-judge: Automatically evaluate response quality at scale.
Used for: regression testing, A/B evaluation, production monitoring.
"""
from dataclasses import dataclass
from typing import Callable
from anthropic import Anthropic

client = Anthropic()

@dataclass
class EvalResult:
    score: int           # 1-5
    reasoning: str
    passed: bool         # score >= threshold

JUDGE_PROMPT = """You are an expert evaluator. Rate the AI response on a scale of 1-5.

Criteria:
- Accuracy: Is the information correct?
- Relevance: Does it answer the question?
- Clarity: Is it easy to understand?
- Completeness: Is it thorough enough?

User Question: {question}
AI Response: {response}
Reference Answer (if available): {reference}

Respond in JSON:
{{"score": 1-5, "reasoning": "one sentence", "issues": ["list", "of", "problems"]}}"""

def evaluate_response(
    question: str,
    response: str,
    reference: str = "N/A",
    threshold: int = 4
) -> EvalResult:
    """Score a single response using LLM-as-judge."""
    import json
    
    judge_response = client.messages.create(
        model="claude-sonnet-4-6",  # Haiku is cheaper but less reliable as judge
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(
                question=question,
                response=response,
                reference=reference
            )
        }]
    )
    
    result = json.loads(judge_response.content[0].text)
    return EvalResult(
        score=result["score"],
        reasoning=result["reasoning"],
        passed=result["score"] >= threshold
    )

def regression_test_suite(
    test_cases: list[dict],  # [{"question": ..., "reference": ..., "min_score": ...}]
    model_fn: Callable[[str], str],
    fail_threshold: float = 0.9  # 90% must pass
) -> dict:
    """Run eval suite; fail if pass rate drops below threshold."""
    results = []
    
    for tc in test_cases:
        response = model_fn(tc["question"])
        eval_result = evaluate_response(
            tc["question"], response,
            tc.get("reference", "N/A"),
            tc.get("min_score", 4)
        )
        results.append({
            "question": tc["question"][:50],
            "score": eval_result.score,
            "passed": eval_result.passed,
            "reasoning": eval_result.reasoning
        })
    
    pass_rate = sum(r["passed"] for r in results) / len(results)
    failures = [r for r in results if not r["passed"]]
    
    return {
        "pass_rate": pass_rate,
        "passed": pass_rate >= fail_threshold,
        "total": len(results),
        "failures": failures,
        "avg_score": sum(r["score"] for r in results) / len(results)
    }

# Example: Run before deploying a new model version
test_cases = [
    {"question": "What is photosynthesis?", "min_score": 4},
    {"question": "Write Python to reverse a string", "min_score": 4},
    {"question": "Explain the CAP theorem", "reference": "Consistency, Availability, Partition tolerance — you can only guarantee two", "min_score": 3},
]

def my_model(q):
    return client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": q}]
    ).content[0].text

suite_result = regression_test_suite(test_cases, my_model)
print(f"Pass rate: {suite_result['pass_rate']*100:.1f}% — {'✓ PASS' if suite_result['passed'] else '✗ FAIL'}")
```

---

## 💡 Interview Tips

**What interviewers test:**
- Can you quantify cost savings? (not just "use caching")
- Do you know the reliability patterns? (circuit breaker, canary, rollback)
- Can you design observability from scratch?
- Do you understand the make-vs-buy decision (self-host vs. API)?

**Key numbers to know:**
- vLLM: ~24x throughput improvement over naive HuggingFace inference
- PagedAttention: eliminates ~60% KV cache memory waste
- Semantic cache: 40-60% API cost reduction for FAQ workloads
- Self-host break-even: ~$10K/month API spend
- Model routing: 70-80% cost reduction with smart routing

**Decision framework for deployment:**
```
Traffic < 1K req/day?          → Managed API (OpenAI/Anthropic)
Traffic 1K–100K req/day?       → Managed API + semantic cache + routing
Traffic > 100K req/day?        → Evaluate self-hosting
Regulated data (HIPAA/GDPR)?  → Self-host or VPC deployment
Need latest models?            → Managed API
Need latency < 100ms?          → Self-host with quantized models
Budget > $10K/month?           → Self-host 70B model
```

---

**Last updated:** 2026-05-23
