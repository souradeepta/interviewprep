# Video Streaming Platform

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A video streaming platform must accept uploaded videos, transcode them into multiple resolutions and
formats, distribute them globally via CDN, and deliver them to viewers with adaptive bitrate
streaming that adjusts quality to available bandwidth. YouTube processes 500 hours of video uploaded
every minute and serves 1 billion hours of video watched per day.

The engineering challenges span multiple domains: storage (petabytes of video data), compute
(transcoding is CPU-intensive), networking (CDN placement and edge caching), and protocol design
(DASH/HLS adaptive bitrate streaming). Understanding the chunked-parallel transcoding pipeline is
the key L5 differentiator.

## Functional Requirements

- Users can upload videos (up to 10GB, any common format: MP4, MOV, AVI, MKV)
- Platform transcodes uploaded videos into multiple resolutions (360p, 480p, 720p, 1080p, 4K)
- Users can stream videos with adaptive bitrate (quality adjusts to bandwidth automatically)
- Videos are searchable by title, description, tags
- Users can view watch history, like/dislike, comment
- Creators see analytics: view count, watch time, audience retention

## Non-Functional Requirements

- **Scale:** 500 hours uploaded/min; 1B hours watched/day; 2B monthly active users
- **Latency:** Video playback starts within 2 seconds of pressing play; no rebuffering at 90th percentile
- **Availability:** 99.95% playback availability; upload can tolerate 99.9%
- **Consistency:** View count eventually consistent (within 5 minutes); metadata eventually consistent

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Upload volume:
  500 hours/min = 30,000 hours/day = 1,800,000 minutes of video/day
  Average compressed input: 1GB per minute of 1080p60 raw
  Input storage needed: 1.8M min × 1GB = 1.8 PB/day → impractical to store raw
  Solution: transcode immediately; store only outputs (much smaller)

Transcoded output per video:
  1 minute of input → outputs: 360p (5MB), 480p (10MB), 720p (20MB), 1080p (40MB)
  Total output per input minute: ~75MB
  Per day: 1.8M min/day × 75MB = 135 TB/day of transcoded video

Cumulative storage:
  135 TB/day × 365 days = 49 PB/year → stored in S3-compatible object storage

Playback bandwidth:
  1B hours/day = 1B × 3600 seconds / 86400 s/day = 41.67M concurrent viewers
  Average 720p stream: 2.5 Mbps
  Total egress: 41.67M × 2.5 Mbps = 104 Tbps
  CDN handles this; origin egress is ~5-10% = 5-10 Tbps from origin

Transcoding compute:
  Transcoding 1 hour of 1080p to 720p: ~2 CPU-hours (x264 encoding)
  30,000 hours uploaded/day → 60,000 CPU-hours of transcoding/day
  60,000 / 24 = 2,500 CPU-hours/hour needed (continuously)
  c5.4xlarge (16 vCPU): 16 CPU-hours/server-hour → need 2,500/16 = 156 transcoding servers
```

### Architecture Diagram

```
[Creator]                    [Viewer]
   │ POST /upload                │ GET /watch?v=abc
   │                             │
   ▼                             ▼
[Upload Service]           [Video Service]
  - Pre-signed S3 URL         - Fetch metadata (DB)
  - Resumable upload           - Generate manifest URL
  - Multi-part upload          - Return playback URLs
   │                             │
   ▼                             ▼
[Raw Video S3 Bucket]      [CDN (CloudFront)]
   │                             │ (HLS/DASH manifest + segments)
   │ (S3 event → SQS)           │
   ▼                             ▼
[Transcoding Pipeline]     [Processed Video S3]
  - Job queue (SQS)             (360p, 480p, 720p, 1080p segments)
  - Worker pool (EC2)
  - Chunked parallel encoding
  - Output → S3 segments

[Metadata DB] (PostgreSQL)
  - videos, channels, tags
  - view_count, like_count (approximate counters)

[Search] (Elasticsearch)
  - title, description, tags index
  - Updated via Kafka CDC

[Thumbnail Service]
  - Extracts frames at N points
  - Stores in S3, CDN-backed

[Analytics Pipeline] (Kafka → Spark/Flink → DW)
  - View events → audience retention
  - Real-time view counter (Redis HyperLogLog)
  - Batch aggregation to BigQuery/Redshift nightly

