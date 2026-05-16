# BGP (Border Gateway Protocol)

## Overview
BGP is the routing protocol used between autonomous systems (AS) on the internet. It determines optimal paths for data routing across different networks.

## Key Concepts

### AS (Autonomous System)
- Independent network with own routing policies
- Assigned unique AS number (ASN)
- Companies, ISPs operate their own AS

### BGP Sessions
- **eBGP:** Between different AS (external BGP)
- **iBGP:** Within same AS (internal BGP)
- Built on TCP port 179

### Path Selection
- Prefix-based routing
- Considers multiple attributes:
  - AS path length
  - Local preference
  - MED (Multi-Exit Discriminator)
  - Weight

## Interview Considerations

**Pros:**
- Internet-scale routing
- Flexible policy control
- Supports multi-homing
- Gradual convergence

**Cons:**
- Complex configuration
- Slow convergence (minutes)
- Potential for route hijacking
- Resource intensive

## Real-World Use

- Internet backbone routing
- ISP interconnection
- Multi-cloud deployments
- Global traffic management

## Related Concepts
- OSPF, IPv4/IPv6, Anycast Routing
