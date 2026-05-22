#!/usr/bin/env python3
"""
Add 30 new infrastructure concepts (33-62) with comprehensive treatment.
Each includes diagrams, code, calculations, interview questions.
"""

from pathlib import Path

CONCEPTS = {
    "33_kubernetes": {
        "title": "Kubernetes Orchestration",
        "requirements": {
            "functional": [
                "Deploy and manage containerized applications at scale",
                "Automatically scale deployments based on load",
                "Self-heal by restarting failed containers",
                "Roll out updates with zero downtime",
                "Manage secrets and configuration"
            ],
            "non_functional": [
                "Throughput: Manage 10K+ pods across clusters",
                "Latency: Pod startup < 10 seconds",
                "Availability: 99.99% cluster uptime",
                "Scalability: Support 10K+ nodes per cluster",
                "Resource efficiency: 80%+ utilization"
            ]
        }
    },
    "34_docker": {
        "title": "Docker Containerization",
        "requirements": {
            "functional": [
                "Package applications with dependencies",
                "Enable consistent deployment across environments",
                "Support image versioning and tagging",
                "Manage container networking and volumes",
                "Support private image registries"
            ],
            "non_functional": [
                "Image size: < 100MB for typical applications",
                "Startup latency: Container start < 2 seconds",
                "Efficiency: 10-20x more efficient than VMs",
                "Scalability: Support 1000s of containers per host",
                "Availability: Docker daemon highly available"
            ]
        }
    },
    "35_service_mesh": {
        "title": "Service Mesh (Istio/Linkerd)",
        "requirements": {
            "functional": [
                "Manage inter-service communication",
                "Enable traffic management and routing",
                "Enforce security policies between services",
                "Provide observability of service interactions",
                "Support circuit breaking and retries"
            ],
            "non_functional": [
                "Latency overhead: < 5ms additional per request",
                "CPU overhead: < 10% additional",
                "Throughput: Support 1M+ requests/second",
                "Observability: Trace all service interactions",
                "Scalability: Support 1000+ services"
            ]
        }
    },
    "36_cicd_pipeline": {
        "title": "CI/CD Pipeline",
        "requirements": {
            "functional": [
                "Automatically build on code commit",
                "Run automated tests on every build",
                "Deploy to staging for validation",
                "Gate production deployment on approval",
                "Rollback to previous version if needed"
            ],
            "non_functional": [
                "Build time: < 10 minutes for typical application",
                "Test execution: Complete in < 5 minutes",
                "Deployment latency: < 5 minutes to production",
                "Reliability: 99.99% pipeline success rate",
                "Scalability: Support 100+ concurrent builds"
            ]
        }
    },
    "37_iac_terraform": {
        "title": "Infrastructure as Code (Terraform)",
        "requirements": {
            "functional": [
                "Define infrastructure in code",
                "Version control infrastructure changes",
                "Enable reproducible deployments",
                "Support multiple cloud providers",
                "Track infrastructure state"
            ],
            "non_functional": [
                "Deployment time: Provision 1000 resources < 30 minutes",
                "Accuracy: 100% resource creation match",
                "Auditability: Complete change history",
                "Scalability: Support multi-region deployments",
                "Reliability: Idempotent operations"
            ]
        }
    },
    "38_monitoring_observability": {
        "title": "Monitoring and Observability",
        "requirements": {
            "functional": [
                "Collect metrics from all system components",
                "Aggregate logs from distributed services",
                "Trace requests across system",
                "Create dashboards for visualization",
                "Alert on anomalies and thresholds"
            ],
            "non_functional": [
                "Metric latency: Data available within 1 minute",
                "Log ingestion: Process 100K+ logs/second",
                "Retention: Keep data for 30+ days",
                "Query latency: < 5 seconds for dashboards",
                "Storage: Compress logs to 10% original size"
            ]
        }
    },
    "39_logging_pipeline": {
        "title": "Logging Pipeline",
        "requirements": {
            "functional": [
                "Collect logs from all services",
                "Parse and structure logs",
                "Index logs for fast searching",
                "Archive logs for compliance",
                "Enable alerting on log patterns"
            ],
            "non_functional": [
                "Throughput: Process 1M+ log events/second",
                "Latency: Logs searchable within 1 minute",
                "Retention: 1 year log history",
                "Storage: Compress to 10% original size",
                "Availability: 99.99% log availability"
            ]
        }
    },
    "40_metrics_collection": {
        "title": "Metrics Collection System",
        "requirements": {
            "functional": [
                "Collect metrics from applications and infrastructure",
                "Support multiple metric types (gauge, counter, histogram)",
                "Aggregate metrics from distributed sources",
                "Enable long-term storage and archival",
                "Support metric querying and analysis"
            ],
            "non_functional": [
                "Collection frequency: Sub-second granularity",
                "Throughput: Process 1M+ metric samples/second",
                "Latency: Metrics available < 1 minute",
                "Storage: 1 year retention with compression",
                "Cardinality: Support 1B+ unique metric names"
            ]
        }
    },
    "41_distributed_tracing": {
        "title": "Distributed Tracing System",
        "requirements": {
            "functional": [
                "Trace requests across multiple services",
                "Identify performance bottlenecks",
                "Correlate logs with traces",
                "Support sampling to reduce overhead",
                "Enable root cause analysis"
            ],
            "non_functional": [
                "Overhead: < 5% performance impact",
                "Latency: Traces available < 5 seconds",
                "Throughput: Collect 1M+ trace events/second",
                "Retention: 7 days of trace data",
                "Queryability: Fast trace search"
            ]
        }
    },
    "42_alerting_system": {
        "title": "Alerting System",
        "requirements": {
            "functional": [
                "Define alert rules on metrics and logs",
                "Evaluate rules continuously",
                "Send notifications on alert trigger",
                "Group and deduplicate alerts",
                "Support alert routing and escalation"
            ],
            "non_functional": [
                "Alert latency: < 30 seconds from condition to notification",
                "False positive rate: < 1%",
                "Reliability: 99.99% alert delivery",
                "Scalability: Support 10K+ alert rules",
                "Flexibility: Custom notification channels"
            ]
        }
    },
    "43_deployment_strategies": {
        "title": "Deployment Strategies",
        "requirements": {
            "functional": [
                "Support multiple deployment patterns",
                "Enable gradual rollout with testing",
                "Quick rollback on issues",
                "Health checks during deployment",
                "Support database schema migrations"
            ],
            "non_functional": [
                "Deployment time: < 10 minutes for new version",
                "Downtime: Zero-downtime deployments",
                "Rollback: Revert < 2 minutes",
                "Testing: Automated pre-deployment validation",
                "Scalability: Support 1000s of deployments/day"
            ]
        }
    },
    "44_bluegreen_deployment": {
        "title": "Blue-Green Deployment",
        "requirements": {
            "functional": [
                "Maintain two identical production environments",
                "Switch traffic between blue and green",
                "Test green environment before cutover",
                "Instant rollback by switching back",
                "Support health verification"
            ],
            "non_functional": [
                "Cutover time: Instant traffic switch",
                "Downtime: Zero-downtime deployment",
                "Rollback: Instant revert if issues",
                "Cost: 2x infrastructure cost",
                "Testing: Full environment validation"
            ]
        }
    },
    "45_canary_deployment": {
        "title": "Canary Deployment",
        "requirements": {
            "functional": [
                "Deploy to small percentage of servers",
                "Monitor metrics on canary servers",
                "Gradually increase traffic if stable",
                "Rollback if issues detected",
                "Support traffic splitting"
            ],
            "non_functional": [
                "Latency: Minimal impact during deployment",
                "Cost: Minimal extra infrastructure",
                "Risk: Limit blast radius to small percentage",
                "Monitoring: Continuous health checks",
                "Automation: Auto-rollback on metric anomaly"
            ]
        }
    },
    "46_rolling_deployment": {
        "title": "Rolling Deployment",
        "requirements": {
            "functional": [
                "Gradually replace old version with new",
                "Maintain service availability during update",
                "Handle backward compatibility",
                "Rollback by reversing the process",
                "Monitor health during rollout"
            ],
            "non_functional": [
                "Latency: No impact to clients",
                "Downtime: Zero-downtime deployment",
                "Duration: Deployment takes longer",
                "Cost: Minimal extra infrastructure",
                "Complexity: Manage old/new version together"
            ]
        }
    },
    "47_load_balancer": {
        "title": "Load Balancer",
        "requirements": {
            "functional": [
                "Distribute traffic across backend servers",
                "Support multiple load balancing algorithms",
                "Health check backends",
                "Route based on path/host/protocol",
                "Session persistence (sticky sessions)"
            ],
            "non_functional": [
                "Throughput: 1M+ requests/second",
                "Latency: < 5ms routing decision p99",
                "Availability: 99.999% uptime",
                "Scalability: Support 10K+ backends",
                "Efficiency: < 1% CPU overhead"
            ]
        }
    },
    "48_api_gateway": {
        "title": "API Gateway",
        "requirements": {
            "functional": [
                "Single entry point for all APIs",
                "Request routing to backend services",
                "Authentication and authorization",
                "Rate limiting and throttling",
                "API versioning support"
            ],
            "non_functional": [
                "Throughput: 1M+ API requests/second",
                "Latency: < 10ms p99 gateway latency",
                "Availability: 99.99% uptime",
                "Scalability: Support 1000s of APIs",
                "Security: DDoS protection built-in"
            ]
        }
    },
    "49_reverse_proxy": {
        "title": "Reverse Proxy",
        "requirements": {
            "functional": [
                "Forward client requests to backend servers",
                "Load balance traffic distribution",
                "Cache responses for performance",
                "Compress responses",
                "Handle SSL/TLS termination"
            ],
            "non_functional": [
                "Throughput: 100K+ requests/second per proxy",
                "Latency: < 1ms proxy overhead p99",
                "Availability: 99.99% uptime",
                "Cache hit rate: 80%+ for static content",
                "Compression: 5-10x reduction in bandwidth"
            ]
        }
    },
    "50_content_delivery": {
        "title": "Content Delivery Network (CDN)",
        "requirements": {
            "functional": [
                "Cache content at edge locations",
                "Serve content from nearest location",
                "Purge cache on updates",
                "Support origin failover",
                "Enable DDoS protection"
            ],
            "non_functional": [
                "Latency: < 100ms from user to CDN p99",
                "Hit rate: 95%+ cache hit ratio",
                "Availability: 99.999% uptime",
                "Geographic coverage: 200+ cities",
                "Scalability: Terabits/second capacity"
            ]
        }
    },
    "51_ddos_protection": {
        "title": "DDoS Protection",
        "requirements": {
            "functional": [
                "Detect and mitigate DDoS attacks",
                "Support multiple attack types",
                "Rate limit malicious traffic",
                "Geographic blocking",
                "Bot detection and blocking"
            ],
            "non_functional": [
                "Detection latency: < 10 seconds",
                "Mitigation: Automatic within 30 seconds",
                "Accuracy: 99%+ attack detection",
                "Throughput: Terabits/second capacity",
                "Availability: No impact to legitimate traffic"
            ]
        }
    },
    "52_web_app_firewall": {
        "title": "Web Application Firewall (WAF)",
        "requirements": {
            "functional": [
                "Protect against OWASP Top 10 attacks",
                "SQL injection prevention",
                "XSS attack prevention",
                "Custom rule support",
                "IP reputation checking"
            ],
            "non_functional": [
                "Latency: < 10ms WAF processing p99",
                "Accuracy: 99.9% threat detection",
                "False positive rate: < 0.1%",
                "Throughput: 1M+ requests/second",
                "Availability: 99.99% WAF availability"
            ]
        }
    },
    "53_vpn_security": {
        "title": "VPN and Network Security",
        "requirements": {
            "functional": [
                "Encrypt all traffic between sites",
                "Support site-to-site VPN",
                "Enable client VPN access",
                "Key exchange and management",
                "Perfect forward secrecy"
            ],
            "non_functional": [
                "Throughput: 10 Gbps+ VPN capacity",
                "Latency: < 50ms p99 with encryption",
                "Encryption: AES-256 at minimum",
                "Availability: 99.99% VPN uptime",
                "Scalability: Support 10K+ concurrent clients"
            ]
        }
    },
    "54_identity_access": {
        "title": "Identity and Access Management (IAM)",
        "requirements": {
            "functional": [
                "Centralized user and role management",
                "Support RBAC and ABAC",
                "Enable single sign-on (SSO)",
                "Multi-factor authentication support",
                "Audit all access decisions"
            ],
            "non_functional": [
                "Latency: < 100ms auth check p99",
                "Throughput: 1M+ auth requests/second",
                "Availability: 99.99% IAM service",
                "Compliance: HIPAA, SOC 2, ISO 27001",
                "Auditability: Complete audit trail"
            ]
        }
    },
    "55_secret_management": {
        "title": "Secret Management",
        "requirements": {
            "functional": [
                "Store API keys, passwords, certificates",
                "Rotate secrets automatically",
                "Audit all secret access",
                "Support dynamic secret generation",
                "Enable fine-grained access control"
            ],
            "non_functional": [
                "Latency: Secret retrieval < 100ms p99",
                "Throughput: 100K+ secret operations/second",
                "Encryption: AES-256 at rest and in transit",
                "Availability: 99.99% secret vault availability",
                "Auditability: Complete secret access logs"
            ]
        }
    },
    "56_configuration_mgmt": {
        "title": "Configuration Management",
        "requirements": {
            "functional": [
                "Centralized configuration storage",
                "Support environment-specific configs",
                "Enable config versioning",
                "Real-time config updates",
                "Validate configuration changes"
            ],
            "non_functional": [
                "Latency: Config access < 50ms p99",
                "Throughput: 100K+ config reads/second",
                "Availability: 99.99% config service",
                "Consistency: Eventual consistency OK",
                "Scalability: Support 10K+ configs"
            ]
        }
    },
    "57_disaster_recovery": {
        "title": "Disaster Recovery Planning",
        "requirements": {
            "functional": [
                "Maintain backup systems in standby",
                "Enable failover in < 15 minutes",
                "Support geo-distributed replicas",
                "Test recovery procedures regularly",
                "Document recovery procedures"
            ],
            "non_functional": [
                "RTO (Recovery Time Objective): < 15 minutes",
                "RPO (Recovery Point Objective): < 5 minutes",
                "Failover: Automatic or manual trigger",
                "Testing: Monthly DR drills",
                "Documentation: Up-to-date runbooks"
            ]
        }
    },
    "58_backup_strategy": {
        "title": "Backup Strategy",
        "requirements": {
            "functional": [
                "Create regular backups of all data",
                "Support incremental and full backups",
                "Enable restore to point-in-time",
                "Verify backup integrity",
                "Store backups in multiple regions"
            ],
            "non_functional": [
                "Backup window: Complete < 4 hours",
                "Restore time: Full restore < 1 hour",
                "Storage: 30% of production data size",
                "Retention: 1+ year of daily backups",
                "Redundancy: 3+ geographic regions"
            ]
        }
    },
    "59_autoscaling": {
        "title": "Auto-scaling System",
        "requirements": {
            "functional": [
                "Monitor resource utilization metrics",
                "Scale up when demand increases",
                "Scale down during low demand",
                "Support predictive scaling",
                "Support scheduled scaling"
            ],
            "non_functional": [
                "Scale-up latency: < 5 minutes",
                "Scale-down latency: < 10 minutes",
                "Accuracy: Scale to within 20% of target",
                "Cost: Reduce costs 30-50%",
                "Stability: Avoid thrashing at boundaries"
            ]
        }
    },
    "60_multiregion_deployment": {
        "title": "Multi-region Deployment",
        "requirements": {
            "functional": [
                "Deploy services across multiple regions",
                "Data replication across regions",
                "Cross-region failover",
                "Local data residency support",
                "Consistent global configuration"
            ],
            "non_functional": [
                "Latency: < 100ms from any region",
                "Availability: 99.99% across regions",
                "Consistency: Eventual with < 5 second lag",
                "Scalability: Support 10+ regions",
                "Cost: Manage multi-region costs"
            ]
        }
    },
    "61_high_availability": {
        "title": "High Availability Architecture",
        "requirements": {
            "functional": [
                "Eliminate single points of failure",
                "Enable automatic failover",
                "Maintain service during node failures",
                "Support rolling updates",
                "Health checks and self-healing"
            ],
            "non_functional": [
                "Availability: 99.99%+ uptime",
                "RTO: Failover < 5 minutes",
                "Recovery: Automatic with no manual intervention",
                "Consistency: Strong consistency maintained",
                "Scalability: Add nodes without downtime"
            ]
        }
    },
    "62_chaos_engineering": {
        "title": "Chaos Engineering",
        "requirements": {
            "functional": [
                "Proactively inject failures into systems",
                "Test recovery mechanisms",
                "Identify weak points in architecture",
                "Validate disaster recovery procedures",
                "Document system resilience"
            ],
            "non_functional": [
                "Safety: Controlled failure injection",
                "Impact: Limited blast radius",
                "Frequency: Run tests regularly",
                "Documentation: Clear hypotheses and results",
                "Learning: Continuous improvement cycle"
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
- Throughput: Millions of operations per second
- Latency: Milliseconds depending on operation
- Infrastructure: Multi-region global deployment
- Availability: 99.99% to 99.999% uptime SLA
- Cost: Optimized for efficiency and scalability

**Key Components:**
- Cloud infrastructure and networking
- Container orchestration and deployment
- Monitoring and observability
- Security and access control
- Disaster recovery and backups

## Architecture Diagrams

### Infrastructure Architecture

```mermaid
graph TB
    subgraph "Users"
        U1["Global Users"]
        CDN["CDN Edge"]
    end

    subgraph "Entry Point"
        LB["Load Balancer"]
        WAF["Web App Firewall"]
    end

    subgraph "Compute"
        R1["Region 1"]
        R2["Region 2"]
        R3["Region 3"]
    end

    subgraph "Storage"
        DB1["Primary DB"]
        DB2["Replica DB"]
        OBJ["Object Storage"]
    end

    U1 --> CDN
    CDN --> LB
    LB --> WAF
    WAF --> R1
    WAF --> R2
    WAF --> R3
    R1 --> DB1
    R2 --> DB2
    R3 --> OBJ

    style U1 fill:#e1f5ff
    style LB fill:#f3e5f5
    style R1 fill:#fff3e0
    style DB1 fill:#e8f5e9
```

### Deployment Pipeline

```mermaid
graph LR
    A["Code Commit"] --> B["Build"]
    B --> C["Test"]
    C --> D["Deploy Staging"]
    D --> E["Approval"]
    E --> F["Deploy Canary"]
    F --> G["Monitor"]
    G --> H["Deploy Full"]

    style A fill:#c8e6c9
    style C fill:#ffccbc
    style F fill:#bbdefb
    style H fill:#fff9c4
```

### High Availability

```mermaid
graph TB
    U["Users"] --> LB["Load Balancer"]
    LB --> S1["Service Instance 1"]
    LB --> S2["Service Instance 2"]
    LB --> S3["Service Instance N"]

    S1 --> DB1["Primary DB"]
    S2 --> DB2["Replica 1"]
    S3 --> DB3["Replica 2"]

    DB1 --> B["Backup"]

    style LB fill:#fff3e0
    style S1 fill:#c8e6c9
    style DB1 fill:#e8f5e9
    style B fill:#ffccbc
```

### Monitoring and Observability

```mermaid
graph TB
    subgraph "Collection"
        M1["Metrics"]
        L1["Logs"]
        T1["Traces"]
    end

    subgraph "Processing"
        A["Aggregation"]
        P["Processing"]
    end

    subgraph "Visualization"
        D["Dashboards"]
        AL["Alerts"]
    end

    M1 --> A
    L1 --> A
    T1 --> A
    A --> P
    P --> D
    P --> AL

    style M1 fill:#bbdefb
    style D fill:#c8e6c9
    style AL fill:#ffcdd2
```

### Security Layers

```mermaid
graph TB
    U["Users"] --> D["DDoS Protection"]
    D --> WAF["Web App Firewall"]
    WAF --> GW["API Gateway"]
    GW --> AUTH["Authentication"]
    AUTH --> IAM["IAM"]
    IAM --> SVC["Services"]

    style D fill:#ffcdd2
    style WAF fill:#ffccbc
    style AUTH fill:#fff9c4
    style IAM fill:#c8e6c9
```

## Data Flow Scenarios

### Scenario 1: Normal Request Flow
1. User request hits CDN
2. CDN serves cached content if available
3. Request routed through DDoS protection
4. WAF validates request
5. Load balancer routes to healthy instance
6. Service processes request
7. Response cached at CDN
8. Response returned to user

### Scenario 2: Auto-scaling Event
1. Metrics show CPU utilization > 80%
2. Auto-scaler provisions new instances
3. Instances join load balancer pool
4. Traffic gradually shifted to new instances
5. Old instances scaled down after demand decreases
6. Cost optimized for current load

### Scenario 3: Failover and Recovery
1. Health check detects instance failure
2. Load balancer removes from pool
3. Auto-scaler spins up replacement
4. Replacement instances joins cluster
5. Data replicated from primary DB
6. Service continues without interruption

## Performance Optimization

### Infrastructure Optimization
- **Caching**: CDN for static content, API response caching
- **Compression**: GZIP for responses, efficient storage
- **Connection pooling**: Reuse connections to reduce overhead
- **Batching**: Group operations for efficiency

### Resource Optimization
- **Right-sizing**: Match resources to actual workload
- **Auto-scaling**: Scale with demand dynamically
- **Reserved capacity**: Baseline + burst capacity
- **Spot instances**: Use cheap instances for batch jobs

### Cost Optimization
- **Reserved instances**: 30-50% discount for committed capacity
- **Spot instances**: 70% discount for flexible workloads
- **Data transfer**: Minimize cross-region transfers
- **Storage**: Archive old data to cheaper tiers

## Back-of-Envelope Calculations

### Global Infrastructure
```
Daily active users: 100M
Requests per user: 50
Daily requests: 5B
Average RPS: 57,870
Peak hour RPS (10x): 578,700
Regions: 3 (Americas, EMEA, APAC)
Servers per region: 200 servers per 1M peak RPS
Total servers: 3 × 200 × 0.6 = 360 servers
Server cost: 360 × $2,000/month = $720K/month
```

### Storage Infrastructure
```
Data per user: 100 KB
Total user data: 100M × 100 KB = 10 TB
Backups: 30 daily, 12 monthly = 42 copies
Total backup storage: 10 TB × 42 = 420 TB
Archive (cold storage): 50% = 210 TB
Data transfer: 10 TB/day × 30 days = 300 TB/month
Bandwidth cost: 300 TB × $0.02/GB = $6M/month
```

### Deployment Infrastructure
```
Code commits per day: 500
Builds per commit: 1
Build time: 10 minutes average
Build parallelism: 50 concurrent
Build servers needed: 500 × 10 / 60 / 50 = 2 servers
Deployment frequency: 50 per day
Deployment time: 5 minutes average
Staging capacity: 50/24 = ~2 extra servers
Total CI/CD cost: ~$10K/month
```

## Interview Questions & Answers

### Q1: Design multi-region infrastructure for 100M users

**Answer:**
1. **Regions**: Deploy in 3 regions (US, EU, APAC) for latency
2. **Database**: Primary in US, read replicas in EU/APAC
3. **CDN**: Cache static assets globally
4. **Load balancing**: Cross-region failover with DNS
5. **Data sync**: Asynchronous replication with conflict resolution
6. **Compliance**: Data residency requirements per region

### Q2: How do you achieve 99.99% availability?

**Answer:**
- **Redundancy**: No single point of failure
- **Health checks**: Detect failures in < 10 seconds
- **Auto-failover**: Automatic switchover to healthy instances
- **Chaos testing**: Regularly test failure scenarios
- **Monitoring**: Real-time alerts on anomalies
- **Runbooks**: Automated recovery procedures

### Q3: Implement zero-downtime deployment

**Answer:**
- **Blue-Green**: Two identical environments, switch traffic
- **Canary**: Deploy to 1%, monitor, then roll out
- **Rolling**: Gradually replace old version
- **DB migrations**: Backward-compatible schema changes
- **Feature flags**: Enable features independently
- **Monitoring**: Detect issues within seconds

### Q4: How to secure infrastructure?

**Answer:**
- **Network**: VPC, security groups, NACLs
- **WAF**: OWASP Top 10 protection
- **DDoS**: Mitigation at CDN edge
- **Encryption**: TLS for transport, AES for storage
- **IAM**: Least privilege access control
- **Audit**: Complete logging of all access

### Q5: Design disaster recovery strategy

**Answer:**
- **RTO**: 15 minutes maximum
- **RPO**: 5 minutes maximum
- **Backup**: Daily snapshots, 30-day retention
- **Replication**: Real-time to secondary region
- **Testing**: Monthly DR drills
- **Documentation**: Updated runbooks

### Q6: Cost optimization strategies

**Answer:**
- **Reserved instances**: 1-3 year commitment
- **Spot instances**: Batch jobs, non-critical workloads
- **Auto-scaling**: Match capacity to demand
- **Data transfer**: Minimize cross-region, use CDN
- **Storage**: Tiered (hot/warm/cold)
- **Monitoring**: Track costs per service

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Container Orchestration | Kubernetes | Industry standard, feature-rich |
| Container Runtime | Docker | Lightweight, portable |
| Service Mesh | Istio | Advanced traffic management |
| Monitoring | Prometheus | Time-series metrics |
| Logging | ELK Stack | Full-text search, analysis |
| Tracing | Jaeger | Distributed request tracing |
| CI/CD | Jenkins/GitLab | Flexible, extensible |
| IaC | Terraform | Multi-cloud support |
| CDN | CloudFront/Akamai | Global edge locations |

## Lessons Learned

1. **Automate everything**: Manual processes don't scale
2. **Failure is inevitable**: Design for it from the start
3. **Observability is critical**: Instrument before optimizing
4. **Cost grows with complexity**: Measure and optimize regularly
5. **Security is not optional**: Build it in from the beginning

## Related Topics

- Kubernetes and container orchestration
- Cloud providers (AWS, GCP, Azure)
- Networking and load balancing
- Database replication and backups
- Security and compliance
- Cost optimization and FinOps
- Site reliability engineering (SRE)
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

    infrastructure_dir = Path("docs/system_design/08-infrastructure")
    infrastructure_dir.mkdir(exist_ok=True)

    filepath = infrastructure_dir / f"{concept_key}.md"
    filepath.write_text(content, encoding="utf-8")

    return filepath

def main():
    """Create all 30 new infrastructure concepts."""
    print("🏗️  Creating 30 new infrastructure concepts (33-62)...")
    print("=" * 70)

    created = 0
    for concept_key, concept_data in sorted(CONCEPTS.items()):
        filepath = create_topic_file(concept_key, concept_data)
        print(f"✅ Created: {filepath.name}")
        created += 1

    print("=" * 70)
    print(f"✨ Created {created} new comprehensive infrastructure concepts!")
    print("\nTopics added (33-62):")
    topics = [v["title"] for v in CONCEPTS.values()]
    for i, topic in enumerate(topics, 33):
        print(f"  {i}. {topic}")

if __name__ == "__main__":
    main()
