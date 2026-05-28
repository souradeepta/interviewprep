# Neural Networks Basics — From Perceptron to Backpropagation

**Level:** L4
**Time to read:** ~20 min

Understanding how neural networks learn.

---

## 🧠 The Perceptron

Simplest neural network: single neuron making binary decision.

```python
# Perceptron: y = sign(w·x + b)
output = sign(weights @ inputs + bias)
```

**Decision boundary:** Linear hyperplane separating two classes
**Limitation:** Can only solve linearly separable problems (XOR fails)

---

## 🔗 Neural Network Architecture

### Layers

**Input Layer:** Raw features
**Hidden Layers:** Learn representations
**Output Layer:** Final prediction

```
Input → Dense → ReLU → Dense → ReLU → Dense → Softmax → Output
 (3)      (64)   (64)    (32)   (32)    (10)     (10)
```

### Neurons & Activation

**Forward pass of single neuron:**
```
z = w₁x₁ + w₂x₂ + ... + wₙxₙ + b    # weighted sum
a = σ(z)                            # activation function
```

### Activation Functions

| Function | Formula | Range | When to Use |
|----------|---------|-------|------------|
| **ReLU** | max(0, x) | [0, ∞) | Hidden layers (default) |
| **Sigmoid** | 1/(1+e^-x) | (0, 1) | Binary classification output |
| **Tanh** | (e^x - e^-x)/(e^x + e^-x) | (-1, 1) | Recurrent networks |
| **Softmax** | e^xᵢ / Σe^xⱼ | (0,1), sums to 1 | Multi-class output |
| **Leaky ReLU** | x if x>0, αx if x≤0 | (-∞, ∞) | Avoid "dying ReLU" |

**Why activation functions matter:**
- Without them, stacking layers just does linear transformation
- Activation introduces non-linearity, letting networks learn complex patterns

---

## 🔄 Backpropagation

How neural networks learn by computing gradients.

### The Chain Rule

```
∂Loss/∂w = ∂Loss/∂a · ∂a/∂z · ∂z/∂w

Working backwards:
1. Compute ∂Loss/∂output
2. Propagate through each layer
3. Update weights in direction of negative gradient
```

### Algorithm Steps

```
Forward Pass:
  x → Linear(w,b) → Activation → ... → Loss

Backward Pass:
  ∂Loss/∂last_w ← ∂Loss/∂output · Chain of derivatives
  ∂Loss/∂prev_w ← ∂Loss/∂hidden · ...
  
Weight Update:
  w_new = w_old - learning_rate · ∂Loss/∂w
```

**Complexity:** O(forward_pass) for both forward and backward

---

## 📈 Optimization Details

### Batch Normalization

Normalize layer outputs to have mean 0, std 1:
```
normalized = (x - mean) / sqrt(variance + ε)
scaled = γ · normalized + β
```

**Benefits:**
- Stabilizes training
- Allows higher learning rates
- Reduces internal covariate shift
- Acts as regularization

**Note:** Behavior different during training (uses batch stats) vs. inference (uses running stats)

### Learning Rate Scheduling

```python
# Step decay
if epoch % 10 == 0:
    learning_rate *= 0.1

# Exponential decay
learning_rate = initial_lr * exp(-decay_rate * epoch)

# Cosine annealing (warms up then decays)
lr = min_lr + 0.5 * (max_lr - min_lr) * (1 + cos(π * epoch / total_epochs))
```

### Momentum & Acceleration

```
# Without momentum: Just follow gradient
w_new = w - lr · ∇w

# With momentum: Accumulate direction
v = β · v + ∇w                    # β usually 0.9
w_new = w - lr · v
```

**Effect:** Speeds up consistent directions, dampens oscillations

---

## 🧮 Common Architectures

### Feedforward (Dense) Networks

- Fully connected layers
- Universal approximators
- Good for tabular data

### Convolutional Networks (CNNs)

**Key insight:** Local structure in images → share weights across space

```
Conv(32 filters, 3×3) → ReLU → MaxPool(2×2) → Conv(64, 3×3) → ...
```

