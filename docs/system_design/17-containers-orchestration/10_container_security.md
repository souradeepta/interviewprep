# Container Security

## Problem Statement

Design a secure container runtime environment covering image security, runtime hardening, secrets management, and Kubernetes RBAC to minimize attack surface and blast radius of compromised containers.

## Scenario

Container Security is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

**Functional Requirements:**
- Correct behavior under all specified operating conditions
- Reliable operation with explicit failure modes
- Data consistency or eventual consistency guarantees as specified
- Clear mechanisms for error handling and recovery
- Monitoring and observability hooks

**Non-Functional Requirements:**
- **Performance**: Sub-100ms P99 latency for standard operations; measure and track tail latencies
- **Availability**: 99.99%+ uptime with automatic failover and graceful degradation
- **Scalability**: Support 10-100x current load with minimal architectural modifications
- **Consistency**: Specify whether strong, eventual, or causal consistency is required
- **Cost Efficiency**: Minimize operational cost per unit of throughput; consider compute, memory, and network costs
- **Operational Simplicity**: Reduce complexity to minimize human error and operational toil

**Constraints:**
- Resource limits (memory for caches, disk for databases, network bandwidth)
- Deployment constraints (cloud provider limits, regulatory requirements)
- Latency budgets (maximum acceptable delay for operations)

## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Code Explanation

The provided implementations demonstrate key architectural concepts and design patterns:

**Python Implementation**: Uses built-in Python structures and standard library features to express the core logic clearly. Python emphasizes readability and conciseness—each operation's purpose should be obvious without extensive comments. You'll see different implementation approaches (e.g., using OrderedDict vs. manual linked lists) that represent trade-offs between convenience and fine-grained control.

**Java Implementation**: Shows how to implement the same logic with explicit memory management and type safety. Java's strong typing forces clear interface design; you'll see how generics, null safety, mutable state, and thread safety are handled. This implementation style is closer to production systems at scale.

**Key Implementation Patterns**:
- **Initialization**: Setting up core data structures, thread pools, or connection pools with specified capacity and configuration
- **Read Operations**: Fetching data while maintaining O(1) or O(log n) access, updating metadata (access times, hit counts, etc.)
- **Write Operations**: Inserting/updating data while handling eviction policies, balancing tree structures, or replicating state
- **Edge Cases**: Handling capacity limits, concurrent access, data consistency, and error conditions
- **Performance Optimization**: Using techniques like batch operations, lazy evaluation, or caching to reduce latency

Each line of code represents a deliberate choice about performance characteristics, memory usage, safety guarantees, and implementation complexity. Understanding these trade-offs is essential for using this component effectively in production systems.

## Architecture Diagram

```mermaid
graph TB
    subgraph Build["Build Time Security"]
        IMG["Base Image\n(minimal/distroless)"]
        SCAN["Image Scanner\nTrivy/Snyk"]
        SIGN["Image Signing\nCosign/Notary"]
        REG["Private Registry\n(no :latest)"]
    end

    subgraph Runtime["Runtime Security"]
        PSP["Pod Security\nAdmission"]
        SEC["securityContext\n(non-root, readOnly FS)"]
        SEC_COMP["Seccomp/AppArmor\nprofile"]
        NET_POL["NetworkPolicy\ndefault-deny"]
    end

    subgraph Secrets["Secrets Management"]
        VAULT["HashiCorp Vault\nor AWS Secrets Manager"]
        ESO["External Secrets\nOperator"]
        K8S_SEC["K8s Secret\n(base64, not encrypted!)"]
    end

    IMG --> SCAN --> SIGN --> REG --> PSP
    PSP --> SEC --> SEC_COMP
    VAULT --> ESO --> K8S_SEC
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant D as Developer
    participant CI as CI Pipeline
    participant REG as Registry
    participant ADM as Admission Controller
    participant VAULT as Vault

    D->>CI: git push
    CI->>CI: Build image
    CI->>CI: trivy image scan (no HIGH/CRITICAL)
    CI->>CI: cosign sign image
    CI->>REG: Push signed image
    
    D->>ADM: kubectl apply pod.yaml
    ADM->>REG: Verify cosign signature
    ADM->>ADM: Check PodSecurity: non-root, no privileged
    ADM->>ADM: OPA/Gatekeeper policy check
    ADM-->>D: Admission denied (missing securityContext)
    
    D->>D: Add securityContext to pod.yaml
    D->>ADM: kubectl apply pod.yaml (fixed)
    ADM-->>D: Admitted
    
    Note over VAULT: At runtime
    ADM->>VAULT: ESO fetch secret
    VAULT-->>ADM: Secret value
    ADM->>ADM: Create K8s Secret
```

