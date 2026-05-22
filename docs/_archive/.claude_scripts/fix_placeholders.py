#!/usr/bin/env python3
"""Replace all placeholder text in system design files with topic-specific content."""
import os, re, glob

# ── Topic-specific requirements database ─────────────────────────────────────

TOPIC_DATA = {
    # 18-messaging-streaming
    "kafka_architecture": {
        "reqs": [
            "Publish messages from producer applications to partitioned topics",
            "Store message streams durably on disk with configurable retention (hours to forever)",
            "Enable multiple independent consumer groups to read at different offsets",
            "Replicate partitions across brokers for fault tolerance",
            "Support horizontal scaling by adding brokers and re-balancing partitions",
        ],
        "key_component": "broker leader", "important_property": "durability and ordering",
        "ops": [("Produce message", "O(1) amortized", "Batched appends to partition log"),
                ("Consume message", "O(1)", "Sequential read with offset tracking"),
                ("Topic creation", "O(B)", "Propagated to all B brokers via ZooKeeper/KRaft")],
    },
    "kafka_producers_consumers": {
        "reqs": [
            "Send messages to Kafka topics with optional key-based partitioning",
            "Configure acknowledgment levels (acks=0/1/all) per durability requirement",
            "Subscribe to topics via consumer groups with automatic partition assignment",
            "Track and commit consumer offsets for at-least-once or exactly-once delivery",
            "Handle rebalancing when consumers join or leave a consumer group",
        ],
        "key_component": "consumer group coordinator", "important_property": "exactly-once delivery",
        "ops": [("send()", "O(1)", "Async append to internal batch buffer"),
                ("poll()", "O(n)", "Fetch n records across assigned partitions"),
                ("commitSync()", "O(1)", "Persist offset to __consumer_offsets topic")],
    },
    "kafka_streams": {
        "reqs": [
            "Process and transform real-time streams using stateless and stateful operations",
            "Maintain local state stores (RocksDB) co-located with stream partitions",
            "Support windowed aggregations with tumbling, hopping, and sliding windows",
            "Handle out-of-order events using event-time semantics and watermarks",
            "Provide exactly-once processing guarantees end-to-end",
        ],
        "key_component": "state store", "important_property": "exactly-once semantics",
        "ops": [("map/filter", "O(n)", "Per-record stateless transformation"),
                ("aggregate (windowed)", "O(1) per record", "State store put per group key"),
                ("join streams", "O(1) per record", "Lookup in co-partitioned state store")],
    },
    "rabbitmq": {
        "reqs": [
            "Route messages from producers to queues via configurable exchanges",
            "Support multiple routing patterns: direct, topic, fanout, and headers",
            "Persist messages to disk for durability across broker restarts",
            "Deliver messages to competing consumers with acknowledgment tracking",
            "Implement dead-letter exchange routing for failed or expired messages",
        ],
        "key_component": "exchange", "important_property": "message routing correctness",
        "ops": [("Publish message", "O(1)", "Write to exchange, route to bound queues"),
                ("Basic consume", "O(1)", "Prefetch N messages from queue"),
                ("Queue declare", "O(1)", "Idempotent; creates if absent")],
    },
    "message_ordering": {
        "reqs": [
            "Guarantee FIFO ordering within a single partition or queue",
            "Provide per-key ordering for messages sharing the same routing key",
            "Detect and handle out-of-order message delivery via sequence numbers",
            "Support redelivery without breaking ordering for failed consumers",
            "Enable ordering across partitions via global sequence coordinators",
        ],
        "key_component": "partition key", "important_property": "strict ordering",
        "ops": [("Sequence assign", "O(1)", "Atomic increment per partition"),
                ("Reorder buffer flush", "O(k log k)", "Sort k buffered messages by sequence"),
                ("Gap detection", "O(1)", "Compare expected vs received sequence")],
    },
    "dead_letter_queues": {
        "reqs": [
            "Capture messages that fail processing after configurable retry attempts",
            "Preserve original message metadata (source queue, error reason, retry count)",
            "Route expired messages (TTL exceeded) to dead-letter destinations",
            "Allow manual inspection, replay, or discard of dead-letter messages",
            "Alert operations teams when dead-letter queue depth exceeds thresholds",
        ],
        "key_component": "retry policy", "important_property": "message recoverability",
        "ops": [("DLQ enqueue", "O(1)", "Append with error metadata after max retries"),
                ("DLQ replay", "O(n)", "Re-publish n messages to source queue"),
                ("DLQ purge", "O(n)", "Discard n dead messages from queue")],
    },
    "event_sourcing_kafka": {
        "reqs": [
            "Persist every state change as an immutable event in an append-only log",
            "Rebuild current state by replaying the event log from any offset",
            "Support multiple projections/views derived from the same event stream",
            "Enable time-travel queries by replaying events up to a given timestamp",
            "Produce commands and publish resulting events transactionally",
        ],
        "key_component": "event log (Kafka topic)", "important_property": "event immutability",
        "ops": [("Append event", "O(1)", "Sequential write to partition"),
                ("Replay from offset", "O(n)", "Sequential reads; n = events to replay"),
                ("Snapshot state", "O(S)", "Serialize S fields of aggregate state")],
    },
    "exactly_once_semantics": {
        "reqs": [
            "Assign each producer a unique producer ID and track epoch to detect zombies",
            "Sequence messages with monotonically increasing sequence numbers per partition",
            "Atomically commit offsets and output records in a single transaction",
            "Abort in-flight transactions and fence zombie producers on failover",
            "Provide idempotent producer guarantees with exactly-once end-to-end",
        ],
        "key_component": "transaction coordinator", "important_property": "idempotency",
        "ops": [("initTransactions()", "O(1)", "Register producer ID with coordinator"),
                ("commitTransaction()", "O(P)", "Write commit markers to P partitions"),
                ("abortTransaction()", "O(P)", "Write abort markers; offsets not advanced")],
    },
    "kafka_connect": {
        "reqs": [
            "Ingest data from external systems (databases, files, APIs) into Kafka topics",
            "Export data from Kafka topics to external sinks (databases, object storage)",
            "Run connectors in distributed mode across a Connect worker cluster",
            "Track source offsets and sink positions for exactly-once or at-least-once delivery",
            "Provide REST API for connector lifecycle management (create, pause, restart, delete)",
        ],
        "key_component": "connector", "important_property": "offset tracking",
        "ops": [("Source poll()", "O(n)", "Fetch n records from source system"),
                ("Sink put()", "O(n)", "Write n records to sink system"),
                ("Offset commit", "O(1)", "Persist source position to internal topic")],
    },
    "stream_processing": {
        "reqs": [
            "Ingest continuous event streams from multiple sources in real time",
            "Apply stateless transformations (filter, map, project) with sub-millisecond latency",
            "Perform stateful aggregations (count, sum, join) over time windows",
            "Emit results downstream as new streams or to sink systems",
            "Recover state and resume processing automatically after failures",
        ],
        "key_component": "stream processor", "important_property": "low-latency throughput",
        "ops": [("Filter/Map", "O(1) per event", "Stateless; no storage needed"),
                ("Windowed aggregate", "O(1) per event", "State store update per key"),
                ("Stream-stream join", "O(1) per event", "Probe co-partitioned state store")],
    },
    "rabbitmq_advanced_patterns": {
        "reqs": [
            "Implement topic-based routing with wildcard exchange bindings",
            "Support priority queues where high-priority messages preempt lower-priority ones",
            "Enable delayed messaging using TTL and dead-letter exchange chaining",
            "Provide message deduplication using idempotency keys",
            "Support publish-subscribe fan-out to multiple independent consumers",
        ],
        "key_component": "exchange binding", "important_property": "routing correctness",
        "ops": [("Publish to fanout", "O(B)", "Copy to B bound queues"),
                ("Priority dequeue", "O(log Q)", "Heap-based priority selection"),
                ("Delayed re-queue", "O(1)", "TTL expiry routes to DLX target queue")],
    },
    "redis_streams": {
        "reqs": [
            "Append time-ordered entries to named streams with auto-generated IDs",
            "Support consumer groups with per-consumer message tracking and acknowledgment",
            "Allow range and reverse-range queries over stream entries by ID or time",
            "Trim streams by length or age to bound memory usage",
            "Replay unacknowledged messages (PEL — Pending Entry List) on consumer failure",
        ],
        "key_component": "consumer group", "important_property": "message acknowledgment",
        "ops": [("XADD", "O(1)", "Append entry; amortized O(1) with MAXLEN"),
                ("XREADGROUP", "O(n)", "Read n messages into consumer's PEL"),
                ("XACK", "O(1)", "Remove from PEL after successful processing")],
    },
    "google_cloud_pubsub": {
        "reqs": [
            "Publish messages to topics with at-least-once delivery guarantees",
            "Route messages to multiple independent subscriptions per topic",
            "Support push (HTTP webhook) and pull (polling) delivery modes per subscription",
            "Retain undelivered messages for up to 7 days with configurable deadlines",
            "Filter messages at subscription level to reduce unnecessary delivery",
        ],
        "key_component": "subscription", "important_property": "at-least-once delivery",
        "ops": [("Publish", "O(1)", "Async; message stored and replicated globally"),
                ("Pull", "O(n)", "Return up to n messages; client acks each"),
                ("Acknowledge", "O(1)", "Remove message from subscription backlog")],
    },
    "aws_kinesis_streams": {
        "reqs": [
            "Ingest real-time streaming data from multiple producer sources at scale",
            "Partition data across shards for parallel ingestion and processing",
            "Deliver records to consumers with configurable retention (24h–365 days)",
            "Support enhanced fan-out for dedicated throughput per consumer",
            "Enable server-side encryption (KMS) for data at rest in shards",
        ],
        "key_component": "shard", "important_property": "ordered delivery per shard",
        "ops": [("PutRecord", "O(1)", "Route to shard by partition key hash"),
                ("GetRecords", "O(n)", "Sequential read up to 10MB per shard/sec"),
                ("UpdateShardCount", "O(S)", "Merge/split S shards; ~30s operation")],
    },
    "mqtt_protocol_and_iot": {
        "reqs": [
            "Connect millions of IoT devices over low-bandwidth, unreliable networks",
            "Support three QoS levels: fire-and-forget, at-least-once, exactly-once",
            "Route telemetry messages from devices to topic-based subscribers",
            "Persist last-known-value messages (retained) for new subscribers",
            "Notify subscribers of device disconnection via Last Will and Testament (LWT)",
        ],
        "key_component": "MQTT broker", "important_property": "low-bandwidth efficiency",
        "ops": [("PUBLISH (QoS 0)", "O(1)", "Fire-and-forget; no acknowledgment"),
                ("PUBLISH (QoS 1)", "O(1)+1RTT", "Broker acks; client retries until acked"),
                ("SUBSCRIBE", "O(T)", "Match against T topic filter patterns")],
    },
    "amqp_advanced_messaging": {
        "reqs": [
            "Establish authenticated, encrypted AMQP connections with virtual host isolation",
            "Declare exchanges and queues with durability, exclusive, and auto-delete flags",
            "Route messages from exchanges to queues via configurable binding rules",
            "Support transactional message publishing with rollback on failure",
            "Enable consumer flow control via channel prefetch (basic.qos)",
        ],
        "key_component": "channel", "important_property": "transactional publish",
        "ops": [("basic.publish", "O(1)", "Write to exchange; async routing to queue"),
                ("basic.consume", "O(1)", "Register consumer tag on queue"),
                ("tx.commit", "O(n)", "Flush n buffered publishes atomically")],
    },
    "grpc_streaming": {
        "reqs": [
            "Define service contracts in Protocol Buffers with strongly-typed messages",
            "Support four communication patterns: unary, server-streaming, client-streaming, bidirectional",
            "Multiplex multiple RPC calls over a single HTTP/2 connection",
            "Propagate deadlines and cancellation signals across service boundaries",
            "Apply per-RPC and per-connection interceptors for auth, logging, and tracing",
        ],
        "key_component": "gRPC channel (HTTP/2 connection)", "important_property": "low-latency multiplexing",
        "ops": [("Unary RPC", "O(1)", "Single request-response; ~1ms overhead"),
                ("Server stream", "O(n)", "n messages sent without extra handshakes"),
                ("Bidirectional stream", "O(n+m)", "n client + m server messages interleaved")],
    },
    "idempotency_in_messaging": {
        "reqs": [
            "Assign globally unique idempotency keys to each message or request",
            "Store processed message IDs in a deduplication store (Redis, DB) with TTL",
            "Detect duplicate deliveries and return cached responses without reprocessing",
            "Ensure idempotency across retries caused by network failures or timeouts",
            "Clear expired deduplication keys to bound storage growth",
        ],
        "key_component": "deduplication store", "important_property": "idempotent processing",
        "ops": [("Check duplicate", "O(1)", "Redis GET by idempotency key"),
                ("Mark processed", "O(1)", "Redis SETEX with TTL after processing"),
                ("Dedup cache eviction", "O(1) amortized", "TTL expiry by Redis background thread")],
    },
    "message_batching_and_aggregation": {
        "reqs": [
            "Buffer individual messages into batches to reduce network round-trips",
            "Flush batches based on configurable size (bytes) and time (linger_ms) thresholds",
            "Compress batches using LZ4, Snappy, or ZSTD before network transmission",
            "Aggregate stream records into micro-batches for downstream processing",
            "Track per-batch delivery status and retry failed batches atomically",
        ],
        "key_component": "batch buffer", "important_property": "throughput vs latency tradeoff",
        "ops": [("Buffer message", "O(1)", "Append to in-memory batch accumulator"),
                ("Flush batch", "O(n)", "Serialize, compress, and send n messages"),
                ("Aggregate window", "O(n)", "Reduce n records into summary metrics")],
    },
    "backpressure_and_flow_control": {
        "reqs": [
            "Signal upstream producers to slow down when consumer queues are full",
            "Implement credit-based flow control to match producer rate to consumer capacity",
            "Apply back-pressure at each stage in a processing pipeline automatically",
            "Drop or reject messages with configurable policies (drop-oldest, reject-latest)",
            "Monitor queue depths and emit alerts when back-pressure is sustained",
        ],
        "key_component": "bounded queue", "important_property": "system stability under overload",
        "ops": [("Producer send (blocked)", "O(1)", "Block until queue has capacity"),
                ("Consumer drain", "O(n)", "Process n messages, freeing n slots"),
                ("Queue depth check", "O(1)", "Atomic compare of current vs max size")],
    },
    "message_ordering_guarantees": {
        "reqs": [
            "Guarantee per-key ordering by routing same-key messages to the same partition",
            "Assign monotonically increasing sequence numbers within each partition",
            "Buffer out-of-order arrivals and release them in order via reorder buffers",
            "Handle producer retries without reordering (idempotent producer with sequence numbers)",
            "Support global ordering when required via a single-partition topic or sequencer service",
        ],
        "key_component": "partition key hash", "important_property": "strict per-key ordering",
        "ops": [("Assign sequence", "O(1)", "Atomic partition-level counter increment"),
                ("Reorder buffer insert", "O(log k)", "Insert into sorted set of k buffered msgs"),
                ("In-order release", "O(1)", "Dequeue when head sequence matches expected")],
    },
    "message_transformations": {
        "reqs": [
            "Apply stateless transformations (filter, map, enrich) to message content",
            "Convert message formats between schemas (Avro, JSON, Protobuf) on-the-fly",
            "Enrich messages with external data from lookup tables or APIs",
            "Split compound messages into individual records for downstream processing",
            "Route transformed messages to different topics based on content rules",
        ],
        "key_component": "transformation pipeline", "important_property": "schema compatibility",
        "ops": [("Map/Filter", "O(1) per message", "Stateless record-by-record transformation"),
                ("Schema convert", "O(F)", "Serialize/deserialize F fields"),
                ("Content-based route", "O(R)", "Evaluate R routing rules per message")],
    },
    "stateful_stream_processing": {
        "reqs": [
            "Maintain per-key state (counters, aggregates, joins) across message streams",
            "Checkpoint state to durable storage for fault-tolerant recovery",
            "Support windowed state with configurable eviction policies",
            "Handle late-arriving events with configurable grace periods",
            "Provide consistent exactly-once state updates across failures and restarts",
        ],
        "key_component": "state store (RocksDB)", "important_property": "fault-tolerant state consistency",
        "ops": [("State get/put", "O(1)", "Local RocksDB lookup by key"),
                ("Window evict", "O(W)", "Remove W expired window entries"),
                ("Checkpoint flush", "O(S)", "Snapshot S bytes of state to object storage")],
    },
    "changelog_streams_and_compaction": {
        "reqs": [
            "Retain only the latest value per key by compacting older records with same key",
            "Emit changelog events to downstream consumers before and after state changes",
            "Enable efficient bootstrapping of state stores by replaying compacted topics",
            "Support tombstone records (null value) to signal key deletion in compacted logs",
            "Configure compaction frequency and minimum compaction ratio per topic",
        ],
        "key_component": "log compaction cleaner", "important_property": "space reclamation with latest-value retention",
        "ops": [("Append record", "O(1)", "Write to active segment"),
                ("Log compact", "O(N)", "Scan N records; deduplicate by key"),
                ("Read latest value", "O(1)", "Seek to key offset in compacted log")],
    },
    "messaging_system_monitoring": {
        "reqs": [
            "Track consumer group lag (messages behind head) per topic and partition",
            "Expose broker throughput, CPU, disk I/O, and network metrics via JMX/Prometheus",
            "Alert on sustained consumer lag growth, under-replicated partitions, or leader election storms",
            "Provide end-to-end message latency tracing from produce to consume",
            "Visualize message flow, partition distribution, and replication health in dashboards",
        ],
        "key_component": "metrics exporter (JMX/Prometheus)", "important_property": "real-time observability",
        "ops": [("Lag calculation", "O(P)", "Log-end-offset minus committed offset per P partitions"),
                ("Metric scrape", "O(M)", "Collect M broker metrics per scrape interval"),
                ("Alert evaluate", "O(A)", "Check A alert rules against current metrics")],
    },
    "multi-tenancy_in_messaging": {
        "reqs": [
            "Isolate tenant data via namespace-scoped topics with separate ACLs",
            "Enforce per-tenant quotas on producer throughput, consumer rate, and storage",
            "Provide tenant-level encryption with separate key hierarchies",
            "Bill tenants based on messages produced, consumed, and bytes stored",
            "Support tenant onboarding and offboarding without cluster downtime",
        ],
        "key_component": "namespace quota enforcer", "important_property": "tenant isolation",
        "ops": [("Quota check", "O(1)", "Token bucket check per tenant ID"),
                ("Namespace create", "O(B)", "Propagate namespace to B brokers"),
                ("Tenant usage report", "O(T×P)", "Aggregate T tenants × P partitions")],
    },
    "disaster_recovery_for_messaging": {
        "reqs": [
            "Replicate topics across geographically separated clusters (MirrorMaker, Confluent Replicator)",
            "Maintain consumer offset mappings between primary and DR clusters",
            "Detect primary cluster failure and trigger controlled failover within RTO",
            "Resume consumer groups from translated offsets with minimal data loss (RPO)",
            "Validate DR readiness with automated failover drills",
        ],
        "key_component": "cross-cluster replicator", "important_property": "low RPO/RTO",
        "ops": [("Replicate partition", "O(n)", "Consume n records from source, produce to DR"),
                ("Offset translate", "O(1)", "Map source offset to DR equivalent"),
                ("Failover trigger", "O(P)", "Reassign P partition leaders on DR cluster")],
    },
    "schema_registry_and_schema_evolution": {
        "reqs": [
            "Store and version Avro, JSON Schema, or Protobuf schemas with unique IDs",
            "Enforce backward, forward, or full schema compatibility on schema registration",
            "Embed schema ID in every message to enable schema-on-read deserialization",
            "Allow adding optional fields (backward-compatible) without breaking consumers",
            "Support schema deletion with configurable soft-delete retention",
        ],
        "key_component": "schema registry", "important_property": "schema compatibility enforcement",
        "ops": [("Register schema", "O(1)", "Store schema; check compatibility with previous"),
                ("Lookup by ID", "O(1)", "Cache hit after first fetch per schema ID"),
                ("Compatibility check", "O(F²)", "Compare F fields between schema versions")],
    },
    "exactly-once_semantics_(eos)": {
        "reqs": [
            "Guarantee no duplicate records in output even with producer retries or broker failover",
            "Use idempotent producer (PID + sequence number) to deduplicate at broker level",
            "Wrap consume-transform-produce in Kafka transactions for atomic delivery",
            "Fence zombie producer instances using epoch-based fencing",
            "Validate end-to-end exactly-once using record count reconciliation",
        ],
        "key_component": "transaction coordinator", "important_property": "idempotent exactly-once delivery",
        "ops": [("Idempotent produce", "O(1)", "Broker deduplicates by PID+sequence"),
                ("Begin transaction", "O(1)", "Coordinator registers transaction state"),
                ("Commit transaction", "O(P+G)", "Write commit markers to P partitions, G groups")],
    },
    "message_deduplication_strategies": {
        "reqs": [
            "Assign deterministic deduplication keys to messages at the producer side",
            "Store seen message IDs in a fast lookup store (Redis Bloom filter or SET)",
            "Reject duplicate messages within a configurable deduplication window",
            "Handle deduplication across consumer restarts using persistent ID store",
            "Expire deduplication records after window to bound storage consumption",
        ],
        "key_component": "deduplication key store", "important_property": "duplicate elimination within window",
        "ops": [("Check duplicate", "O(1)", "Redis GET or Bloom filter probe"),
                ("Register seen ID", "O(1)", "Redis SET with TTL expiry"),
                ("Window cleanup", "O(D)", "Expire D old entries after TTL")],
    },
    "kafka_connect_and_integration": {
        "reqs": [
            "Deploy source connectors to stream CDC events from relational databases to Kafka",
            "Deploy sink connectors to write Kafka topic data to data warehouses or object stores",
            "Manage connector lifecycle (create, pause, resume, delete) via REST API",
            "Handle schema evolution automatically when upstream database schemas change",
            "Scale connector tasks horizontally across Connect worker nodes",
        ],
        "key_component": "Kafka Connect worker", "important_property": "schema-aware data pipeline",
        "ops": [("Source task poll", "O(n)", "Fetch n CDC events from source DB"),
                ("Sink task put", "O(n)", "Write n records to sink system"),
                ("Task rebalance", "O(T/W)", "Distribute T tasks across W workers")],
    },
    "change_data_capture_(cdc)": {
        "reqs": [
            "Capture row-level INSERT, UPDATE, and DELETE events from database transaction logs",
            "Stream CDC events to Kafka topics with schema information via Debezium",
            "Preserve transaction boundaries and ordering within the changelog stream",
            "Enable downstream consumers to maintain eventually consistent read models",
            "Support initial snapshot bootstrapping for new consumers",
        ],
        "key_component": "log-based CDC connector (Debezium)", "important_property": "low-latency change capture",
        "ops": [("Read WAL/binlog", "O(1) per tx", "Stream changes as they are committed"),
                ("Schema inference", "O(C)", "Parse C column definitions from DB metadata"),
                ("Initial snapshot", "O(R)", "Full table scan of R rows at snapshot time")],
    },
    "real-time_analytics_with_streaming": {
        "reqs": [
            "Ingest high-volume event streams into a streaming analytics engine",
            "Compute real-time aggregates (counts, sums, percentiles) over sliding windows",
            "Join streaming data with static reference tables for enrichment",
            "Persist aggregated results to OLAP stores for dashboard queries",
            "Emit alerts when streaming metrics breach configurable thresholds",
        ],
        "key_component": "streaming aggregation engine", "important_property": "sub-second analytics latency",
        "ops": [("Ingest event", "O(1)", "Append to in-memory window buffer"),
                ("Window aggregate", "O(W)", "Reduce W events in window per key"),
                ("OLAP upsert", "O(1)", "Write pre-aggregated row to columnar store")],
    },
    "distributed_tracing_in_messaging": {
        "reqs": [
            "Inject trace context (trace ID, span ID) into message headers on publish",
            "Extract and propagate trace context on consume to link spans across services",
            "Record producer and consumer spans with latency, queue depth, and lag metadata",
            "Visualize end-to-end message latency from produce to consumer acknowledgment",
            "Support W3C TraceContext and B3 propagation formats",
        ],
        "key_component": "trace context propagator", "important_property": "end-to-end traceability",
        "ops": [("Inject context", "O(1)", "Write trace headers into message metadata"),
                ("Extract context", "O(1)", "Parse trace headers on consumer side"),
                ("Export span", "O(1) async", "Buffer and send to tracing backend")],
    },
    "circuit_breakers_for_messaging": {
        "reqs": [
            "Monitor downstream consumer error rates and latency per messaging endpoint",
            "Open circuit when error threshold is breached, fast-failing new messages",
            "Allow periodic probe requests in half-open state to test recovery",
            "Close circuit and resume full traffic when probes succeed consistently",
            "Emit circuit state change events for observability and alerting",
        ],
        "key_component": "circuit breaker state machine", "important_property": "fast-fail under degradation",
        "ops": [("Record outcome", "O(1)", "Sliding window counter update"),
                ("State transition", "O(1)", "CLOSED→OPEN or HALF-OPEN→CLOSED check"),
                ("Probe request", "O(1)", "Single test message to consumer endpoint")],
    },
    "geo-distributed_messaging": {
        "reqs": [
            "Replicate message streams across geographically separated data centers",
            "Route producer writes to the nearest regional cluster to minimize latency",
            "Enable consumers in each region to read from a local replica",
            "Resolve cross-region write conflicts using vector clocks or last-writer-wins",
            "Ensure global ordering within partitions using a designated primary region",
        ],
        "key_component": "geo-replication bridge", "important_property": "low cross-region write latency",
        "ops": [("Local produce", "O(1)", "Write to regional cluster partition"),
                ("Cross-region replicate", "O(n)", "Mirror n records to remote cluster"),
                ("Offset reconcile", "O(P)", "Align P partition offsets across regions")],
    },
    "message_expiration_and_ttl": {
        "reqs": [
            "Set per-message or per-queue TTL to automatically expire stale messages",
            "Route expired messages to dead-letter exchange/topic for inspection",
            "Compact log-based topics by time (retention.ms) or size (retention.bytes)",
            "Prevent expired messages from being delivered to consumers",
            "Notify producers when their messages have been discarded due to TTL",
        ],
        "key_component": "expiration checker / TTL enforcement", "important_property": "bounded queue depth",
        "ops": [("Set message TTL", "O(1)", "Store expiry timestamp in message header"),
                ("Expiry scan", "O(E)", "Check E messages near front of queue"),
                ("Log segment trim", "O(S)", "Delete S log segments beyond retention window")],
    },
    "performance_tuning_for_brokers": {
        "reqs": [
            "Tune producer batch size and linger time to maximize throughput",
            "Configure optimal number of partitions to parallelize both produce and consume",
            "Size broker JVM heap and off-heap (page cache) for optimal I/O performance",
            "Apply OS-level tuning (tcp_rmem/wmem, vm.dirty_ratio, noatime mounts)",
            "Benchmark and profile broker under realistic workloads with different codec settings",
        ],
        "key_component": "page cache and I/O scheduler", "important_property": "sustained high throughput",
        "ops": [("Batch produce", "O(n/B)", "n messages in B-sized batches reduces RTTs"),
                ("Zero-copy sendfile", "O(1)", "Kernel DMA bypasses user-space copy"),
                ("Partition rebalance", "O(P×B)", "Reassign P partitions across B brokers")],
    },
    "consumer_lag_and_catchup": {
        "reqs": [
            "Measure consumer lag as difference between log-end-offset and committed offset",
            "Alert when lag exceeds configurable thresholds or grows continuously",
            "Scale consumer group horizontally by adding partitions and consumer instances",
            "Implement catch-up replay mode using increased fetch size and parallelism",
            "Prioritize fresh messages over catching up when lag is within acceptable bounds",
        ],
        "key_component": "consumer group lag monitor", "important_property": "lag convergence to zero",
        "ops": [("Lag calculation", "O(P)", "Subtract offsets across P partitions"),
                ("Consumer scale-out", "O(P/N)", "Redistribute P partitions across N consumers"),
                ("Catch-up fetch", "O(n)", "Fetch n records in large batches to reduce RTTs")],
    },
    "transactional_outbox_pattern": {
        "reqs": [
            "Write domain events to an outbox table in the same database transaction as business data",
            "Poll or tail the outbox table to relay events to the message broker reliably",
            "Guarantee at-least-once event delivery even if the relay process crashes mid-publish",
            "De-duplicate events on the consumer side using event IDs",
            "Archive or delete successfully relayed outbox rows to prevent unbounded growth",
        ],
        "key_component": "outbox table relay (CDC or polling)", "important_property": "dual-write atomicity",
        "ops": [("Write to outbox", "O(1)", "INSERT in same local DB transaction"),
                ("Relay poll", "O(n)", "SELECT n unrelayed rows; publish; mark sent"),
                ("Outbox cleanup", "O(n)", "DELETE n old sent rows in background batch")],
    },

    # 10-advanced-algorithms (original 5 files)
    "consistent_hashing": {
        "reqs": [
            "Distribute keys across a ring of virtual nodes using a deterministic hash function",
            "Add or remove nodes while minimizing key remapping (only K/N keys reassigned)",
            "Replicate each key to R successor nodes for fault tolerance",
            "Route client requests to the responsible node with O(log N) lookup",
            "Rebalance key distribution automatically when nodes join or leave",
        ],
        "key_component": "hash ring", "important_property": "minimal remapping on topology change",
        "ops": [("Key lookup", "O(log N)", "Binary search on sorted ring of N virtual nodes"),
                ("Node add", "O(K/N + log N)", "Rehash K/N keys; insert N virtual nodes"),
                ("Node remove", "O(K/N + log N)", "Reassign K/N keys to successor node")],
    },
    "geohashing": {
        "reqs": [
            "Encode latitude/longitude pairs into a fixed-length alphanumeric string",
            "Support configurable precision levels (1–12 characters) for different granularity",
            "Enable proximity queries by returning the 8 neighboring geohash cells",
            "Index geohash strings in a database for efficient prefix-based range queries",
            "Support radius search by selecting cells within a bounding box",
        ],
        "key_component": "geohash index", "important_property": "spatial locality preservation",
        "ops": [("Encode lat/lon", "O(P)", "P = precision bits; interleave coordinates"),
                ("Neighbor lookup", "O(1)", "Return 8 adjacent cells for given geohash"),
                ("Radius search", "O(k log n)", "Query k cells; n = indexed points")],
    },
    "trie_data_structure": {
        "reqs": [
            "Insert words character-by-character into a tree of nodes",
            "Search for exact words and detect prefix membership efficiently",
            "Support autocomplete by traversing all paths below a prefix node",
            "Delete words by removing leaf nodes and pruning empty branches",
            "Store metadata at terminal nodes for ranked suggestions",
        ],
        "key_component": "trie node", "important_property": "O(m) operations independent of corpus size",
        "ops": [("Insert word", "O(m)", "m = word length; create m nodes if absent"),
                ("Search exact", "O(m)", "Traverse m edges; check is_end flag"),
                ("Prefix autocomplete", "O(m + k)", "Traverse m; enumerate k matching words")],
    },
    "hyperloglog": {
        "reqs": [
            "Estimate cardinality of large multisets within 0.81–2% standard error",
            "Use constant memory (12KB for 2% error, 1.5KB for 3%) regardless of set size",
            "Support merge of multiple HyperLogLog sketches for distributed counting",
            "Provide count-distinct estimates suitable for unique visitor, session, and query counting",
            "Tolerate streaming updates without storing individual elements",
        ],
        "key_component": "register array (m buckets)", "important_property": "O(1) memory per counter",
        "ops": [("Add element", "O(1)", "Hash element; update register maximum leading zeros"),
                ("Estimate cardinality", "O(m)", "Harmonic mean of m register values"),
                ("Merge sketches", "O(m)", "Take element-wise max of m registers")],
    },
    "simulation_algorithms": {
        "reqs": [
            "Model stochastic systems by sampling from defined probability distributions",
            "Perform Monte Carlo integration to estimate expected values over complex domains",
            "Simulate discrete-event systems (queues, networks) with event-driven scheduling",
            "Generate reproducible results with configurable random seeds",
            "Parallelize independent simulation runs across CPU cores",
        ],
        "key_component": "random number generator (RNG)", "important_property": "statistical accuracy with bounded variance",
        "ops": [("Sample draw", "O(1)", "Inverse-CDF or rejection sampling"),
                ("MC estimate", "O(N)", "Average N samples; error ∝ 1/√N"),
                ("Event simulation step", "O(log E)", "Pop min-time event from priority queue of E events")],
    },

    # 11-advanced-patterns (original 6 files)
    "proxy_pattern": {
        "reqs": [
            "Intercept calls to a real subject through an interface-compatible proxy object",
            "Add cross-cutting concerns (access control, caching, logging) without modifying the subject",
            "Support lazy initialization by creating the real subject only when first needed",
            "Enable remote proxies to transparently communicate with objects in other processes",
            "Allow virtual proxies to defer expensive object creation until first use",
        ],
        "key_component": "proxy interface", "important_property": "transparency to the client",
        "ops": [("Proxy method call", "O(1) overhead", "Delegate to real subject after pre-processing"),
                ("Cache check", "O(1)", "Return cached result if valid; else forward"),
                ("Access control", "O(R)", "Evaluate R permission rules per call")],
    },
    "composite_pattern": {
        "reqs": [
            "Represent part-whole hierarchies in a uniform tree structure",
            "Allow clients to treat individual objects and compositions identically via a common interface",
            "Support recursive operations (render, calculate, validate) on nested composites",
            "Enable dynamic addition and removal of child components at runtime",
            "Provide safe navigation of the composite tree with type-checked child access",
        ],
        "key_component": "component interface", "important_property": "uniform leaf/composite treatment",
        "ops": [("add(child)", "O(1)", "Append child reference to composite's children list"),
                ("remove(child)", "O(n)", "Linear scan and remove from n children"),
                ("operation() (recursive)", "O(N)", "Visit all N nodes in subtree")],
    },
    "template_method": {
        "reqs": [
            "Define the skeleton of an algorithm in a base class with fixed step ordering",
            "Allow subclasses to override specific steps without changing the overall structure",
            "Mark invariant steps as final and variable steps as abstract or hook methods",
            "Prevent code duplication by centralizing the algorithm skeleton in one place",
            "Support optional hook methods with default no-op implementations in the base class",
        ],
        "key_component": "abstract base class template", "important_property": "algorithm skeleton immutability",
        "ops": [("templateMethod()", "O(S)", "Execute all S fixed + variable steps in order"),
                ("primitiveOperation()", "O(1)", "Subclass-specific step implementation"),
                ("hook()", "O(1)", "Optional override; default is no-op")],
    },
    "chain_of_responsibility": {
        "reqs": [
            "Pass a request along a linked chain of handlers until one handles it",
            "Allow handlers to be added, removed, or reordered without changing client code",
            "Give each handler the option to pass the request to the next or stop the chain",
            "Decouple request senders from concrete handlers via a common handler interface",
            "Support middleware pipelines for request processing (auth, logging, rate limiting)",
        ],
        "key_component": "handler chain", "important_property": "decoupled handler selection",
        "ops": [("handleRequest()", "O(H)", "Traverse up to H handlers until one claims"),
                ("addHandler()", "O(1)", "Append to end of chain"),
                ("removeHandler()", "O(H)", "Scan and unlink from chain of H handlers")],
    },
    "visitor_pattern": {
        "reqs": [
            "Define a new operation on elements of an object structure without modifying element classes",
            "Support double dispatch so visitor behavior varies by both visitor and element type",
            "Accumulate results across all visited elements (e.g., totals, reports)",
            "Allow multiple independent visitors over the same object structure",
            "Separate algorithms from the objects they operate on for clean extensions",
        ],
        "key_component": "visitor interface with per-type visit methods", "important_property": "open/closed principle for operations",
        "ops": [("accept(visitor)", "O(1)", "Call visitor.visit(this) — double dispatch"),
                ("visit(ElementA)", "O(1)", "Type-specific operation implementation"),
                ("traverseAll(visitor)", "O(N)", "Accept visitor on all N elements in structure")],
    },
    "memento_pattern": {
        "reqs": [
            "Capture and externalize an object's internal state without violating encapsulation",
            "Restore an object to a previous state using a stored memento",
            "Maintain a history stack of mementos for multi-level undo/redo",
            "Limit memento storage to bound memory usage (max history depth)",
            "Serialize mementos for persistence across process restarts",
        ],
        "key_component": "memento store (history stack)", "important_property": "encapsulated state snapshot",
        "ops": [("createMemento()", "O(S)", "Deep copy S fields of originator state"),
                ("restore(memento)", "O(S)", "Write S fields back into originator"),
                ("undo (pop history)", "O(1)", "Pop top memento from history stack")],
    },

    # 12-database-internals (original 5 files)
    "btree_bplus_tree": {
        "reqs": [
            "Store keys in sorted order across balanced tree nodes for efficient range scans",
            "Maintain O(log N) height by splitting full nodes and merging under-full nodes",
            "Keep all values in leaf nodes (B+ tree) linked in a doubly-linked list for scans",
            "Fit each node to page size (4–16KB) to minimize disk I/O per operation",
            "Support concurrent reads and writes with latch coupling (crabbing)",
        ],
        "key_component": "page-aligned tree node", "important_property": "O(log N) I/O for point and range queries",
        "ops": [("Point lookup", "O(log N)", "Traverse root-to-leaf in log_B(N) I/Os"),
                ("Range scan", "O(log N + K)", "Find start; scan K leaf pointers"),
                ("Insert/split", "O(log N)", "Traverse down; split on full nodes back up")],
    },
    "lsm_tree": {
        "reqs": [
            "Buffer writes in an in-memory component (MemTable) before flushing to disk",
            "Flush immutable MemTables to sorted SSTable files on disk",
            "Merge overlapping SSTables in background compaction to reclaim space",
            "Use Bloom filters to skip SSTables that cannot contain a queried key",
            "Support point lookups and range scans across multiple LSM levels",
        ],
        "key_component": "SSTable and MemTable", "important_property": "write-optimized with sequential I/O",
        "ops": [("Write", "O(1) amortized", "Append to MemTable; async flush to SSTable"),
                ("Point read", "O(L × B)", "Check L levels; B = Bloom filter false positive"),
                ("Range scan", "O(log N + K)", "Merge-scan K results across L sorted SSTables")],
    },
    "mvcc": {
        "reqs": [
            "Assign a unique transaction ID (timestamp or sequence) to each transaction",
            "Store multiple versions of each row, tagged with creation and expiration transaction IDs",
            "Allow readers to see a consistent snapshot without blocking writers",
            "Allow writers to proceed without blocking readers by writing new versions",
            "Garbage-collect old row versions no longer visible to any active transaction",
        ],
        "key_component": "version chain per row", "important_property": "readers never block writers",
        "ops": [("Snapshot read", "O(V)", "Walk version chain of V versions; return latest visible"),
                ("Write new version", "O(1)", "Append new version; mark old version's xmax"),
                ("Vacuum/GC", "O(D)", "Remove D versions with xmax < oldest active txn")],
    },
    "query_optimization": {
        "reqs": [
            "Parse SQL into an abstract syntax tree and validate against schema metadata",
            "Transform the AST into a logical query plan using relational algebra",
            "Enumerate possible physical plans and estimate costs using column statistics",
            "Select the lowest-cost plan considering join order, index usage, and parallelism",
            "Cache and reuse plans for parameterized queries (prepared statements)",
        ],
        "key_component": "cost-based optimizer", "important_property": "near-optimal plan selection",
        "ops": [("Parse + analyze", "O(T)", "Tokenize and validate T SQL tokens"),
                ("Plan enumeration", "O(3^N)", "Dynamic programming join order for N tables"),
                ("Stats estimation", "O(1) per predicate", "Histogram-based row count estimate")],
    },
    "replication_strategies": {
        "reqs": [
            "Replicate writes from a primary node to one or more replicas",
            "Support synchronous replication for strong consistency and async for low latency",
            "Detect primary failure and elect a new primary via leader election protocol",
            "Handle replication lag monitoring and alert when replicas fall behind",
            "Support read scaling by routing read queries to healthy replicas",
        ],
        "key_component": "replication log (WAL/binlog)", "important_property": "data durability with minimal replication lag",
        "ops": [("Write to primary", "O(1)", "Write WAL entry; send to replicas"),
                ("Replica apply", "O(1) per op", "Replay WAL entry on replica state"),
                ("Leader failover", "O(R log R)", "Elect leader from R replicas by log position")],
    },

    # 13-realworld-systems (original 6 files)
    "instagram_scale": {
        "reqs": [
            "Store and serve billions of photos and videos globally with low latency",
            "Generate personalized home feeds for 500M+ daily active users",
            "Handle 100M+ daily uploads with image processing (resize, filter, transcode)",
            "Support real-time notifications for likes, comments, follows, and mentions",
            "Provide search and discovery of content, hashtags, and user accounts",
        ],
        "key_component": "CDN and object storage", "important_property": "high read throughput with global distribution",
        "ops": [("Photo upload", "O(1)", "S3 upload + async transcoding job enqueue"),
                ("Feed generation", "O(F log F)", "Merge and rank F followings' recent posts"),
                ("Story delivery", "O(1)", "CDN-cached; short TTL for real-time updates")],
    },
    "uber_ride_matching": {
        "reqs": [
            "Match rider requests to nearby available drivers within seconds",
            "Track real-time driver GPS locations with sub-minute update frequency",
            "Estimate ETAs and surge pricing based on supply-demand balance",
            "Route matched trips efficiently with real-time traffic data",
            "Handle driver and rider cancellations with re-matching logic",
        ],
        "key_component": "geospatial driver index (S2/geohash)", "important_property": "sub-5-second matching latency",
        "ops": [("Driver location update", "O(log N)", "Geospatial index update for N active drivers"),
                ("Nearest driver search", "O(k log N)", "kNN query in geospatial index"),
                ("ETA calculation", "O(E)", "Dijkstra on road graph with E edges")],
    },
    "netflix_streaming": {
        "reqs": [
            "Stream video content to 200M+ subscribers with adaptive bitrate (ABR)",
            "Personalize content recommendations using collaborative filtering at scale",
            "Manage a global CDN (Open Connect) for edge-cached video delivery",
            "Handle concurrent peak load of 15%+ of internet traffic without buffering",
            "Support multiple device types and screen resolutions with transcoded profiles",
        ],
        "key_component": "Open Connect CDN appliances", "important_property": "consistent streaming quality globally",
        "ops": [("Video transcode", "O(D)", "Encode D-second chunk in parallel"),
                ("ABR bitrate switch", "O(1)", "Select next chunk quality from manifest"),
                ("Recommendation serve", "O(k log M)", "Top-k score from M candidate items")],
    },
    "github_collaboration": {
        "reqs": [
            "Store Git repositories as distributed content-addressable objects",
            "Support pull request workflows with code review, comments, and CI integration",
            "Run automated CI/CD pipelines on every push and pull request event",
            "Provide fast code search across billions of lines of code",
            "Handle high concurrent push and pull operations from global developer teams",
        ],
        "key_component": "Git object store (packs + loose objects)", "important_property": "distributed version control integrity",
        "ops": [("git push", "O(Δ)", "Upload Δ delta-compressed objects to remote"),
                ("PR diff render", "O(L)", "Myers diff across L changed lines"),
                ("Code search", "O(log C)", "Inverted index lookup across C code tokens")],
    },
    "airbnb_booking": {
        "reqs": [
            "Search and filter listings by location, dates, price, and amenities",
            "Check real-time availability and prevent double-booking via inventory lock",
            "Process payments securely with multi-currency support and split payouts",
            "Support host calendar management and dynamic pricing",
            "Handle cancellations, refunds, and dispute resolution workflows",
        ],
        "key_component": "inventory availability calendar", "important_property": "double-booking prevention",
        "ops": [("Search listings", "O(log N + K)", "Geospatial + availability filter on N listings"),
                ("Reserve dates", "O(1)", "Optimistic lock on calendar rows for chosen dates"),
                ("Payment process", "O(1)", "Stripe API call; async host payout")],
    },
    "linkedin_recommendations": {
        "reqs": [
            "Recommend connections using graph-based People You May Know (PYMK) algorithms",
            "Surface relevant job listings based on skills, title, and career trajectory",
            "Generate personalized newsfeed by ranking professional content and updates",
            "Recommend courses and learning paths based on skill gaps and peer activity",
            "Re-rank recommendations in real time based on freshness and engagement signals",
        ],
        "key_component": "professional graph engine", "important_property": "relevance + diversity in top-k results",
        "ops": [("PYMK graph traversal", "O(F²)", "2-hop common connections for F first-degree"),
                ("Candidate score", "O(k × D)", "Score k candidates on D feature dimensions"),
                ("Feed ranking", "O(k log k)", "Sort k feed items by predicted engagement")],
    },

    # 14-ml-recommendations (original 5 files)
    "collaborative_filtering": {
        "reqs": [
            "Build user-item interaction matrix from explicit ratings or implicit feedback",
            "Compute user-user or item-item similarity using cosine or Pearson correlation",
            "Generate top-N recommendations by aggregating scores from similar neighbors",
            "Handle cold-start problem for new users with popularity-based fallback",
            "Update model incrementally as new interactions arrive",
        ],
        "key_component": "user-item interaction matrix", "important_property": "personalization via peer similarity",
        "ops": [("User similarity", "O(U × I)", "Dot product across I items for U user pairs"),
                ("Top-N recommend", "O(k log k)", "Sort k candidate items by predicted score"),
                ("Incremental update", "O(F)", "Update F factor vectors for new interaction")],
    },
    "content_based_filtering": {
        "reqs": [
            "Extract features from item content (text, tags, metadata) to build item profiles",
            "Build user profiles from the features of items they have interacted with",
            "Score candidate items by similarity between item profile and user profile",
            "Explain recommendations using the features driving similarity scores",
            "Update user profiles incrementally as new interactions are recorded",
        ],
        "key_component": "item feature extractor", "important_property": "explainable recommendations",
        "ops": [("Feature extract", "O(W)", "TF-IDF or embedding over W words/tags"),
                ("Profile similarity", "O(F)", "Cosine similarity on F-dimensional vectors"),
                ("Top-N score", "O(I)", "Score I candidate items; partial sort for top-N")],
    },
    "ranking_systems": {
        "reqs": [
            "Score items using a learned ranking model (LambdaRank, LightGBM, DNN)",
            "Optimize for ranking metrics (NDCG, MAP, MRR) rather than pointwise accuracy",
            "Apply diversity constraints to prevent top-N from being too similar",
            "Re-rank in real time using fresh user context signals (session, location)",
            "A/B test ranking model changes with interleaving or holdout experiments",
        ],
        "key_component": "learning-to-rank model", "important_property": "optimized NDCG on held-out eval set",
        "ops": [("Score candidates", "O(k × F)", "Model inference on k items with F features"),
                ("Sort ranked list", "O(k log k)", "Partial sort for top-N from k candidates"),
                ("Diversity rerank", "O(k²)", "MMR or DPP diversity enforcement on k items")],
    },
    "feature_engineering": {
        "reqs": [
            "Extract, transform, and select features from raw user, item, and context data",
            "Compute real-time features (session activity, query context) with sub-50ms latency",
            "Store precomputed batch features in a feature store for training and serving",
            "Detect and handle missing values, outliers, and distribution shift",
            "Version features to enable reproducible model training and debugging",
        ],
        "key_component": "feature store", "important_property": "training-serving feature consistency",
        "ops": [("Online feature fetch", "O(1)", "Redis lookup by entity key"),
                ("Batch feature compute", "O(N × F)", "Compute F features for N entities"),
                ("Feature join", "O(N log N)", "Join N user records with N item feature rows")],
    },
    "ab_testing_framework": {
        "reqs": [
            "Randomly assign users to experiment variants with configurable traffic splits",
            "Track metric events (clicks, conversions, revenue) per variant assignment",
            "Compute statistical significance (t-test, chi-square) with configurable power",
            "Support multiple concurrent experiments with overlap detection",
            "Generate experiment reports with confidence intervals and p-values",
        ],
        "key_component": "user assignment store (experiment config)", "important_property": "unbiased random assignment",
        "ops": [("Assign variant", "O(1)", "Hash(user_id + experiment_id) modulo splits"),
                ("Log metric event", "O(1)", "Async write to event pipeline"),
                ("Significance test", "O(N)", "Aggregate N observations per variant")],
    },

    # 15-security (original 3 files)
    "oauth_sso": {
        "reqs": [
            "Authenticate users via a centralized Identity Provider (IdP) using OAuth 2.0 / OIDC",
            "Issue short-lived access tokens and longer-lived refresh tokens after successful auth",
            "Support PKCE flow for public clients (mobile, SPA) without client secrets",
            "Propagate Single Sign-On sessions so users authenticate once across services",
            "Revoke tokens on logout, password change, or security events",
        ],
        "key_component": "authorization server (IdP)", "important_property": "delegated access without sharing passwords",
        "ops": [("Authorization code exchange", "O(1)", "Code for token pair at token endpoint"),
                ("Token introspection", "O(1)", "Cache JWT signature verification result"),
                ("Token revocation", "O(1)", "Mark token ID invalid in revocation store")],
    },
    "encryption_tls": {
        "reqs": [
            "Authenticate server identity using X.509 certificates signed by a trusted CA",
            "Negotiate cipher suites and session keys via TLS 1.3 handshake",
            "Encrypt all data in transit with authenticated encryption (AES-256-GCM)",
            "Support TLS session resumption (tickets, PSK) to reduce handshake latency",
            "Rotate TLS certificates before expiry with automated tooling (cert-manager)",
        ],
        "key_component": "X.509 certificate chain", "important_property": "confidentiality, integrity, and authenticity",
        "ops": [("TLS 1.3 handshake", "O(1)+1RTT", "Key exchange + certificate verify"),
                ("Record encrypt/decrypt", "O(L)", "AES-GCM over L bytes per record"),
                ("Cert validation", "O(C)", "Verify C certificates in chain")],
    },
    "access_control": {
        "reqs": [
            "Enforce Role-Based Access Control (RBAC) by assigning permissions to roles",
            "Evaluate Attribute-Based Access Control (ABAC) policies for fine-grained decisions",
            "Apply principle of least privilege: grant minimum permissions required",
            "Log all access decisions (allow and deny) for audit trail",
            "Invalidate cached permission decisions on role or policy change",
        ],
        "key_component": "policy decision point (PDP)", "important_property": "least-privilege enforcement",
        "ops": [("Permission check", "O(R)", "Evaluate R role-permission mappings"),
                ("Policy evaluate (ABAC)", "O(A)", "Match A attribute rules against request context"),
                ("Cache invalidate", "O(1)", "Purge permission cache on role change")],
    },
}

