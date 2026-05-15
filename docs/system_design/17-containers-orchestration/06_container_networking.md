# Container Networking (CNI)

## Problem Statement

Understand how containers and pods communicate across nodes using the Container Network Interface (CNI), covering overlay networks, pod CIDR allocation, and network policies.

## Architecture Diagram

```mermaid
graph TB
    subgraph Node1["Node 1 (192.168.1.10)"]
        P1["Pod A\n10.244.1.2"]
        P2["Pod B\n10.244.1.3"]
        VE1["veth pair"]
        BR1["cni0 bridge\n10.244.1.1/24"]
        FL1["flannel.1 VTEP\nVXLAN encap"]
    end
    subgraph Node2["Node 2 (192.168.1.11)"]
        P3["Pod C\n10.244.2.2"]
        VE2["veth pair"]
        BR2["cni0 bridge\n10.244.2.1/24"]
        FL2["flannel.1 VTEP"]
    end

    P1 --> VE1 --> BR1 --> FL1
    P2 --> VE1
    FL1 -->|"VXLAN UDP 8472\nouter: 192.168.1.10->192.168.1.11\ninner: 10.244.1.2->10.244.2.2"| FL2
    FL2 --> BR2 --> VE2 --> P3
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant PA as Pod A (10.244.1.2)
    participant BR1 as Bridge (Node 1)
    participant VTEP1 as VTEP (Node 1)
    participant VTEP2 as VTEP (Node 2)
    participant BR2 as Bridge (Node 2)
    participant PC as Pod C (10.244.2.2)

    PA->>BR1: IP packet: src=10.244.1.2, dst=10.244.2.2
    BR1->>BR1: No local route for 10.244.2.x -> default gw
    BR1->>VTEP1: Forward to flannel.1
    VTEP1->>VTEP1: Lookup: 10.244.2.0/24 -> Node2 (192.168.1.11)
    VTEP1->>VTEP2: VXLAN: outer src=192.168.1.10, dst=192.168.1.11\ninner: original IP packet
    VTEP2->>VTEP2: Decapsulate VXLAN
    VTEP2->>BR2: Inner packet to 10.244.2.2
    BR2->>PC: Deliver to Pod C
```

## Design

### CNI Plugins

```
Flannel (simple, VXLAN overlay):
  - Assigns /24 subnet per node from larger /16
  - VXLAN tunnels between nodes (UDP port 8472)
  - Overhead: 50 bytes per packet (VXLAN header)
  - No network policy support (use with Calico NetworkPolicy)

Calico (BGP, no overlay):
  - Native IP routing via BGP between nodes
  - No encapsulation overhead (pure IP routing)
  - Full NetworkPolicy support
  - eBPF dataplane option for high performance

Cilium (eBPF):
  - Replaces kube-proxy entirely with eBPF
  - Kernel-level packet processing (no iptables)
  - Native NetworkPolicy + L7 (HTTP, gRPC) policies
  - Hubble for network observability
  - 10-30% lower latency than iptables

Weave:
  - Fast datapath + encrypted overlay
  - No configuration needed (auto-peer discovery)
  - Multicast via UDP broadcast for discovery
```

### Pod IP Assignment

```
IPAM (IP Address Management):
  Cluster CIDR: 10.244.0.0/16 (65534 pod IPs)
  Per-node: /24 subnet = 254 pods per node
  
  Node 1: 10.244.1.0/24 (10.244.1.1 - 10.244.1.254)
  Node 2: 10.244.2.0/24
  ...
  Node 255: 10.244.255.0/24

Pod lifecycle:
  1. kubelet calls CNI plugin (ADD)
  2. CNI creates veth pair: one end in pod ns, one in host ns
  3. CNI assigns IP from node subnet
  4. CNI adds routes in both namespaces
  5. Pod gets IP, default gateway

  On pod delete:
  1. kubelet calls CNI (DEL)
  2. veth pair removed, IP returned to pool
```

### Network Policy

```
Default: All pods can communicate with all pods (flat network)

NetworkPolicy example:
  spec:
    podSelector: {matchLabels: {app: backend}}
    policyTypes: [Ingress, Egress]
    ingress:
      - from:
        - podSelector: {matchLabels: {app: frontend}}
        ports: [{port: 8080}]
    egress:
      - to:
        - podSelector: {matchLabels: {app: postgres}}
        ports: [{port: 5432}]

Implementation: CNI plugin programs iptables/eBPF rules
  - Calico: iptables chains per policy
  - Cilium: eBPF maps for O(1) policy evaluation
```

## Common Questions & Answers

**Q: How does a pod on Node 1 reach a pod on Node 2?** A: VXLAN overlay: original packet (10.244.1.2 -> 10.244.2.2) wrapped in UDP with outer IPs (192.168.1.10 -> 192.168.1.11). Destination node decapsulates and delivers to pod.

**Q: What is a veth pair?** A: Virtual Ethernet pair: two virtual NICs connected back-to-back. One end in container's network namespace (eth0), other end in host namespace (vethXXXX). Packets entering one end emerge from the other.

