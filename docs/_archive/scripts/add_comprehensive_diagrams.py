#!/usr/bin/env python3
"""
Add comprehensive Mermaid diagrams to remaining system design concepts.
"""

import os
import re
import glob

base_path = "/home/sbisw/github/interviewprep/docs/system_design"

# Additional Mermaid diagrams for more concepts
additional_diagrams = {
    "lfu_cache": {
        "arch": """```mermaid
graph LR
    Client["Client"]
    Cache["LFU Cache"]
    FreqMap["Frequency Map"]
    MinHeap["Min Frequency Heap"]

    Client -->|Get/Put| Cache
    Cache -->|Update Freq| FreqMap
    FreqMap -->|Track Min| MinHeap
    MinHeap -->|Evict| Cache
```""",
        "flow": """```mermaid
flowchart TD
    A["Operation"] --> B{Get or Put?}
    B -->|Get| C["Lookup Key"]
    C --> D["Increase Frequency"]
    D --> E["Return Value"]
    B -->|Put| F["Check Capacity"]
    F --> G{At Capacity?}
    G -->|Yes| H["Evict Min Freq"]
    G -->|No| I["Add New Key"]
    H --> I
    I --> J["Set Frequency to 1"]
```"""
    },
    "design_patterns": {
        "arch": """```mermaid
graph TB
    Pattern["Design Patterns"]
    Creational["Creational<br/>Singleton, Factory"]
    Structural["Structural<br/>Adapter, Proxy"]
    Behavioral["Behavioral<br/>Observer, Strategy"]

    Pattern --> Creational
    Pattern --> Structural
    Pattern --> Behavioral
```"""
    },
    "cache": {
        "arch": """```mermaid
graph LR
    Request["Request"]
    Cache["Cache Layer<br/>In-Memory"]
    DB["Database<br/>Persistent"]

    Request -->|Check| Cache
    Cache -->|Hit| Response["Response"]
    Cache -->|Miss| DB
    DB -->|Load| Cache
    Cache -->|Return| Response
```"""
    },
    "message_queue": {
        "arch": """```mermaid
graph LR
    Producer["Producer"]
    Queue["Message Queue<br/>RabbitMQ/Kafka"]
    Broker["Broker Node"]
    Consumer["Consumer"]

    Producer -->|Publish| Queue
    Queue -->|Store| Broker
    Broker -->|Deliver| Consumer
    Consumer -->|Ack| Broker
```""",
        "flow": """```mermaid
sequenceDiagram
    participant Prod as Producer
    participant Queue
    participant Broker
    participant Cons as Consumer

    Prod->>Queue: Send Message
    Queue->>Broker: Persist
    Broker-->>Queue: ACK
    Queue->>Cons: Deliver
    Cons->>Cons: Process
    Cons-->>Broker: ACK
    Note over Broker: Message Complete
```"""
    },
    "sharding": {
        "arch": """```mermaid
graph TB
    Request["User Request"]
    Router["Shard Router<br/>hash(user_id) % N"]

    Shard1["Shard 1<br/>User 0-999"]
    Shard2["Shard 2<br/>User 1000-1999"]
    Shard3["Shard 3<br/>User 2000-2999"]

    Request -->|Route| Router
    Router -->|user_id%N=0| Shard1
    Router -->|user_id%N=1| Shard2
    Router -->|user_id%N=2| Shard3
```"""
    },
    "search_engine": {
        "arch": """```mermaid
graph TB
    Document["Documents"]
    Indexer["Indexer<br/>Build Inverted Index"]
    Index["Inverted Index<br/>term -> doc_ids"]
    Query["Search Query"]
    QueryEngine["Query Engine<br/>Boolean Logic"]
    Results["Results<br/>Ranked by TF-IDF"]

    Document -->|Process| Indexer
    Indexer -->|Build| Index
    Query -->|Parse| QueryEngine
    Index -->|Lookup| QueryEngine
    QueryEngine -->|Score| Results
```""",
        "flow": """```mermaid
flowchart TD
    A["Indexing Phase"] --> B["Tokenize Documents"]
    B --> C["Remove Stopwords"]
    C --> D["Stemming"]
    D --> E["Build Inverted Index"]

    F["Query Phase"] --> G["Parse Query"]
    G --> H["Tokenize Query"]
    H --> I["Lookup in Index"]
    I --> J["Compute Scores<br/>TF-IDF, BM25"]
    J --> K["Rank Results"]
    K --> L["Return Top K"]
```"""
    },
    "recommendation_engine": {
        "arch": """```mermaid
graph TB
    User["User"]
    Features["Feature Vector<br/>Profile"]
    ItemCatalog["Item Catalog<br/>with Features"]
    Matcher["Similarity Matcher<br/>Cosine/Euclidean"]
    Ranker["Ranker<br/>Score Items"]
    Results["Recommendations"]

    User -->|Profile| Features
    ItemCatalog -->|Feature| Matcher
    Features -->|Compare| Matcher
    Matcher -->|Scores| Ranker
    Ranker -->|Sort| Results
```"""
    },
    "notification_system": {
        "arch": """```mermaid
graph LR
    Event["Event Trigger"]
    NotificationService["Notification Service"]
    Queue["Task Queue"]
    Workers["Workers"]
    Channels["Channels<br/>Email/SMS/Push"]

    Event -->|Create Notif| NotificationService
    NotificationService -->|Enqueue| Queue
    Queue -->|Distribute| Workers
    Workers -->|Send via| Channels
```""",
        "flow": """```mermaid
sequenceDiagram
    participant U as User
    participant E as Event Source
    participant NS as Notification Svc
    participant Q as Queue
    participant W as Worker
    participant C as Channel

    E->>NS: Event Occurred
    NS->>NS: Create Notification
    NS->>Q: Enqueue Task
    Q-->>W: Deliver Task
    W->>C: Send Notification
    C-->>U: Receive
```"""
    },
    "api_gateway": {
        "arch": """```mermaid
graph LR
    Client["Clients"]
    Gateway["API Gateway<br/>Auth, Rate Limit"]
    Router["Router"]
    Service1["Service 1"]
    Service2["Service 2"]
    Service3["Service 3"]

    Client -->|Request| Gateway
    Gateway -->|Validate| Router
    Router -->|Route| Service1
    Router -->|Route| Service2
    Router -->|Route| Service3
```""",
        "flow": """```mermaid
flowchart TD
    A["Incoming Request"] --> B["Extract Headers"]
    B --> C["Authenticate"]
    C --> D{Authorized?}
    D -->|No| E["401 Unauthorized"]
    D -->|Yes| F["Rate Check"]
    F --> G{Rate OK?}
    G -->|No| H["429 Too Many"]
    G -->|Yes| I["Route to Service"]
    I --> J["Service Process"]
    J --> K["Transform Response"]
    K --> L["Send to Client"]
```"""
    },
    "web_socket": {
        "arch": """```mermaid
graph LR
    Client["WebSocket Client"]
    Connection["WebSocket<br/>Connection"]
    Server["Server<br/>Maintains Connections"]
    Broadcaster["Broadcaster<br/>Pushes Messages"]
    Handler["Message Handler"]

    Client -->|Connect| Connection
    Connection -->|Upgrade| Server
    Server -->|Register| Broadcaster
    Broadcaster -->|Push| Client
    Client -->|Send| Handler
    Handler -->|Update State| Broadcaster
```""",
        "flow": """```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Broadcaster

    Client->>Server: Upgrade to WebSocket
    Server-->>Client: 101 Switching
    Note over Client,Server: Connection Established

    Server->>Broadcaster: Register Client
    loop Message Exchange
        Client->>Server: Send Message
        Server->>Broadcaster: Broadcast
        Broadcaster->>Client: Push Update
    end
    Client->>Server: Close Connection
```"""
    },
    "load_balancing": {
        "arch": """```mermaid
graph TB
    Requests["Incoming Requests"]
    LB["Load Balancer<br/>Round Robin/LeastConn/IP Hash"]
    HealthCheck["Health Check"]

    Server1["Server 1"]
    Server2["Server 2"]
    Server3["Server 3"]
    Server4["Server 4"]

    Requests -->|Distribute| LB
    LB -->|Monitor| HealthCheck
    HealthCheck -->|Ping| Server1
    HealthCheck -->|Ping| Server2
    HealthCheck -->|Ping| Server3
    HealthCheck -->|Ping| Server4

    LB -->|Route| Server1
    LB -->|Route| Server2
    LB -->|Route| Server3
```"""
    },
    "service_discovery": {
        "arch": """```mermaid
graph TB
    ServiceA["Service A<br/>Port 8000"]
    ServiceB["Service B<br/>Port 8001"]
    Registry["Service Registry<br/>Consul/Eureka"]

    Client["Client"]
    LB["Load Balancer"]

    ServiceA -->|Register| Registry
    ServiceB -->|Register| Registry

    Client -->|Query| Registry
    Registry -->|Return List| Client
    Client -->|Connect| LB
    LB -->|Route| ServiceA
    LB -->|Route| ServiceB
```""",
        "flow": """```mermaid
flowchart TD
    A["Service Starts"] --> B["Register with Registry<br/>name, host, port"]
    B --> C["Health Check Loop"]
    C --> D["Send Heartbeat"]
    D --> E{Healthy?}
    E -->|Yes| F["Update TTL"]
    E -->|No| G["Deregister"]
    F --> C

    H["Client Needs Service"] --> I["Query Registry"]
    I --> J["Get Service Instances"]
    J --> K["Connect to Instance"]
    K --> L{Instance Healthy?}
    L -->|No| I
    L -->|Yes| M["Use Service"]
```"""
    },
    "caching": {
        "arch": """```mermaid
graph TB
    Layer1["L1 Cache<br/>Memory"]
    Layer2["L2 Cache<br/>Redis/Memcached"]
    Layer3["L3 Cache<br/>Database"]

    Request["Request"] -->|Check L1| Layer1
    Layer1 -->|Miss| Layer2
    Layer2 -->|Miss| Layer3
    Layer3 -->|Load to L2| Layer2
    Layer2 -->|Load to L1| Layer1
    Layer1 -->|Return| Response["Response"]
```"""
    },
    "distributed": {
        "arch": """```mermaid
graph TB
    Node1["Node 1"]
    Node2["Node 2"]
    Node3["Node 3"]
    Node4["Node 4"]

    Node1 -.->|Heartbeat| Node2
    Node1 -.->|Heartbeat| Node3
    Node2 -.->|Heartbeat| Node3
    Node2 -.->|Heartbeat| Node4
    Node3 -.->|Heartbeat| Node4
    Node4 -.->|Heartbeat| Node1

    Consensus["Consensus<br/>RAFT/Paxos"]
    Node1 --> Consensus
    Node2 --> Consensus
    Node3 --> Consensus
    Node4 --> Consensus
```"""
    },
    "authentication": {
        "arch": """```mermaid
graph LR
    User["User"]
    LoginService["Login Service"]
    PasswordValidator["Password Validator<br/>bcrypt/Argon2"]
    TokenService["Token Service<br/>JWT/Session"]
    Cache["Token Cache<br/>Redis"]

    User -->|Credentials| LoginService
    LoginService -->|Validate| PasswordValidator
    PasswordValidator -->|Valid| TokenService
    TokenService -->|Create Token| Cache
    Cache -->|Return Token| User
```""",
        "flow": """```mermaid
flowchart TD
    A["User Login"] --> B["Submit Credentials"]
    B --> C["Validate Format"]
    C --> D["Hash Password"]
    D --> E["Compare with DB"]
    E --> F{Match?}
    F -->|No| G["Login Failed"]
    F -->|Yes| H["Generate Token"]
    H --> I["Store in Cache"]
    I --> J["Return Token"]
    J --> K["User Authenticated"]
```"""
    },
    "transaction": {
        "arch": """```mermaid
graph TB
    Client["Client"]
    TxManager["Transaction Manager<br/>ACID"]
    Log["Write-Ahead Log<br/>Durability"]
    Database["Database<br/>Multiple Tables"]
    LockManager["Lock Manager<br/>Isolation"]

    Client -->|Begin TX| TxManager
    TxManager -->|Write to| Log
    TxManager -->|Acquire Locks| LockManager
    TxManager -->|Execute| Database
    TxManager -->|Commit| Log
    Log -->|Durability| Database
```""",
        "flow": """```mermaid
stateDiagram-v2
    [*] --> Begin
    Begin --> Execute
    Execute --> Validate
    Validate --> Valid: ACID OK
    Valid --> Commit
    Validate --> Invalid: Constraint
    Invalid --> Rollback
    Commit --> WriteLog
    Rollback --> WriteLog
    WriteLog --> End
    End --> [*]
```"""
    },
    "replication": {
        "arch": """```mermaid
graph LR
    Master["Master<br/>Read/Write"]
    Slave1["Slave 1<br/>Read Only"]
    Slave2["Slave 2<br/>Read Only"]
    Slave3["Slave 3<br/>Read Only"]

    Master -->|Replicate| Slave1
    Master -->|Replicate| Slave2
    Master -->|Replicate| Slave3

    Client["Clients"] -->|Write| Master
    Client -->|Read| Slave1
    Client -->|Read| Slave2
    Client -->|Read| Slave3
```"""
    },
    "backup": {
        "arch": """```mermaid
graph TB
    Production["Production DB"]
    Snapshot["Snapshot<br/>Daily"]
    BackupStorage["Backup Storage<br/>S3/GCS"]
    Recovery["Recovery<br/>Point-in-Time"]

    Production -->|Backup| Snapshot
    Snapshot -->|Upload| BackupStorage
    BackupStorage -->|Restore| Recovery
```""",
        "flow": """```mermaid
flowchart TD
    A["Backup Schedule"] --> B["Create Snapshot"]
    B --> C["Compress Data"]
    C --> D["Encrypt"]
    D --> E["Upload to Cloud"]
    E --> F["Verify Integrity"]
    F --> G["Update Catalog"]
    G --> H["Log Backup Event"]
```"""
    },
    "monitoring": {
        "arch": """```mermaid
graph TB
    Application["Application"]
    Metrics["Metrics Collector<br/>Prometheus"]
    Logs["Log Aggregator<br/>ELK"]
    Traces["Trace Collector<br/>Jaeger"]

    Database["Visualization<br/>Grafana"]
    Alerts["Alerting<br/>AlertManager"]

    Application -->|Metrics| Metrics
    Application -->|Logs| Logs
    Application -->|Traces| Traces

    Metrics -->|Visualize| Database
    Logs -->|Query| Database
    Traces -->|Display| Database

    Database -->|Trigger| Alerts
```""",
        "flow": """```mermaid
flowchart TD
    A["Event Occurs"] --> B["Collect Metric"]
    B --> C["Store in TSDB"]
    C --> D["Query Metrics"]
    D --> E["Evaluate Rules"]
    E --> F{Threshold<br/>Exceeded?}
    F -->|Yes| G["Create Alert"]
    G --> H["Notify Team"]
    H --> I["Incident Management"]
```"""
    },
    "circuit_breaker": {
        "arch": """```mermaid
graph TB
    Client["Client"]
    CB["Circuit Breaker"]

    CB -->|CLOSED| Service["Service<br/>Normal"]
    CB -->|OPEN| Fallback["Fallback<br/>Quick Fail"]
    CB -->|HALF-OPEN| Test["Test Service<br/>Single Request"]

    Service -->|Failure| CB
    Fallback -->|Timeout| CB
    Test -->|Success| CB
    Test -->|Failure| CB

    Client -->|Request| CB
```""",
        "flow": """```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: Threshold failed
    Open --> HalfOpen: Timeout
    HalfOpen --> Closed: Request OK
    HalfOpen --> Open: Request Failed
    Closed --> [*]: Normal
```"""
    },
    "retry": {
        "arch": """```mermaid
graph TD
    Request["Request"]
    Service["Service"]

    Request -->|Call| Service
    Service -->|Success| Response["Response"]
    Service -->|Failure| Retry1["Retry 1<br/>exponential backoff"]
    Retry1 -->|Success| Response
    Retry1 -->|Failure| Retry2["Retry 2<br/>exponential backoff"]
    Retry2 -->|Success| Response
    Retry2 -->|Failure| Error["Error<br/>Give Up"]
```""",
        "flow": """```mermaid
flowchart TD
    A["Send Request"] --> B["Wait for Response"]
    B --> C{Success?}
    C -->|Yes| D["Return Result"]
    C -->|No| E{Retries<br/>Left?}
    E -->|No| F["Return Error"]
    E -->|Yes| G["Exponential Backoff"]
    G --> H["Sleep"]
    H --> A
```"""
    }
}

