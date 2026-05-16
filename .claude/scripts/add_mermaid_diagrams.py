#!/usr/bin/env python3
"""
Script to add comprehensive Mermaid diagrams to all 36 real-world system design files.
Adds: architecture, data flow, failover, and scaling diagrams.
"""

import re
from pathlib import Path

# System-specific diagram configurations
system_diagrams = {
    "Facebook Social Network": {
        "arch_title": "Facebook Architecture",
        "key_components": ["API Gateway", "Service Tier", "Cache (Redis)", "Primary DB", "Read Replicas", "Kafka Queue", "Elasticsearch", "Data Lake"],
        "data_path": "User Request → API Gateway → Load Balancer → Service → Cache/DB",
    },
    "WhatsApp Messaging": {
        "arch_title": "WhatsApp Architecture",
        "key_components": ["Mobile Client", "API Gateway", "Message Service", "Cache (Redis)", "Message Queue", "Primary DB", "Replicas", "Notification Service"],
        "data_path": "Message → API → Queue → Storage → Delivery",
    },
    "Slack Team Communication": {
        "arch_title": "Slack Architecture",
        "key_components": ["Web/Desktop Client", "API Gateway", "Message Service", "Cache", "Primary DB", "Search Index", "Analytics", "Webhooks"],
        "data_path": "Message → Service → Queue → Search Index & Storage",
    },
    "Twitter Feed": {
        "arch_title": "Twitter Architecture",
        "key_components": ["Web/Mobile", "API Gateway", "Timeline Service", "Cache (Redis)", "Primary DB", "Tweet Cache", "Search", "Analytics"],
        "data_path": "Tweet → Service → Cache → Followers → Timeline",
    },
    "Discord Gaming Chat": {
        "arch_title": "Discord Architecture",
        "key_components": ["Client (Web/Mobile)", "Gateway", "Voice/Video Service", "Message Service", "Cache", "Primary DB", "Analytics", "CDN"],
        "data_path": "User Event → Gateway → Service → Cache/DB → Broadcast",
    },
    "Telegram Secure Messaging": {
        "arch_title": "Telegram Architecture",
        "key_components": ["Client App", "API Gateway", "Encryption Service", "Message Queue", "Storage", "Cache", "Analytics", "Notification"],
        "data_path": "Message → Encrypt → Queue → Storage → Delivery",
    },
    "YouTube Video Platform": {
        "arch_title": "YouTube Architecture",
        "key_components": ["Client Browser", "API Gateway", "Video Service", "Transcoding", "CDN", "Search Index", "Analytics", "Cache"],
        "data_path": "Upload → Transcode → CDN → Delivery to Billions",
    },
    "Twitch Live Streaming": {
        "arch_title": "Twitch Architecture",
        "key_components": ["Broadcaster", "Ingest Server", "Cache", "HLS/RTMP", "CDN", "Message Service", "Analytics", "Recommendation"],
        "data_path": "Stream → Ingest → Cache → CDN → Viewers",
    },
    "TikTok Short Video": {
        "arch_title": "TikTok Architecture",
        "key_components": ["Mobile App", "API Gateway", "Upload Service", "ML Pipeline", "Video Cache", "Feed Service", "Search", "Analytics"],
        "data_path": "Video → ML Ranking → Feed → Billions of Users",
    },
    "Spotify Music Streaming": {
        "arch_title": "Spotify Architecture",
        "key_components": ["Mobile/Desktop", "API Gateway", "Stream Service", "Playlist Service", "Cache", "Primary DB", "CDN", "Analytics"],
        "data_path": "Play Request → Service → CDN Audio → User Device",
    },
    "Disney Video Streaming": {
        "arch_title": "Disney+ Architecture",
        "key_components": ["Streaming Client", "API Gateway", "DRM Service", "Video Service", "CDN", "Cache", "Analytics", "Subscription"],
        "data_path": "Auth → DRM → CDN → Adaptive Bitrate Stream",
    },
    "Dropbox File Sync": {
        "arch_title": "Dropbox Architecture",
        "key_components": ["Desktop App", "API Gateway", "Sync Service", "Block Storage", "Cache", "Primary DB", "Search Index", "Analytics"],
        "data_path": "File Change → Sync Service → Block Store → All Devices",
    },
    "Amazon E-Commerce": {
        "arch_title": "Amazon Architecture",
        "key_components": ["Web/Mobile", "API Gateway", "Product Service", "Inventory", "Cart Service", "Order Service", "Search", "Recommendation"],
        "data_path": "Browse → Search → Cart → Order → Inventory",
    },
    "eBay Auction System": {
        "arch_title": "eBay Architecture",
        "key_components": ["Web/Mobile", "API Gateway", "Auction Service", "Bid Service", "Payment", "Inventory", "Search", "Analytics"],
        "data_path": "Listing → Bid → Settlement → Fulfillment",
    },
    "Shopify Store Platform": {
        "arch_title": "Shopify Architecture",
        "key_components": ["Merchant Admin", "Storefront", "API Gateway", "Product Service", "Order Service", "Payment", "Analytics", "Fulfillment"],
        "data_path": "Merchant Setup → Storefront → Order → Fulfillment",
    },
    "Payment Processing": {
        "arch_title": "Payment Architecture",
        "key_components": ["Payment Gateway", "Validator", "Processor", "Ledger", "Settlement", "Fraud Detection", "Compliance", "Analytics"],
        "data_path": "Payment → Validation → Processing → Settlement",
    },
    "Stripe Payment Api": {
        "arch_title": "Stripe Architecture",
        "key_components": ["Client API", "Payment Gateway", "Processor Network", "Ledger", "Settlement", "Fraud Detection", "Reporting", "Cache"],
        "data_path": "Charge Request → Processor → Ledger → Settlement",
    },
    "Robinhood Trading": {
        "arch_title": "Robinhood Architecture",
        "key_components": ["Mobile App", "API Gateway", "Order Service", "Matching Engine", "Ledger", "Settlement", "Compliance", "Analytics"],
        "data_path": "Order → Matching → Ledger → Settlement",
    },
    "Square Pos": {
        "arch_title": "Square Architecture",
        "key_components": ["POS Device", "API Gateway", "Transaction Service", "Settlement", "Reporting", "Inventory", "Analytics", "Offline Mode"],
        "data_path": "Transaction → Processing → Settlement → Dashboard",
    },
    "Paypal Digital Wallet": {
        "arch_title": "PayPal Architecture",
        "key_components": ["Web/Mobile", "API Gateway", "Wallet Service", "Payment Processor", "Ledger", "Risk/Compliance", "Settlement", "Analytics"],
        "data_path": "User Login → Wallet → Payment → Settlement",
    },
    "Google Search": {
        "arch_title": "Google Search Architecture",
        "key_components": ["Search Client", "Frontend", "Query Parser", "Index Shards", "Ranker", "Result Cache", "Analytics", "Spam Filter"],
        "data_path": "Query → Parser → Index Search → Ranking → Results",
    },
    "Elastic Search": {
        "arch_title": "Elasticsearch Architecture",
        "key_components": ["Client Library", "Coordinating Node", "Data Nodes", "Index Shards", "Replica Shards", "Search Query", "Aggregation", "Analytics"],
        "data_path": "Document → Index → Shard → Query Execution",
    },
    "Databricks Analytics": {
        "arch_title": "Databricks Architecture",
        "key_components": ["Data Source", "Spark Cluster", "Distributed Processing", "Delta Lake", "ML Lib", "SQL Engine", "Dashboard", "API"],
        "data_path": "Data Ingestion → Spark Processing → Delta Lake → Analysis",
    },
    "Notion Workspace": {
        "arch_title": "Notion Architecture",
        "key_components": ["Web/Mobile App", "API Gateway", "CRDT Service", "Block Store", "Index", "Permission Service", "Search", "Sync"],
        "data_path": "Edit → CRDT Sync → Block Store → All Clients",
    },
    "Figma Design Tool": {
        "arch_title": "Figma Architecture",
        "key_components": ["Browser Client", "WebSocket Server", "Rendering Engine", "Document Store", "Collaboration Service", "Export Service", "Analytics"],
        "data_path": "Design Event → Collab Service → All Editors → Render",
    },
    "Confluence Wiki": {
        "arch_title": "Confluence Architecture",
        "key_components": ["Web Client", "API Gateway", "Page Service", "Permission Service", "Search Index", "Attachment Storage", "Versioning", "Analytics"],
        "data_path": "Page Edit → Storage → Index → All Spaces",
    },
    "Doordash Food Delivery": {
        "arch_title": "DoorDash Architecture",
        "key_components": ["Consumer App", "Restaurant App", "Dasher App", "Matching Service", "Order Service", "Payment", "Analytics", "Notification"],
        "data_path": "Order → Matching → Dasher → Delivery → Payment",
    },
    "Booking Travel Marketplace": {
        "arch_title": "Booking Architecture",
        "key_components": ["Search Client", "Search Service", "Inventory", "Pricing Engine", "Booking Service", "Payment", "Verification", "Analytics"],
        "data_path": "Search → Filter → Availability → Booking → Payment",
    },
    "Multiplayer Game Backend": {
        "arch_title": "Game Backend Architecture",
        "key_components": ["Game Client", "Connection Service", "World Service", "State Manager", "Persistence", "Matchmaking", "Analytics", "Chat"],
        "data_path": "Player Event → World Service → State Update → All Players",
    },
}

