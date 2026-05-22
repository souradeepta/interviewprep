#!/usr/bin/env python3
"""
Add diagrams to remaining older system design files.
"""

import os
import re
import glob

base_path = "/home/sbisw/github/interviewprep/docs/system_design"

remaining_diagrams = {
    # Old file naming patterns
    "observer": """### Architecture Diagram

```mermaid
graph TB
    Subject["Subject<br/>notifyObservers()"]
    Observer1["Observer 1<br/>update()"]
    Observer2["Observer 2<br/>update()"]
    Observer3["Observer 3<br/>update()"]

    Subject -->|notify| Observer1
    Subject -->|notify| Observer2
    Subject -->|notify| Observer3
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant E as Event
    participant S as Subject
    participant O1 as Observer 1
    participant O2 as Observer 2

    E->>S: Change State
    S->>O1: notifyObservers()
    S->>O2: notifyObservers()
    O1->>O1: update()
    O2->>O2: update()
```""",

    "strategy": """### Architecture Diagram

```mermaid
graph TB
    Context["Context<br/>strategy: Strategy"]
    Strategy["Strategy<br/>execute()"]
    StrategyA["ConcreteA<br/>execute()"]
    StrategyB["ConcreteB<br/>execute()"]

    Context -->|uses| Strategy
    Strategy <|--|StrategyA
    Strategy <|--|StrategyB
```

### Flow Diagram

```mermaid
flowchart TD
    A["Client selects Strategy"] --> B["Context.setStrategy()"]
    B --> C["Context.execute()"]
    C --> D{"Which Strategy?"}
    D -->|A| E["StrategyA.execute()"]
    D -->|B| F["StrategyB.execute()"]
    E --> G["Result"]
    F --> G
```""",

    "adapter": """### Architecture Diagram

```mermaid
graph LR
    Client["Client"]
    Target["Target Interface"]
    Adapter["Adapter<br/>implements Target"]
    Adaptee["Adaptee<br/>incompatible"]

    Client -->|uses| Target
    Adapter -->|implements| Target
    Adapter -->|wraps| Adaptee
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Adapter
    participant E as Adaptee

    C->>A: request()
    A->>A: translate format
    A->>E: specificRequest()
    E-->>A: response
    A->>A: translate format
    A-->>C: response
```""",

    "pub_sub": """### Architecture Diagram

```mermaid
graph TB
    Publisher["Publisher"]
    Broker["Message Broker<br/>Topic/Queue"]
    Consumer1["Consumer 1"]
    Consumer2["Consumer 2"]
    Consumer3["Consumer 3"]

    Publisher -->|Publish| Broker
    Broker -->|Deliver| Consumer1
    Broker -->|Deliver| Consumer2
    Broker -->|Deliver| Consumer3
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant Pub as Publisher
    participant B as Broker
    participant C1 as Consumer 1
    participant C2 as Consumer 2

    Pub->>B: Send Message
    B->>B: Store in Topic
    B->>C1: Deliver
    B->>C2: Deliver
    C1->>C1: Process
    C2->>C2: Process
    C1-->>B: ACK
    C2-->>B: ACK
```""",

    "thread_pool": """### Architecture Diagram

```mermaid
graph TB
    Task["Task Queue"]
    Pool["Thread Pool<br/>N Worker Threads"]
    Worker1["Worker 1"]
    Worker2["Worker 2"]
    WorkerN["Worker N"]

    Task -->|Distribute| Pool
    Pool --> Worker1
    Pool --> Worker2
    Pool --> WorkerN
```

### Flow Diagram

```mermaid
flowchart TD
    A["Task Submitted"] --> B["Add to Queue"]
    B --> C{"Worker Available?"}
    C -->|Yes| D["Assign to Worker"]
    C -->|No| E["Wait in Queue"]
    D --> F["Execute Task"]
    E --> G["Wait for Worker"]
    G --> D
    F --> H["Return Result"]
```""",

    "load_balancer": """### Architecture Diagram

```mermaid
graph TB
    Clients["Clients"]
    LB["Load Balancer<br/>Round Robin/LeastConn"]
    HealthCheck["Health Checker"]

    Server1["Server 1"]
    Server2["Server 2"]
    Server3["Server 3"]
    Server4["Server 4"]

    Clients -->|Request| LB
    LB -->|Monitor| HealthCheck
    LB -->|Route| Server1
    LB -->|Route| Server2
    LB -->|Route| Server3
```

### Flow Diagram

```mermaid
flowchart TD
    A["Request Arrives"] --> B["Get Active Servers"]
    B --> C["Select Server"]
    C --> D{"Algorithm"}
    D -->|Round Robin| E["Next"]
    D -->|Least Conn| F["Lowest Load"]
    E --> G["Route"]
    F --> G
```""",

    "news_feed": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    PostService["Post Service"]
    FeedService["Feed Service"]
    Cache["Cache<br/>Redis"]
    DB["Database"]

    User -->|Create Post| PostService
    PostService -->|Store| DB
    User -->|Get Feed| FeedService
    FeedService -->|Check| Cache
    Cache -->|Miss| DB
    FeedService -->|Return| User
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant PS as Post Service
    participant FS as Feed Service
    participant C as Cache

    U->>PS: Create Post
    PS->>DB: Save
    U->>FS: Get Feed
    FS->>C: Check Cache
    alt Hit
        C-->>FS: Feed
    else Miss
        FS->>DB: Query
        DB-->>FS: Results
        FS->>C: Update
    end
    FS-->>U: Feed
```""",

    "ecommerce": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    ProductService["Product Service"]
    CartService["Cart Service"]
    PaymentService["Payment Service"]
    OrderService["Order Service"]

    User -->|Browse| ProductService
    User -->|Add to Cart| CartService
    User -->|Checkout| PaymentService
    PaymentService -->|Create| OrderService
```

### Flow Diagram

```mermaid
flowchart TD
    A["Browse Products"] --> B["Add to Cart"]
    B --> C["Checkout"]
    C --> D["Payment"]
    D --> E{Success?}
    E -->|Yes| F["Create Order"]
    E -->|No| G["Retry"]
    F --> H["Confirmation"]
```""",

    "ride_sharing": """### Architecture Diagram

```mermaid
graph TB
    Rider["Rider"]
    Driver["Driver"]
    Matching["Matching Service"]
    Location["Location Service"]
    Payment["Payment Service"]

    Rider -->|Request| Matching
    Driver -->|Update Loc| Location
    Matching -->|Query| Location
    Matching -->|Assign| Driver
    Rider -->|Pay| Payment
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant R as Rider
    participant M as Matching
    participant L as Location
    participant D as Driver

    R->>M: Request Ride
    M->>L: Get nearby drivers
    L-->>M: Drivers
    M->>D: Offer ride
    D->>D: Accept/Reject
    alt Accepted
        M->>R: Driver assigned
    end
```""",

    "chat_system": """### Architecture Diagram

```mermaid
graph TB
    User1["User 1"]
    User2["User 2"]
    WebSocket["WebSocket Server"]
    MessageQueue["Message Queue"]
    Storage["Storage"]

    User1 -->|Send| WebSocket
    WebSocket -->|Enqueue| MessageQueue
    MessageQueue -->|Deliver| User2
    MessageQueue -->|Store| Storage
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant U1 as User 1
    participant WS as WebSocket
    participant Q as Queue
    participant U2 as User 2

    U1->>WS: Send Message
    WS->>Q: Enqueue
    Q->>U2: Deliver (if online)
    alt Offline
        Q->>Storage: Mark unread
    end
```""",

    "video_streaming": """### Architecture Diagram

```mermaid
graph TB
    User["Viewer"]
    Player["Player<br/>Adaptive Bitrate"]
    CDN["CDN Edge"]
    Origin["Origin Server"]
    Transcoder["Transcoder"]

    User -->|Request| Player
    Player -->|Fetch| CDN
    CDN -->|Miss| Origin
    Origin -->|Store| Transcoder
```

### Flow Diagram

```mermaid
flowchart TD
    A["Video Upload"] --> B["Transcode"]
    B --> C["Multiple Bitrates"]
    C --> D["Store Segments"]
    D --> E["User Request"]
    E --> F["Measure Bandwidth"]
    F --> G["Select Bitrate"]
    G --> H["Adapt if needed"]
```""",

    "database_sharding": """### Architecture Diagram

```mermaid
graph TB
    Client["Client"]
    Router["Shard Router"]
    Shard1["Shard 1"]
    Shard2["Shard 2"]
    Shard3["Shard 3"]

    Client -->|Query| Router
    Router -->|Route| Shard1
    Router -->|Route| Shard2
    Router -->|Route| Shard3
```

### Flow Diagram

```mermaid
flowchart TD
    A["Query"] --> B["Extract Shard Key"]
    B --> C["Compute Shard ID"]
    C --> D["Lookup Config"]
    D --> E["Connect"]
    E --> F["Execute"]
    F --> G["Return"]
```""",

    "message_queue": """### Architecture Diagram

```mermaid
graph LR
    Producer["Producer"]
    Broker["Kafka/RabbitMQ"]
    Consumer1["Consumer 1"]
    Consumer2["Consumer 2"]

    Producer -->|Publish| Broker
    Broker -->|Partition 1| Consumer1
    Broker -->|Partition 2| Consumer2
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant P as Producer
    participant B as Broker
    participant C1 as Consumer 1
    participant C2 as Consumer 2

    P->>B: Send Message
    B->>B: Partition & Store
    B->>C1: Deliver
    B->>C2: Deliver
    C1->>C1: Process
    C2->>C2: Process
```""",

    "search_engine": """### Architecture Diagram

```mermaid
graph TB
    Docs["Documents"]
    Indexer["Indexer"]
    Index["Inverted Index"]
    Query["Query"]
    Results["Results"]

    Docs -->|Process| Indexer
    Indexer -->|Build| Index
    Query -->|Search| Index
    Index -->|Score| Results
```

### Flow Diagram

```mermaid
flowchart TD
    A["Query:"] --> B["Parse"]
    B --> C["Tokenize"]
    C --> D["Search Index"]
    D --> E["Score TF-IDF"]
    E --> F["Rank"]
    F --> G["Return Top K"]
```""",

    "recommendation": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    Features["Features"]
    Model["ML Model"]
    Scorer["Scorer"]
    Results["Results"]

    User -->|Profile| Features
    Features -->|Input| Model
    Model -->|Vectors| Scorer
    Scorer -->|Rank| Results
```

### Flow Diagram

```mermaid
flowchart TD
    A["Get User Vector"] --> B["Find Similar"]
    B --> C["Score"]
    C --> D["Filter"]
    D --> E["Rank"]
    E --> F["Return Top 10"]
```""",

    "leaderboard": """### Architecture Diagram

```mermaid
graph TB
    User["User Scores"]
    Update["Update Service"]
    Redis["Redis<br/>Sorted Set"]
    DB["Database"]
    Ranking["Ranking"]

    User -->|Score| Update
    Update -->|Increment| Redis
    Update -->|Persist| DB
    Ranking -->|Compute| Redis
```

### Flow Diagram

```mermaid
flowchart TD
    A["New Score"] --> B["Update Redis"]
    B --> C["Persist DB"]
    C --> D["Compute Ranks"]
    D --> E["Cache Top 100"]
    E --> F["Query Leaderboard"]
```""",

    "payment": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    PaymentGateway["Payment Gateway"]
    Processor["Processor"]
    Bank["Bank"]
    Ledger["Ledger"]

    User -->|Payment| PaymentGateway
    PaymentGateway -->|Process| Processor
    Processor -->|Authorize| Bank
    PaymentGateway -->|Log| Ledger
```

### Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> Initiated
    Initiated --> Validating
    Validating --> Authorized: Valid
    Authorized --> Captured
    Captured --> Settled: Success
    Captured --> Failed
    Settled --> [*]
    Failed --> [*]
```""",

    "wallet": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    Wallet["Wallet Service"]
    Balance["Balance"]
    Transaction["Transaction Log"]

    User -->|Add Funds| Wallet
    User -->|Spend| Wallet
    Wallet -->|Update| Balance
    Wallet -->|Record| Transaction
```

### Flow Diagram

```mermaid
flowchart TD
    A["User Action"] --> B{"Type?"}
    B -->|Add| C["Deposit"]
    B -->|Spend| D["Charge"]
    C --> E["Update Balance"]
    D --> E
    E --> F["Log Transaction"]
    F --> G["Return Status"]
```""",

    "followers": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    FollowService["Follow Service"]
    Graph["Graph DB"]
    Cache["Cache"]

    User -->|Follow/Unfollow| FollowService
    FollowService -->|Store| Graph
    FollowService -->|Cache| Cache
```

### Flow Diagram

```mermaid
flowchart TD
    A["Follow Request"] --> B["Check if exists"]
    B --> C{"Already following?"}
    C -->|Yes| D["Error"]
    C -->|No| E["Add Edge"]
    E --> F["Update Cache"]
    F --> G["Confirm"]
```""",

    "notification": """### Architecture Diagram

```mermaid
graph TB
    Event["Event"]
    NotificationService["Notification Service"]
    Queue["Task Queue"]
    Workers["Workers"]
    Channels["Email/SMS/Push"]

    Event -->|Create| NotificationService
    NotificationService -->|Enqueue| Queue
    Queue -->|Distribute| Workers
    Workers -->|Send| Channels
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant E as Event
    participant NS as Service
    participant Q as Queue
    participant W as Worker
    participant C as Channel

    E->>NS: Notification Event
    NS->>Q: Enqueue
    Q-->>W: Task
    W->>C: Send
    C-->>User: Delivered
```""",

    "api_gateway": """### Architecture Diagram

```mermaid
graph LR
    Client["Clients"]
    Gateway["API Gateway<br/>Auth, Rate Limit"]
    Service1["Service 1"]
    Service2["Service 2"]

    Client -->|Request| Gateway
    Gateway -->|Validate| Gateway
    Gateway -->|Route| Service1
    Gateway -->|Route| Service2
```

### Flow Diagram

```mermaid
flowchart TD
    A["Request"] --> B["Authenticate"]
    B --> C{"Valid?"}
    C -->|No| D["401"]
    C -->|Yes| E["Rate Check"]
    E --> F{"OK?"}
    F -->|No| G["429"]
    F -->|Yes| H["Route"]
    H --> I["Service Process"]
```""",

    "websocket": """### Architecture Diagram

```mermaid
graph LR
    Client["WebSocket Client"]
    Server["WebSocket Server"]
    Broadcast["Broadcaster"]

    Client -->|Connect| Server
    Server -->|Register| Broadcast
    Client -->|Send| Broadcast
    Broadcast -->|Push| Client
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant B as Broadcaster

    C->>S: Upgrade to WebSocket
    S-->>C: 101 Switching
    C->>S: Send Message
    S->>B: Broadcast
    B->>C: Push Update
```""",

    "distributed_transaction": """### Architecture Diagram

```mermaid
graph TB
    Transaction["Transaction"]
    TxManager["Transaction Manager"]
    WAL["Write-Ahead Log"]
    Service1["Service 1"]
    Service2["Service 2"]

    Transaction -->|Begin| TxManager
    TxManager -->|Write| WAL
    TxManager -->|Execute| Service1
    TxManager -->|Execute| Service2
```

### Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> Begin
    Begin --> Execute
    Execute --> Validate
    Validate --> Valid: ACID OK
    Valid --> Commit
    Validate --> Invalid: Error
    Invalid --> Rollback
    Commit --> End
    Rollback --> End
    End --> [*]
```""",

    "circuit_breaker": """### Architecture Diagram

```mermaid
graph TB
    Client["Client"]
    CB["Circuit Breaker"]
    Service["Service"]
    Fallback["Fallback"]

    Client -->|Request| CB
    CB -->|CLOSED| Service
    CB -->|OPEN| Fallback
    Service -->|Failure| CB
```

### Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: Threshold failed
    Open --> HalfOpen: Timeout
    HalfOpen --> Closed: Request OK
    HalfOpen --> Open: Request Failed
```""",

    "saga_pattern": """### Architecture Diagram

```mermaid
graph TB
    Client["Client"]
    SagaOrchestrator["Saga Orchestrator"]
    Service1["Service 1"]
    Service2["Service 2"]
    Service3["Service 3"]

    Client -->|Request| SagaOrchestrator
    SagaOrchestrator -->|Execute| Service1
    Service1 -->|Success| Service2
    Service2 -->|Success| Service3
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant S1 as Service 1
    participant S2 as Service 2
    participant S3 as Service 3

    O->>S1: Execute Step 1
    S1-->>O: Success
    O->>S2: Execute Step 2
    S2-->>O: Success
    O->>S3: Execute Step 3
    S3-->>O: Success/Fail
    alt Fail
        O->>S1: Compensate
        O->>S2: Compensate
    end
```""",

    "photo_sharing": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    PhotoService["Photo Service"]
    Storage["S3/GCS"]
    DB["Database"]
    Search["Search Index"]

    User -->|Upload| PhotoService
    PhotoService -->|Store| Storage
    PhotoService -->|Metadata| DB
    PhotoService -->|Index| Search
```

### Flow Diagram

```mermaid
flowchart TD
    A["Upload Photo"] --> B["Resize"]
    B --> C["Generate Thumbnails"]
    C --> D["Upload to Storage"]
    D --> E["Store Metadata"]
    E --> F["Index for Search"]
    F --> G["Confirm"]
```""",

    "time_series": """### Architecture Diagram

```mermaid
graph TB
    Metrics["Metrics"]
    Ingestion["Ingestion Service"]
    Storage["Time Series DB"]
    Query["Query Engine"]
    Visualization["Visualization"]

    Metrics -->|Stream| Ingestion
    Ingestion -->|Store| Storage
    Query -->|Read| Storage
    Query -->|Render| Visualization
```

### Flow Diagram

```mermaid
flowchart TD
    A["Metric arrives"] --> B["Timestamp"]
    B --> C["Tags"]
    C --> D["Value"]
    D --> E["Compress"]
    E --> F["Store Block"]
    F --> G["Index"]
```""",

    "log_aggregation": """### Architecture Diagram

```mermaid
graph TB
    Services["Services"]
    Collector["Log Collector"]
    Storage["Storage"]
    Parser["Parser"]
    Search["Search Engine"]

    Services -->|Stream Logs| Collector
    Collector -->|Parse| Parser
    Parser -->|Store| Storage
    Storage -->|Index| Search
```

### Flow Diagram

```mermaid
flowchart TD
    A["Log Line"] --> B["Collect"]
    B --> C["Parse"]
    C --> D["Extract Fields"]
    D --> E["Enrich"]
    E --> F["Store"]
    F --> G["Index"]
```""",

    "like_comment": """### Architecture Diagram

```mermaid
graph TB
    User["User"]
    LikeService["Like Service"]
    CommentService["Comment Service"]
    Cache["Cache"]
    DB["Database"]

    User -->|Like| LikeService
    User -->|Comment| CommentService
    LikeService -->|Store| Cache
    CommentService -->|Store| Cache
    Cache -->|Persist| DB
```

### Flow Diagram

```mermaid
flowchart TD
    A["User Action"] --> B{"Type?"}
    B -->|Like| C["Increment Count"]
    B -->|Comment| D["Create Comment"]
    C --> E["Update Cache"]
    D --> E
    E --> F["Persist"]
    F --> G["Notify"]
```""",

    "transaction_ledger": """### Architecture Diagram

```mermaid
graph TB
    Transaction["Transaction"]
    Ledger["Ledger Service"]
    Storage["Storage"]
    Audit["Audit Trail"]

    Transaction -->|Record| Ledger
    Ledger -->|Store| Storage
    Ledger -->|Log| Audit
```

### Flow Diagram

```mermaid
flowchart TD
    A["Transaction"] --> B["Generate Entry"]
    B --> C["Sign/Hash"]
    C --> D["Append to Ledger"]
    D --> E["Replicate"]
    E --> F["Confirm"]
```""",

    "consensus": """### Architecture Diagram

```mermaid
graph TB
    Node1["Node 1"]
    Node2["Node 2"]
    Node3["Node 3"]
    Consensus["Consensus<br/>RAFT/Paxos"]

    Node1 -->|Heartbeat| Consensus
    Node2 -->|Heartbeat| Consensus
    Node3 -->|Heartbeat| Consensus
```

### Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> Follower
    Follower --> Candidate: Timeout
    Candidate --> Leader: Win election
    Candidate --> Follower: Higher term
    Leader --> Follower: Higher term
    Leader --> Leader: Heartbeat
```"""
}

def update_old_file(filepath, filename):
    """Update older format files with diagrams."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Skip if already has mermaid
        if "```mermaid" in content:
            return False

        # Find matching diagram
        for key, diagram_content in remaining_diagrams.items():
            if key in filename.lower():
                # Replace the placeholder section or add before Implementation
                if "## Implementation" in content:
                    # Add diagrams before Implementation
                    content = content.replace(
                        "## Implementation",
                        diagram_content + "\n\n## Implementation"
                    )
                else:
                    # Add at end before last section
                    content = content.replace(
                        "## Complexity",
                        diagram_content + "\n\n## Complexity"
                    )

                with open(filepath, 'w') as f:
                    f.write(content)
                return True

        return False

    except Exception as e:
        print(f"Error: {filepath}: {e}")
        return False

# Process remaining files
remaining_files = [
    "03-design-patterns/06_observer_pattern.md",
    "03-design-patterns/07_strategy_pattern.md",
    "03-design-patterns/10_adapter_pattern.md",
    "04-distributed-systems/11_pub_sub_system.md",
    "04-distributed-systems/12_thread_pool.md",
    "04-distributed-systems/13_load_balancer.md",
    "05-real-world-apps/14_news_feed.md",
    "05-real-world-apps/15_ecommerce.md",
    "05-real-world-apps/16_ride_sharing.md",
    "05-real-world-apps/17_chat_system.md",
    "05-real-world-apps/18_video_streaming.md",
    "06-data-systems/19_database_sharding.md",
    "06-data-systems/20_message_queue.md",
    "06-data-systems/21_search_engine.md",
    "06-data-systems/22_recommendation_engine.md",
    "06-data-systems/23_leaderboard.md",
    "06-data-systems/24_payment_system.md",
    "06-data-systems/25_wallet_system.md",
    "07-social-features/26_followers_system.md",
    "07-social-features/27_notifications.md",
    "07-social-features/28_api_gateway.md",
    "07-social-features/29_websocket_server.md",
    "08-infrastructure/30_distributed_transaction.md",
    "08-infrastructure/31_circuit_breaker.md",
    "08-infrastructure/32_saga_pattern.md",
    "09-storage-analytics/33_photo_sharing.md",
    "09-storage-analytics/34_time_series_db.md",
    "09-storage-analytics/35_log_aggregation.md",
    "09-storage-analytics/36_like_comment_system.md",
    "09-storage-analytics/38_transaction_ledger.md",
    "09-storage-analytics/39_consensus_algorithm.md"
]

added = 0
for relative_path in remaining_files:
    filepath = os.path.join(base_path, relative_path)
    if os.path.exists(filepath):
        filename = os.path.basename(filepath).replace(".md", "").lower()
        if update_old_file(filepath, filename):
            added += 1
            print(f"✓ {relative_path}")

print(f"\n✅ Added diagrams to {added} remaining files")
print(f"Total coverage now: {added + 89 + 3} out of 92 files")