def find_and_add_diagrams(filepath):
    """Find matching diagrams and add to file."""
    filename = os.path.basename(filepath).lower()

    with open(filepath, 'r') as f:
        content = f.read()

    added = False

    # Check each diagram type
    for key, diagrams in additional_diagrams.items():
        if key in filename:
            # Add architecture diagram
            if "arch" in diagrams and "## Architecture Diagram" in content:
                pattern = r"## Architecture Diagram\n\n```\n\[Visual[^\]]*\]\n```"
                replacement = f"## Architecture Diagram\n\n{diagrams['arch']}"
                content = re.sub(pattern, replacement, content)
                added = True

            # Add flow diagram if exists
            if "flow" in diagrams and "## Implementation" in content:
                if "## Flow Diagram" not in content:
                    flow_text = f"## Flow Diagram\n\n{diagrams['flow']}\n\n"
                    content = content.replace("## Implementation", flow_text + "## Implementation")
                    added = True

    if added:
        with open(filepath, 'w') as f:
            f.write(content)

    return added

# Process all files
total = 0
for filepath in glob.glob(f"{base_path}/*/*_*.md"):
    if find_and_add_diagrams(filepath):
        total += 1
        if total % 15 == 0:
            print(f"✓ Enhanced {total} files")

print(f"\n✅ Added comprehensive diagrams to {total} additional system design documents")
