# Deep Learning Essentials — CNNs, RNNs, and Advanced Architectures

Building blocks for modern deep learning systems.

---

## 🖼️ Convolutional Neural Networks (CNNs)

### Core Insight

Images have local structure: pixels near each other are related. Share weights across space.

### Architecture

```
Input (3×224×224) →
Conv(32 filters, 3×3) → 32×222×222 →
ReLU →
MaxPool(2×2) → 32×111×111 →
Conv(64, 3×3) → 64×109×109 →
ReLU →
MaxPool(2×2) → 64×54×54 →
Flatten → 64×54×54 →
Dense(128) → ReLU →
Dense(10) → Softmax →
Output (10 classes)
```

### Convolution Operation

```
Input (4×4):
1 2 3 4
5 6 7 8
9 10 11 12
13 14 15 16

Filter (2×2):
1 0
0 1

Convolution at (0,0):
1×1 + 2×0 + 5×0 + 6×1 = 7

Stride: How much to move filter (usually 1)
Padding: Add zeros around edges (preserve size)
```

### Key Parameters

```
Filters: How many patterns to detect
- Shallow layers: Low-level (edges, colors)
- Deep layers: High-level (shapes, objects)

Kernel size: Filter dimensions (usually 3×3)

Stride: Step size when applying filter

Padding: Add zeros around input
- "same": Output same size as input
- "valid": No padding, smaller output

Pooling: Downsampling
- Max pooling: Take max value
- Average pooling: Take average
- Reduces spatial dimensions, computation
```

### Why CNNs Work

1. **Local connectivity:** Neurons see local region
2. **Weight sharing:** Same weights across positions
3. **Hierarchical:** Stack to learn complex patterns
4. **Translation invariance:** Works regardless of position

---

## 🔄 Recurrent Neural Networks (RNNs)

### Core Insight

Sequences have temporal structure: current output depends on previous inputs. Maintain hidden state.

### Architecture

```
For each time step t:
h_t = tanh(W_h × h_{t-1} + W_x × x_t + b)
y_t = W_y × h_t + b

Hidden state h_t carries information from past
```

### Unrolling

```
Time step 1:
x_1 → RNN → y_1
        ↓ h_1

Time step 2:
x_2 → RNN → y_2 (uses h_1)
        ↓ h_2

Time step 3:
x_3 → RNN → y_3 (uses h_2)
```

### Problems

**Vanishing Gradient:**
```
Loss(y_t, target) computed
∂L/∂h_1 = ∂L/∂y_t × ∂y_t/∂h_t × ∂h_t/∂h_{t-1} × ... × ∂h_2/∂h_1

If ∂h/∂h < 1: Gradient → 0 exponentially
h_1 barely updates, doesn't learn long-range dependencies
```

**Exploding Gradient:**
```
If ∂h/∂h > 1: Gradient → ∞
Updates are huge, training unstable (NaN)
```

**Solutions:**
- Gradient clipping: Cap gradient norm
- LSTM/GRU: Gating mechanism preserves gradients
- Residual connections: Direct gradient path

---

## 🔗 LSTM (Long Short-Term Memory)

Gating mechanism to control information flow:

```
Cell state C_t: "Memory" of network
h_t: Hidden state (output)

Gate equations:
f_t = sigmoid(W_f × [h_{t-1}, x_t] + b_f)  # Forget gate
i_t = sigmoid(W_i × [h_{t-1}, x_t] + b_i)  # Input gate
C̃_t = tanh(W_c × [h_{t-1}, x_t] + b_c)   # Candidate
C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t           # Cell state update
o_t = sigmoid(W_o × [h_{t-1}, x_t] + b_o)  # Output gate
h_t = o_t ⊙ tanh(C_t)                       # Hidden state
```

### Intuition

- **Forget gate:** What to discard from memory
- **Input gate:** What new info to add
- **Cell state:** Long-term memory (additive updates)
- **Output gate:** What to output

### Why It Works

```
Cell state updates additively (+ not ×)
∂C_t/∂C_{t-1} = f_t (values 0-1, gentle gradient)
Not exponential, gradient doesn't vanish

LSTM can learn to:
- Keep memory for 100s of steps
- Selectively add/remove info
```

---

## ⚙️ GRU (Gated Recurrent Unit)

Simpler than LSTM, similar performance:

```
Reset gate: r_t = sigmoid(W_r × [h_{t-1}, x_t])
Update gate: z_t = sigmoid(W_z × [h_{t-1}, x_t])
Candidate: h̃_t = tanh(W × [r_t ⊙ h_{t-1}, x_t])
Output: h_t = (1 - z_t) ⊙ h̃_t + z_t ⊙ h_{t-1}

Fewer parameters than LSTM (3 gates vs 4)
Faster to train, often comparable performance
```

---

## 🔗 Attention & Transformers

### Why Attention?

RNNs process sequentially (slow). Attention lets all positions interact directly.

### Self-Attention

```
For each position, compute:
Q (Query): "What am I looking for?"
K (Key): "What can I offer?"
V (Value): "Here's what I have"

Attention score = softmax(Q × K^T / √d) × V
```

### Multi-Head Attention

```
8 parallel attention heads, each learning different relationships
Results concatenated, projected back
```

### Transformer Block

```
Input →
Self-Attention (with residual connection) →
Feed-Forward (dense layers) →
Output (with residual connections)
```

**Advantages:**
- Parallel (all positions simultaneously)
- Long-range dependencies (direct attention)
- Highly parallelizable
- Scales well with data

---

## 🎯 Architecture Design Choices

### For Image Classification

```
CNN:
- ConvBlock (Conv + ReLU + MaxPool)
- Repeat 4-5 times
- Global average pooling
- Dense for classification

Modern: ResNet, EfficientNet
- Skip connections prevent gradient vanishing
- More efficient architecture
```

### For Time Series

```
LSTM/GRU:
- Simpler, works well
- Seq length <= 500

Attention:
- Better long-range dependencies
- Scales to longer sequences
```

### For Text/Language

```
Transformer (primary):
- BERT, GPT, T5
- Parallelizable
- Scales to billions of parameters
```

### For Video

```
3D CNN:
- Conv in space + time
- Learns motion patterns

Or: CNN per frame + RNN
- Separate space (CNN) and time (RNN)
```

---

## ❓ Interview Q&A

**Q: Why use CNNs for images instead of dense networks?**
A: CNNs use local connectivity and weight sharing, reducing parameters and computation 100x+ while capturing spatial structure. Dense networks don't scale to large images.

**Q: What's the vanishing gradient problem and how do LSTMs fix it?**
A: Gradients multiply by <1 at each step, shrinking exponentially. LSTMs use additive updates (cell state), keeping gradients constant, enabling learning over long sequences.

**Q: When would you use GRU vs. LSTM?**
A: GRU is simpler, fewer parameters, faster training. LSTM more expressive for complex tasks. Start with GRU, upgrade to LSTM if needed.

**Q: How do attention mechanisms differ from RNNs?**
A: RNNs process sequentially (bottleneck). Attention lets all positions attend to all others directly (parallelizable). Transformers scale better with data.

---

## ✅ Checklist

- [ ] Understand convolution operation and CNN architecture
- [ ] Know why CNNs work (local connectivity, weight sharing)
- [ ] Understand RNNs and hidden state
- [ ] Know vanishing gradient problem
- [ ] Understand LSTM gates and how they solve vanishing gradient
- [ ] Know attention mechanism basics
- [ ] Understand Transformer architecture
- [ ] Can choose architecture for given problem

---

**Last updated:** 2026-05-22
