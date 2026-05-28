# ML Fundamentals — Core Concepts & Algorithms

**Level:** L4
**Time to read:** ~20 min

Essential machine learning concepts for interview preparation.

---

## 🎯 Core Concepts

### Supervised vs. Unsupervised Learning

**Supervised Learning:** Learn from labeled data (input → output pairs)
- **Classification:** Predict discrete categories (email: spam or not)
- **Regression:** Predict continuous values (house price)
- Examples: Linear regression, logistic regression, decision trees, SVM, neural networks

**Unsupervised Learning:** Find patterns in unlabeled data
- **Clustering:** Group similar data (customer segmentation)
- **Dimensionality Reduction:** Compress data (PCA, embeddings)
- Examples: K-means, hierarchical clustering, DBSCAN, autoencoders

### Semi-supervised & Self-supervised Learning

**Semi-supervised:** Mix of labeled and unlabeled data
- Use unlabeled data to improve learning
- Example: Label propagation, pseudo-labeling

**Self-supervised:** Create labels from data itself
- Example: Predicting next word (like LLM pretraining)

---

## 📊 Key Metrics

### Classification Metrics

| Metric | Formula | When to Use |
|--------|---------|------------|
| **Accuracy** | (TP+TN)/(TP+TN+FP+FN) | Balanced classes |
| **Precision** | TP/(TP+FP) | Focus on false positives |
| **Recall** | TP/(TP+FN) | Focus on false negatives |
| **F1-Score** | 2×(Precision×Recall)/(Precision+Recall) | Balance precision & recall |
| **AUC-ROC** | Area under ROC curve | Binary classification, class imbalance |

**Example:**
- Spam detection: High recall (catch all spam) might matter more
- Loan approval: High precision (few false positives) might matter more

### Regression Metrics

| Metric | Formula | Characteristics |
|--------|---------|-----------------|
| **MAE** | Σ\|y_true - y_pred\|/n | Robust to outliers |
| **MSE** | Σ(y_true - y_pred)²/n | Penalizes large errors |
| **RMSE** | √MSE | Interpretable in original units |
| **R²** | 1 - (SS_res/SS_tot) | 0-1 score, 1 is perfect |

---

## 🔄 Training Fundamentals

### The Training Loop

```python
# Pseudo-code
model = initialize_model()
for epoch in range(num_epochs):
    for batch in training_data:
        # Forward pass
        predictions = model.forward(batch.X)
        # Compute loss
        loss = compute_loss(predictions, batch.y)
        # Backward pass
        gradients = compute_gradients(loss)
        # Update weights
        model.update_weights(gradients, learning_rate)
    # Evaluate on validation set
    val_loss = evaluate(model, validation_data)
```

### Overfitting vs. Underfitting

| Problem | Cause | Solution |
|---------|-------|----------|
| **Overfitting** | Model too complex, learns noise | Regularization, more data, early stopping |
| **Underfitting** | Model too simple, can't learn patterns | More complex model, more features |

**How to detect:**
- Overfitting: Train loss low, validation loss high
- Underfitting: Both train and validation loss high

---

## 🎲 Regularization Techniques

### L1 & L2 Regularization

**L2 Regularization (Ridge):**
```
Loss = MSE + λ × Σ(weights²)
Effect: Shrink weights, preferred when many weak features matter
```

**L1 Regularization (Lasso):**
```
Loss = MSE + λ × Σ(|weights|)
Effect: Force some weights to zero (feature selection)
```

### Dropout

Random neurons "dropped" during training:
- Prevents co-adaptation
- Acts like training ensemble
- Typically 10-50% dropout rate

### Early Stopping

Monitor validation loss, stop when it increases:
- Prevents overfitting
- Saves training time
- Often combined with L2

---

## 🔀 Data Handling

### Train/Validation/Test Split

```
80% Train: Learn parameters
10% Validation: Tune hyperparameters
10% Test: Final evaluation (touch only once)
```

**For small datasets:** K-fold cross-validation (5 or 10 folds)

### Imbalanced Datasets

**Problem:** Few samples of minority class (e.g., 99% negative, 1% positive)

**Solutions:**
1. **Resampling:** Oversample minority or undersample majority
2. **Class weights:** Give higher loss weight to minority
3. **Sampling:** Stratified K-fold to maintain ratios
4. **Metrics:** Use F1, precision-recall, AUC instead of accuracy

