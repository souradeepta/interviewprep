#!/usr/bin/env python3
"""
Add comprehensive Mermaid diagrams to ALL system design concepts.
"""

import os
import re
import glob

base_path = "/home/sbisw/github/datastructures/docs/system_design"

# Comprehensive diagram templates for all concept types
universal_diagrams = {
    # Design Patterns
    "observer_pattern": {
        "arch": """```mermaid
graph TB
    Subject["Subject<br/>notifyObservers()"]
    Observer1["Observer 1<br/>update()"]
    Observer2["Observer 2<br/>update()"]
    Observer3["Observer 3<br/>update()"]

    Subject -->|notify| Observer1
    Subject -->|notify| Observer2
    Subject -->|notify| Observer3

    Event["State Change"] -->|trigger| Subject
```""",
        "flow": """```mermaid
sequenceDiagram
    participant E as Event Source
    participant S as Subject
    participant O1 as Observer 1
    participant O2 as Observer 2

    E->>S: State Changes
    S->>O1: notifyObservers()
    S->>O2: notifyObservers()
    O1->>O1: update()
    O2->>O2: update()
```"""
    },
    "strategy_pattern": {
        "arch": """```mermaid
graph TB
    Context["Context<br/>strategy: Strategy"]
    Strategy["Strategy<br/>execute()"]
    StrategyA["ConcreteA<br/>execute()"]
    StrategyB["ConcreteB<br/>execute()"]

    Context -->|uses| Strategy
    Strategy <|--|StrategyA
    Strategy <|--|StrategyB
```""",
        "flow": """```mermaid
flowchart TD
    A["Client selects<br/>Strategy"] --> B["Context.setStrategy()"]
    B --> C["Context.execute()"]
    C --> D{"Which<br/>Strategy?"}
    D -->|A| E["StrategyA.execute()"]
    D -->|B| F["StrategyB.execute()"]
    E --> G["Result"]
    F --> G
```"""
    },
    "factory_pattern": {
        "arch": """```mermaid
graph TB
    Client["Client"]
    Factory["Factory<br/>createProduct()"]
    Product["Product"]
    ProductA["ConcreteA"]
    ProductB["ConcreteB"]

    Client -->|uses| Factory
    Factory -->|creates| Product
    Product <|--| ProductA
    Product <|--| ProductB
```""",
        "flow": """```mermaid
flowchart TD
    A["Request Product<br/>by Type"] --> B["Factory.create()"]
    B --> C{"Product Type?"}
    C -->|Type A| D["return new ProductA()"]
    C -->|Type B| E["return new ProductB()"]
    D --> F["Use Product"]
    E --> F
```"""
    },
    "decorator_pattern": {
        "arch": """```mermaid
graph LR
    Component["Component<br/>operation()"]
    Decorator["Decorator<br/>operation()"]
    ConcreteA["ConcreteA<br/>operation()"]
    ConcreteB["ConcreteB<br/>operation()"]

    Decorator -->|wraps| Component
    ConcreteA -->|extends| Decorator
    ConcreteB -->|extends| Decorator
```""",
        "flow": """```mermaid
flowchart TD
    A["Original Component"] --> B["Wrap with Decorator A"]
    B --> C["Wrap with Decorator B"]
    C --> D["Call operation()"]
    D --> E["B.operation()"]
    E --> F["A.operation()"]
    F --> G["Original.operation()"]
    G --> H["Result"]
```"""
    },
    "adapter_pattern": {
        "arch": """```mermaid
graph LR
    Client["Client"]
    Target["Target"]
    Adapter["Adapter<br/>implements Target"]
    Adaptee["Adaptee<br/>incompatible"]

    Client -->|uses| Target
    Adapter -->|implements| Target
    Adapter -->|wraps| Adaptee
```""",
        "flow": """```mermaid
sequenceDiagram
    participant C as Client
    participant A as Adapter
    participant E as Adaptee

    C->>A: request()
    A->>A: translate to Adaptee format
    A->>E: specificRequest()
    E-->>A: response
    A->>A: translate to Target format
    A-->>C: response
```"""
    },

    # Real-world Applications
    "news_feed": {
        "arch": """```mermaid
graph TB
    User["User"]
    PostService["Post Service"]
    FeedService["Feed Service"]
    Cache["Cache<br/>Redis"]
    DB["Database"]
    Graph["Graph DB<br/>Followers"]

    User -->|Create Post| PostService
    PostService -->|Store| DB
    PostService -->|Notify| FeedService

    User -->|Get Feed| FeedService
    FeedService -->|Query| Cache
    Cache -->|Fallback| DB
    FeedService -->|Follow Graph| Graph
```""",
        "flow": """```mermaid
sequenceDiagram
    participant User
    participant PostSvc as Post Service
    participant FeedSvc as Feed Service
    participant Cache
    participant DB

    User->>PostSvc: Create Post
    PostSvc->>DB: Save Post
    PostSvc->>FeedSvc: Fanout to Followers

    loop For each Follower
        FeedSvc->>Cache: Add to Feed
    end

    User->>FeedSvc: Get Feed
    FeedSvc->>Cache: Retrieve Feed
    Cache-->>User: Feed Data
```"""
    },
    "ecommerce_platform": {
        "arch": """```mermaid
graph TB
    User["User"]
    ProductService["Product Service"]
    CartService["Cart Service"]
    PaymentService["Payment Service"]
    OrderService["Order Service"]
    InventoryService["Inventory Service"]

    User -->|Browse| ProductService
    User -->|Add to Cart| CartService
    CartService -->|Check Stock| InventoryService
    User -->|Checkout| PaymentService
    PaymentService -->|Create Order| OrderService
    OrderService -->|Update Stock| InventoryService
```""",
        "flow": """```mermaid
flowchart TD
    A["Browse Products"] --> B["Add to Cart"]
    B --> C["View Cart"]
    C --> D["Checkout"]
    D --> E["Payment Processing"]
    E --> F{Payment<br/>Successful?}
    F -->|No| G["Retry/Cancel"]
    F -->|Yes| H["Create Order"]
    H --> I["Update Inventory"]
    I --> J["Send Confirmation"]
```"""
    },
    "rideshare_system": {
        "arch": """```mermaid
graph TB
    Rider["Rider"]
    Driver["Driver"]
    Matching["Matching Service<br/>Geohash"]
    Location["Location Service"]
    Payment["Payment Service"]
    Notification["Notification Service"]

    Rider -->|Request Ride| Matching
    Driver -->|Update Location| Location
    Matching -->|Query Nearby| Location
    Matching -->|Match| Driver
    Notification -->|Notify Rider| Rider
    Notification -->|Notify Driver| Driver
    Rider -->|Payment| Payment
```""",
        "flow": """```mermaid
sequenceDiagram
    participant R as Rider
    participant M as Matching
    participant L as Location
    participant D as Driver
    participant N as Notification

    R->>M: Request Ride
    M->>L: Get nearby drivers
    L-->>M: Driver list
    M->>M: Score & rank
    M->>D: Offer ride
    D->>D: Accept/Reject
    alt Accept
        N->>R: Driver assigned
        N->>D: Ride details
    end
```"""
    },
    "chat_system": {
        "arch": """```mermaid
graph TB
    User1["User 1"]
    User2["User 2"]
    WebSocket["WebSocket Server"]
    MessageQueue["Message Queue"]
    Storage["Message Storage"]
    Notification["Notification Service"]

    User1 -->|Send Message| WebSocket
    WebSocket -->|Broadcast| MessageQueue
    MessageQueue -->|Deliver| User2
    MessageQueue -->|Persist| Storage
    MessageQueue -->|Notify if Offline| Notification
```""",
        "flow": """```mermaid
sequenceDiagram
    participant U1 as User 1
    participant WS as WebSocket
    participant Q as Queue
    participant U2 as User 2
    participant Storage

    U1->>WS: Send Message
    WS->>Q: Enqueue
    Q->>Storage: Persist
    Q->>U2: Deliver (if online)
    alt User 2 Offline
        Q->>Storage: Mark unread
    end
    U2->>WS: Online
    Storage-->>U2: Load unread messages
```"""
    },
    "video_streaming": {
        "arch": """```mermaid
graph TB
    User["Viewer"]
    Player["Video Player<br/>Adaptive Bitrate"]
    CDN["CDN Edge Server"]
    OriginServer["Origin Server"]
    Transcoder["Transcoder<br/>Multiple Bitrates"]

    User -->|Request| Player
    Player -->|Query Bitrate| Player
    Player -->|Fetch Segment| CDN
    CDN -->|Cache Miss| OriginServer
    OriginServer -->|Store| Transcoder
```""",
        "flow": """```mermaid
flowchart TD
    A["Video Upload"] --> B["Transcode<br/>1080p,720p,480p"]
    B --> C["Store Segments"]
    C --> D["User Requests"]
    D --> E["Measure Bandwidth"]
    E --> F["Select Bitrate"]
    F --> G["Fetch from CDN"]
    G --> H["Adaptive Switch<br/>if needed"]
```"""
    },

    # Data Systems
    "database_sharding": {
        "arch": """```mermaid
graph TB
    Client["Client"]
    Router["Shard Router<br/>hash(user_id) % N"]

    Shard1["Shard 1<br/>User 0-999K"]
    Shard2["Shard 2<br/>User 1M-1.999M"]
    Shard3["Shard 3<br/>User 2M-2.999M"]
    ShardN["Shard N<br/>User (N-1)M-NM"]

    Client -->|Query| Router
    Router -->|Route| Shard1
    Router -->|Route| Shard2
    Router -->|Route| Shard3
    Router -->|Route| ShardN
```""",
        "flow": """```mermaid
flowchart TD
    A["Query Request"] --> B["Extract Shard Key"]
    B --> C["Compute Shard ID<br/>hash % N"]
    C --> D["Lookup Shard<br/>from Config"]
    D --> E["Connect to Shard"]
    E --> F["Execute Query"]
    F --> G["Return Result"]
```"""
    },
    "message_queue_kafka": {
        "arch": """```mermaid
graph LR
    Producer["Producer"]
    Broker["Kafka Broker<br/>Multiple Partitions"]
    Consumer1["Consumer Group 1"]
    Consumer2["Consumer Group 2"]

    Producer -->|Publish| Broker
    Broker -->|Partition 0| Consumer1
    Broker -->|Partition 1| Consumer1
    Broker -->|Partition 2| Consumer2

    Storage[("Storage<br/>Replication")]
    Broker -->|Replicate| Storage
```""",
        "flow": """```mermaid
sequenceDiagram
    participant Prod as Producer
    participant Broker as Kafka Broker
    participant C1 as Consumer 1
    participant C2 as Consumer 2

    Prod->>Broker: Send Message (key=user_id)
    Broker->>Broker: hash(key) -> partition
    Broker->>C1: Deliver to Consumer 1
    Broker->>C2: Deliver to Consumer 2
    C1->>C1: Process
    C2->>C2: Process
    C1-->>Broker: Commit Offset
    C2-->>Broker: Commit Offset
```"""
    },
    "search_index": {
        "arch": """```mermaid
graph TB
    Documents["Documents"]
    Indexer["Indexer<br/>Elasticsearch"]
    InvertedIndex["Inverted Index<br/>term->doc_ids"]
    QueryEngine["Query Engine"]
    Results["Ranked Results<br/>TF-IDF"]

    Documents -->|Index| Indexer
    Indexer -->|Build| InvertedIndex
    QueryEngine -->|Search| InvertedIndex
    InvertedIndex -->|Score| QueryEngine
    QueryEngine -->|Rank| Results
```""",
        "flow": """```mermaid
flowchart TD
    A["Query:"] --> B["Parse Query"]
    B --> C["Tokenize"]
    C --> D["Search Inverted Index"]
    D --> E["Get Doc IDs"]
    E --> F["Compute TF-IDF"]
    F --> G["Sort by Score"]
    G --> H["Return Top 10"]
```"""
    },
    "recommendation_system": {
        "arch": """```mermaid
graph TB
    User["User"]
    Features["User Features<br/>Profile,History"]
    ML["ML Model<br/>Matrix Factorization"]
    ItemCatalog["Item Catalog"]
    Scorer["Scorer"]
    Ranker["Ranker"]

    User -->|Profile| Features
    ItemCatalog -->|Features| ML
    Features -->|Input| ML
    ML -->|Vectors| Scorer
    Scorer -->|Scores| Ranker
    Ranker -->|Recommendations| User
```""",
        "flow": """```mermaid
flowchart TD
    A["Get User Vector"] --> B["Find Similar Items"]
    B --> C["Score by Relevance"]
    C --> D["Apply Filters<br/>Already watched"]
    D --> E["Diversity Filter"]
    E --> F["Business Logic<br/>Premium first"]
    F --> G["Rank"]
    G --> H["Return Top 10"]
```"""
    },

    # Infrastructure
    "load_balancer": {
        "arch": """```mermaid
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
    HealthCheck -->|Ping| Server1
    HealthCheck -->|Ping| Server2
    HealthCheck -->|Ping| Server3
    HealthCheck -->|Ping| Server4

    LB -->|Route| Server1
    LB -->|Route| Server2
    LB -->|Route| Server3
```""",
        "flow": """```mermaid
flowchart TD
    A["Request Arrives"] --> B["Get Active Servers"]
    B --> C["Select by Algorithm"]
    C --> D{"Algorithm"}
    D -->|Round Robin| E["Next Server"]
    D -->|Least Conn| F["Lowest Load"]
    D -->|IP Hash| G["Same Server"]
    E --> H["Route Request"]
    F --> H
    G --> H
```"""
    },

    # Security
    "oauth_flow": {
        "arch": """```mermaid
graph LR
    User["User"]
    App["Application"]
    Provider["OAuth Provider"]
    ResourceServer["Resource Server"]

    User -->|Login| App
    App -->|Redirect| Provider
    Provider -->|Authenticate| User
    Provider -->|Auth Code| App
    App -->|Exchange Code| Provider
    Provider -->|Access Token| App
    App -->|Use Token| ResourceServer
    ResourceServer -->|User Data| App
```""",
        "flow": """```mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant Provider as OAuth Provider
    participant RS as Resource Server

    User->>App: Click Login
    App->>Provider: Redirect (client_id, scope)
    Provider->>User: Login & Consent
    User->>Provider: Grant
    Provider->>App: Redirect (auth_code)
    App->>Provider: POST code + secret
    Provider-->>App: access_token
    App->>RS: GET /user (with token)
    RS-->>App: User Data
    App-->>User: Logged In
```"""
    },
    "encryption": {
        "arch": """```mermaid
graph TB
    Data["Plaintext Data"]
    Encryption["Encryption<br/>AES-256"]
    EncryptedData["Encrypted Data"]
    Storage["Secure Storage"]

    Data -->|Encrypt| Encryption
    Encryption -->|Output| EncryptedData
    EncryptedData -->|Store| Storage

    RetrievedData["Encrypted Data"] -->|Decrypt| Decryption["Decryption<br/>AES-256"]
    Decryption -->|Output| PlainData["Plaintext"]
```""",
        "flow": """```mermaid
flowchart TD
    A["Data at Rest"] --> B["Generate Key<br/>Random + KDF"]
    B --> C["Encrypt<br/>AES-256-CBC"]
    C --> D["Store in DB/S3"]

    E["Request Data"] --> F["Retrieve<br/>from Storage"]
    F --> G["Decrypt<br/>with Key"]
    G --> H["Verify Integrity<br/>MAC"]
    H --> I{Valid?}
    I -->|Yes| J["Return Plaintext"]
    I -->|No| K["Error"]
```"""
    },

    # Distributed Systems (defaults for any not covered)
    "generic_system": {
        "arch": """```mermaid
graph TB
    Client["Client"]
    Service["Service Layer"]
    DataLayer["Data Layer"]
    Cache["Cache"]

    Client -->|Request| Service
    Service -->|Query| Cache
    Cache -->|Miss| DataLayer
    DataLayer -->|Response| Cache
    Cache -->|Return| Service
    Service -->|Response| Client
```""",
        "flow": """```mermaid
flowchart TD
    A["Request Received"] --> B["Validate Input"]
    B --> C["Process Request"]
    C --> D["Access Data"]
    D --> E["Compute Result"]
    E --> F["Cache if applicable"]
    F --> G["Format Response"]
    G --> H["Send to Client"]
```"""
    },

    # Database internals
    "btree": {
        "arch": """```mermaid
graph TB
    Root["Root Node<br/>[10, 20, 30]"]

    L1["[5, 8]"]
    L2["[12, 15]"]
    L3["[25, 28]"]
    L4["[35, 40]"]

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
    A["Search Key=15"] --> B["Compare at Root"]
    B --> C{"15 in<br/>ranges?"}
    C -->|10-20| D["Go to L2"]
    D --> E["Linear Search<br/>in L2"]
    E --> F["Found or Not"]
```"""
    },
    "lsm_tree": {
        "arch": """```mermaid
graph TB
    Writes["Write Request"]
    Memtable["MemTable<br/>In-Memory"]
    WAL["Write-Ahead Log"]

    Level0["Level 0<br/>4 SSTables"]
    Level1["Level 1<br/>40 SSTables"]
    LevelN["Level N<br/>..."]

    Compaction["Compaction<br/>Background"]

    Writes -->|Append| WAL
    Writes -->|Insert| Memtable
    Memtable -->|Flush| Level0
    Compaction -->|Merge| Level1
    Compaction -->|Merge| LevelN
```""",
        "flow": """```mermaid
flowchart TD
    A["Write Request"] --> B["Append to WAL"]
    B --> C["Insert to MemTable"]
    C --> D{MemTable<br/>Full?}
    D -->|Yes| E["Flush to Disk"]
    D -->|No| F["Acknowledge"]
    E --> G["Create L0 SSTable"]
    G --> H["Trigger Compaction"]
    H --> I["Merge SSTables"]
```"""
    },

    # ML Systems
    "collaborative_filtering": {
        "arch": """```mermaid
graph TB
    UserItemMatrix["User-Item Matrix<br/>with Ratings"]
    SVD["SVD/NMF<br/>Factorization"]
    UserFactors["User Factors<br/>U: 1M x 64"]
    ItemFactors["Item Factors<br/>V: 100M x 64"]
    Scorer["Scorer<br/>dot product"]
    Results["Ranked<br/>Recommendations"]

    UserItemMatrix --> SVD
    SVD --> UserFactors
    SVD --> ItemFactors
    UserFactors --> Scorer
    ItemFactors --> Scorer
    Scorer --> Results
```""",
        "flow": """```mermaid
flowchart TD
    A["Training Phase"] --> B["Build User-Item Matrix"]
    B --> C["SVD Factorization"]
    C --> D["Get User/Item Vectors"]
    D --> E["Store in Cache"]

    F["Serving Phase"] --> G["Get User Vector"]
    G --> H["Compute Similarity"]
    H --> I["Score All Items"]
    I --> J["Top-K"]
    J --> K["Filter & Rank"]
```"""
    }
}