def generate_architecture_diagram(system_name, config):
    """Generate architecture diagram in Mermaid format."""
    return """### System Architecture

```mermaid
graph TB
    Client["Client/User"]
    Gateway["API Gateway<br/>Rate Limit, Auth"]
    LB["Load Balancer"]
    Service["Service Tier<br/>Business Logic"]
    Cache["Cache Layer<br/>Redis/Memcached"]
    Primary["Primary DB<br/>ACID Guarantees"]
    Replica["Read Replica<br/>Async Sync"]
    Queue["Message Queue<br/>Kafka/RabbitMQ"]
    Workers["Async Workers<br/>Background Jobs"]
    Index["Search Index<br/>Elasticsearch"]
    Lake["Data Lake<br/>S3/HDFS"]
    Analytics["Analytics Pipeline<br/>Spark/Presto"]

    Client -->|Request| Gateway
    Gateway -->|Route| LB
    LB -->|Distribute| Service
    Service -->|Check Cache| Cache
    Service -->|Query| Replica
    Service -->|Write| Primary
    Primary -->|Replicate| Replica
    Service -->|Publish Event| Queue
    Queue -->|Consume| Workers
    Workers -->|Index| Index
    Workers -->|Archive| Lake
    Lake -->|Process| Analytics
    Cache -->|Return| Service
    Index -->|Search Results| Service
    Service -->|Response| Gateway
    Gateway -->|Return| Client

    style Gateway fill:#ff9999
    style LB fill:#ff9999
    style Service fill:#99ccff
    style Cache fill:#99ff99
    style Primary fill:#ffcc99
    style Replica fill:#ffcc99
    style Queue fill:#cc99ff
    style Workers fill:#cc99ff
    style Index fill:#ffff99
    style Lake fill:#99ffff
    style Analytics fill:#99ffff
```"""