# ── Replacement functions ─────────────────────────────────────────────────────

def get_topic_key(filepath: str) -> str:
    """Derive topic key from filename."""
    name = os.path.basename(filepath)
    name = re.sub(r'^\d+_', '', name)   # strip leading number
    return name.replace('.md', '').lower()

def fix_functional_requirements(content: str, data: dict) -> str:
    """Replace [Core operation X: description] placeholders."""
    reqs = data.get("reqs", [])
    if not reqs:
        return content
    # Build replacement block
    new_reqs = "\n".join(f"- {r}" for r in reqs)
    # Replace all 5 placeholder lines as a block
    pattern = r'- \[Core operation \d+: description\]\n?'
    # Count how many exist
    existing = re.findall(pattern, content)
    if not existing:
        return content
    # Replace first occurrence of the block
    content = re.sub(
        r'(- \[Core operation \d+: description\]\n?){1,10}',
        new_reqs + "\n",
        content,
        count=1
    )
    return content

def fix_key_ops_table(content: str, data: dict) -> str:
    """Replace [Key Op X] and [Explanation] in complexity tables."""
    ops = data.get("ops", [])
    if not ops:
        return content
    for i, (op, complexity, note) in enumerate(ops, start=1):
        content = content.replace(f"[Key Op {i}]", op)
    # Replace [Explanation] pattern with notes
    for i, (op, complexity, note) in enumerate(ops, start=1):
        # Replace the explanation for this row
        content = re.sub(
            r'\| ' + re.escape(op) + r' \| [^\|]+ \| \[Explanation\] \|',
            f"| {op} | {complexity} | {note} |",
            content
        )
    # Clean up any remaining [Explanation] placeholders
    content = re.sub(r'\[Explanation\]', 'See implementation notes above', content)
    return content

