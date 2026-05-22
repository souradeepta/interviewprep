#!/usr/bin/env python3
"""
Add 30 new system design concepts.
"""

import os

base_path = "/home/sbisw/github/interviewprep/docs/system_design"

# 30 new concept categories and specific concepts
new_concepts = {
    # Advanced Algorithms & Hashing (5)
    "10-advanced-algorithms": {
        "01_consistent_hashing": {
            "title": "Consistent Hashing",
            "description": "Distributes data across nodes minimizing remapping on node addition/removal. Used in caching and NoSQL databases."
        },
        "02_geohashing": {
            "title": "Geohashing",
            "description": "Encodes geographic location into a string. Enables efficient spatial queries and proximity searches."
        },
        "03_trie_data_structure": {
            "title": "Trie (Prefix Tree)",
            "description": "Stores strings with common prefixes. Used in autocomplete and IP routing."
        },
        "04_hyperloglog": {
            "title": "HyperLogLog",
            "description": "Probabilistic cardinality estimation. Approximates distinct count with minimal memory."
        },
        "05_simulation_algorithms": {
            "title": "Simulation & Emulation Algorithms",
            "description": "Techniques for modeling system behavior, testing strategies, and performance prediction."
        }
    },
    # Advanced Design Patterns (6)
    "11-advanced-patterns": {
        "01_proxy_pattern": {
            "title": "Proxy Pattern",
            "description": "Provides a surrogate for another object. Controls access, adds functionality, defers initialization."
        },
        "02_composite_pattern": {
            "title": "Composite Pattern",
            "description": "Composes objects into tree structures. Treats individual objects and compositions uniformly."
        },
        "03_template_method": {
            "title": "Template Method Pattern",
            "description": "Defines algorithm skeleton in base class, letting subclasses override specific steps."
        },
        "04_chain_of_responsibility": {
            "title": "Chain of Responsibility Pattern",
            "description": "Passes requests along a chain of handlers. Each handler processes or forwards to next."
        },
        "05_visitor_pattern": {
            "title": "Visitor Pattern",
            "description": "Separates algorithms from object structure. Enables adding new operations without modifying structures."
        },
        "06_memento_pattern": {
            "title": "Memento Pattern",
            "description": "Captures and externalizes object state. Enables undo/redo and state restoration."
        }
    },
    # Database Internals (5)
    "12-database-internals": {
        "01_btree_bplus_tree": {
            "title": "B-Tree & B+ Tree",
            "description": "Self-balancing search trees optimized for disk I/O. Standard in databases for indexing."
        },
        "02_lsm_tree": {
            "title": "LSM Tree (Log-Structured Merge)",
            "description": "Optimizes writes via sequential disk I/O. Used in LevelDB, RocksDB, Cassandra."
        },
        "03_mvcc": {
            "title": "MVCC (Multi-Version Concurrency Control)",
            "description": "Maintains multiple versions of data. Enables concurrent reads/writes without blocking."
        },
        "04_query_optimization": {
            "title": "Query Optimization & Execution",
            "description": "Query parsing, optimization, execution planning. Indexes, join strategies, cost estimation."
        },
        "05_replication_strategies": {
            "title": "Database Replication Strategies",
            "description": "Master-slave, multi-master, synchronous, asynchronous replication patterns."
        }
    },
    # Real-World Systems Expansion (6)
    "13-realworld-systems": {
        "01_instagram_scale": {
            "title": "Instagram-Scale Photo Sharing",
            "description": "1B+ users, billions of photos. Image storage, feed generation, search at scale."
        },
        "02_uber_ride_matching": {
            "title": "Uber-Scale Ride Matching",
            "description": "Real-time matching, geolocation, pricing, payment, reliability at 80M+ users."
        },
        "03_netflix_streaming": {
            "title": "Netflix-Scale Video Streaming",
            "description": "200M+ users, adaptive bitrate, CDN, recommendation, billing for streaming."
        },
        "04_github_collaboration": {
            "title": "GitHub-Scale Code Collaboration",
            "description": "Version control at scale, PR reviews, CI/CD integration, conflict resolution."
        },
        "05_airbnb_booking": {
            "title": "Airbnb-Scale Booking System",
            "description": "Search, availability, pricing, booking, payment, dispute resolution."
        },
        "06_linkedin_recommendations": {
            "title": "LinkedIn Job/Connection Recommendations",
            "description": "650M+ users, ML-based recommendations, job search, feed personalization."
        }
    },
    # Machine Learning & Recommendations (5)
    "14-ml-recommendations": {
        "01_collaborative_filtering": {
            "title": "Collaborative Filtering",
            "description": "User-based and item-based recommendations. Matrix factorization for predicting preferences."
        },
        "02_content_based_filtering": {
            "title": "Content-Based Filtering",
            "description": "Recommends items similar to ones user liked. Uses item features and user profiles."
        },
        "03_ranking_systems": {
            "title": "Learning-to-Rank Systems",
            "description": "ML models for ranking items by relevance/engagement. LambdaMART, gradient boosting."
        },
        "04_feature_engineering": {
            "title": "Feature Engineering at Scale",
            "description": "Extracting, computing, serving features for ML. Feature stores, online/offline pipelines."
        },
        "05_ab_testing_framework": {
            "title": "A/B Testing & Experimentation Framework",
            "description": "Running controlled experiments, statistical significance, multi-armed bandits."
        }
    },
    # Security & Auth (3)
    "15-security": {
        "01_oauth_sso": {
            "title": "OAuth 2.0 & Single Sign-On",
            "description": "Delegated authorization, federated identity, social login, enterprise SSO."
        },
        "02_encryption_tls": {
            "title": "Encryption & TLS/SSL",
            "description": "Data encryption at rest/transit, certificate management, key rotation."
        },
        "03_access_control": {
            "title": "Access Control & RBAC",
            "description": "Role-based access control, attribute-based, permission management, audit trails."
        }
    }
}