def generate_data_flow_diagram(system_name):
    """Generate data flow diagram."""
    return """### Data Flow: Read vs Write

```mermaid
graph LR
    subgraph Read["Read Operation (Fast Path)"]
        R1["Request"] --> R2{"Cache Hit?"}
        R2 -->|Yes| R3["Return from Cache<br/>P99 < 10ms"]
        R2 -->|No| R4["Query Replica<br/>P99 < 50ms"]
        R4 --> R5["Update Cache"]
        R5 --> R3
    end

    subgraph Write["Write Operation (Consistency Path)"]
        W1["Request"] --> W2["Validate & Auth"]
        W2 --> W3["Write to Primary<br/>Sync Durability"]
        W3 --> W4["Update Cache<br/>Write-Through"]
        W4 --> W5["Publish Event"]
        W5 --> W6["Acknowledge Client"]
        W5 --> W7["Async Workers<br/>Background Processing"]
    end

    style Read fill:#e1f5e1
    style Write fill:#fff4e1
    style R3 fill:#90EE90
    style W6 fill:#FFD700
```"""

def generate_failover_diagram():
    """Generate failover and recovery diagram."""
    return """### Failover & Recovery Flow

```mermaid
graph TD
    Normal["System Operating Normally"]
    Detect["Detect Primary Failure<br/>3 failed checks = 30-60s"]
    Promote["Promote Read Replica<br/>to Primary<br/>10-20s"]
    DNS["Update DNS<br/>Propagate<br/>30s-5min"]
    Recovery["System Recovers<br/>RTO &lt; 2 minutes"]
    Verify["Verify Data<br/>Consistency"]
    Monitor["Monitor Catchup<br/>Apply WAL"]
    Restore["Restore from Backup<br/>Point-in-time Recovery<br/>RTO &lt; 30min"]

    Normal -->|Health Check Fails| Detect
    Detect --> Promote
    Promote --> DNS
    DNS --> Recovery
    Recovery --> Verify
    Verify --> Monitor
    Monitor --> Normal
    Normal -->|Data Corruption| Restore
    Restore --> Verify

    style Normal fill:#90EE90
    style Detect fill:#FFB6C1
    style Promote fill:#FF69B4
    style DNS fill:#FF69B4
    style Recovery fill:#FFD700
    style Verify fill:#87CEEB
    style Monitor fill:#87CEEB
    style Restore fill:#FF69B4
```"""

