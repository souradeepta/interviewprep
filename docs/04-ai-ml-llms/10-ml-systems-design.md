# ML Systems Design — Building End-to-End Pipelines

**Level:** L4-L5
**Time to read:** ~20 min

Designing complete machine learning systems for production.

---

## 🏗️ ML System Components

### Training Pipeline

```
Data Ingestion → Preprocessing → Feature Engineering → Training → Evaluation → Deployment
     ↓              ↓                ↓                    ↓            ↓
  Collect       Clean data      Create features    Update model   Monitor
  from sources  Handle nulls     Scaling, encoding   Tune params   Performance
```

### Inference Pipeline

```
Request → Preprocessing → Model Inference → Postprocessing → Response
           Get features      Predict         Format output
```

### Monitoring & Feedback

```
Production Data → Monitor (data drift, model drift) → Retrain trigger
                     ↓
                  Alert if issues
```

---

## 📊 Complete Example: Recommendation System

### Problem
"Recommend products to users. 100M users, 1M products, 1B+ interactions/day"

### Architecture

```
Data Layer:
- User interaction logs (clicks, purchases)
- Product metadata (category, price, features)
- Time-series data (seasonality)

Feature Engineering:
- User features: Age, location, purchase history
- Item features: Category, price, popularity
- Interaction features: Time since last purchase, frequency

Model Training:
- Matrix factorization / Collaborative filtering
- Neural network (embedding + MLP)
- Hybrid approach

Serving:
- Batch: Pre-compute recommendations offline
- Real-time: Fast inference for on-demand requests

Evaluation:
- Offline: Precision, recall on held-out data
- Online: A/B test with users
```

---

## 🔄 Training Infrastructure

### Data Management

```
Data versioning:
- Track which data was used for training
- Reproducibility: Same data = same results
- Tools: DVC, Pachyderm

Data validation:
- Check schema (columns, types)
- Detect outliers/anomalies
- Monitor data quality

Data pipeline:
- Collect from sources
- Transform (feature engineering)
- Store for training
```

### Experiment Tracking

```
MLflow / Weights & Biases:
- Track hyperparameters
- Log metrics (loss, accuracy)
- Compare experiments
- Version code & models

Example:
exp_1: lr=0.01, batch=32 → accuracy=0.92, f1=0.89
exp_2: lr=0.001, batch=64 → accuracy=0.94, f1=0.91 ✅
exp_3: lr=0.0001, batch=64 → accuracy=0.93, f1=0.90

Choose exp_2 for production
```

### Model Registry

```
Version models:
- v1.0: Initial model, accuracy 92%
- v2.0: Fine-tuned on new data, accuracy 94%
- v3.0: Production ready, passed validation

Rollback capability:
- Issue found in v3.0?
- Roll back to v2.0 instantly
```

---

## ⚡ Inference at Scale

### Batch Inference

```
Problem: Generate predictions for 1M items every day

Solution: Batch process overnight
1. Read 1M items from database
2. Generate features for each (1 GPU, 1000 items/min)
3. Inference: 1000 items/sec
4. Write predictions to cache
5. Serve from cache

Cost: 1 GPU × 8 hours = $4
Latency: Pre-computed, instant serving
```

### Real-time Inference

```
Problem: User opens app, needs recommendation NOW

Solution: 
1. Load pre-computed embeddings in memory
2. User logs in
3. Get user embedding from database (low latency)
4. Compute similarity: user embedding × item embeddings
5. Return top K in <100ms

Cost: GPU + fast memory
Latency: <100ms
```

### Hybrid Approach

```
Pre-compute popular items (80% of requests):
- Fast batch computation
- Serve from cache

Compute personalized for rest (20%):
- Real-time inference with user context
- More expensive but used less
```

---

## 🚨 Model Monitoring

### Data Drift

```
Detect when input distribution changes:

Before:
Average user age: 25-45
Product price range: $10-100

After:
Average user age: 18-30
Product price range: $100-500

Model was trained on old distribution!
Predictions likely wrong.
Solution: Retrain on new distribution
```

### Model Drift

```
Detect when model performance degrades:

Week 1: Precision=0.95, Recall=0.92
Week 2: Precision=0.92, Recall=0.89
Week 3: Precision=0.88, Recall=0.85 ← Alert!

Something changed (data drift, model bug, etc.)
Investigate and retrain.
```

### Prediction Drift

```
Monitor what model predicts:

Before: 60% recommend category A, 40% category B
After: 80% recommend category A, 20% category B

Distribution changed! Might indicate:
- New seasonal trends (expected)
- Model collapse (bug)
- Training data bias (investigate)
```

---

## 🔄 Retraining Strategy

### When to Retrain?

```
Scheduled:
- Daily: High-frequency data (stock prices)
- Weekly: Moderate frequency (recommendations)
- Monthly: Stable domains (credit scoring)

Triggered:
- Data drift detected → Immediate
- Model drift > threshold → Immediate
- Performance metric < threshold → Next cycle

Example:
- Monitor accuracy every hour
- If drops below 90% for 2 hours → Alert
- If still low after 6 hours → Trigger retrain
```

### Retraining Process

```
1. Collect new data since last training
2. Run data validation (schema, quality checks)
3. Train new model on old + new data
4. Evaluate on hold-out test set
5. Compare with production model
6. If better: Shadow deploy (parallel)
7. If still good after 1 week: Promote to production
8. Keep old model as fallback
```

---

## 💻 Technology Stack

### Data
- Data warehouse: BigQuery, Snowflake
- Data lakes: S3, HDFS
- Feature store: Feast, Tecton

### Training
- Frameworks: PyTorch, TensorFlow
- Experiment tracking: MLflow, W&B
- Orchestration: Airflow, Kubeflow

### Serving
- Batch: Spark, Airflow
- Real-time: FastAPI, TensorFlow Serving, Ray Serve
- Model serving: vLLM, TensorRT

### Monitoring
- Metrics: Prometheus, Grafana
- Logging: ELK stack, CloudWatch
- Alerting: PagerDuty

---

## ❓ Interview Q&A

**Q: Design an ML system for X.**
A: Cover: data pipeline → feature engineering → model → inference → monitoring → retraining

**Q: How would you detect model degradation?**
A: Monitor performance metrics (accuracy, precision, recall), data drift (input distribution), and model drift (prediction distribution). Alert if any deviates significantly.

**Q: When would you retrain vs. improve features?**
A: Start with better features (quick). Retrain when data distribution changes or model drifts. Both usually needed.

**Q: What's the cost of serving an ML model at scale?**
A: Infrastructure (GPU/CPU), storage (data + model), network (requests). Example: 1M users → $10-100k/month depending on frequency and model size.

---

## ✅ Checklist

- [ ] Understand end-to-end ML pipeline
- [ ] Know data management and versioning
- [ ] Understand experiment tracking and model registry
- [ ] Know batch vs. real-time inference trade-offs
- [ ] Understand monitoring (data drift, model drift)
- [ ] Know retraining strategies
- [ ] Understand technology choices and trade-offs
- [ ] Can design ML system for given problem

---

**Last updated:** 2026-05-22
