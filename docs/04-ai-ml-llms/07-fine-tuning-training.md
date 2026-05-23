# Fine-tuning & Training Strategies — Adapting LLMs Efficiently

How to adapt pre-trained models for specific tasks without retraining from scratch.

---

## 🎯 When to Fine-tune?

### Prompt Engineering First
```
Try 1: Basic prompt → OK results
Try 2: Few-shot examples → Better
Try 3: Chain-of-thought → Good

Stop here if results are acceptable!
Prompt engineering is 10x faster than fine-tuning.
```

### When Fine-tuning is Necessary

```
Cases:
✅ Specific writing style (professional vs. casual)
✅ Domain-specific terminology (medical, legal)
✅ Consistent output format (JSON, structured)
✅ Specific task performance (classification accuracy)
✅ Knowledge updates (retrain on new data)
✅ Cost reduction (smaller fine-tuned model)
```

---

## 📚 Full Fine-tuning

Traditional approach: Update all model weights.

```
Computational cost: HIGH
- Memory: O(parameters) for gradients
- Time: Hours to days for large models
- Cost: $1000+ for 7B model

Pros:
✅ Maximum expressiveness
✅ Learn custom behaviors thoroughly

Cons:
❌ Expensive
❌ Requires significant compute
❌ Risk of catastrophic forgetting
```

---

## ⚡ Parameter-Efficient Fine-tuning

### LoRA (Low-Rank Adaptation)

Instead of updating full weight matrix, learn low-rank modifications:

```
Original weight update:
W_new = W_old + ΔW  (expensive, full matrix)

LoRA:
ΔW = A × B  (where A is m×r, B is r×n, r << n)
Saves 99% of parameters!

Example:
- Full fine-tune: 7B model = 7B parameters to update
- LoRA (r=8): Only 8×d + d×output = ~67M parameters

Memory: 7B → ~1GB (10x reduction)
Time: 24h → 2h (typical speedup)
Cost: $500+ → $50
```

**Implementation:**
```python
from peft import get_peft_model, LoraConfig

config = LoraConfig(
    r=8,  # Rank
    lora_alpha=16,  # Scaling
    target_modules=["q_proj", "v_proj"],  # Which layers
    lora_dropout=0.05,
)

model = get_peft_model(base_model, config)
# Now train model normally - LoRA layers get gradient updates
```

### QLoRA (Quantized LoRA)

Further reduce memory with quantization:

```
LoRA memory: 1GB
Quantize base model (8-bit): 2GB
Total: 3GB (vs 28GB for full 7B model)

Cost: Single GPU is enough!
```

---

## 🎓 Instruction Tuning

Fine-tune on (instruction, response) pairs:

```python
dataset = [
    {
        "instruction": "Summarize this text",
        "input": "Long document...",
        "output": "Summary..."
    },
    {
        "instruction": "Classify sentiment",
        "input": "I love this!",
        "output": "positive"
    },
    ...
]

# Train model to follow instructions
```

**Result:** Model becomes better at following user instructions in-context.

---

## 🔄 RLHF (Reinforcement Learning from Human Feedback)

Multi-stage process to align model with human values.

### Stage 1: Supervised Fine-tuning

```
Train on high-quality (prompt, response) pairs
Result: Better baseline model
```

### Stage 2: Reward Model

```
1. Collect pairs of model responses to same prompt
2. Get human preferences ("Response A is better")
3. Train reward model to predict which is better

Reward model learns: "Response A" → 0.8 (good), "Response B" → 0.3
```

### Stage 3: RL Training

```
RL Objective: Maximize reward while staying close to original model

Use RL algorithm (PPO) to:
- Generate responses
- Score with reward model
- Update model to increase high-scoring responses

Loss = -reward + KL_divergence(original_model)
         ↑                      ↑
      maximize               prevent drift
```

**Result:** Model produces responses humans prefer, aligned with values.

---

## 📊 Practical Training Tips

### Data Preparation