## Design

### Container Hardening

```yaml
# Secure pod security context
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault  # Restrict syscalls

  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
          add: []  # Add only what's needed (NET_BIND_SERVICE for port 80)
      volumeMounts:
        - name: tmp
          mountPath: /tmp  # Writable temp dir
  
  volumes:
    - name: tmp
      emptyDir: {}
```

### Pod Security Admission (replaces PodSecurityPolicy)

```
Three profiles:
  Privileged: No restrictions (system components only)
  Baseline:   Prevents known privilege escalations
  Restricted: Strongly hardened (non-root, no capabilities)

Enforce per namespace:
  kubectl label namespace production \
    pod-security.kubernetes.io/enforce=restricted \
    pod-security.kubernetes.io/enforce-version=v1.28
```

### Secrets Best Practices

```
NEVER:
  - Secrets in environment variables (visible in ps, logs, crash dumps)
  - Secrets in ConfigMaps (unencrypted)
  - Secrets in Docker image layers (docker history exposes them)
  - secrets in git

USE:
  External Secrets Operator + Vault/AWS Secrets Manager:
    - Secret values never stored in git
    - Automatic rotation
    - Audit trail

  Secret as volume mount (preferred over env vars):
    - File permissions controllable
    - Harder to leak in logs
    - Volume: secretName: db-credentials
```

### RBAC Least Privilege

```yaml
# Service account for application
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp
  namespace: production
automountServiceAccountToken: false  # Disable unless needed

---
# Role: only what this app needs
kind: Role
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]  # Read only, not create/delete/update

---
# Bind role to service account
kind: RoleBinding
subjects:
  - kind: ServiceAccount
    name: myapp
```

## Common Questions & Answers

**Q: Why is `latest` tag dangerous in production?** A: No immutability — same tag can point to different images over time. If a node re-pulls, it may get a different version than other nodes. Always use digest (`image@sha256:...`) or version tags.

**Q: What is the difference between a K8s Secret and an encrypted secret?** A: K8s Secrets are base64-encoded (NOT encrypted) in etcd by default. Enable etcd encryption at rest. Or use Sealed Secrets (encrypt in git) or External Secrets Operator (never in K8s at all).

**Q: What does `readOnlyRootFilesystem: true` protect against?** A: Prevents attackers from writing malware, modifying binaries, or persisting data after container restart. Forces explicit volume mounts for writable paths (/tmp, /var/run). Writes outside mounts fail with EROFS.

**Q: What is a seccomp profile?** A: Syscall filter. Container can only call kernel functions in the allowlist. `RuntimeDefault` blocks ~300+ dangerous syscalls (ptrace, mount, create_module). Custom profiles allow even fewer. Reduces kernel attack surface.

**Q: How do you prevent container escape?** A: (1) Non-root user. (2) No privileged mode. (3) Drop ALL capabilities. (4) seccomp RuntimeDefault. (5) AppArmor/SELinux profile. (6) No hostPID/hostNetwork/hostIPC. (7) Read-only root FS. Defense in depth.

## Back-of-Envelope Calculations

```
Image scan time:
  Trivy scan 100MB image: ~5-10s
  Daily scans of 100 images: 500-1000s = ~15min scan job
  At 10 pipelines parallel: ~1.5min

RBAC rule count at scale:
  100 microservices x 3 roles each = 300 Roles
  Each with 5 rules: 1500 policy rules in etcd
  Admission check: O(1) (cached by API server)

Secret rotation:
  Vault TTL: 1 hour
  1000 pods refreshing hourly: ~17 req/min to Vault
  Vault handles 10K+ req/sec: trivial

Container escape blast radius:
  Privileged container: full node compromise (dangerous)
  Non-root container: limited to pod namespace
  readOnlyFS: no persistence after restart
  Seccomp: 0-day exploit harder to execute

Image scanning CVEs:
  Alpine base: ~10-20 CVEs (mostly low)
  Ubuntu base: ~100-200 CVEs
  Distroless: ~0-5 CVEs (no shell, no package manager)
```

## Design Choices

