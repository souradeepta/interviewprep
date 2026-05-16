# Configuration Management

## Problem Statement

### Functional Requirements
- Centralized configuration storage
- Support environment-specific configs
- Enable config versioning
- Real-time config updates
- Validate configuration changes

### Non-Functional Requirements
- Latency: Config access < 50ms p99
- Throughput: 100K+ config reads/second
- Availability: 99.99% config service
- Consistency: Eventual consistency OK
- Scalability: Support 10K+ configs

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