**Benefits:**
- Fewer parameters than dense
- Translation invariance
- Learns hierarchical features (edges → shapes → objects)

### Recurrent Networks (RNNs)

**Key insight:** Sequence data → maintain hidden state

```
h_t = activation(W_h · h_{t-1} + W_x · x_t + b)
y_t = W_y · h_t + b
```

**Problems:**
- **Vanishing gradient:** Gradients → 0 over long sequences
- **Exploding gradient:** Gradients → ∞, causes NaN

**Solutions:**
- **LSTM (Long Short-Term Memory):** Gate mechanism preserves gradients
- **GRU (Gated Recurrent Unit):** Simpler than LSTM, similar performance
- **Gradient clipping:** Cap gradient norm

---

## 🎯 Loss Functions

### Classification

**Cross-Entropy Loss (most common):**
```
L = -Σ y_true · log(y_pred)
```
- Penalizes confident wrong predictions heavily
- Interpretable as information theory

**Binary Cross-Entropy:**
```
L = -(y·log(p) + (1-y)·log(1-p))
```

### Regression

**Mean Squared Error (MSE):**
```
L = (1/n) · Σ(y_true - y_pred)²
```
- Quadratic penalty, outlier-sensitive

**Mean Absolute Error (MAE):**
```
L = (1/n) · Σ|y_true - y_pred|
```
- Linear penalty, more robust to outliers

---

## 🚀 Training Tips

### Initialization

**Poor initialization:** Weights all zero or too large
```
# Xavier/Glorot initialization
std = sqrt(2 / (n_in + n_out))
weights ~ Normal(0, std)
```

Proper init prevents saturation and ensures signal flows through network.

### Batch Size

- **Small (16-32):** Noisier updates, regularization effect, slower convergence
- **Large (256+):** Stable updates, faster training, may generalize worse
- **Sweet spot:** 32-128 for most tasks

### Number of Epochs & Early Stopping

```python
best_val_loss = inf
patience = 10
for epoch in range(max_epochs):
    train_loss = train_one_epoch()
    val_loss = validate()
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience = 10  # Reset
    else:
        patience -= 1
        if patience == 0:
            break  # Stop if no improvement
```

---

## 🔍 Debugging Neural Networks

**Low train accuracy:** Model too simple or learning rate too small
- Increase model size/capacity
- Increase learning rate, try different optimizers

**Overfit (high train, low validation):** Model too complex or data too small
- Add L2 regularization, dropout
- Use data augmentation
- Use fewer parameters

**NaN/Inf loss:** Numerical instability
- Reduce learning rate
- Check for gradient explosion (use gradient clipping)
- Normalize input data

**Slow convergence:** Learning rate or initialization issue
- Adjust learning rate (often too small)
- Try different optimizer (SGD vs. Adam)
- Use batch normalization

---

## ❓ Interview Q&A

**Q: Why do we need activation functions?**
A: Without them, stacking layers just does linear transformation. Activations introduce non-linearity so the network can learn complex patterns.

**Q: Explain backpropagation in one sentence.**
A: Compute loss, then propagate gradients backward through layers using the chain rule to update weights.

**Q: What's vanishing gradient problem and how to fix it?**
A: Gradients shrink exponentially going backward, preventing learning in early layers. Fix with LSTM/GRU, residual connections, or careful initialization.

**Q: Why use batch normalization?**
A: Normalizes layer outputs, stabilizes training, allows higher learning rates, and reduces internal covariate shift.

**Q: Difference between dropout and L2 regularization?**
A: L2 shrinks all weights smoothly. Dropout randomly zeros neurons, like training ensemble. Both prevent overfitting.

---

## ✅ Checklist

- [ ] Understand perceptron and why it's limited
- [ ] Know neural network architecture (layers, neurons)
- [ ] Explain activation functions and their purposes
- [ ] Understand backpropagation and chain rule
- [ ] Know common optimizers (SGD, Adam, momentum)
- [ ] Explain batch normalization
- [ ] Understand CNN and RNN architectures
- [ ] Know vanishing gradient problem and solutions
- [ ] Debug common training issues
- [ ] Choose appropriate loss functions

---

**Last updated:** 2026-05-22
