#!/usr/bin/env python3
"""
Add comprehensive Mermaid diagrams to all system design concepts.
"""

import os
import glob
import re

base_path = "/home/sbisw/github/interviewprep/docs/system_design"

# Mermaid diagrams by concept type
mermaid_diagrams = {
    # Caching
    "lru_cache": {
        "architecture": """```mermaid
graph LR
    Client["Client Request"]
    Cache["LRU Cache<br/>Max Size: 1000"]
    DB["Database"]

    Client -->|Check Cache| Cache
    Cache -->|Hit| Client
    Cache -->|Miss| DB
    DB -->|Fetch Data| Cache
    Cache -->|Return & Evict LRU| Client
```""",
        "flow": """```mermaid
sequenceDiagram
    participant C as Client
    participant Cache as LRU Cache
    participant DB as Database

    C->>Cache: Get Key
    alt Hit
        Cache-->>C: Return Value
    else Miss
        Cache->>DB: Query
        DB-->>Cache: Return Data
        Cache->>Cache: Update position to head
        Cache->>Cache: Check if evict needed
        Cache-->>C: Return Value
    end
```"""
    },
    "lfu_cache": {
        "architecture": """```mermaid
graph TB
    Client["Client"]
    Cache["LFU Cache<br/>Tracks Frequency"]
    FreqMap["Frequency Map<br/>freq -> LRU List"]

    Client -->|Get/Put| Cache
    Cache -->|Update Freq| FreqMap
    FreqMap -->|Evict Min Freq| Cache
```""",
        "flow": """```mermaid
stateDiagram-v2
    [*] --> Request
    Request --> CacheCheck
    CacheCheck --> Hit: Found
    CacheCheck --> Miss: Not Found
    Hit --> UpdateFreq
    UpdateFreq --> Return
    Miss --> Fetch
    Fetch --> Cache
    Cache --> UpdateFreq
    Return --> [*]
```"""
    },

    # Rate Limiting
    "rate_limiter": {
        "architecture": """```mermaid
graph LR
    User["User Request"]
    Limiter["Token Bucket<br/>Capacity: C<br/>Rate: R"]
    Queue["Request Queue"]
    Service["Service"]

    User -->|Request| Limiter
    Limiter -->|Token Available| Service
    Limiter -->|Token Depleted| Queue
    Limiter -->|Refill Tokens| Limiter
    Queue -->|Wait| Limiter
    Service -->|Response| User
```""",
        "flow": """```mermaid
flowchart TD
    A["Request Arrives"] --> B["Get Current Tokens"]
    B --> C{"Tokens >= Cost?"}
    C -->|Yes| D["Deduct Tokens"]
    C -->|No| E["Queue Request"]
    D --> F["Process Request"]
    E --> G["Wait for Tokens"]
    G --> B
    F --> H["Return Response"]
```"""
    },

    # URL Shortener
    "url_shortener": {
        "architecture": """```mermaid
graph LR
    LongURL["Long URL Input"]
    Encoder["Base62 Encoder<br/>Snowflake ID Gen"]
    ShortURL["Short URL<br/>6-8 chars"]
    DB["Key-Value Store<br/>Short -> Long"]
    Cache["Redis Cache"]

    LongURL -->|Generate ID| Encoder
    Encoder -->|Create| ShortURL
    ShortURL -->|Store| DB
    ShortURL -->|Cache| Cache

    Client["Client"] -->|Redirect Request| Cache
    Cache -->|Hit| Redirect["302 Redirect"]
    Cache -->|Miss| DB
    DB -->|Return| Redirect
```""",
        "flow": """```mermaid
sequenceDiagram
    participant Client
    participant Service as URL Service
    participant Encoder as Snowflake Encoder
    participant DB as Database
    participant Cache as Redis

    Client->>Service: POST /shorten (long_url)
    Service->>Encoder: Generate ID
    Encoder-->>Service: short_id
    Service->>DB: Store mapping
    Service->>Cache: Cache mapping
    Service-->>Client: short_url

    Client->>Service: GET /redirect/short_id
    Service->>Cache: Check
    alt Cache Hit
        Cache-->>Service: long_url
    else Cache Miss
        Service->>DB: Fetch
        DB-->>Service: long_url
        Service->>Cache: Update cache
    end
    Service-->>Client: 302 + long_url
```"""
    },

    # Parking Lot
    "parking_lot": {
        "architecture": """```mermaid
graph TB
    ParkingLot["Parking Lot System"]

    ParkingLot --> Entrance["Entrance Gate"]
    ParkingLot --> Levels["Multiple Levels"]
    ParkingLot --> Spots["Parking Spots<br/>S, M, L, XL"]
    ParkingLot --> Display["Available Spots Display"]
    ParkingLot --> Exit["Exit Gate"]

    Entrance --> TicketMachine["Ticket Machine"]
    TicketMachine --> SpotFinder["Find Available Spot"]
    SpotFinder --> ParkingSpot["Park Vehicle"]
    ParkingSpot --> Payment["Payment System"]
    Payment --> Exit
```""",
        "flow": """```mermaid
stateDiagram-v2
    [*] --> Entrance
    Entrance --> CheckAvailability
    CheckAvailability --> AvailableSpots
    AvailableSpots --> GetTicket
    GetTicket --> Park
    Park --> Parked
    Parked --> CheckOut
    CheckOut --> Payment
    Payment --> Exit
    Exit --> [*]
```"""
    },

    # Distributed Systems
    "pub_sub_system": {
        "architecture": """```mermaid
graph TB
    Publisher["Publisher"]
    Broker["Message Broker<br/>Kafka/RabbitMQ"]
    Topic["Topic/Queue"]
    Consumer1["Consumer 1"]
    Consumer2["Consumer 2"]
    Consumer3["Consumer 3"]

    Publisher -->|Publish Message| Broker
    Broker -->|Store in| Topic
    Topic -->|Deliver to| Consumer1
    Topic -->|Deliver to| Consumer2
    Topic -->|Deliver to| Consumer3

    Consumer1 --> Process1["Process 1"]
    Consumer2 --> Process2["Process 2"]
    Consumer3 --> Process3["Process 3"]
```""",
        "flow": """```mermaid
sequenceDiagram
    participant Pub as Publisher
    participant Broker as Message Broker
    participant T as Topic
    participant C1 as Consumer 1
    participant C2 as Consumer 2

    Pub->>Broker: Send Message
    Broker->>T: Enqueue
    par Parallel Delivery
        T-->>C1: Deliver
        T-->>C2: Deliver
    end
    C1->>C1: Process
    C2->>C2: Process
    C1-->>Broker: Acknowledge
    C2-->>Broker: Acknowledge
```"""
    },

    # Load Balancer
    "load_balancer": {
        "architecture": """```mermaid
graph LR
    Client["Clients"]
    LB["Load Balancer<br/>Round Robin/Least Conn"]
    HealthCheck["Health Checker<br/>Ping every 10s"]

    Server1["Server 1<br/>Healthy"]
    Server2["Server 2<br/>Healthy"]
    Server3["Server 3<br/>Down"]

    Client -->|Request| LB
    LB -->|Route| Server1
    LB -->|Route| Server2
    LB -.->|Skip| Server3
    HealthCheck -->|Monitor| Server1
    HealthCheck -->|Monitor| Server2
    HealthCheck -->|Monitor| Server3
```""",
        "flow": """```mermaid
flowchart TD
    A["Request Arrives"] --> B["Get Active Servers<br/>from Health Check"]
    B --> C["Select Server<br/>Round Robin"]
    C --> D["Forward Request"]
    D --> E["Server Processes"]
    E --> F["Return Response"]
    F --> G["Send to Client"]
```"""
    },

    # Auction System
    "auction_system": {
        "architecture": """```mermaid
graph TB
    User["User"]
    API["API Gateway"]
    AuctionService["Auction Service"]
    BidService["Bid Service"]
    DB["Database"]
    Redis["Redis Cache"]
    PaymentService["Payment Service"]

    User -->|Create/Place Bid| API
    API --> AuctionService
    API --> BidService
    AuctionService -->|Store| DB
    AuctionService -->|Cache| Redis
    BidService -->|Validate| Redis
    BidService -->|Store| DB
    BidService -->|Winner| PaymentService
    PaymentService -->|Process| Payment["Payment Gateway"]
```""",
        "flow": """```mermaid
sequenceDiagram
    participant User
    participant API
    participant AuctionSvc as Auction Service
    participant BidSvc as Bid Service
    participant DB
    participant Payment

    User->>API: Create Auction
    API->>AuctionSvc: Create
    AuctionSvc->>DB: Store

    User->>API: Place Bid
    API->>BidSvc: Validate Bid
    BidSvc->>DB: Check Current Highest
    BidSvc->>DB: Store Bid

    Note over User,Payment: At Auction End
    AuctionSvc->>DB: Finalize
    AuctionSvc->>Payment: Process Payment
    Payment-->>User: Confirmation
```"""
    },

    # Payment System
    "payment_system": {
        "architecture": """```mermaid
graph LR
    User["User"]
    App["Application"]
    Gateway["Payment Gateway<br/>Stripe/PayPal"]
    Processor["Payment Processor"]
    Bank["Bank Network"]
    Ledger["Transaction Ledger"]

    User -->|Initiate Payment| App
    App -->|Create Transaction| Ledger
    App -->|Process| Gateway
    Gateway -->|Token| Processor
    Processor -->|Authorize| Bank
    Bank -->|Response| Processor
    Processor -->|Status| Gateway
    Gateway -->|Result| App
    App -->|Update| Ledger
```""",
        "flow": """```mermaid
stateDiagram-v2
    [*] --> Initiated
    Initiated --> Validating
    Validating --> Authorized: Valid
    Validating --> Rejected: Invalid
    Rejected --> Failed
    Authorized --> Processing
    Processing --> Captured
    Captured --> Settled: Success
    Captured --> Failed: Error
    Settled --> [*]
    Failed --> [*]
```"""
    },

    # Leaderboard
    "leaderboard": {
        "architecture": """```mermaid
graph TB
    User["User Plays Game"]
    ScoreEvent["Score Event"]
    UpdateService["Update Service"]
    Redis["Redis Sorted Set<br/>user_id -> score"]
    DB["Database<br/>Persistent Store"]
    RankingEngine["Ranking Engine"]
    Cache["Leaderboard Cache"]
    Client["Client App"]

    User -->|Submit Score| ScoreEvent
    ScoreEvent -->|Update| UpdateService
    UpdateService -->|Increment| Redis
    UpdateService -->|Persist| DB
    UpdateService -->|Trigger| RankingEngine
    RankingEngine -->|Compute Ranks| Cache
    Client -->|Get Leaderboard| Cache
    Cache -->|Fallback| Redis
```""",
        "flow": """```mermaid
sequenceDiagram
    participant Game
    participant ScoreService
    participant Redis as Redis<br/>Sorted Set
    participant DB
    participant RankEngine
    participant LeaderboardAPI

    Game->>ScoreService: Report Score
    ScoreService->>Redis: ZADD user_id score
    par Async Update
        ScoreService->>DB: INSERT score_record
    end
    ScoreService->>RankEngine: Trigger Ranking
    RankEngine->>Redis: ZRANGE 0 99
    RankEngine->>Redis: Cache top 100

    LeaderboardAPI->>Redis: Get Top 100
    Redis-->>LeaderboardAPI: Scores + Ranks
```"""
    },

    # Consistent Hashing
    "consistent_hashing": {
        "architecture": """```mermaid
graph TB
    Client["Client"]
    ConsistentHash["Consistent Hash Ring"]

    Node1["Server 1<br/>Hash: 0-90"]
    Node2["Server 2<br/>Hash: 90-180"]
    Node3["Server 3<br/>Hash: 180-270"]
    Node4["Server 4<br/>Hash: 270-360"]

    Client -->|Key| ConsistentHash
    ConsistentHash -->|Route| Node1
    ConsistentHash -->|Route| Node2
    ConsistentHash -->|Route| Node3
    ConsistentHash -->|Route| Node4

    Node1 -.->|Replica on| Node2
    Node2 -.->|Replica on| Node3
    Node3 -.->|Replica on| Node4
```""",
        "flow": """```mermaid
flowchart TD
    A["Key Arrives"] --> B["Hash Key<br/>to ring position"]
    B --> C["Find Server<br/>Clockwise from Hash"]
    C --> D["Check if Server Up"]
    D --> E{Server Healthy?}
    E -->|Yes| F["Route to Server"]
    E -->|No| G["Skip to Next<br/>Server on Ring"]
    G --> D
    F --> H["Store/Retrieve Data"]
```"""
    },

    # Trie Data Structure
    "trie_data_structure": {
        "architecture": """```mermaid
graph TB
    Root["Root"]
    C["c"]
    A1["a"]
    D["d"]
    A2["a"]
    T["t"]
    R["r"]

    Root --> C
    Root --> D
    C --> A1
    D --> A2
    A1 --> T
    A1 --> R
    A2 --> R

    T -.->|End: cat| T
    R -.->|End: car| R
    R -.->|End: dog| R
```""",
        "flow": """```mermaid
flowchart TD
    A["Input String"] --> B["Start at Root"]
    B --> C["For each Character"]
    C --> D{Child Node<br/>Exists?}
    D -->|Yes| E["Move to Child"]
    D -->|No| F["Insert New Node"]
    E --> C
    F --> C
    C --> G{More<br/>Characters?}
    G -->|Yes| C
    G -->|No| H["Mark as Word End"]
    H --> I["Return"]
```"""
    },

    # Database Concepts
    "btree_bplus_tree": {
        "architecture": """```mermaid
graph TB
    Root["Root<br/>[1, 5, 10, 15]"]

    L1["[1, 3, 4]"]
    L2["[5, 7, 8]"]
    L3["[10, 12, 14]"]
    L4["[15, 18, 20]"]

    Root --> L1
    Root --> L2
    Root --> L3
    Root --> L4

    L1 --> Data1["Data Pointers"]
    L2 --> Data2["Data Pointers"]
    L3 --> Data3["Data Pointers"]
    L4 --> Data4["Data Pointers"]
```""",
        "flow": """```mermaid
flowchart TD
    A["Search for Key"] --> B["Start at Root"]
    B --> C["Find Range<br/>Using Comparisons"]
    C --> D{Leaf Node?}
    D -->|No| E["Go to Child"]
    E --> C
    D -->|Yes| F["Binary Search<br/>in Leaf"]
    F --> G["Return Value<br/>or NULL"]
```"""
    },

    # Distributed Tracing
    "distributed_tracing": {
        "architecture": """```mermaid
graph LR
    Client["Client Request"]
    API["API Gateway<br/>Span: API-1"]
    Auth["Auth Service<br/>Span: Auth-1"]
    DB["Database<br/>Span: DB-1"]
    Cache["Cache<br/>Span: Cache-1"]
    Collector["Trace Collector<br/>Jaeger/Zipkin"]
    Visualization["Visualization"]

    Client -->|Trace ID| API
    API -->|Parent: API-1| Auth
    API -->|Parent: API-1| Cache
    API -->|Parent: API-1| DB

    Auth -->|Send Span| Collector
    Cache -->|Send Span| Collector
    DB -->|Send Span| Collector
    Collector -->|Process| Visualization
```""",
        "flow": """```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant AuthSvc as Auth Service
    participant Cache
    participant Collector as Collector

    Client->>API: Request (trace_id=123)
    Note over API: Span: API-1 (0-100ms)
    par
        API->>AuthSvc: Verify (parent=API-1)
        Note over AuthSvc: Span: Auth-1 (10-40ms)
        API->>Cache: Get Data (parent=API-1)
        Note over Cache: Span: Cache-1 (50-80ms)
    end
    API-->>Client: Response
    API->>Collector: Send Spans
    AuthSvc->>Collector: Send Span
    Cache->>Collector: Send Span
```"""
    },

    # Recommendation System
    "collaborative_filtering": {
        "architecture": """```mermaid
graph TB
    UserItemMatrix["User-Item Matrix<br/>with Ratings"]
    Factorization["SVD/NMF<br/>Factorization"]
    UserFactors["User Factor Matrix<br/>U: 1M x 64"]
    ItemFactors["Item Factor Matrix<br/>V: 100M x 64"]
    Scorer["Scorer<br/>U[i] · V[j]"]
    Ranker["Rank Items<br/>by Score"]
    Recommendations["Recommendations"]

    UserItemMatrix --> Factorization
    Factorization --> UserFactors
    Factorization --> ItemFactors

    UserFactors --> Scorer
    ItemFactors --> Scorer
    Scorer --> Ranker
    Ranker --> Recommendations
```""",
        "flow": """```mermaid
flowchart TD
    A["Training Data<br/>User-Item Matrix"] --> B["Factorize<br/>SVD"]
    B --> C["Generate User<br/>& Item Vectors"]
    C --> D["Store in Cache/<br/>Feature Store"]

    E["New User Request"] --> F["Get User Vector"]
    F --> G["Compute Similarity<br/>with All Items"]
    G --> H["Top K Items"]
    H --> I["Apply Business<br/>Logic/Filters"]
    I --> J["Rank & Serve"]
```"""
    },

    # Real-world Systems
    "instagram_scale": {
        "architecture": """```mermaid
graph TB
    User["User"]
    API["API Gateway"]
    PhotoService["Photo Service"]
    FeedService["Feed Service"]
    S3["S3 Storage<br/>100PB Photos"]
    DB["Database<br/>Photo Metadata"]
    Redis["Redis<br/>Feed Cache"]
    ES["Elasticsearch<br/>Search Index"]

    User -->|Upload| API
    API -->|Store| PhotoService
    PhotoService -->|Upload| S3
    PhotoService -->|Store Meta| DB

    User -->|View Feed| API
    API -->|Get Feed| FeedService
    FeedService -->|Cache| Redis
    FeedService -->|Fallback| DB

    User -->|Search| API
    API -->|Query| ES
```""",
        "flow": """```mermaid
sequenceDiagram
    participant User
    participant API
    participant PhotoSvc
    participant S3
    participant DB
    participant Cache
    participant ES

    User->>API: Upload Photo
    API->>PhotoSvc: Create Photo
    PhotoSvc->>S3: Upload Image
    PhotoSvc->>DB: Store Metadata
    PhotoSvc->>ES: Index for Search

    User->>API: Get Feed
    API->>Cache: Check Cache
    alt Cache Hit
        Cache-->>API: Feed Data
    else
        API->>DB: Query Feed
        DB-->>API: Results
        API->>Cache: Update
    end
    API-->>User: Feed
```"""
    },

    # OAuth/SSO
    "oauth_sso": {
        "architecture": """```mermaid
graph LR
    User["User"]
    App["Application"]
    OAuthProvider["OAuth Provider<br/>Google/Facebook"]

    User -->|Login| App
    App -->|Redirect| OAuthProvider
    OAuthProvider -->|Auth| User
    User -->|Authorize| OAuthProvider
    OAuthProvider -->|Auth Code| App
    App -->|Exchange Code| OAuthProvider
    OAuthProvider -->|Access Token| App
    App -->|Validate Token| OAuthProvider
    OAuthProvider -->|User Info| App
    App -->|Logged In| User
```""",
        "flow": """```mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant Provider as OAuth Provider

    User->>App: Click Login
    App->>Provider: Redirect with client_id
    Provider->>User: Show Login
    User->>Provider: Enter Credentials
    Provider->>User: Request Permissions
    User->>Provider: Grant
    Provider->>App: Redirect with auth_code
    App->>Provider: POST code + client_secret
    Provider-->>App: access_token
    App->>Provider: GET user_info
    Provider-->>App: User Data
    App-->>User: Logged In
```"""
    }
}