### Data Preprocessing

**Scaling/Normalization:**
- Standardization: (x - mean) / std
- Min-max normalization: (x - min) / (max - min)
- Important for algorithms sensitive to magnitude (KNN, SVM, neural networks)

**Handling Missing Data:**
- Remove rows (if <5% missing)
- Imputation (mean, median, forward-fill for time series)
- Use algorithms that handle missing data (tree-based)

---

## 🎯 Common Algorithms

### Linear Models

**Linear Regression:**
- Predicts continuous value
- Closed-form solution: weights = (X^T X)^(-1) X^T y
- O(n³) complexity, fast for small data

**Logistic Regression:**
- Classification despite the name
- Outputs probability (sigmoid)
- Linear decision boundary

### Tree-Based Models

**Decision Trees:**
- Interpretable, handles non-linear relationships
- Information gain/Gini impurity for splits
- Prone to overfitting

**Random Forest:**
- Ensemble of trees
- Reduces overfitting
- Feature importance from tree splits

**Gradient Boosting (XGBoost, LightGBM):**
- Sequential trees, each corrects previous
- Often wins Kaggle competitions
- More complex, slower training

### Support Vector Machines (SVM)

- Find decision boundary maximizing margin
- Works in high dimensions
- Kernel trick for non-linear separation
- Slow for large datasets (O(n²) to O(n³))

### K-Means Clustering

- Partition data into K clusters
- Iterative: assign points, update centers
- Sensitive to initialization, K choice
- O(nkd) per iteration (n=points, k=clusters, d=dimensions)

---

## 🧠 Optimization Basics

### Gradient Descent Variants

**Batch GD:** Update on all data, stable but slow
**Stochastic GD:** Update on single sample, noisy but fast  
**Mini-batch GD:** Update on batch, balance between both

### Adaptive Optimizers

**SGD with Momentum:**
- Accelerates convergence in consistent direction
- Typical momentum: 0.9

**Adam (Adaptive Moment Estimation):**
- Combines momentum and RMSprop
- Default for deep learning
- Learning rates: 0.001-0.01

### Learning Rate Scheduling

- Start high, decrease over time
- Step decay: Divide by 10 every N epochs
- Exponential decay, cosine annealing
- Prevents oscillation near minimum

---

## 🔍 Model Evaluation

### Bias-Variance Trade-off

```
Total Error = Bias² + Variance + Irreducible Error

High Bias (Underfitting):
- Model too simple, misses patterns
- Low train and validation accuracy

High Variance (Overfitting):
- Model too complex, fits noise
- High train accuracy, low validation
```

### Cross-Validation

```
k-fold: Split data into k folds
- Train on k-1 folds, validate on 1
- Repeat k times, average scores
- Better estimate of true performance
```

### Hyperparameter Tuning

**Grid Search:** Try all combinations (exhaustive)
**Random Search:** Random combinations (faster, often comparable)
**Bayesian Optimization:** Use previous results to guide search (efficient)

---

## ❓ Interview Q&A

**Q: How do you choose between classification and regression?**
A: Use regression for continuous output (price), classification for discrete categories (spam/not spam).

**Q: Explain the bias-variance trade-off.**
A: High bias = underfitting (too simple), high variance = overfitting (too complex). Sweet spot balances both.

**Q: When would you use L1 vs. L2 regularization?**
A: L1 for feature selection (forces irrelevant weights to zero), L2 when all features potentially matter (shrinks weights).

**Q: How do you handle imbalanced datasets?**
A: Class weights, resampling, use F1/AUC metrics instead of accuracy.

**Q: What's the difference between train and validation loss?**
A: Train loss measures fitting, validation loss measures generalization. Large gap = overfitting.

---

## ✅ Checklist

- [ ] Understand supervised vs. unsupervised learning
- [ ] Know common classification and regression metrics
- [ ] Explain overfitting and regularization techniques
- [ ] Understand optimization (SGD, Adam, learning rates)
- [ ] Know key algorithms (linear models, trees, SVM, K-means)
- [ ] Explain bias-variance trade-off
- [ ] Handle imbalanced data and preprocessing
- [ ] Use cross-validation and hyperparameter tuning

---

**Last updated:** 2026-05-22