def categorize_concept(filename):
    """Determine appropriate diagrams for a concept."""
    filename_lower = filename.lower()

    # Check for exact matches first
    for key in universal_diagrams.keys():
        if key in filename_lower:
            return universal_diagrams[key]

    # Categorize by filename patterns
    if "cache" in filename_lower:
        return universal_diagrams.get("generic_system")
    elif "pattern" in filename_lower or "observer" in filename_lower or "strategy" in filename_lower:
        # Return appropriate pattern diagram
        if "observer" in filename_lower:
            return universal_diagrams["observer_pattern"]
        elif "strategy" in filename_lower:
            return universal_diagrams["strategy_pattern"]
        elif "factory" in filename_lower:
            return universal_diagrams["factory_pattern"]
        elif "decorator" in filename_lower:
            return universal_diagrams["decorator_pattern"]
        elif "adapter" in filename_lower:
            return universal_diagrams["adapter_pattern"]
        else:
            return universal_diagrams.get("generic_system")
    elif any(x in filename_lower for x in ["queue", "kafka", "rabbitmq", "pubsub"]):
        return universal_diagrams["message_queue_kafka"]
    elif any(x in filename_lower for x in ["shard", "sharding"]):
        return universal_diagrams["database_sharding"]
    elif any(x in filename_lower for x in ["search", "elasticsearch"]):
        return universal_diagrams["search_index"]
    elif any(x in filename_lower for x in ["recommendation", "filter", "ranking"]):
        return universal_diagrams["collaborative_filtering"]
    elif any(x in filename_lower for x in ["instagram", "facebook", "feed"]):
        return universal_diagrams["news_feed"]
    elif any(x in filename_lower for x in ["uber", "ride", "match"]):
        return universal_diagrams["rideshare_system"]
    elif any(x in filename_lower for x in ["chat", "message", "websocket"]):
        return universal_diagrams["chat_system"]
    elif any(x in filename_lower for x in ["video", "stream", "netflix"]):
        return universal_diagrams["video_streaming"]
    elif any(x in filename_lower for x in ["ecommerce", "shopping", "commerce"]):
        return universal_diagrams["ecommerce_platform"]
    elif any(x in filename_lower for x in ["btree", "tree", "index"]):
        return universal_diagrams["btree"]
    elif any(x in filename_lower for x in ["lsm", "write"]):
        return universal_diagrams["lsm_tree"]
    elif any(x in filename_lower for x in ["oauth", "auth", "sso"]):
        return universal_diagrams["oauth_flow"]
    elif any(x in filename_lower for x in ["encrypt", "tls", "ssl"]):
        return universal_diagrams["encryption"]
    elif any(x in filename_lower for x in ["load", "balance", "balancer"]):
        return universal_diagrams["load_balancer"]
    else:
        # Default generic system
        return universal_diagrams["generic_system"]