**Q: Why does Calico outperform Flannel?** A: Calico uses BGP for direct IP routing (no tunnel overhead). Each node acts as a BGP router, advertising its pod subnet. No VXLAN encapsulation = 50 bytes less overhead per packet.

**Q: What is the Container Network Interface (CNI)?** A: Standard interface for network plugins. Kubernetes calls CNI binary with ADD/DEL/CHECK when pods are created/destroyed. Plugin handles IP assignment, routing, and interface creation.

**Q: How does NetworkPolicy scale?** A: iptables: O(n) rules evaluated linearly. At 10K pods with 100 policies each: 1M iptables rules. Cilium eBPF: O(1) hash map lookup. Critical for large clusters.

## Back-of-Envelope Calculations

```
VXLAN overhead:
  Original packet: 1460 bytes (TCP MSS)
  VXLAN header: 8B + UDP: 8B + outer IP: 20B + outer Ethernet: 14B = 50B overhead
  Effective MTU: 1500 - 50 = 1450B (jumbo frames recommended)
  Overhead: 50/1460 = 3.4% bandwidth overhead

Pod density per node:
  Node subnet: /24 = 254 usable IPs
  Max 254 pods per node (default AWS EKS: 110)
  AWS VPC CNI: limited by instance type ENIs

CNI plugin add latency:
  IPAM + veth creation: ~5-10ms per pod start
  Negligible vs. image pull time (~10-30s)

Network policy at scale:
  iptables: 10K policies = 10K rules, ~5ms per packet evaluation
  Cilium eBPF: 10K policies = O(1) hash lookup, ~10 microseconds
  At 100K req/s: iptables adds 500ms/sec CPU, eBPF adds 1ms/sec CPU
```

## Design Choices

| CNI | Overhead | NetworkPolicy | Complexity | Use Case |
|---|---|---|---|---|
| Flannel | VXLAN +50B | No | Low | Simple dev/test |
| Calico (BGP) | None | Yes | Medium | Production, bare metal |
| Calico (IPIP) | +20B | Yes | Medium | Cloud (no BGP) |
| Cilium | None (eBPF) | L3-L7 | High | Performance-critical |
| AWS VPC CNI | None | No (use Calico) | Low | EKS (native VPC IPs) |

## Follow-up Questions

1. How does AWS VPC CNI differ from overlay networking?
2. What is the Kubernetes multi-network proposal (Multus CNI)?
3. How does Cilium implement L7 network policies (HTTP method-level)?
4. How does service mesh (Istio) relate to CNI networking?
5. What is a NetworkPolicy default-deny baseline and why is it important?

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import ipaddress
import struct
import hashlib

@dataclass
class PodInterface:
    veth_host: str  # vethXXXX in host ns
    veth_pod: str   # eth0 in pod ns
    pod_ip: str
    gateway: str
    mac: str

class IPAMPool:
    def __init__(self, cluster_cidr: str = "10.244.0.0/16"):
        self._network = ipaddress.IPv4Network(cluster_cidr)
        self._subnets = list(self._network.subnets(prefixlen_diff=8))  # /24 per node
        self._node_subnets: Dict[str, ipaddress.IPv4Network] = {}
        self._allocated: Dict[str, set] = {}

    def assign_node_subnet(self, node_name: str) -> ipaddress.IPv4Network:
        idx = len(self._node_subnets)
        subnet = self._subnets[idx]
        self._node_subnets[node_name] = subnet
        self._allocated[node_name] = set()
        print(f"[IPAM] Node {node_name} assigned {subnet}")
        return subnet

    def allocate_pod_ip(self, node_name: str) -> Optional[str]:
        subnet = self._node_subnets.get(node_name)
        if not subnet:
            return None
        hosts = list(subnet.hosts())
        hosts = hosts[1:]  # Skip gateway (.1)
        for ip in hosts:
            ip_str = str(ip)
            if ip_str not in self._allocated[node_name]:
                self._allocated[node_name].add(ip_str)
                return ip_str
        return None  # Exhausted

    def release_pod_ip(self, node_name: str, ip: str):
        self._allocated[node_name].discard(ip)

    def gateway_for_node(self, node_name: str) -> str:
        subnet = self._node_subnets[node_name]
        return str(list(subnet.hosts())[0])  # .1 address

class VXLANNetwork:
    def __init__(self):
        self._node_vtep: Dict[str, str] = {}  # node -> physical IP
        self._subnet_to_node: Dict[str, str] = {}

    def register_node(self, node_name: str, node_ip: str, pod_subnet: str):
        self._node_vtep[node_name] = node_ip
        self._subnet_to_node[pod_subnet] = node_name
        print(f"[VXLAN] Registered {node_name}: {node_ip}, pod subnet: {pod_subnet}")

    def route_pod_to_pod(self, src_pod_ip: str, dst_pod_ip: str) -> dict:
        # Find which node hosts the dst pod
        dst_subnet = ".".join(dst_pod_ip.split(".")[:3]) + ".0/24"
        dst_node = self._subnet_to_node.get(dst_subnet)
        if not dst_node:
            return {"error": f"No route to {dst_pod_ip}"}
        dst_vtep = self._node_vtep[dst_node]
        return {
            "inner_src": src_pod_ip,
            "inner_dst": dst_pod_ip,
            "outer_src": "auto",  # source node's IP
            "outer_dst": dst_vtep,
            "protocol": "VXLAN",
            "vni": 1,
            "udp_port": 8472,
        }

