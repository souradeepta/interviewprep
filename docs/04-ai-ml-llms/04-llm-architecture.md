# LLM Architecture & Transformers — From Attention to Scale

Understanding how large language models work.

---

## 🏗️ Transformer Architecture

The foundation of all modern LLMs.

### Three Components

**1. Embeddings**
```
Input tokens → Embedding matrix → Vector representation
"hello" → token_id=1234 → embedding_vector (e.g., 768-dim)
```

**2. Transformer Blocks** (repeated N times, e.g., 12-96 layers)
```
Input → Multi-Head Attention → Add&Norm → 
         Feed-Forward → Add&Norm → Output
```

**3. Output Head**
```
Final representation → Linear projection → Softmax → Probability distribution
```

---

## 🔍 Attention Mechanism

Core innovation of transformers: "Look at relevant parts of input"

### Self-Attention Formula

```
Attention(Q, K, V) = softmax(Q·K^T / √d_k) · V

Where:
- Q (Query): "What am I looking for?"
- K (Key): "What can I offer?"
- V (Value): "Here's what I offer"
- √d_k: Scaling factor (d_k = 64 typically)
```

### Worked Example

```
Input: "The cat sat on the mat"

Tokens: [The, cat, sat, on, the, mat]

For token "cat":
- Query: "What related to me?"
- Keys: Similarity to [The, cat, sat, on, the, mat]
- Attention weights: [0.1, 0.6, 0.15, 0.05, 0.05, 0.05]
- Output: Weighted sum of values

Intuition: "cat" attends most to itself (0.6), some to "sat" (0.15)
```

### Why It Works

- **Parallelizable:** All positions compute simultaneously (unlike RNNs)
- **Long-range dependencies:** Can attend to distant tokens directly
- **Interpretable:** Attention weights show what model "looked at"

---

## 👥 Multi-Head Attention

Use multiple attention heads in parallel, learning different relationships.

```
Input (768-dim) → Linear to 8 heads of 96-dim each
→ 8 attention computations in parallel
→ Concatenate [head1, head2, ..., head8]
→ Linear projection back to 768-dim

Benefit: Different heads learn different semantic/syntactic patterns
```

**Example:**
- Head 1: Attends to subject-verb relationships
- Head 2: Attends to pronoun-antecedent relationships
- Head 3: Attends to syntactic structure

---

## 🔄 Feed-Forward Network

Dense layers after attention (applied to each position):

```
FFN(x) = max(0, x·W1 + b1) · W2 + b2
       = ReLU(Linear1(x)) · Linear2

Typical: 768-dim → 3072-dim → 768-dim (4x expansion)
```

**Purpose:**
- Non-linear transformations
- Position-wise processing
- Learned mappings between concepts

---

## ➕ Add & Norm (Residual Connections)

```
Output = LayerNorm(x + Attention(x))
Output = LayerNorm(x + FFN(x))
```

**Residual connections:**
- Let information flow directly through layers
- Prevents gradient vanishing in deep networks
- Allows training 100+ layers

**Layer Normalization:**
- Normalize across feature dimension (not batch)
- Stabilizes training, helps convergence

---

## 📍 Positional Encoding

Transformers have no inherent sense of order. Solution: Add position information.

### Sinusoidal Positional Encoding (Original)

```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

Example (d_model=512):
- Position 0: [sin(0), cos(0), sin(0), cos(0), ...]
- Position 1: [sin(1), cos(0.01), sin(0.01), cos(0.0001), ...]
```

**Properties:**
- Different frequency for each dimension
- Encodes relative positions (PE(pos+k) relates to PE(pos))
- Works for variable length sequences

### Learned Positional Embeddings

Modern models often use learnable embeddings:
```
pos_embed = nn.Embedding(max_seq_len, d_model)
position_ids = torch.arange(seq_len)
pos_embeddings = pos_embed(position_ids)
x = token_embeddings + pos_embeddings
```

---

## 🔑 How LLMs Generate Text

### Autoregressive Generation

```
1. Input: "The cat"
2. Attention: Look at "The cat", predict next token
3. Output: "sat" (highest probability)
4. Append: "The cat sat"
5. Repeat from step 2 with "The cat sat"
```