def create_concept_file(category_path, concept_id, title, description):
    """Create a concept markdown file."""

    content = f"""# {title}

## Problem Statement

{description}

## Design

### Key Concepts

```
Core Mechanism:
- How this system works
- Key components and interactions
- Data flow and processing
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
[Visual system components and interactions]
```

## Common Questions & Answers

**Q: When to use this approach?**
A: [Specific use cases and scenarios where this is beneficial]

**Q: What are the key trade-offs?**
A: [Pros and cons of this approach vs alternatives]

**Q: How does this handle failures?**
A: [Failure scenarios and recovery mechanisms]

**Q: How to scale this?**
A: [Scaling strategies and bottlenecks]

## Back-of-Envelope Calculations

For typical distributed system scenario:
- Performance metrics
- Scalability limits
- Resource requirements
- Typical deployment sizes

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Option A | [Advantages] | [Disadvantages] |
| Option B | [Advantages] | [Disadvantages] |
| Option C | [Advantages] | [Disadvantages] |

## Follow-up Interview Questions

1. How would you implement this at scale (1M+ operations/sec)?
2. What happens if the [key component] fails?
3. How to ensure [important property] in this system?
4. What's the bottleneck at 10x current scale?
5. How would you monitor and debug [specific aspect]?

## Example Scenario Walkthrough

Scenario: [Concrete example with 5-10 steps showing system in action]

## Implementation

### Python Implementation

```python
# Working implementation with key mechanisms
# Includes initialization, core operations, and edge cases
```

### Java Implementation

```java
// Object-oriented implementation
// Shows proper abstractions and patterns
```

### Production Considerations

- **Concurrency**: Thread safety and synchronization
- **Error Handling**: Fault tolerance and recovery
- **Monitoring**: Observability and metrics
- **Performance**: Optimization strategies

## Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| [Key Op 1] | O(n) | [Explanation] |
| [Key Op 2] | O(log n) | [Explanation] |
| [Key Op 3] | O(1) | [Explanation] |

## Real-world Applications

- Use case 1
- Use case 2
- Use case 3

## Related Concepts

- Concept A (see documentation)
- Concept B (see documentation)
- Concept C (see documentation)

## Further Reading

- Academic papers
- System design references
- Implementation guides
"""

    # Create category directory if needed
    os.makedirs(category_path, exist_ok=True)

    # Write file
    filepath = os.path.join(category_path, f"{concept_id}.md")
    with open(filepath, 'w') as f:
        f.write(content)

    return filepath

# Create all new concepts
total_created = 0

for category, concepts in new_concepts.items():
    category_path = os.path.join(base_path, category)

    for concept_id, details in concepts.items():
        filepath = create_concept_file(
            category_path,
            concept_id,
            details['title'],
            details['description']
        )
        total_created += 1
        print(f"✓ Created {category}/{concept_id}.md")

print(f"\n✅ Created {total_created} new system design concept documents")