class NetworkPolicyEngine:
    def __init__(self):
        self._policies: List[dict] = []

    def add_policy(self, namespace: str, pod_selector: Dict[str, str],
                   ingress_from: List[Dict], egress_to: List[Dict]):
        self._policies.append({
            "namespace": namespace,
            "pod_selector": pod_selector,
            "ingress": ingress_from,
            "egress": egress_to,
        })

    def _labels_match(self, pod_labels: Dict, selector: Dict) -> bool:
        return all(pod_labels.get(k) == v for k, v in selector.items())

    def is_allowed(self, src_pod_labels: Dict, dst_pod_labels: Dict,
                   dst_port: int, namespace: str) -> bool:
        applicable = [p for p in self._policies
                      if p["namespace"] == namespace
                      and self._labels_match(dst_pod_labels, p["pod_selector"])]
        if not applicable:
            return True  # No policy = allow all
        for policy in applicable:
            for rule in policy["ingress"]:
                from_sel = rule.get("from_selector", {})
                ports = rule.get("ports", [])
                if self._labels_match(src_pod_labels, from_sel):
                    if not ports or dst_port in ports:
                        return True
        return False

# Usage
ipam = IPAMPool("10.244.0.0/16")
vxlan = VXLANNetwork()

for node, ip in [("node-1", "192.168.1.10"), ("node-2", "192.168.1.11")]:
    subnet = ipam.assign_node_subnet(node)
    vxlan.register_node(node, ip, str(subnet))

pod1_ip = ipam.allocate_pod_ip("node-1")
pod2_ip = ipam.allocate_pod_ip("node-2")
print(f"\nPod IPs: node-1={pod1_ip}, node-2={pod2_ip}")

route = vxlan.route_pod_to_pod(pod1_ip, pod2_ip)
print(f"VXLAN route: {route}")

# Network policy
policy_engine = NetworkPolicyEngine()
policy_engine.add_policy(
    namespace="prod",
    pod_selector={"app": "backend"},
    ingress_from=[{"from_selector": {"app": "frontend"}, "ports": [8080]}],
    egress_to=[{"to_selector": {"app": "postgres"}, "ports": [5432]}]
)
print(f"\nFrontend -> Backend:8080 allowed: {policy_engine.is_allowed({'app':'frontend'}, {'app':'backend'}, 8080, 'prod')}")
print(f"Unknown -> Backend:8080 allowed: {policy_engine.is_allowed({'app':'unknown'}, {'app':'backend'}, 8080, 'prod')}")
```

## Java Implementation

```java
import java.util.*;
import java.util.stream.*;

public class ContainerNetworking {
    static class IPAMPool {
        private int nextNode = 1;
        private Map<String, Integer> nodeSubnets = new HashMap<>();
        private Map<String, Set<Integer>> allocated = new HashMap<>();

        String assignNodeSubnet(String node) {
            nodeSubnets.put(node, nextNode++);
            allocated.put(node, new HashSet<>());
            return "10.244." + nodeSubnets.get(node) + ".0/24";
        }

        String allocatePodIp(String node) {
            Set<Integer> used = allocated.get(node);
            for (int i = 2; i < 255; i++) {
                if (!used.contains(i)) {
                    used.add(i);
                    return "10.244." + nodeSubnets.get(node) + "." + i;
                }
            }
            return null;
        }
    }

    record VXLANPacket(String innerSrc, String innerDst, String outerDst) {}

    static VXLANPacket buildVXLAN(String srcPodIp, String dstPodIp, String dstNodeIp) {
        return new VXLANPacket(srcPodIp, dstPodIp, dstNodeIp);
    }

    public static void main(String[] args) {
        IPAMPool ipam = new IPAMPool();
        System.out.println(ipam.assignNodeSubnet("node-1"));
        System.out.println(ipam.assignNodeSubnet("node-2"));
        String pod1 = ipam.allocatePodIp("node-1");
        String pod2 = ipam.allocatePodIp("node-2");
        System.out.printf("Pod IPs: %s, %s%n", pod1, pod2);
        VXLANPacket pkt = buildVXLAN(pod1, pod2, "192.168.1.11");
        System.out.printf("VXLAN: %s -> %s via %s%n", pkt.innerSrc(), pkt.innerDst(), pkt.outerDst());
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Pod IP allocation | O(1) amortized |
| VXLAN encap/decap | O(1) |
| NetworkPolicy evaluation (iptables) | O(rules) |
| NetworkPolicy evaluation (Cilium eBPF) | O(1) |
| FDB lookup for VXLAN | O(1) hash table |