```python
# Quality matters more than quantity
# Best: 100 high-quality examples
# Worse: 10,000 low-quality examples

# Format consistently
dataset = [
    {"prompt": "...", "completion": "..."},
    {"prompt": "...", "completion": "..."},
]

# Test/validation split
train_ratio = 0.8
train_data = dataset[:int(len(dataset) * 0.8)]
val_data = dataset[int(len(dataset) * 0.8):]
```

### Hyperparameter Selection

```
Learning rate: 1e-5 to 1e-3 (start low, increase if underfitting)
Batch size: 8-64 (depends on GPU memory)
Epochs: Usually 3-5 (more can overfit)
Warmup: 10% of total steps helps stability

Example:
epochs = 3
batch_size = 16
total_steps = (len(train_data) / batch_size) * epochs
warmup_steps = int(total_steps * 0.1)
```

### Avoiding Catastrophic Forgetting

```
Problem: Fine-tuning erases original knowledge

Solution 1: Mix in original data
- Original task examples: 80%
- New task examples: 20%

Solution 2: Lower learning rate
- Smaller updates preserve original weights

Solution 3: Use LoRA
- Only train 0.1% of parameters, less damage
```

---

## 📈 Monitoring & Validation

### Metrics

```
Training loss: Should decrease over time
Validation loss: Should decrease, then plateau or slightly increase (overfit)
Exact match: % of perfect matches (for classification tasks)
BLEU/ROUGE: Token overlap (for generation tasks)
```

### Early Stopping

```python
best_val_loss = float('inf')
patience = 3
patience_counter = 0

for epoch in range(max_epochs):
    train()
    val_loss = validate()
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        save_checkpoint()
    else:
        patience_counter += 1
        if patience_counter >= patience:
            load_checkpoint()
            break
```

---

## 💰 Cost Comparison

| Approach | Cost | Time | Data | Quality |
|----------|------|------|------|---------|
| Prompt engineering | $1-10 | Minutes | 0 | Good |
| Fine-tune (LoRA) | $50-500 | 2-24h | 100s-1000s | Better |
| Full fine-tune | $500-5000+ | 1-7 days | 1000s-10k+ | Best |
| RLHF | $5000+ | 1-2 weeks | 10k+ examples | Best+ |

---

## 🤝 Companies & Approaches

**OpenAI (GPT-4):** RLHF + constitutional AI
**Anthropic (Claude):** RLHF + detailed instructions
**Meta (Llama 2):** SFT + DPO (Direct Preference Optimization)
**Google (Gemini):** Constitutional AI + RLHF
**Mistral:** LoRA fine-tuning focus for efficiency

---

## ❓ Interview Q&A

**Q: Should we fine-tune or use prompt engineering?**
A: Start with prompt engineering (fast, cheap). Fine-tune only if prompt engineering doesn't reach desired quality.

**Q: What's LoRA and why is it better than full fine-tuning?**
A: LoRA learns low-rank modifications instead of full weights. 10-100x fewer parameters, 10x faster, 10x cheaper. Trades off expressiveness but usually worth it.

**Q: How do you prevent catastrophic forgetting?**
A: Mix original and new data, use lower learning rate, or use LoRA (limits changes).

**Q: What's RLHF and when would you use it?**
A: Multi-stage training using human preferences to align model. Use when instruction-following quality matters, quality > cost.

**Q: How much data do you need to fine-tune?**
A: For LoRA: 100-500 high-quality examples. For full fine-tune: 1000+ examples.

---

## ✅ Checklist

- [ ] Know when to fine-tune vs. prompt engineer
- [ ] Understand LoRA and its advantages
- [ ] Know how to prevent catastrophic forgetting
- [ ] Understand RLHF stages
- [ ] Know data preparation best practices
- [ ] Understand hyperparameter selection
- [ ] Know how to monitor training (early stopping)
- [ ] Understand cost/time trade-offs

---

**Last updated:** 2026-05-22