| Security Layer | Approach | Protection | Cost |
|---|---|---|---|
| Base image | Distroless | No shell/package manager | Harder to debug |
| Image scanning | Trivy in CI | Block vulnerable images | +10s per build |
| Secrets | External Secrets + Vault | No secrets in etcd | Vault infra needed |
| Runtime | seccomp + caps drop | Syscall restriction | Near zero overhead |
| Network | NetworkPolicy default-deny | Lateral movement | Policy maintenance |
| RBAC | Per-service SA, no automount | Token theft protection | Config overhead |

## Follow-up Questions

1. How do you implement image scanning in a CI/CD pipeline with quality gates?
2. What is Falco and how does it detect runtime threats in containers?
3. How does Vault agent sidecar inject secrets into pods?
4. How do you audit Kubernetes API access with audit logs?
5. What is supply chain security (SLSA) and how does Cosign help?

## Python Implementation

```python
import os
import base64
import hmac
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

@dataclass
class Capability:
    name: str

DANGEROUS_CAPS = {"SYS_ADMIN", "NET_ADMIN", "SYS_PTRACE", "DAC_OVERRIDE", "SETUID"}

@dataclass
class SecurityContext:
    run_as_user: int = 1000
    run_as_non_root: bool = True
    read_only_root_filesystem: bool = True
    allow_privilege_escalation: bool = False
    capabilities_drop: List[str] = field(default_factory=lambda: ["ALL"])
    capabilities_add: List[str] = field(default_factory=list)
    seccomp_type: str = "RuntimeDefault"

    def validate(self) -> List[str]:
        violations = []
        if self.run_as_user == 0 and self.run_as_non_root:
            violations.append("runAsUser=0 conflicts with runAsNonRoot=true")
        if not self.run_as_non_root and self.run_as_user == 0:
            violations.append("Container running as root")
        if self.allow_privilege_escalation:
            violations.append("allowPrivilegeEscalation=true is risky")
        for cap in self.capabilities_add:
            if cap in DANGEROUS_CAPS:
                violations.append(f"Dangerous capability: {cap}")
        if not self.read_only_root_filesystem:
            violations.append("Writable root filesystem")
        return violations

class AdmissionController:
    def __init__(self, policy: str = "restricted"):
        self.policy = policy

    def admit(self, pod_spec: dict) -> tuple[bool, List[str]]:
        violations = []
        containers = pod_spec.get("containers", [])
        pod_security_ctx = pod_spec.get("securityContext", {})

        if pod_spec.get("hostNetwork"):
            violations.append("hostNetwork=true violates isolation")
        if pod_spec.get("hostPID"):
            violations.append("hostPID=true allows host process visibility")

        for container in containers:
            name = container.get("name", "?")
            ctx_dict = container.get("securityContext", {})

            if container.get("privileged"):
                violations.append(f"{name}: privileged=true (full host access)")

            sc = SecurityContext(
                run_as_user=ctx_dict.get("runAsUser", 0),
                run_as_non_root=ctx_dict.get("runAsNonRoot", False),
                read_only_root_filesystem=ctx_dict.get("readOnlyRootFilesystem", False),
                allow_privilege_escalation=ctx_dict.get("allowPrivilegeEscalation", True),
                capabilities_drop=ctx_dict.get("capabilities", {}).get("drop", []),
                capabilities_add=ctx_dict.get("capabilities", {}).get("add", []),
            )
            violations.extend([f"{name}: {v}" for v in sc.validate()])

            image = container.get("image", "")
            if ":latest" in image or (":" not in image):
                violations.append(f"{name}: unpinned image tag '{image}'")

        return len(violations) == 0, violations

class VaultSecretsManager:
    def __init__(self):
        self._vault: Dict[str, Dict[str, str]] = {}

    def write_secret(self, path: str, data: Dict[str, str]):
        self._vault[path] = data
        print(f"[Vault] Stored secret at {path}")

    def read_secret(self, path: str) -> Optional[Dict[str, str]]:
        return self._vault.get(path)

    def rotate_secret(self, path: str, new_data: Dict[str, str]):
        self._vault[path] = new_data
        print(f"[Vault] Rotated secret at {path}")

class KubernetesRBAC:
    def __init__(self):
        self._role_bindings: Dict[str, Set[str]] = {}  # (sa, resource) -> verbs
        self._roles: Dict[str, List[dict]] = {}

    def create_role(self, name: str, rules: List[dict]):
        self._roles[name] = rules
        print(f"[RBAC] Role '{name}' created")

    def bind_role(self, sa: str, role: str):
        rules = self._roles.get(role, [])
        for rule in rules:
            for resource in rule.get("resources", []):
                key = f"{sa}/{resource}"
                self._role_bindings[key] = set(rule.get("verbs", []))
        print(f"[RBAC] Bound role '{role}' to SA '{sa}'")

    def check(self, sa: str, resource: str, verb: str) -> bool:
        key = f"{sa}/{resource}"
        allowed_verbs = self._role_bindings.get(key, set())
        return verb in allowed_verbs

# --- Admission control demo ---
print("=== Admission Control ===")
admission = AdmissionController(policy="restricted")

bad_pod = {
    "containers": [{
        "name": "app",
        "image": "myapp:latest",
        "privileged": True,
        "securityContext": {"runAsUser": 0}
    }],
    "hostNetwork": True
}

good_pod = {
    "containers": [{
        "name": "app",
        "image": "myapp:1.2.3",
        "securityContext": {
            "runAsUser": 1000,
            "runAsNonRoot": True,
            "readOnlyRootFilesystem": True,
            "allowPrivilegeEscalation": False,
            "capabilities": {"drop": ["ALL"]}
        }
    }]
}

for name, pod in [("bad", bad_pod), ("good", good_pod)]:
    allowed, violations = admission.admit(pod)
    status = "ALLOWED" if allowed else "DENIED"
    print(f"\n{name} pod: {status}")
    for v in violations:
        print(f"  - {v}")

# --- Secrets management ---
print("\n=== Secrets Management ===")
vault = VaultSecretsManager()
vault.write_secret("secret/myapp/db", {"password": "s3cr3t", "host": "db.internal"})
secret = vault.read_secret("secret/myapp/db")
print(f"[ESO] Synced to K8s Secret: {list(secret.keys())}")

# --- RBAC ---
print("\n=== RBAC Check ===")
rbac = KubernetesRBAC()
rbac.create_role("app-reader", [{"resources": ["configmaps", "secrets"], "verbs": ["get", "list"]}])
rbac.bind_role("sa/myapp", "app-reader")
print(f"myapp can GET configmaps: {rbac.check('sa/myapp', 'configmaps', 'get')}")
print(f"myapp can DELETE secrets: {rbac.check('sa/myapp', 'secrets', 'delete')}")
```