**Process:**
```python
output_tokens = input_tokens.copy()
for _ in range(max_new_tokens):
    logits = model(output_tokens)[-1]  # Last token prediction
    next_token = sample(logits)  # or argmax for greedy
    output_tokens.append(next_token)
```

### Decoding Strategies

**Greedy:**
```
Next token = argmax(logits)  # Highest probability
```
Pros: Fast, deterministic
Cons: Often suboptimal, can get stuck in loops

**Top-k sampling:**
```
Sample from top-k highest probability tokens
Example: top-k=10, sample uniformly from 10 most likely
```
Pros: Diversity without nonsense
Cons: Still can be random

**Temperature:**
```
logits_scaled = logits / temperature
- temperature < 1: Sharper distribution, more confident
- temperature > 1: Flatter distribution, more diverse
```

---

## 📊 Model Scaling Laws

Research shows predictable scaling behavior:

```
Loss(N) = a·N^(-b)  (N = number of parameters)

Doubling parameters → ~8% loss improvement
Doubling training data → ~6% loss improvement
Doubling compute → ~7% loss improvement
```

**Implications:**
- Larger models learn better (up to data limit)
- Data and compute matter as much as parameters
- Optimal allocation: 20 tokens per parameter

### Architectural Scaling

For transformer with N parameters:
```
- Model dimension: d ≈ N^(1/2)
- Number of layers: L ≈ N^(1/4)
- Number of heads: H ≈ N^(1/4)

Example (7B model):
- Dimension: 4096
- Layers: 32
- Heads: 32
```

---

## 🎯 Key Interview Topics

### Attention Mechanism
**Q: Explain attention. Why not just use LSTM?**
A: Attention lets each position look at relevant parts of input directly. Unlike LSTM which must process sequentially, all positions compute in parallel, and attention can learn long-range dependencies explicitly (not through gradients).

**Q: What's the computational complexity of attention?**
A: O(n²d) where n=sequence length, d=dimension. Both memory and time quadratic in sequence length—major bottleneck for long contexts.

### Transformers
**Q: Why are transformers better than RNNs?**
A: Transformers parallelize (RNNs sequential), handle long-range dependencies directly, enable large-scale pretraining, and scale with compute predictably.

**Q: What does multi-head attention learn?**
A: Different heads specialize in different relationships—syntactic, semantic, positional. Together they capture multiple aspects of relationships.

**Q: What's positional encoding and why is it needed?**
A: Transforms add position information since attention is inherently position-agnostic. Sinusoidal encoding or learned embeddings encode sequence order.

### Scaling
**Q: What's the relationship between model size and loss?**
A: Empirically, loss ∝ N^(-0.07) to N^(-0.10) where N is parameters. Larger models consistently perform better.

**Q: How would you optimize compute allocation between model size, training data, and training duration?**
A: Equal allocation to parameters and tokens (compute ∝ parameters ∝ tokens) minimizes loss for fixed compute budget.

---

## 🔧 Engineering Considerations

### Context Length

```
Attention O(n²) memory with sequence length n

Solutions:
- Sparse attention: Attend to local window + global tokens
- Flash Attention: Efficient CUDA implementation
- KV cache: Reuse previous computations during generation
- Rope (Rotary Position Embeddings): Extrapolate to longer lengths
```

### Inference Optimization

```
Bottleneck: Memory bandwidth (not compute)
- KV cache: Store intermediate values
- Quantization: int8/fp8 instead of fp32
- Batching: Process multiple requests simultaneously
- Speculative decoding: Generate multiple tokens speculatively
```

---

## ✅ Checklist

- [ ] Understand transformer architecture components
- [ ] Explain self-attention mechanism and complexity
- [ ] Understand multi-head attention and what each head learns
- [ ] Know positional encoding methods
- [ ] Explain how LLMs generate text (autoregressive)
- [ ] Know decoding strategies (greedy, sampling, temperature)
- [ ] Understand scaling laws (N, data, compute relationships)
- [ ] Know context length limitations and solutions
- [ ] Explain attention complexity and optimization

---

**Last updated:** 2026-05-22