Playback flow:
  Player → CDN → fetch manifest.m3u8 → parse segment URLs →
  fetch first 2-3 segments → start playing →
  ABR algorithm adjusts quality based on throughput measurement
```

### Data Model

```sql
-- Videos metadata
CREATE TABLE videos (
    video_id     VARCHAR(11) PRIMARY KEY,  -- YouTube-style base64 11-char ID
    channel_id   BIGINT NOT NULL,
    title        VARCHAR(500) NOT NULL,
    description  TEXT,
    duration_sec INT,
    status       VARCHAR(20) DEFAULT 'processing',  -- processing|ready|deleted
    visibility   VARCHAR(20) DEFAULT 'public',       -- public|unlisted|private
    view_count   BIGINT DEFAULT 0,          -- eventually consistent counter
    like_count   INT DEFAULT 0,
    upload_raw_key VARCHAR(512),            -- S3 key of original upload
    created_at   TIMESTAMP DEFAULT NOW()
);

-- Video renditions (one row per quality per video)
CREATE TABLE video_renditions (
    video_id     VARCHAR(11),
    quality      VARCHAR(10),   -- '360p', '720p', '1080p'
    codec        VARCHAR(20),   -- 'h264', 'vp9', 'av1'
    bitrate_kbps INT,
    manifest_key VARCHAR(512),  -- S3 key to HLS playlist (.m3u8) for this rendition
    segment_prefix VARCHAR(512), -- S3 key prefix for .ts/.m4s segments
    PRIMARY KEY (video_id, quality, codec)
);

-- Channels
CREATE TABLE channels (
    channel_id   BIGINT PRIMARY KEY,
    owner_user_id BIGINT UNIQUE,
    name         VARCHAR(256),
    subscriber_count INT DEFAULT 0,
    created_at   TIMESTAMP
);

-- User watch history (Cassandra wide-row for fast per-user lookup)
CREATE TABLE watch_history (
    user_id       BIGINT,
    watched_at    TIMESTAMP,
    video_id      VARCHAR(11),
    progress_sec  INT,           -- seconds into the video when last watched
    PRIMARY KEY ((user_id), watched_at, video_id)
) WITH CLUSTERING ORDER BY (watched_at DESC);

-- Transcoding jobs
CREATE TABLE transcode_jobs (
    job_id       BIGINT PRIMARY KEY,
    video_id     VARCHAR(11),
    status       VARCHAR(20),  -- queued|processing|done|failed
    raw_s3_key   VARCHAR(512),
    created_at   TIMESTAMP,
    completed_at TIMESTAMP
);
```

### API Design

```
# Upload flow
POST /v1/uploads/initiate
  Body: { "title": "My Video", "description": "...", "file_size_bytes": 1073741824 }
  Response: { "upload_id": "up_abc", "upload_url": "https://s3.aws.com/...?presigned",
              "video_id": "dQw4w9WgXcQ" }

POST /v1/uploads/{upload_id}/complete
  Body: { "etag": "abc123" }  -- S3 multipart upload completion
  Response: { "video_id": "...", "status": "processing" }

# Playback
GET /v1/videos/{video_id}
  Response: { "video_id": "...", "title": "...", "duration_sec": 213,
              "manifest_url": "https://cdn.example.com/v/dQw4w9WgXcQ/manifest.m3u8",
              "thumbnail_url": "https://cdn.example.com/t/dQw4w9WgXcQ/hq.jpg",
              "view_count": 1234567890 }

GET /v1/videos/{video_id}/progress   -- resume position
  Response: { "progress_sec": 142 }

POST /v1/videos/{video_id}/watch-event
  Body: { "progress_sec": 143, "quality": "720p", "buffering_events": 0 }
  Response: { "status": "ok" }

# Search
GET /v1/search?q=cats+playing&page=1&limit=20
  Response: { "results": [...], "total": 45230 }
