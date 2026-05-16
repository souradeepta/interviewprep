# Container Orchestration Basics: Kubernetes Fundamentals

Understand containerization and orchestration for modern deployment.

---

## Containers vs VMs

### Virtual Machine
```
Physical Server
├─ Hypervisor
├─ VM 1 (Linux OS, 2GB RAM, 10GB Disk)
│  └─ Python app
├─ VM 2 (Linux OS, 2GB RAM, 10GB Disk)
│  └─ Python app
└─ VM 3 (Linux OS, 2GB RAM, 10GB Disk)
   └─ Python app

Heavy: Each VM is full OS (slow boot, high overhead)
```

### Container
```
Physical Server
├─ Linux OS
├─ Docker Engine
├─ Container 1 (app + dependencies)
├─ Container 2 (app + dependencies)
└─ Container 3 (app + dependencies)

Light: Containers share OS kernel (fast boot, low overhead)
```

---

## Docker Basics

### Dockerfile
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Build and Run
```bash
docker build -t my-app:v1.0 .
docker run -p 8000:8000 my-app:v1.0
```

---

## Kubernetes Fundamentals

### Problem: Container Orchestration at Scale

```
Challenges:
- 1000 containers across 100 servers
- Auto-scaling based on load
- Rolling updates without downtime
- Persistent storage across nodes
- Service discovery
- Health checks and restart

Solution: Kubernetes (K8s)
```

### Key Concepts

| Concept | Role |
|---------|------|
| **Pod** | Smallest deployable unit (one or more containers) |
| **Node** | Physical or virtual machine running pods |
| **Cluster** | Collection of nodes |
| **Deployment** | Describes desired state (# replicas, image, etc.) |
| **Service** | Network abstraction (DNS + load balancing) |
| **PersistentVolume** | Storage abstraction |

### Simple Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3  # 3 copies of pod
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: app
        image: my-app:v1.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

---

## Kubernetes Operations

### Deploy
```bash
kubectl apply -f deployment.yaml
# Creates 3 pods running my-app:v1.0
```

### Scale
```bash
kubectl scale deployment web-app --replicas=10
# Increases to 10 replicas
```

### Rolling Update
```bash
kubectl set image deployment/web-app app=my-app:v2.0
# Gradually replaces v1.0 with v2.0 (no downtime)
```

### Health Checks
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

## Storage in Kubernetes

### Persistent Volume (PV)
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: data-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  nfs:
    server: nfs-server.example.com
    path: /data
```

### Persistent Volume Claim (PVC)
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

---

## Service Discovery

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Result:**
- DNS name: web-service.default.svc.cluster.local
- LoadBalancer distributes traffic to all pods with label `app: web`

---

## Container Orchestration Checklist

- ✓ Containerized application (Dockerfile)
- ✓ Image registry (Docker Hub, ECR, GCR)
- ✓ Kubernetes cluster (EKS, GKE, AKS)
- ✓ Deployments with proper resource limits
- ✓ Health checks (liveness and readiness probes)
- ✓ Services for networking
- ✓ Persistent volumes for data
- ✓ Rolling updates for zero-downtime deployments
- ✓ Auto-scaling policies (HPA)
- ✓ Logging and monitoring (EFK, Prometheus)

