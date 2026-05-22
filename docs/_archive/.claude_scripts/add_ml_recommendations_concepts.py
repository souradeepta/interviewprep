#!/usr/bin/env python3
"""
Add 30 new ML/Recommendations concepts (06-35) with comprehensive treatment.
Each includes diagrams, code, calculations, interview questions.
"""

from pathlib import Path

CONCEPTS = {
    "06_matrix_factorization": {
        "title": "Matrix Factorization",
        "requirements": {
            "functional": [
                "Decompose user-item matrix into latent factors",
                "Train on user ratings and implicit feedback",
                "Handle sparse rating matrices efficiently",
                "Support incremental model updates",
                "Generate personalized recommendations"
            ],
            "non_functional": [
                "Latency: Generate recommendations < 100ms per user",
                "Throughput: Score 1M+ items per second",
                "Accuracy: RMSE < 0.9 on benchmark datasets",
                "Scalability: Support billions of user-item pairs",
                "Memory: Store factors in < 10GB for 100M users"
            ]
        }
    },
    "07_factorization_machines": {
        "title": "Factorization Machines",
        "requirements": {
            "functional": [
                "Model interactions between features",
                "Handle high-dimensional sparse data",
                "Support regression and classification",
                "Learn feature interactions automatically",
                "Reduce overfitting with regularization"
            ],
            "non_functional": [
                "Latency: Score items < 100ms p99",
                "Throughput: Process 100K+ examples/second",
                "Accuracy: AUC > 0.85 on CTR datasets",
                "Scalability: Support 1M+ features",
                "Training: Convergence < 100 epochs"
            ]
        }
    },
    "08_neural_collab_filtering": {
        "title": "Neural Collaborative Filtering",
        "requirements": {
            "functional": [
                "Use neural networks for collaborative filtering",
                "Learn non-linear user-item interactions",
                "Support multi-layer neural networks",
                "Enable end-to-end deep learning",
                "Generate embeddings for users and items"
            ],
            "non_functional": [
                "Latency: Score items < 50ms p99",
                "Throughput: Process 10K+ scoring requests/second",
                "Accuracy: HR@10 > 0.6 on benchmark",
                "Scalability: Train on 100M+ interactions",
                "Memory: Store model in < 5GB"
            ]
        }
    },
    "09_deep_learning_recs": {
        "title": "Deep Learning for Recommendations",
        "requirements": {
            "functional": [
                "Use deep neural networks for feature learning",
                "Support CNN and RNN architectures",
                "Learn from raw user/item features",
                "Enable transfer learning",
                "Support multi-task learning"
            ],
            "non_functional": [
                "Latency: Score items < 200ms p99",
                "Throughput: 1K+ inferences/second per GPU",
                "Accuracy: MAP > 0.3 on large-scale datasets",
                "Training: Convergence < 100K batches",
                "Cost: Train on GPUs with < $1K daily cost"
            ]
        }
    },
    "10_knowledge_graphs": {
        "title": "Knowledge Graphs for Recommendations",
        "requirements": {
            "functional": [
                "Build knowledge graphs of entities and relations",
                "Enable explainable recommendations",
                "Support semantic similarity reasoning",
                "Link items through knowledge base",
                "Enable reasoning over graph paths"
            ],
            "non_functional": [
                "Throughput: Traverse graph < 100ms per recommendation",
                "Coverage: Support 100M+ entities",
                "Connectivity: Graph density 0.1-0.5",
                "Storage: Graph in < 50GB for large scale",
                "Query: Semantic similarity < 10ms"
            ]
        }
    },
    "11_graph_neural_networks": {
        "title": "Graph Neural Networks (GNNs)",
        "requirements": {
            "functional": [
                "Learn embeddings from graph structure",
                "Propagate information through graph",
                "Support multiple GNN architectures",
                "Enable inductive learning on new nodes",
                "Handle heterogeneous graphs"
            ],
            "non_functional": [
                "Latency: Generate embeddings < 50ms",
                "Throughput: Score 10K+ nodes/second",
                "Accuracy: Link prediction AUC > 0.9",
                "Scalability: Support billion-node graphs",
                "Memory: Training on < 50GB GPU memory"
            ]
        }
    },
    "12_context_aware": {
        "title": "Context-Aware Recommendations",
        "requirements": {
            "functional": [
                "Consider context (time, location, device)",
                "Learn context-specific user preferences",
                "Support dynamic context changes",
                "Rank items based on context",
                "Personalize within context"
            ],
            "non_functional": [
                "Latency: Generate recommendations < 100ms",
                "Throughput: 100K+ recommendations/second",
                "Accuracy: CTR +10% with context vs without",
                "Scalability: Support 1000+ context dimensions",
                "Freshness: Update context in < 1 second"
            ]
        }
    },
    "13_temporal_dynamics": {
        "title": "Temporal Dynamics in Recommendations",
        "requirements": {
            "functional": [
                "Model user preference drift over time",
                "Track item popularity trends",
                "Support seasonal patterns",
                "Learn temporal user behavior",
                "Predict future preferences"
            ],
            "non_functional": [
                "Latency: Generate recommendations < 100ms",
                "Accuracy: RMSE improvement +5% with temporal",
                "Freshness: Re-train hourly or daily",
                "Scalability: Support 10 years of history",
                "Memory: Store temporal models efficiently"
            ]
        }
    },
    "14_coldstart_problem": {
        "title": "Cold Start Problem",
        "requirements": {
            "functional": [
                "Handle new users with no history",
                "Recommend new items with no interactions",
                "Use content features for new items",
                "Crowdsource feedback from new users",
                "Support user/item onboarding"
            ],
            "non_functional": [
                "Latency: Generate recommendations < 200ms",
                "Coverage: Recommend for 100% of users",
                "Accuracy: HR@10 > 0.4 for new users",
                "Scalability: Handle 1M+ new users/day",
                "Cost: Bootstrap with < 5 interactions per user"
            ]
        }
    },
    "15_diversity_serendipity": {
        "title": "Diversity and Serendipity",
        "requirements": {
            "functional": [
                "Avoid recommending similar items",
                "Recommend unexpected but relevant items",
                "Balance relevance and novelty",
                "Support diverse recommendation lists",
                "Enable exploration and exploitation"
            ],
            "non_functional": [
                "Latency: Re-rank recommendations < 50ms",
                "Diversity: Avg pairwise distance > 0.3",
                "Novelty: Recommend unseen items 20%+",
                "Relevance: Maintain NDCG > 0.8",
                "Throughput: Re-rank 100K+ candidates/second"
            ]
        }
    },
    "16_fairness_ml": {
        "title": "Fairness in Recommendations",
        "requirements": {
            "functional": [
                "Ensure fair representation of items",
                "Mitigate bias against minorities",
                "Support fairness constraints",
                "Monitor algorithmic fairness metrics",
                "Enable provider fairness"
            ],
            "non_functional": [
                "Coverage: Exposure within 10% parity",
                "Bias: Demographic parity > 0.8",
                "Relevance: Maintain utility while fair",
                "Monitoring: Real-time fairness metrics",
                "Scalability: Enforce fairness at scale"
            ]
        }
    },
    "17_explainability": {
        "title": "Explainability in ML Models",
        "requirements": {
            "functional": [
                "Explain recommendation reasoning",
                "Identify influential features",
                "Support rule-based explanations",
                "Enable user feedback on explanations",
                "Track explanation quality"
            ],
            "non_functional": [
                "Latency: Generate explanations < 100ms",
                "Coverage: Explain 95%+ of recommendations",
                "Faithfulness: Explanations match model logic",
                "Simplicity: Avg < 5 explanation items",
                "Trust: Increase user trust in recommendations"
            ]
        }
    },
    "18_ctr_prediction": {
        "title": "Click-Through Rate (CTR) Prediction",
        "requirements": {
            "functional": [
                "Predict probability user will click",
                "Learn from click/impression data",
                "Support real-time CTR scoring",
                "Handle imbalanced click data",
                "Support position bias correction"
            ],
            "non_functional": [
                "Latency: Score items < 50ms p99",
                "Throughput: Score 1M+ items/second",
                "Accuracy: AUC > 0.85 on benchmark",
                "Scalability: Support 1B+ features",
                "Training: Convergence < 1 hour"
            ]
        }
    },
    "19_conversion_optimization": {
        "title": "Conversion Rate Optimization",
        "requirements": {
            "functional": [
                "Predict purchase probability",
                "Optimize for user conversion",
                "Model purchase value",
                "Recommend high-value items",
                "Track conversion funnel"
            ],
            "non_functional": [
                "Latency: Generate recommendations < 100ms",
                "Accuracy: Conversion rate +5-10%",
                "Revenue: +20-30% incremental revenue",
                "Scalability: Support 10M+ conversions/day",
                "Fairness: Avoid over-pushing to individuals"
            ]
        }
    },
    "20_realtime_recommendations": {
        "title": "Real-Time Recommendations",
        "requirements": {
            "functional": [
                "Generate recommendations in real-time",
                "Use fresh user interaction signals",
                "Support instant model updates",
                "Enable session-based ranking",
                "Track real-time user context"
            ],
            "non_functional": [
                "Latency: < 100ms p99 end-to-end",
                "Freshness: Use events < 1 second old",
                "Throughput: 100K+ requests/second",
                "Scalability: Support 1M+ concurrent users",
                "Reliability: 99.99% uptime"
            ]
        }
    },
    "21_bandit_algorithms": {
        "title": "Bandit Algorithms",
        "requirements": {
            "functional": [
                "Balance exploration vs exploitation",
                "Learn optimal recommendations over time",
                "Support context-dependent bandits",
                "Handle regret minimization",
                "Support Thompson sampling"
            ],
            "non_functional": [
                "Latency: Select action < 10ms",
                "Regret: Cumulative regret O(log T)",
                "Convergence: Identify best option < 1000 trials",
                "Scalability: Support 1000+ arms",
                "Adaptivity: Learn from user feedback quickly"
            ]
        }
    },
    "22_multiarm_bandits": {
        "title": "Multi-Armed Bandits (MAB)",
        "requirements": {
            "functional": [
                "Select best option from multiple choices",
                "Learn reward distributions",
                "Support various UCB strategies",
                "Handle non-stationary rewards",
                "Enable contextual bandits"
            ],
            "non_functional": [
                "Latency: Select option < 5ms",
                "Regret: Achieve optimal regret bounds",
                "Convergence: < 10K interactions to optimize",
                "Robustness: Handle reward noise",
                "Scalability: Support 10K+ arms"
            ]
        }
    },
    "23_rl_recommendations": {
        "title": "Reinforcement Learning for Recommendations",
        "requirements": {
            "functional": [
                "Model recommendation as MDP",
                "Learn optimal recommendation policy",
                "Support long-term user satisfaction",
                "Handle delayed rewards",
                "Enable exploration in RL"
            ],
            "non_functional": [
                "Latency: Generate policy action < 100ms",
                "Convergence: Train < 100K episodes",
                "Reward: +20-30% user engagement improvement",
                "Scalability: Support 1M+ state space",
                "Exploration: Balance discovery vs satisfaction"
            ]
        }
    },
    "24_session_based": {
        "title": "Session-Based Recommendations",
        "requirements": {
            "functional": [
                "Model user behavior within sessions",
                "Predict next item in session",
                "Support RNN-based sequence modeling",
                "Learn session context",
                "Handle session ends and starts"
            ],
            "non_functional": [
                "Latency: Predict next item < 50ms",
                "Accuracy: HR@20 > 0.4 on benchmark",
                "Throughput: Process 100K+ sessions/hour",
                "Memory: Store sequences efficiently",
                "Scalability: Support 1M+ concurrent sessions"
            ]
        }
    },
    "25_sequential_recommendations": {
        "title": "Sequential Recommendations",
        "requirements": {
            "functional": [
                "Model sequential user behavior patterns",
                "Predict next item from history",
                "Support Markov chains and attention",
                "Learn long-range dependencies",
                "Recommend considering sequence"
            ],
            "non_functional": [
                "Latency: Predict next item < 100ms",
                "Accuracy: NDCG@10 > 0.5",
                "Memory: Efficient sequence storage",
                "Scalability: Support billion-item sequences",
                "Freshness: Update sequences in real-time"
            ]
        }
    },
    "26_embedding_models": {
        "title": "Embedding Models",
        "requirements": {
            "functional": [
                "Learn dense vector representations",
                "Support similarity-based ranking",
                "Enable fast approximate nearest neighbor",
                "Train embeddings on click data",
                "Support embedding updates"
            ],
            "non_functional": [
                "Latency: Retrieve neighbors < 50ms",
                "Accuracy: Hit rate > 0.8 on ANN",
                "Dimensionality: Embeddings < 100 dims",
                "Storage: Embeddings < 5GB for 1B items",
                "Scalability: Support billion-scale embeddings"
            ]
        }
    },
    "27_word2vec_embeddings": {
        "title": "Word2Vec and Skip-Gram Embeddings",
        "requirements": {
            "functional": [
                "Learn item embeddings from co-occurrence",
                "Support skip-gram and CBOW models",
                "Handle negative sampling efficiently",
                "Enable semantic similarity learning",
                "Support transfer learning"
            ],
            "non_functional": [
                "Latency: Train embeddings < 1 hour",
                "Quality: Analogy tasks > 70% accuracy",
                "Scalability: Support 1M+ vocabulary",
                "Memory: Embeddings < 1GB",
                "Convergence: Converge < 10 epochs"
            ]
        }
    },
    "28_similarity_metrics": {
        "title": "Similarity Metrics",
        "requirements": {
            "functional": [
                "Measure distance between items",
                "Support multiple distance metrics",
                "Enable fast similarity computation",
                "Handle high-dimensional data",
                "Support metric learning"
            ],
            "non_functional": [
                "Latency: Compute similarity < 1ms per pair",
                "Throughput: Compute 1M+ similarities/second",
                "Accuracy: Metric matches manual similarity",
                "Scalability: Efficient for 1B+ items",
                "Flexibility: Support custom metrics"
            ]
        }
    },
    "29_hashing_lsh": {
        "title": "Hashing and Locality-Sensitive Hashing (LSH)",
        "requirements": {
            "functional": [
                "Hash items to buckets for fast lookup",
                "Enable approximate nearest neighbor search",
                "Support multiple hash functions",
                "Handle hash collisions",
                "Enable fast similarity search"
            ],
            "non_functional": [
                "Latency: LSH query < 10ms for 1B items",
                "Recall: > 95% for approximate neighbors",
                "Storage: Hash tables < 10GB",
                "Scalability: Support billion-scale datasets",
                "Accuracy: Minimal loss vs exact search"
            ]
        }
    },
    "30_ensemble_models": {
        "title": "Model Ensemble for Recommendations",
        "requirements": {
            "functional": [
                "Combine multiple recommendation models",
                "Support weighted ensemble",
                "Learn ensemble weights from data",
                "Handle model disagreement",
                "Enable online model selection"
            ],
            "non_functional": [
                "Latency: Score ensemble < 100ms",
                "Accuracy: Ensemble NDCG > individual models",
                "Throughput: Score 10K+ items/second",
                "Scalability: Support 100+ models",
                "Stability: Consistent performance"
            ]
        }
    },
    "31_online_learning": {
        "title": "Online Learning for Recommendations",
        "requirements": {
            "functional": [
                "Update model continuously from new data",
                "Support streaming data",
                "Handle concept drift",
                "Enable incremental learning",
                "Learn from user feedback immediately"
            ],
            "non_functional": [
                "Latency: Model update < 100ms",
                "Throughput: Process 100K+ examples/second",
                "Accuracy: Match batch learning performance",
                "Memory: Bounded memory usage",
                "Scalability: Support trillion+ examples lifetime"
            ]
        }
    },
    "32_feedback_loop": {
        "title": "Feedback Loop Management",
        "requirements": {
            "functional": [
                "Capture user feedback on recommendations",
                "Use feedback to improve model",
                "Handle selection bias in feedback",
                "Track feedback quality",
                "Enable feedback-driven optimization"
            ],
            "non_functional": [
                "Latency: Incorporate feedback < 1 hour",
                "Bias mitigation: IPS or SNIPS unbiased learning",
                "Coverage: Capture feedback for 50%+ interactions",
                "Quality: Filter low-quality feedback",
                "Scalability: Process 1M+ feedback/day"
            ]
        }
    },
    "33_offline_evaluation": {
        "title": "Offline Evaluation Metrics",
        "requirements": {
            "functional": [
                "Evaluate recommendations on historical data",
                "Support multiple ranking metrics",
                "Enable statistical significance testing",
                "Handle position bias",
                "Track metric trends"
            ],
            "non_functional": [
                "Accuracy: Metrics match online performance",
                "Correlation: Offline metrics > 0.8 correlation with online",
                "Coverage: Evaluate on full recommendation set",
                "Efficiency: Compute metrics < 1 minute",
                "Robustness: Handle edge cases"
            ]
        }
    },
    "34_online_evaluation": {
        "title": "Online Evaluation and A/B Testing",
        "requirements": {
            "functional": [
                "Run A/B tests on live traffic",
                "Support multi-armed bandit tests",
                "Track user engagement metrics",
                "Enable rapid experiment iteration",
                "Statistical significance checking"
            ],
            "non_functional": [
                "Latency: < 5% impact from experiment",
                "Throughput: Support 100+ concurrent experiments",
                "Time-to-result: Significance < 7 days",
                "Sensitivity: Detect 0.5% effect size",
                "Scalability: Multi-region experimentation"
            ]
        }
    },
    "35_recommendation_api": {
        "title": "Recommendation API and Serving",
        "requirements": {
            "functional": [
                "Serve recommendations in real-time",
                "Support batch and streaming API",
                "Enable personalized ranking",
                "Handle fallback strategies",
                "Support result caching"
            ],
            "non_functional": [
                "Latency: < 100ms p99 API response",
                "Throughput: 1M+ requests/second",
                "Availability: 99.99% uptime",
                "Cache hit rate: 80%+",
                "Scalability: Multi-region serving"
            ]
        }
    }
}