def fix_interview_placeholders(content: str, data: dict) -> str:
    """Replace [key component] and [important property] in interview questions."""
    key_component = data.get("key_component", "core component")
    important_property = data.get("important_property", "correctness and performance")
    content = content.replace("[key component]", key_component)
    content = content.replace("[important property]", important_property)
    return content

def process_file(filepath: str) -> bool:
    """Process a single file, returning True if changes were made."""
    content = open(filepath, encoding='utf-8', errors='ignore').read()

    # Check if has any placeholders
    if not re.search(r'\[Core operation \d+: description\]|\[Key Op \d+\]|\[key component\]|\[important property\]', content):
        return False

    topic_key = get_topic_key(filepath)
    data = TOPIC_DATA.get(topic_key, {})

    if not data:
        # Try partial match
        for key in TOPIC_DATA:
            if key in topic_key or topic_key in key:
                data = TOPIC_DATA[key]
                break

    if not data:
        # Generic fallback requirements based on directory
        dirpath = os.path.dirname(filepath)
        dirname = os.path.basename(dirpath)
        data = {
            "reqs": [
                f"Implement core {topic_key.replace('_', ' ')} functionality at production scale",
                "Handle concurrent requests with thread-safe operations",
                "Provide monitoring and observability via metrics and structured logging",
                "Support graceful degradation and failure recovery",
                "Enable horizontal scaling to meet throughput requirements",
            ],
            "key_component": "core processing engine",
            "important_property": "reliability and performance",
            "ops": [
                ("Primary operation", "O(log N)", "Main operation on N-element dataset"),
                ("Secondary operation", "O(1)", "Cached or pre-computed result"),
                ("Cleanup/GC", "O(N)", "Scan and evict N stale entries"),
            ],
        }

    original = content
    content = fix_functional_requirements(content, data)
    content = fix_key_ops_table(content, data)
    content = fix_interview_placeholders(content, data)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = sorted(glob.glob("docs/system_design/**/*.md", recursive=True))
    print(f"Scanning {len(files)} files for placeholders...\n")
    fixed = 0
    for f in files:
        if process_file(f):
            print(f"  ✅ Fixed: {os.path.relpath(f)}")
            fixed += 1
    print(f"\nFixed {fixed} files.")

if __name__ == "__main__":
    main()