```

### Basic Scaling

- **Pre-signed S3 upload:** Client uploads directly to S3 using a time-limited pre-signed URL (valid 1 hour). Upload Service never handles the raw video bytes — only the metadata and the URL generation. This offloads gigabytes of upload traffic to S3 directly.
- **S3 event → SQS → transcoding workers:** S3 publishes `ObjectCreated` event to SQS when upload completes. Transcoding workers poll SQS; process one job per worker. Auto Scaling Group scales worker count based on SQS queue depth.
- **HLS/DASH segmentation:** Transcoded video split into 6-second segments (`.ts` for HLS, `.m4s` for DASH). Each segment independently CDN-cached. Player pre-fetches 3 segments (18 seconds buffer) before starting playback.
- **CDN-first delivery:** All video segments and thumbnails served from CloudFront. S3 origin only hit on cache miss (first view of a segment at that edge PoP). For popular videos, cache hit ratio > 99%.

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Chunked parallel transcoding pipeline:
  Problem: transcoding 1 hour of 4K video takes 4+ hours on 1 server (serial)
  Solution: split video into 30-second chunks → transcode chunks in parallel → stitch

  Chunk-based parallelism:
    1-hour video = 120 × 30s chunks
    Transcode each chunk on a separate c5.4xlarge (16 vCPU)
    Chunk transcoding time: 30s of 4K input → ~60s of encoding per rendition (2:1 real-time)
    4 renditions in parallel (360/480/720/1080) per chunk: 60s per chunk
    Total wall-clock time: max over all chunks = 60s (vs 4 hours serial!)
    EC2 spot cost for 1-hour video: 120 chunks × $0.272/hr × (60/3600)hr = $0.54/video

  Transcoding farm sizing:
    30,000 hours uploaded/day = 30,000 × 120 chunks = 3.6M chunks/day
    3.6M / 86400s = 41.7 chunks/sec
    Each chunk takes 60s: 41.7 × 60 = 2,500 concurrent chunk workers needed
    2,500 × c5.4xlarge at $0.272/hr = $680/hr = $489,600/month (on-demand)
    Spot instances (~70% cheaper): $0.082/hr × 2,500 = $205/hr = $147,600/month

CDN capacity:
  104 Tbps total egress
  CloudFront: 230+ PoPs globally; each handles 1+ Tbps → sufficient
  CDN cache efficiency: popular top-10% of videos drive 90% of watch time
    10% of videos cached at edge → 90% cache hit → origin sees 10% = 10 Tbps
  Long-tail: 90% of videos rarely viewed → likely not in edge cache → S3 origin miss
    Solution: tiered storage (hot/warm/cold) + CDN hierarchy

Storage tiering:
  Hot  (< 30 days or > 10K views): full CDN distribution, all qualities cached
  Warm (30d-1yr, 100-10K views): 720p/1080p on S3 Standard; others on S3-IA
  Cold (> 1yr, < 100 views): all qualities on S3 Glacier Instant Retrieval
    Retrieval: 1-3 hours → pre-warm CDN on traffic spike
    Cost: $0.004/GB vs $0.023/GB Standard = 83% savings on cold content

Total storage at steady state:
  135 TB/day × 365 × 5 years = 246 PB transcoded content
  Hot tier (last 30 days): 135 TB × 30 = 4 PB on S3 Standard
  Warm/cold: 242 PB on S3-IA/Glacier → significant cost savings
```

### Failure Modes

```
Scenario 1: Transcoding worker crashes mid-job
  - Worker disappears; SQS message visibility timeout (15 minutes) expires
  - SQS re-delivers message to another worker
  - Idempotent job: each chunk has deterministic S3 output key → restart is safe
  - Progress tracking: job marks each completed chunk; on retry, skip already-done chunks
  - Dead letter queue (DLQ): after 3 retries, move to DLQ; alert operator

Scenario 2: CDN PoP goes down (loses regional cache)
  - Viewers in that region: next request goes to nearest working PoP (anycast/DNS failover)
  - Cache miss storm: 10M viewers suddenly hit another PoP → origin gets spike
  - CDN handles by serving stale (stale-while-revalidate) and pulling from next PoP before origin
  - Origin rate limiting: CloudFront origin shield (single region origin cache) absorbs spike

Scenario 3: Corrupt upload (incomplete upload, codec unsupported)
  - Transcoding fails after 30 seconds of work
  - Error handling: transcode_jobs.status = 'failed'; push notification to creator
  - Partial output cleanup: S3 lifecycle rule deletes orphaned segment prefixes after 24h
  - Fallback: accept WebM, AVI → convert to MP4 in preprocessing step before transcoding

Scenario 4: View count hotspot (viral video)
  - Video goes viral: 100M views in 1 hour = 27K view events/sec to view_count update
  - Single DB row update at 27K writes/sec → hot row lock contention
  - Fix 1: Redis INCR counter (atomic, 500K ops/sec) → periodic sync to PostgreSQL
  - Fix 2: Probabilistic counting (count 1% of views × 100) → ±10% accuracy, 100× throughput
  - Fix 3: Sharded counters (10 shard rows, INCR random shard, SUM at read time)
  - YouTube's actual approach: aggregate in pipeline (Kafka + Flink), batch update every 5 minutes

Scenario 5: Storage cost explosion from low-quality uploads
  - Creators upload 30-second 4K clips that get <10 views total
  - Transcoding all qualities is wasteful
  - Fix: transcoding waterfall — start with 360p only; if video reaches 1,000 views → transcode 720p;
    if reaches 10,000 views → transcode 1080p/4K
  - This approach (used by Netflix/YouTube) reduces transcoding cost by 40-60%
```