def generate_scaling_diagram():
    """Generate scaling strategies diagram."""
    return """### Scaling Strategies

```mermaid
graph TD
    Load["Increasing Load"]
    CS1["Add Redis Nodes"]
    CS2["Consistent Hashing"]
    CS3["Replicate Hot Keys"]
    SS1["Horizontal Scaling"]
    SS2["Stateless Instances"]
    SS3["Auto-scaling Groups"]
    DS1["Read Replicas"]
    DS2["Sharding by User ID"]
    DS3["Split Hot Shards"]
    ES1["Index Sharding"]
    ES2["Multiple Nodes"]
    ES3["Tiered Indexes"]
    Scale["System Scales<br/>10x Capacity"]

    Load -->|Cache Tier| CS1
    CS1 --> CS2
    CS2 --> CS3
    Load -->|Service Tier| SS1
    SS1 --> SS2
    SS2 --> SS3
    Load -->|Database Tier| DS1
    DS1 --> DS2
    DS2 --> DS3
    Load -->|Search Tier| ES1
    ES1 --> ES2
    ES2 --> ES3
    CS3 --> Scale
    SS3 --> Scale
    DS3 --> Scale
    ES3 --> Scale

    style Load fill:#FFB6C1
    style Scale fill:#90EE90
    style CS3 fill:#87CEEB
    style SS3 fill:#87CEEB
    style DS3 fill:#87CEEB
    style ES3 fill:#87CEEB
```"""

def generate_consistency_diagram():
    """Generate data consistency diagram."""
    return """### Data Consistency Patterns

```mermaid
graph TB
    Write["Write to Primary Database<br/>Sync Durability Guarantee"]
    Choice{"Consistency<br/>Level Needed?"}
    Strong["Synchronous Replication<br/>Wait for all replicas<br/>Higher latency, higher reliability"]
    Eventual["Asynchronous Replication<br/>Don't wait for replicas<br/>Low latency, temporary inconsistency"]
    Causal["Track causal dependencies<br/>Causally related ops ordered<br/>Balance latency and consistency"]
    Replicate["Replicate to All Nodes<br/>Confirm before ACK"]
    ReplicateA["Replicate to All Nodes<br/>ACK immediately"]
    ReplicateC["Replicate with Version Info<br/>Maintain causal order"]
    Data["All replicas<br/>have latest data<br/>RPO = 0"]
    DataA["Replicas lag<br/>behind primary<br/>RPO = seconds"]
    DataC["Causally dependent<br/>operations ordered<br/>RPO = seconds"]

    Write --> Choice
    Choice -->|Strong| Strong
    Choice -->|Eventual| Eventual
    Choice -->|Causal| Causal
    Strong --> Replicate
    Eventual --> ReplicateA
    Causal --> ReplicateC
    Replicate --> Data
    ReplicateA --> DataA
    ReplicateC --> DataC

    style Write fill:#FFD700
    style Choice fill:#FFA500
    style Strong fill:#FF6B6B
    style Eventual fill:#4ECDC4
    style Causal fill:#95E1D3
```"""

def add_diagrams_to_file(filepath, system_name):
    """Add Mermaid diagrams to system design file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if diagrams already added
    if "```mermaid" in content:
        return False

    # Find insertion point (before "Capacity Planning" section)
    insertion_point = content.find("## Capacity Planning")

    if insertion_point == -1:
        insertion_point = content.find("## Lessons Learned")

    if insertion_point == -1:
        return False

    # Generate diagrams
    arch_diagram = generate_architecture_diagram(system_name, system_diagrams.get(system_name, {}))
    data_flow_diagram = generate_data_flow_diagram(system_name)
    failover_diagram = generate_failover_diagram()
    scaling_diagram = generate_scaling_diagram()
    consistency_diagram = generate_consistency_diagram()

    # Combine all diagrams
    diagrams_section = f"""
## Architecture & Flow Diagrams

{arch_diagram}

{data_flow_diagram}

{failover_diagram}

{scaling_diagram}

{consistency_diagram}

"""

    # Insert diagrams before "Capacity Planning"
    new_content = content[:insertion_point] + diagrams_section + "\n" + content[insertion_point:]

    with open(filepath, 'w') as f:
        f.write(new_content)

    return True

def main():
    """Process all system design files."""
    base_path = Path("docs/system_design/13-realworld-systems")

    if not base_path.exists():
        print(f"❌ Directory not found: {base_path}")
        return

    files = sorted(base_path.glob("*.md"))

    print(f"📊 Adding Mermaid diagrams to {len(files)} system design files...")
    print("=" * 60)

    success_count = 0
    for filepath in files:
        # Extract system name from filename
        filename = filepath.stem
        parts = filename.split('_', 1)[1]
        system_name = ' '.join(word.capitalize() for word in parts.split('_'))

        try:
            if add_diagrams_to_file(filepath, system_name):
                print(f"✅ Added diagrams: {system_name}")
                success_count += 1
            else:
                print(f"⏭️  Already has diagrams: {system_name}")
        except Exception as e:
            print(f"❌ Error in {system_name}: {e}")

    print("=" * 60)
    print(f"✨ Added diagrams to {success_count} system files!")

if __name__ == '__main__':
    main()