def add_mermaid_diagrams(filepath, filename):
    """Add Mermaid diagrams to a concept file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Find matching diagrams for this file
        for concept_key, diagrams in mermaid_diagrams.items():
            if concept_key in filename.lower():
                # Add architecture diagram before Architecture Diagram section
                if "## Architecture Diagram" in content:
                    # Add after Architecture Diagram section
                    arch_section = f"""## Architecture Diagram

{diagrams.get('architecture', '')}"""

                    # Replace the architecture diagram placeholder
                    content = re.sub(
                        r"## Architecture Diagram\n\n```\n\[Visual system components[^\n]*\n```",
                        arch_section,
                        content
                    )

                # Add flow diagram before Implementation
                if "## Implementation" in content and "flow" in diagrams:
                    flow_section = f"""## Flow Diagram

{diagrams['flow']}

"""
                    content = content.replace("## Implementation", flow_section + "## Implementation")

                with open(filepath, 'w') as f:
                    f.write(content)

                return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return False

# Process all files
processed = 0
for filepath in glob.glob(f"{base_path}/*/*_*.md"):
    filename = os.path.basename(filepath)
    if add_mermaid_diagrams(filepath, filename):
        processed += 1
        if processed % 10 == 0:
            print(f"✓ Added diagrams to {processed} files")

print(f"\n✅ Added Mermaid diagrams to {processed} system design documents")