### Consistency Boundaries

```
View count consistency:
  Eventual: Redis counter updated in real-time; PostgreSQL updated every 5 minutes
  Viewers see different counts depending on whether they read from DB or Redis
  Acceptable: exact view count is not critical; approximate is fine (show "1.2M views")
  Strong count correctness: batch reconciliation (Spark job) nightly

Metadata consistency:
  Strong: title, description, visibility changes → PostgreSQL write → immediately consistent
  Eventual: Elasticsearch search index updated via Kafka CDC within 1-5 seconds of DB change
  Result: search may show old title for up to 5 seconds after creator edits

Watch progress consistency:
  Eventually consistent: progress synced to server every 30 seconds
  If network drops mid-video: last 30s of progress may be lost
  Acceptable: viewer can resume from 30s before where they left off
  On app reopen: fetch last saved progress from server

Transcoding pipeline consistency:
  Video not available for playback until at least 360p transcoding completes
  video.status = 'ready' only after minimum rendition is available
  Higher renditions appear as they complete (manifest updated incrementally)
  Creator sees "360p available, 1080p processing" during multi-quality progress

DASH/HLS consistency:
  Manifest file (.m3u8 / .mpd) lists all available segment URLs
  Cached at CDN with 60s TTL; updated as new segments complete
  Player uses ETag/If-None-Match to detect manifest updates efficiently
```

### Cost Model