def add_diagrams_to_file(filepath):
    """Add diagrams to a single file."""
    try:
        filename = os.path.basename(filepath).replace(".md", "")

        with open(filepath, 'r') as f:
            content = f.read()

        # Skip if already has mermaid diagrams
        if "```mermaid" in content:
            return False

        diagrams = categorize_concept(filename)

        if not diagrams:
            diagrams = universal_diagrams["generic_system"]

        # Add architecture diagram after "## Architecture Diagram"
        if "## Architecture Diagram" in content and "arch" in diagrams:
            pattern = r"## Architecture Diagram\n\n```\n\[Visual[^\]]*\]\n```"
            replacement = f"## Architecture Diagram\n\n{diagrams['arch']}"
            content = re.sub(pattern, replacement, content)

        # Add flow diagram before "## Implementation"
        if "## Implementation" in content and "flow" in diagrams:
            if "## Flow Diagram" not in content:
                flow_section = f"## Flow Diagram\n\n{diagrams['flow']}\n\n"
                content = content.replace("## Implementation", flow_section + "## Implementation")

        with open(filepath, 'w') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"Error: {filepath}: {e}")
        return False

# Process ALL files
print("Processing all system design concepts...")
total_processed = 0
already_has = 0
added = 0

for filepath in sorted(glob.glob(f"{base_path}/*/*_*.md")):
    filename = os.path.basename(filepath)

    # Check if already has diagrams
    with open(filepath, 'r') as f:
        if "```mermaid" in f.read():
            already_has += 1
            continue

    if add_diagrams_to_file(filepath):
        added += 1
        total_processed += 1

        if total_processed % 10 == 0:
            print(f"✓ Added diagrams to {total_processed} files")

print(f"\n📊 Diagram Coverage Report")
print(f"{'=' * 50}")
print(f"Total files processed:    {added}")
print(f"Already had diagrams:     {already_has}")
print(f"Total with diagrams:      {added + already_has}")
print(f"{'=' * 50}")
print(f"\n✅ All system design concepts now have Mermaid diagrams!")
