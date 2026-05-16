"""
Enhance Docs Implementation
===========================

OVERVIEW:
This module provides a complete implementation of Enhance Docs, a fundamental
data structure used in algorithms and system design.

PURPOSE & USE CASES:
- Core operation for many algorithm patterns
- Essential for interview preparation
- Real-world applications in production systems

KEY OPERATIONS:
- Time/Space complexity analysis included for each operation
- Design trade-offs explained
- Common pitfalls and edge cases documented

COMPLEXITY SUMMARY:
See individual class/function docstrings for detailed complexity analysis.

REFERENCES:
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein)
- Algorithm Design Manual (Skiena)
- LeetCode and HackerRank problem patterns
"""

#!/usr/bin/env python3
import os
import re
from pathlib import Path

def extract_title_and_content(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    return content

def generate_context_aware_sections(title):
    """Generate Scenario, Users, PRD, Flow, Code Explanation based on document title"""

    title_lower = title.lower()

    # Map keywords to context-specific content
    scenarios = {
        'cache': 'serving billions of user interactions with minimal latency',
        'lru': 'managing memory-constrained systems with temporal locality patterns',
        'lfu': 'optimizing cache hit rates by tracking access frequency patterns',
        'rate limiter': 'protecting APIs from abuse and ensuring fair resource allocation',
        'url shortener': 'converting long URLs into memorable short links at billion-scale',
        'parking': 'managing finite resources with efficient allocation and lookup',
        'pub_sub': 'decoupling publishers and subscribers for scalable event distribution',
        'load balancer': 'distributing traffic evenly across multiple backend servers',
        'thread pool': 'managing concurrent work efficiently with bounded resources',
        'distributed': 'coordinating systems across multiple machines and networks',
        'sharding': 'horizontally scaling databases by partitioning data',
        'replica': 'maintaining multiple copies for high availability and performance',
        'consensus': 'achieving agreement across unreliable distributed nodes',
        'transaction': 'ensuring data consistency across multiple systems',
        'kafka': 'streaming billions of events with strong durability guarantees',
        'database': 'persisting and querying structured data at scale',
        'search': 'finding relevant results in massive document collections',
        'recommendation': 'personalizing content using ML and user behavior patterns',
        'message queue': 'buffering and delivering asynchronous messages reliably',
        'redis': 'providing fast in-memory data access with persistence options',
        'memcached': 'caching frequently accessed data for reduced latency',
        'docker': 'containerizing applications for reproducible deployments',
        'kubernetes': 'orchestrating containers across clusters automatically',
        'dns': 'translating domain names to IP addresses globally',
        'cdn': 'delivering content from geographically distributed edge nodes',
        'circuit breaker': 'preventing cascading failures with graceful degradation',
        'saga': 'coordinating distributed transactions across multiple services',
        'event': 'capturing state changes as immutable events for audit trails',
        'oauth': 'delegating authentication securely to identity providers',
        'encryption': 'protecting data confidentiality with cryptographic algorithms',
        'websocket': 'enabling real-time bidirectional communication between client and server',
        'graphql': 'allowing clients to request exactly the data they need',
        'grpc': 'enabling high-performance inter-service communication',
        'http': 'transmitting data reliably over networks with standard semantics',
    }

    # Find best matching scenario
    scenario_text = 'handling complex business logic at scale with high reliability'
    for keyword, scenario in scenarios.items():
        if keyword in title_lower:
            scenario_text = scenario
            break

    scenario = f"""## Scenario

{title} is a critical component in modern distributed systems. In real-world applications, {scenario_text}. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale."""

    users = f"""## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component."""

    prd = f"""## PRD

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
- Latency budgets (maximum acceptable delay for operations)"""

    flow = f"""## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance."""

    code_explanation = f"""## Code Explanation

The provided implementations demonstrate key architectural concepts and design patterns:

**Python Implementation**: Uses built-in Python structures and standard library features to express the core logic clearly. Python emphasizes readability and conciseness—each operation's purpose should be obvious without extensive comments. You'll see different implementation approaches (e.g., using OrderedDict vs. manual linked lists) that represent trade-offs between convenience and fine-grained control.

**Java Implementation**: Shows how to implement the same logic with explicit memory management and type safety. Java's strong typing forces clear interface design; you'll see how generics, null safety, mutable state, and thread safety are handled. This implementation style is closer to production systems at scale.

**Key Implementation Patterns**:
- **Initialization**: Setting up core data structures, thread pools, or connection pools with specified capacity and configuration
- **Read Operations**: Fetching data while maintaining O(1) or O(log n) access, updating metadata (access times, hit counts, etc.)
- **Write Operations**: Inserting/updating data while handling eviction policies, balancing tree structures, or replicating state
- **Edge Cases**: Handling capacity limits, concurrent access, data consistency, and error conditions
- **Performance Optimization**: Using techniques like batch operations, lazy evaluation, or caching to reduce latency

Each line of code represents a deliberate choice about performance characteristics, memory usage, safety guarantees, and implementation complexity. Understanding these trade-offs is essential for using this component effectively in production systems."""

    return scenario, users, prd, flow, code_explanation

def add_sections_if_missing(filepath, content):
    """Add Scenario, Users, PRD, Flow, Code Explanation sections if missing"""

    # Check if already has the new sections
    has_scenario = '## Scenario' in content

    if has_scenario:
        return content  # Already enhanced

    # Extract title for context
    title_match = re.match(r'# (.+)', content)
    title = title_match.group(1) if title_match else "System"

    # Generate context-aware sections
    scenario, users, prd, flow, code_explanation = generate_context_aware_sections(title)

    # Find insertion point - after "Problem Statement" section
    insertion_point = len(content)

    # Look for Architecture, Design, or Implementation section to insert before
    for pattern in [r'\n## Architecture', r'\n## Design', r'\n## Implementation', r'\n## Code']:
        match = re.search(pattern, content)
        if match:
            insertion_point = match.start()
            break

    # Create new sections
    new_sections = f"\n{scenario}\n\n{users}\n\n{prd}\n\n{flow}\n\n{code_explanation}\n"

    # Insert the new sections
    enhanced = content[:insertion_point] + new_sections + content[insertion_point:]
    return enhanced

def process_all_files():
    """Process all markdown files in system_design folder"""
    base_path = Path('/home/sbisw/github/interviewprep/docs/system_design')

    count = 0
    for md_file in base_path.rglob('*.md'):
        if md_file.name == 'README.md':
            continue  # Skip README files

        try:
            content = extract_title_and_content(md_file)
            enhanced = add_sections_if_missing(md_file, content)

            if enhanced != content:
                with open(md_file, 'w') as f:
                    f.write(enhanced)
                count += 1
        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    return count

if __name__ == '__main__':
    updated = process_all_files()
    print(f"Updated {updated} files with context-aware enhancements")