```
Infrastructure at YouTube scale (500 hrs/min upload, 1B hrs/day watch):

Transcoding (EC2 Spot):
  2,500 spot workers × c5.4xlarge ($0.082/hr) = $205/hr = $147,600/month
  (Largest single compute cost)

Storage:
  Hot (4 PB S3 Standard): 4,000,000 GB × $0.023 = $92,000/month
  Warm/Cold (242 PB S3-IA/Glacier): managed at ~$0.004/GB avg = ~$970,000/month
  Total storage: ~$1,062,000/month
  (Dominant cost; 246 PB is enormous)

CDN (CloudFront):
  10 Tbps origin egress × $0.09/GB × 86400s × 30 days = $2,332,800/month
  CDN egress from edge: charged to viewers in their regions; varies by geography
  Bulk CDN contract: ~$0.01-0.02/GB negotiated → reduces to $233K-466K/month

Application servers (metadata, upload, search):
  50 × c6i.4xlarge ($0.680/hr × 50) = $24,720/month

Kafka (view event pipeline):
  20 brokers × m6i.4xlarge ($0.768/hr × 20) = $11,059/month

PostgreSQL + Elasticsearch:
  DB: 3 nodes = $2,074/month
  ES: 10 nodes = $3,628/month

Total: ~$1.5M/month at full YouTube scale
Per-view cost: 1B hours/day × 30 days = 30B hours/month
  (1B hours = ~40B video views/month at 1.5 min avg)
  $1.5M / 40B views = $0.0000375 per view

Dominant cost: Storage (242 PB cold content) + CDN egress
Optimization: AV1 codec reduces bitrate 30-50% vs H.264 → proportional CDN + storage savings
  Google has been re-encoding YouTube library to AV1 since 2018; projected $1B+ savings
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **HLS (HTTP Live Streaming)** | Apple native support, wide compatibility, works through CDN | Higher latency (6s min segment = 6s startup), Apple proprietary origin | iOS/macOS streaming, live events on CDN |
| **DASH (Dynamic Adaptive Streaming over HTTP)** | Open standard, flexible segment size (2s possible), codec-agnostic | Not natively supported on iOS (requires Media Source Extensions) | Web players, Android, cross-platform |
| **Progressive download (MP4)** | Simple, single file, works everywhere | No adaptive bitrate, must download all qualities, no seeking without full download | Short clips, simple use cases |
| **Chunked parallel transcoding** | 60s wall-clock for 1-hour video, horizontally scalable | Complex orchestration (split, parallel transcode, stitch), more S3 reads/writes | Large video platform with SLA on processing time |
| **Serial transcoding** | Simple implementation | 4+ hours for 1-hour 4K video; not scalable | Low-volume or dev/test environments |
| **AV1 codec** | 30-50% bitrate reduction vs H.264 at same quality | 5-10× slower encoding vs H.264; encoding cost trades against storage/CDN savings | New uploads on large platforms (Netflix, YouTube) |

## Follow-up Questions (escalating difficulty)

1. **(L3)** Why does a video streaming platform use chunked segments (HLS/DASH) instead of serving the entire video file?
   → A 1080p 2-hour movie is ~8GB. Serving the whole file would require the client to start downloading 8GB before watching. With chunked streaming (6-second segments), the player downloads only 3-4 segments ahead (18-24 seconds of buffer). CDN caches individual segments — a segment cached at an edge PoP benefits all viewers at that PoP. Adaptive bitrate requires segments to switch quality mid-stream; this is impossible with a single file.

2. **(L3)** What is adaptive bitrate streaming and why does it need multiple renditions?
   → ABR (e.g., HLS ABR) measures download throughput continuously. If a 2Mbps (720p) segment takes longer than 6 seconds to download, the player switches to the 500Kbps (360p) version for the next segment — preventing rebuffering. Without multiple pre-transcoded renditions at different bitrates, there is no lower-quality version to fall back to. The manifest lists all available quality levels with their bandwidth requirements; the player selects the best one it can sustain.

3. **(L4)** Why is the upload flow designed to send video directly to S3 rather than through the API server?
   → A 10GB upload through an API server would require: the server to receive 10GB (using RAM/disk), then re-upload to S3. This doubles network traffic, requires the server to hold 10GB per concurrent upload (a dozen concurrent uploads = 120GB of server RAM), and makes the server a bottleneck. Pre-signed S3 URLs allow the client to upload directly to S3 at full S3 bandwidth — the API server only generates the URL (trivial) and receives completion notification.

4. **(L4)** How do you handle resumable uploads for large video files?
   → S3 Multipart Upload: the client splits the file into 5MB+ chunks and uploads each independently. If the upload fails mid-way, only failed chunks need retransmission. The client tracks which parts (ETags) have been uploaded (stored locally or in the API server's DB). On resume: call `ListMultipartUpload` to find already-uploaded parts → skip them → upload remaining → `CompleteMultipartUpload`. AWS S3 holds partially uploaded parts for 24h before auto-expiring.

5. **(L5)** Walk through the chunked parallel transcoding pipeline end-to-end.
   → Video lands in S3 (raw bucket). S3 event triggers SQS message. Orchestrator service dequeues job: (1) probes video metadata (duration, codec, resolution) using ffprobe; (2) divides video into 30s chunks using keyframe-aligned splits (MP4 box headers); (3) enqueues N chunk transcode jobs in SQS. Chunk workers (EC2 Spot) each: download their chunk from S3 → transcode to all target qualities using ffmpeg → upload output segments to processed S3 bucket. Orchestrator monitors completion; when all chunks done → runs stitching job (ffmpeg concat demuxer, no re-encoding) → generates HLS playlists (master.m3u8 + per-rendition playlists) → marks video as 'ready' in DB → invalidates CDN cache for manifest.

6. **(L5)** How does Netflix differ from YouTube in its transcoding approach?
   → Netflix uses per-title encoding (2015): instead of fixed bitrate ladders (720p=2Mbps always), they analyze each title's complexity and encode at the minimum bitrate that achieves target visual quality (VMAF score). An animated cartoon (low complexity) at 720p might use 500Kbps; a fast-action film might need 4Mbps. Netflix also uses shot-based encoding: different scenes within one title can use different quality levels (per-shot optimal encoding). Result: average 20% bitrate reduction industry-wide, saving Netflix ~$1B/year in CDN costs.

7. **(L5+)** Design a system to re-encode YouTube's entire 800M video library from H.264 to AV1 while serving live traffic.
   → Offline re-encoding pipeline: (1) Identify priority order: videos with highest watch hours get re-encoded first (Pareto: top 1% of videos = 99% of watch time). (2) Parallel batch: 100K EC2 Spot workers continuously re-encode; each worker fetches original upload from cold S3, re-encodes to AV1, stores in new S3 prefix. (3) Gradual rollout: after AV1 version ready, update manifest to list AV1 as preferred; browsers with AV1 support (MSE) auto-select it; older browsers fall back to H.264. (4) A/B test VMAF quality parity before switching default. (5) H.264 versions retained for 1 year post-AV1-availability, then migrated to Glacier. At 100K workers processing 1 minute of video in 5 minutes: 100K × (60/300) = 20K minutes/sec of throughput. 800M videos × 12 minutes average = 9.6B minutes total → 9.6B/20K = 480,000 seconds ≈ 5.5 days to re-encode the entire library.

## Anti-patterns / Things NOT to Say

- **"Serve video files directly from the origin server (not CDN)"** — At 104 Tbps of video egress, direct origin serving would require a data center with more outbound bandwidth than the entire internet's backbone capacity for a mid-sized ISP. CDNs exist precisely to distribute this load to hundreds of edge PoPs. Always CDN-first for video; origin serves only CDN cache misses.
- **"Transcode the video serially (one resolution at a time)"** — Serial transcoding of a 1-hour 4K video takes 4+ hours. With chunked parallel transcoding, the same video is ready in 60 seconds. Creators expect their video to be available within minutes of upload. Serial transcoding cannot meet this SLA at YouTube scale.
- **"Store the original raw upload indefinitely"** — Raw camera footage is 2-10× larger than compressed output. Storing 1.8 PB/day of raw input in addition to 135 TB/day of transcoded output adds enormous cost. Archive original uploads to Glacier (for Creator re-download and re-processing purposes) but charge storage cost against the creator's account or expire after 30 days.
- **"Use a single video quality for all viewers"** — Serving 1080p to a mobile user on 3G results in constant rebuffering (requires 4Mbps; 3G delivers 1-3Mbps). Serving 360p to a 4K TV on gigabit fiber wastes quality. Adaptive bitrate (ABR) solves this by continuously selecting the best quality the viewer's bandwidth can sustain. Not implementing ABR is a major user experience failure.
- **"Update view_count in the database on every view event"** — At 27K view events/sec for a viral video, a PostgreSQL row update serializes all writers through a row-level lock — effective throughput ~5K updates/sec. The remaining 22K updates/sec accumulate in a queue or fail. Use Redis INCR (atomic, 500K ops/sec) + periodic batch sync to PostgreSQL every 5 minutes. Exact real-time counts are not worth the consistency overhead.

## Python Implementation (sketch)

```python
import os
import time
import uuid
import threading
import queue
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

