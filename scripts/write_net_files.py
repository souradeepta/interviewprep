#!/usr/bin/env python3
import os, sys

BASE = "docs/system_design/16-networking"
os.makedirs(BASE, exist_ok=True)

# Read content from separate per-file content modules
import importlib.util

files = [
    "05_load_balancer_l4_l7.md",
    "06_reverse_proxy.md",
    "07_rest_graphql_grpc.md",
    "08_http2_http3_quic.md",
    "09_websockets_sse.md",
    "10_nat_ip_routing.md",
    "11_connection_pooling.md",
    "12_network_topology.md",
    "13_anycast_routing.md",
    "14_vpn_tunneling.md",
    "15_bandwidth_latency.md",
]

for f in files:
    path = os.path.join(BASE, f)
    if os.path.exists(path):
        print(f"  exists: {f}")
    else:
        print(f"  missing: {f}")