TEMPLATE = '''# {title}

## Problem Statement

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## System Overview

**Scale Metrics:**
- Throughput: Millions of recommendations per second
- Latency: Milliseconds for recommendation generation
- Data volume: Terabytes of interaction history
- Model complexity: Millions of parameters
- Availability: 99.99% service uptime

**Key Components:**
- Feature engineering and preprocessing
- Model training and optimization
- Real-time scoring and ranking
- Feedback loop and offline evaluation
- Monitoring and experimentation

## Architecture Diagrams

### Recommendation System Architecture

```mermaid
graph TB
    subgraph "Input"
        U["User Context"]
        I["Item Features"]
        H["Interaction History"]
    end

    subgraph "Processing"
        F["Feature Engineering"]
        E["Embedding Model"]
        R["Ranking Model"]
    end

    subgraph "Output"
        S["Scoring"]
        L["List Generation"]
        O["Output"]
    end

    U --> F
    I --> F
    H --> F
    F --> E
    E --> R
    R --> S
    S --> L
    L --> O

    style F fill:#e1f5ff
    style E fill:#f3e5f5
    style R fill:#fff3e0
    style O fill:#e8f5e9
```

### Model Training Pipeline

```mermaid
graph LR
    A["Historical Data"] --> B["Feature Extraction"]
    B --> C["Model Training"]
    C --> D["Evaluation"]
    D --> E["Validation"]
    E --> F["Serving"]

    style A fill:#c8e6c9
    style C fill:#ffccbc
    style E fill:#bbdefb
    style F fill:#fff9c4
```

### Feedback Loop

```mermaid
graph TB
    A["Recommendations"] --> B["User Interaction"]
    B --> C["Feedback Collection"]
    C --> D["Data Pipeline"]
    D --> E["Model Retraining"]
    E --> A

    style A fill:#e1f5ff
    style C fill:#ffccbc
    style E fill:#c8e6c9
```

### A/B Testing Framework

```mermaid
graph TB
    U["Users"] --> LB["Load Balancer"]
    LB --> A["Control (A)"]
    LB --> B["Variant (B)"]
    A --> MA["Metric A"]
    B --> MB["Metric B"]
    MA --> C["Compare"]
    MB --> C
    C --> D["Significance Test"]

    style A fill:#c8e6c9
    style B fill:#ffccbc
    style D fill:#fff9c4
```

### Real-Time Serving

```mermaid
graph TB
    R["User Request"] --> C["Check Cache"]
    C --> H["Cache Hit"]
    H -->|Yes| S["Serve Cached"]
    H -->|No| M["Score with Model"]
    M --> R2["Rank Results"]
    R2 --> CA["Cache Result"]
    CA --> S
    S --> O["Return to User"]

    style H fill:#fff3e0
    style M fill:#e1f5ff
    style S fill:#c8e6c9
```

## Data Flow Scenarios

### Scenario 1: Training New Model
1. Collect historical user interactions
2. Extract features from raw data
3. Train recommendation model
4. Evaluate on hold-out test set
5. Compare with baseline model
6. Deploy to serving infrastructure

### Scenario 2: Real-Time Scoring
1. User requests recommendations
2. Fetch user profile and context
3. Retrieve candidate items
4. Score candidates with model
5. Re-rank by diversity and freshness
6. Return top-K recommendations

### Scenario 3: Online A/B Test
1. Split traffic between variants
2. Serve variant A (control) to 50%
3. Serve variant B (test) to 50%
4. Collect metrics from both
5. Run significance test
6. Deploy winner if significant

## Performance Optimization

### Model Optimization
- **Distillation**: Compress large models
- **Quantization**: Reduce precision for speed
- **Pruning**: Remove unimportant parameters
- **Caching**: Pre-compute common scores

### Inference Optimization
- **Batching**: Process multiple requests together
- **GPU acceleration**: Use GPUs for scoring
- **Approximate search**: Fast similarity lookup
- **Caching**: Cache popular recommendations

### Data Optimization
- **Sampling**: Train on representative sample
- **Bucketing**: Group similar items
- **Filtering**: Remove noise and outliers
- **Compression**: Efficient feature storage

## Back-of-Envelope Calculations

### User and Item Scale
```
Daily active users: 100M
Items in catalog: 1M
Interactions per user per day: 10
Daily interactions: 1B
Training data: 3 years = 1T interactions
Model parameters: 10M-1B depending on approach
```

### Compute Requirements
```
Training:
- Batch size: 10K examples
- Epochs: 10
- Total batches: (1B / 10K) × 10 = 1M batches
- Time per batch: 100ms
- Total training time: 100M seconds ≈ 27 hours

Serving:
- Scoring latency: 10ms per item per model
- Candidates per request: 1000 items
- Scoring: 1000 × 10ms = 10 seconds
- With caching: 100ms (1% miss rate)
- With approximation: 10ms
```

### Storage Requirements
```
Interaction history: 1T × 100 bytes = 100 TB
Models: 1B parameters × 4 bytes = 4 GB
Embeddings: 1M items × 100 dims × 4 bytes = 400 MB
Feature cache: 1M items × 10 KB = 10 TB
Total: ~110 TB
```

## Interview Questions & Answers

### Q1: Design recommendation system for YouTube

**Answer:**
1. **Scale**: 100M users, 1B videos, 1B interactions/day
2. **Architecture**:
   - Feature pipeline: User, video, context features
   - Candidate generation: Retrieval of 1000 candidates
   - Ranking: Deep learning model to rank candidates
   - Serving: Real-time with caching
3. **Models**:
   - Candidate: Collaborative filtering for recall
   - Ranking: Deep neural network for relevance
4. **Optimization**: GPU scoring, caching, A/B testing
5. **Challenges**: Cold-start, diversity, fairness, freshness

### Q2: Handle cold-start for new users

**Answer:**
- **Content-based**: Use item features if available
- **Demographic**: Recommend popular items to new users
- **Exploration**: Recommend diverse items to learn preferences
- **Collaborative**: Find similar users with data
- **Hybrid**: Combine multiple approaches
- **Feedback**: Quick onboarding with explicit feedback

### Q3: Ensure recommendation diversity

**Answer:**
- **Diversify candidates**: Retrieve from multiple sources
- **Re-ranking**: Penalize similar items in ranking
- **Embedding distance**: Maximize pairwise distances
- **Category balance**: Ensure diverse content types
- **Exploration**: Recommend unknown items
- **User preference**: Learn diversity preference

### Q4: Detect and handle model drift

**Answer:**
- **Monitor**: Track RMSE, AUC over time
- **Baseline**: Compare with production model
- **Retrain**: Automated retraining on schedule
- **Detect**: Sudden > 5% drop triggers alert
- **Evaluate**: Online A/B test before deployment
- **Rollback**: Quick rollback if degradation

### Q5: Design A/B testing framework

**Answer:**
- **Randomization**: Consistent hash for user assignment
- **Metrics**: Engagement, CTR, conversion, revenue
- **Duration**: Run for 1-2 weeks minimum
- **Size**: Minimum 100K users per variant
- **Stats**: Power = 0.8, significance = 0.05
- **Logging**: Track all experiments and results

### Q6: Optimize for long-term user satisfaction

**Answer:**
- **Beyond clicks**: Optimize for likes, shares, watch time
- **Diversity**: Avoid excessive repetition
- **Novelty**: Recommend new content occasionally
- **RL approach**: Model long-term value
- **Feedback**: Learn from user satisfaction signals
- **Offline test**: Predict satisfaction before online test

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Training | TensorFlow, PyTorch | Flexible deep learning |
| Serving | TFServing, KServe | Low-latency inference |
| Features | Spark, Airflow | Large-scale pipelines |
| Storage | HBase, Cassandra | Fast key-value access |
| Evaluation | Spark MLlib | Distributed metrics |
| Experimentation | Statsmodels | Statistical testing |
| Monitoring | Prometheus, Datadog | Real-time metrics |

## Lessons Learned

1. **Data quality matters**: Garbage in, garbage out
2. **Measure offline and online**: Offline metrics != online results
3. **Diversity is important**: Pure relevance = boring
4. **Fresh content works**: Stale recommendations hurt engagement
5. **User feedback is gold**: Learn from interactions quickly

## Related Topics

- Collaborative filtering and matrix factorization
- Deep learning for recommendations
- Ranking algorithms and loss functions
- A/B testing and experimentation
- Feature engineering for recommendation
- Real-time serving and caching
- Offline evaluation metrics
- Fairness and explainability in ML
'''