QUALITIES = [
    ("360p",  640,  360,  500),   # (label, width, height, target_kbps)
    ("480p",  854,  480,  1000),
    ("720p",  1280, 720,  2500),
    ("1080p", 1920, 1080, 5000),
]

CHUNK_DURATION_SEC = 30

@dataclass
class TranscodeChunk:
    job_id: str
    video_id: str
    chunk_index: int
    start_sec: float
    duration_sec: float
    raw_s3_key: str

@dataclass
class TranscodeJob:
    job_id: str
    video_id: str
    raw_s3_key: str
    duration_sec: float
    status: str = "queued"        # queued|processing|done|failed
    chunks_total: int = 0
    chunks_done: int = 0
    created_at: float = field(default_factory=time.time)

class TranscodingPipeline:
    """Simulates chunked-parallel video transcoding."""

    def __init__(self, worker_count: int = 4):
        self._jobs: Dict[str, TranscodeJob] = {}
        self._chunk_queue: queue.Queue = queue.Queue()
        self._s3: Dict[str, bytes] = {}   # fake S3 (key → data)
        self._lock = threading.Lock()
        # Start worker threads
        for i in range(worker_count):
            threading.Thread(target=self._worker, args=(i,), daemon=True).start()

    def submit(self, video_id: str, raw_s3_key: str,
               duration_sec: float) -> str:
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        n_chunks = max(1, int(duration_sec / CHUNK_DURATION_SEC))
        job = TranscodeJob(
            job_id=job_id,
            video_id=video_id,
            raw_s3_key=raw_s3_key,
            duration_sec=duration_sec,
            chunks_total=n_chunks,
        )
        with self._lock:
            self._jobs[job_id] = job

        # Enqueue all chunks
        for i in range(n_chunks):
            chunk = TranscodeChunk(
                job_id=job_id,
                video_id=video_id,
                chunk_index=i,
                start_sec=i * CHUNK_DURATION_SEC,
                duration_sec=min(CHUNK_DURATION_SEC,
                                 duration_sec - i * CHUNK_DURATION_SEC),
                raw_s3_key=raw_s3_key,
            )
            self._chunk_queue.put(chunk)

        return job_id

    def _transcode_chunk(self, chunk: TranscodeChunk) -> List[str]:
        """Simulate ffmpeg encoding: produce output segment keys."""
        output_keys = []
        for quality, _, _, _ in QUALITIES:
            # Simulate encoding time proportional to chunk duration
            time.sleep(chunk.duration_sec * 0.001)  # 1ms per sec of video (sped up)
            key = f"processed/{chunk.video_id}/{quality}/chunk_{chunk.chunk_index:04d}.ts"
            self._s3[key] = f"<encoded {quality} chunk {chunk.chunk_index}>".encode()
            output_keys.append(key)
        return output_keys

    def _generate_manifest(self, video_id: str, n_chunks: int) -> Dict[str, str]:
        """Generate HLS master + per-rendition playlists."""
        manifests = {}
        master_lines = ["#EXTM3U"]
        for quality, w, h, kbps in QUALITIES:
            master_lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={kbps*1000},RESOLUTION={w}x{h}")
            master_lines.append(f"{quality}/playlist.m3u8")
            # Per-rendition playlist
            pl = ["#EXTM3U", "#EXT-X-VERSION:3", "#EXT-X-TARGETDURATION:30"]
            for i in range(n_chunks):
                pl.append(f"#EXTINF:{CHUNK_DURATION_SEC},")
                pl.append(f"processed/{video_id}/{quality}/chunk_{i:04d}.ts")
            pl.append("#EXT-X-ENDLIST")
            manifests[f"processed/{video_id}/{quality}/playlist.m3u8"] = "\n".join(pl)
        manifests[f"processed/{video_id}/master.m3u8"] = "\n".join(master_lines)
        return manifests

    def _worker(self, worker_id: int) -> None:
        while True:
            chunk = self._chunk_queue.get()
            try:
                keys = self._transcode_chunk(chunk)
                with self._lock:
                    job = self._jobs[chunk.job_id]
                    job.chunks_done += 1
                    if job.chunks_done == job.chunks_total:
                        # All chunks done: generate manifest
                        manifests = self._generate_manifest(
                            job.video_id, job.chunks_total)
                        for k, v in manifests.items():
                            self._s3[k] = v.encode()
                        job.status = "done"
                        elapsed = time.time() - job.created_at
                        print(f"[Worker {worker_id}] Job {job.job_id} DONE "
                              f"({job.chunks_total} chunks, {elapsed:.2f}s wall-clock)")
            except Exception as e:
                with self._lock:
                    self._jobs[chunk.job_id].status = "failed"
                print(f"[Worker {worker_id}] Chunk {chunk.chunk_index} FAILED: {e}")
            finally:
                self._chunk_queue.task_done()

    def get_job(self, job_id: str) -> Optional[TranscodeJob]:
        return self._jobs.get(job_id)

    def get_manifest_url(self, video_id: str) -> Optional[str]:
        key = f"processed/{video_id}/master.m3u8"
        if key in self._s3:
            return f"https://cdn.example.com/{key}"
        return None


# Demo
if __name__ == "__main__":
    pipeline = TranscodingPipeline(worker_count=8)

    # Simulate uploading a 3-minute video
    video_id = "dQw4w9WgXcQ"
    job_id = pipeline.submit(
        video_id=video_id,
        raw_s3_key=f"raw/{video_id}/upload.mp4",
        duration_sec=180.0  # 3-minute video → 6 chunks of 30s
    )
    print(f"Submitted job {job_id} for video {video_id}")
    print(f"Chunks to transcode: {pipeline.get_job(job_id).chunks_total} "
          f"× {len(QUALITIES)} qualities = "
          f"{pipeline.get_job(job_id).chunks_total * len(QUALITIES)} segment batches")

    # Wait for completion
    pipeline._chunk_queue.join()
    job = pipeline.get_job(job_id)
    print(f"Job status: {job.status}")
    url = pipeline.get_manifest_url(video_id)
    print(f"Playback URL: {url}")
```