## Java Implementation

```java
import java.util.*;

public class ContainerSecurity {
    record SecurityCtx(int runAsUser, boolean runAsNonRoot, boolean readOnlyFs, boolean allowPrivEsc) {}

    static List<String> validateSecurityCtx(String container, SecurityCtx ctx, String image) {
        List<String> violations = new ArrayList<>();
        if (!ctx.runAsNonRoot() && ctx.runAsUser() == 0)
            violations.add(container + ": running as root");
        if (!ctx.readOnlyFs())
            violations.add(container + ": writable root filesystem");
        if (ctx.allowPrivEsc())
            violations.add(container + ": allowPrivilegeEscalation=true");
        if (image.endsWith(":latest") || !image.contains(":"))
            violations.add(container + ": unpinned image " + image);
        return violations;
    }

    static class VaultSimulator {
        private Map<String, Map<String, String>> store = new HashMap<>();
        void write(String path, Map<String, String> data) { store.put(path, data); }
        Map<String, String> read(String path) { return store.getOrDefault(path, Map.of()); }
    }

    public static void main(String[] args) {
        // Security context validation
        SecurityCtx bad = new SecurityCtx(0, false, false, true);
        SecurityCtx good = new SecurityCtx(1000, true, true, false);
        System.out.println("Bad violations: " + validateSecurityCtx("app", bad, "myapp:latest"));
        System.out.println("Good violations: " + validateSecurityCtx("app", good, "myapp:v1.2.3"));

        // Vault secrets
        VaultSimulator vault = new VaultSimulator();
        vault.write("secret/myapp", Map.of("db_pass", "s3cr3t"));
        System.out.println("Secret keys: " + vault.read("secret/myapp").keySet());
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Admission webhook validation | O(containers x rules) |
| RBAC check | O(1) (cached) |
| Image signature verify | O(1) network round-trip |
| Seccomp rule evaluation | O(1) per syscall |
| Secret rotation | O(pods) for ESO sync |
