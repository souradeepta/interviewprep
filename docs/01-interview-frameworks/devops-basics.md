# DevOps Basics — Infrastructure as Code and Deployment

Essential DevOps concepts for all engineers.

---

## 🔄 CI/CD Pipeline

**Continuous Integration:** Code changes merged frequently, tested automatically
**Continuous Deployment:** Tested code automatically deployed to production

### Pipeline Stages

```
Commit Code → Tests → Build → Deploy to Staging → Deploy to Production

Feedback: Minutes from commit to production
```

### Tools

**GitHub Actions:** Built into GitHub
**GitLab CI:** Built into GitLab
**Jenkins:** Self-hosted orchestration
**CircleCI:** Cloud-based CI/CD

---

## 📦 Infrastructure as Code

**Define infrastructure in code, version control it**

```yaml
# docker-compose.yml
version: '3'
services:
  web:
    image: myapp:v1
    ports:
      - "8080:8080"
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: secret
```

### Tools

**Docker:** Containerize application
**Kubernetes:** Orchestrate containers
**Terraform:** Infrastructure automation
**Ansible:** Configuration management

---

## 🚀 Deployment Strategies

**Blue-Green:** Two production environments, switch between
- Instant rollback
- Zero downtime

**Canary:** Gradual rollout to % of users
- Detect issues early
- Monitor before full deployment

**Rolling:** Gradual replacement of old with new
- No downtime
- Rollback takes time

---

## 📊 Monitoring & Logging

```
Logs: What happened (ELK, CloudWatch)
Metrics: How much (Prometheus, Grafana)
Traces: Where it happened (Jaeger, Zipkin)
Alerts: Notify on issues (PagerDuty, Opsgenie)
```

---

## ❓ Interview Q&A

**Q: Design CI/CD pipeline for scalable service.**
A: Tests on commit, staging deploy on PR merge, production canary deploy with monitoring. Rollback on alert.

**Q: How to do zero-downtime deployment?**
A: Blue-green (switch instantly) or canary (gradual). Health checks. Database migrations backwards compatible.

**Q: How to monitor production system?**
A: Logs, metrics, traces. Alert on error rate, latency, resource usage. Dashboard for visibility.

---

**Last updated:** 2026-05-22
