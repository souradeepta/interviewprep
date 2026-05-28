# CI/CD & DevOps: Automating Deployment and Testing

**Level:** L4-L5
**Time to read:** ~20 min

Master continuous integration and deployment practices.

---

## CI/CD Pipeline Overview

```
Code Commit
  ↓
Build (compile, package)
  ↓
Test (unit, integration, E2E)
  ↓
Deploy to staging
  ↓
Integration tests
  ↓
Deploy to production (canary, blue-green)
  ↓
Monitor
```

---

## Continuous Integration (CI)

### On Every Commit:

1. **Run tests**
```bash
pytest tests/
pytest tests/ --cov=myapp
flake8 myapp/  # Linting
mypy myapp/    # Type checking
```

2. **Build**
```bash
docker build -t myapp:${GIT_SHA} .
```

3. **Validate**
- Code coverage > 80%
- No linting errors
- No security vulnerabilities

---

## Continuous Deployment (CD)

### Strategy 1: Blue-Green Deployment

```
Blue (current)  → 100% traffic
Green (new)     → 0% traffic

Test Green thoroughly
Switch: 100% traffic to Green
Blue stays running for quick rollback
```

### Strategy 2: Canary Deployment

```
Version 1.0 → 99% traffic
Version 2.0 → 1% traffic

Monitor error rate, latency
1.0 → 90%, 2.0 → 10%
1.0 → 50%, 2.0 → 50%
1.0 → 0%, 2.0 → 100%

If error spike: Rollback immediately
```

### Strategy 3: Rolling Update

```
Server 1: v1.0 → v2.0 (1 request fail possible)
  ↓ wait
Server 2: v1.0 → v2.0
  ↓ wait
Server 3: v1.0 → v2.0

Gradual, but brief downtime possible
```

---

## GitHub Actions Example

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8
      
      - name: Lint
        run: flake8 myapp/
      
      - name: Test
        run: pytest --cov=myapp
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
      
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag myapp:${{ github.sha }} myapp:latest
          docker push myapp:latest
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/myapp app=myapp:${{ github.sha }}
          kubectl rollout status deployment/myapp
```

---

## Infrastructure as Code (IaC)

### Terraform Example

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  count         = 3
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "web-server-${count.index}"
  }
}

resource "aws_security_group" "allow_http" {
  name = "allow_http"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Benefits:**
- Version control for infrastructure
- Reproducible deployments
- Easy rollback

---

## Monitoring & Alerting

```yaml
# Prometheus alerting rules
groups:
  - name: web-app
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        annotations:
          summary: "High error rate ({{ $value }})"
      
      - alert: HighLatency
        expr: histogram_quantile(0.99, http_request_duration_seconds) > 1
        annotations:
          summary: "P99 latency > 1s ({{ $value }})"
```

---

## Deployment Checklist

- ✓ Automated testing (unit, integration, E2E)
- ✓ Code coverage > 80%
- ✓ Linting and type checking
- ✓ Docker image builds and pushed
- ✓ Security scanning (vulnerabilities, secrets)
- ✓ Staging deployment and testing
- ✓ Canary or blue-green deployment strategy
- ✓ Automated rollback on failures
- ✓ Monitoring and alerting configured
- ✓ Runbooks for incidents
- ✓ Infrastructure as code (Terraform, CloudFormation)
- ✓ Database migrations automated and tested