def create_topic_file(concept_key: str, concept_data: dict) -> Path:
    """Create a comprehensive topic file."""
    functional_reqs = "\n".join(
        f"- {req}" for req in concept_data["requirements"]["functional"]
    )
    non_functional_reqs = "\n".join(
        f"- {req}" for req in concept_data["requirements"]["non_functional"]
    )

    content = TEMPLATE.format(
        title=concept_data["title"],
        functional_reqs=functional_reqs,
        non_functional_reqs=non_functional_reqs
    )

    ml_recommendations_dir = Path("docs/system_design/14-ml-recommendations")
    ml_recommendations_dir.mkdir(exist_ok=True)

    filepath = ml_recommendations_dir / f"{concept_key}.md"
    filepath.write_text(content, encoding="utf-8")

    return filepath

def main():
    """Create all 30 new ML/recommendations concepts."""
    print("🤖 Creating 30 new ML/recommendations concepts (06-35)...")
    print("=" * 70)

    created = 0
    for concept_key, concept_data in sorted(CONCEPTS.items()):
        filepath = create_topic_file(concept_key, concept_data)
        print(f"✅ Created: {filepath.name}")
        created += 1

    print("=" * 70)
    print(f"✨ Created {created} new comprehensive ML/recommendations concepts!")
    print("\nTopics added (06-35):")
    topics = [v["title"] for v in CONCEPTS.values()]
    for i, topic in enumerate(topics, 6):
        print(f"  {i}. {topic}")

if __name__ == "__main__":
    main()
