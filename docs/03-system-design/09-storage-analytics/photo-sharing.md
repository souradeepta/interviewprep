# Photo Sharing System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Photo sharing platforms like Instagram handle hundreds of millions of photo uploads per day, serving billions of views to users around the world. The core challenge is not just storing photos — it is the asymmetry between write volume (500M uploads/day) and read volume (50B+ views/day), requiring aggressive caching and CDN delivery, while also managing metadata, social graph integration, and privacy controls.

The system must handle uploads reliably (no lost photos), generate multiple resolutions for different device types, strip privacy-sensitive EXIF data, and deliver images from edge locations within 100ms globally.

## Functional Requirements

- Users can upload photos (JPEG, PNG, HEIC) up to 50MB
- System generates thumbnails in multiple resolutions (150px, 320px, 640px, 1080px, original)
- Photos are associated with a user, can be tagged, added to albums, and given a caption
- Photos are served via CDN for low-latency delivery worldwide
- Users can like, comment on, and share photos
- Photos can be public or private; private photos only visible to followers

## Non-Functional Requirements

- **Scale:** 500M uploads/day (~5,800 uploads/sec peak), 50B photo views/day (~580K views/sec)
- **Latency:** Upload: P99 < 3s; Photo delivery: P99 < 100ms globally
- **Availability:** 99.99% for reads; 99.9% for uploads (slight degradation acceptable)
- **Consistency:** Eventual — slight delay between upload and global availability acceptable

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Uploads: 500M/day = 5,800/sec average; 17,400/sec peak (3x)
Avg photo size (after compression): 3 MB
Upload throughput: 5,800 * 3MB = 17.4 GB/sec incoming bandwidth
Storage per day: 500M * 3MB = 1.5 PB/day

Thumbnail generation: 5 resolutions per photo
  - 150px: ~15KB, 320px: ~60KB, 640px: ~200KB, 1080px: ~800KB, original: ~3MB
  - Total per photo: ~4MB (original + thumbnails)
  - Total storage per day: 500M * 4MB = 2 PB/day

Reads: 50B views/day = 580K views/sec; assume 90% from CDN cache
  - CDN cache hit rate: 90% → origin: 58K req/sec
  - Average served resolution: 640px (200KB)
  - CDN egress: 580K * 200KB = 116 GB/sec

Metadata:
  - Photos table: 500M/day * 365 days = 182.5B rows/year
  - Per row: ~500 bytes → 91 TB/year of metadata (use distributed DB, shard by user_id)
```

### Architecture Diagram

```
Upload Flow:
Client
  |
  | (HTTPS multipart upload)
  v
+----------------+
| Upload Service |  <-- Validates file type, size; generates upload_id
+----------------+
  |                   |
  | write original    | emit PhotoUploaded event
  v                   v
+--------+       +-----------+
| S3     |       | Kafka     |
| Object |       | (upload   |
| Store  |       |  events)  |
+--------+       +-----------+
                      |
                      v
              +------------------+
              | Thumbnail Worker |  <-- Async: generates 5 resolutions
              | (Lambda / K8s)   |      strips EXIF, writes to S3
              +------------------+
                      |
              [PhotoProcessed event]
                      |
              +------------------+
              | Metadata Writer  |  <-- Writes to Photos DB, updates CDN
              +------------------+

Read Flow:
Client
  |
  | GET photo_id
  v
+------+        Cache Miss         +----------+
| CDN  | -----------------------> | Image    |
|(Edge)|                           | Service  |
|      | <-- 200 OK (image bytes)--|          |
+------+                           +----------+
                                        |
                                   Reads from S3
                                   (origin pull)
```

### Data Model

```sql
-- Photos: core metadata
CREATE TABLE photos (
    photo_id      UUID PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    s3_key        VARCHAR(500) NOT NULL,      -- Path in S3 bucket
    caption       TEXT,
    width         INT,
    height        INT,
    file_size_kb  INT,
    mime_type     VARCHAR(50),
    status        VARCHAR(20) DEFAULT 'PROCESSING', -- PROCESSING, ACTIVE, DELETED
    visibility    VARCHAR(10) DEFAULT 'PUBLIC',     -- PUBLIC, FOLLOWERS, PRIVATE
    taken_at      TIMESTAMPTZ,               -- From EXIF, if present
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    INDEX (user_id, created_at DESC)
);

-- Thumbnails: one row per resolution per photo
CREATE TABLE photo_thumbnails (
    photo_id     UUID REFERENCES photos(photo_id),
    resolution   VARCHAR(10),   -- '150', '320', '640', '1080', 'original'
    s3_key       VARCHAR(500),
    width        INT,
    height       INT,
    file_size_kb INT,
    PRIMARY KEY (photo_id, resolution)
);

-- Albums: groupings of photos
CREATE TABLE albums (
    album_id   UUID PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    name       VARCHAR(200),
    cover_photo_id UUID REFERENCES photos(photo_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Photo tags (user tagging other users)
CREATE TABLE photo_tags (
    photo_id    UUID REFERENCES photos(photo_id),
    tagged_user_id BIGINT,
    tagged_by   BIGINT,
    x_pos       FLOAT,   -- 0.0–1.0 normalized position
    y_pos       FLOAT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (photo_id, tagged_user_id)
);
```

### API Design

```
POST /photos/upload
  Content-Type: multipart/form-data
  Body: { file: <binary>, caption: "...", visibility: "PUBLIC", album_id?: "..." }
  Response: { photo_id, status: "PROCESSING", estimated_ready_ms: 5000 }

GET /photos/{photo_id}
  Response: { photo_id, user_id, caption, urls: { "150": "cdn.../...", "640": "..." }, ... }

GET /users/{user_id}/photos?cursor=<...>&limit=20
  Response: { photos: [...], next_cursor: "..." }

DELETE /photos/{photo_id}
  Response: 204 No Content (soft delete: status=DELETED; S3 key retained for 30 days)

POST /photos/{photo_id}/tags
  Body: { tagged_user_id, x_pos: 0.3, y_pos: 0.4 }
  Response: { tag_id, status: "PENDING_APPROVAL" }

GET /photos/{photo_id}/status
  Response: { photo_id, status: "ACTIVE" | "PROCESSING", thumbnails_ready: [...] }
```

### Basic Scaling

- Store originals and thumbnails in S3 (11 nines durability); organize by `user_id/date/photo_id` for lifecycle policies
- Use CloudFront (or Fastly) as CDN; configure origin pull from S3 with long cache TTLs (1 year for immutable photo URLs)
- Shard the Photos DB by `user_id` — most queries are per-user (user's feed, profile photos)
- Generate thumbnails asynchronously after upload; return `status: PROCESSING` immediately to the client

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Upload pipeline:
  - Upload Service: 20 instances (c5.2xlarge, 8 vCPU, 16GB RAM)
    Each handles: 17,400 peak / 20 = 870 concurrent uploads
    Bandwidth per instance: 870 * 3MB / 8 vCPU = ~320 MB/sec (network bound, not CPU)
    Use S3 multipart upload: upload directly from client to S3 via pre-signed URL → bypass Upload Service for bandwidth

  - Thumbnail Workers: 200 instances (c5.xlarge, 4 vCPU)
    Processing time per photo: 2s (5 resolutions, image decode + resize + encode)
    Throughput per worker: 0.5 photos/sec
    Required for peak: 17,400 / 0.5 = 34,800 workers (use auto-scaling Lambda → burst to thousands)
    Cost: Lambda at 2s * 512MB * 17,400/sec peak = $0.0000002 * 2 * 512MB * 17,400 = $3.6/hr peak

S3 storage costs (per month):
  - New uploads: 2 PB/day * 30 = 60 PB/month
  - S3 Standard: $0.023/GB → 60 PB = $1.4M/month (too expensive)
  - Intelligent-Tiering: transitions to Infrequent Access after 30 days
    Photos older than 30 days: $0.0125/GB (IA tier)
    Assume 80% of photos rarely accessed after 30 days → $0.0125 * 0.8 * 60 PB = $600K/month
  - Original files: archive to Glacier after 1 year ($0.004/GB)
  - Total S3 cost: ~$600K-$800K/month (Instagram-scale; factored into $0.10/user/month)

CDN cost:
  - 580K views/sec * 200KB = 116 GB/sec = 9.7 PB/day egress
  - CloudFront: $0.0085/GB for 100+ PB/month → $82/day per PB = $800K/month
  - Optimization: use WebP format (50% smaller than JPEG) → halves CDN egress cost
```

### Failure Modes

```
Failure: Thumbnail worker crashes mid-processing
  Impact: Photo stuck in PROCESSING state; user never sees it as ACTIVE
  Mitigation:
    - Kafka consumer group: if worker crashes, message is re-delivered to another worker
    - Idempotency: worker writes thumbnails to S3 under deterministic key (photo_id/resolution)
      Re-processing is safe — overwrites existing file with identical content
    - Timeout monitor: scans for photos with status=PROCESSING older than 5 minutes → re-enqueues

Failure: S3 outage in primary region
  Impact: New uploads fail; reads from origin fail (CDN cache still serves)
  Mitigation:
    - Write to 2 S3 regions simultaneously (cross-region replication or dual-write)
    - CDN cache shields reads: P99 CDN cache hit 90% means 90% of reads unaffected
    - Upload degradation: queue uploads to local disk, replay when S3 recovers (rare)

Failure: CDN cache invalidation on photo delete
  Impact: Deleted photo still served from CDN for up to TTL duration (1 year)
  Mitigation:
    - Use capability URLs (signed URLs with expiry) rather than public URLs
    - Signed URL expiry: 1 hour → deleted photos become inaccessible within 1 hour
    - For legal takedowns (CSAM, DMCA): emergency CDN purge via CloudFront invalidation API
      Cost: $0.005 per path invalidation → acceptable for urgent takedowns

Failure: EXIF stripping fails — GPS coordinates leak
  Impact: Privacy violation; user location metadata exposed
  Mitigation:
    - Strip EXIF in thumbnail worker BEFORE writing to S3 (not after)
    - Use ExifTool or Pillow's image.info stripping; validate by re-reading EXIF after write
    - Original file (with EXIF) stored in user-private S3 bucket (not CDN-accessible)
    - Only thumbnails (EXIF-stripped) are served via CDN
```

### Consistency Boundaries

```
Upload → availability delay: ~5 seconds (thumbnail generation pipeline lag)
  - Acceptable: client polls /photos/{photo_id}/status until ACTIVE
  - Alternative: WebSocket push when photo becomes ACTIVE (better UX)

CDN cache consistency:
  - Photo URL is immutable once ACTIVE (content-addressed by photo_id + resolution)
  - Caption edits: only metadata changes → served from Photos DB, not CDN
  - CDN serves only the image bytes (immutable); caption/like counts from API

Privacy change (PUBLIC → PRIVATE):
  - Photos DB update is immediate
  - CDN cache: signed URL TTL expires in 1 hour → effectively private within 1 hour
  - For immediate privacy requirement: use CDN signed URLs with 5-minute TTL
    (trade-off: more origin requests when users share photos widely)

Like/comment counts:
  - Eventual consistency: counters stored in Redis, periodically flushed to DB
  - Acceptable: counts may lag by seconds; precise counts in DB reconciled every minute
  - See like-comment-system.md for full counter design
```

### Cost Model

```
Storage (S3 Intelligent-Tiering): ~$700K/month
CDN (CloudFront): ~$400K/month (with WebP optimization)
Compute (upload + thumbnails): ~$200K/month (Lambda + EC2)
Database (Aurora PostgreSQL sharded): ~$100K/month

Total: ~$1.4M/month for Instagram-scale (500M uploads/day, 50B views/day)
Revenue at 500M MAU * $0.50 ARPU: $250M/month
Infrastructure as % of revenue: ~0.56%

Per user per month (500M MAU):
  - Storage: $700K / 500M = $0.0014/user
  - CDN: $400K / 500M = $0.0008/user
  - Total infra: ~$0.003/user/month
```

---

## Trade-off Comparison

| Approach                        | Pros                                             | Cons                                                | Best For                              |
|---------------------------------|--------------------------------------------------|-----------------------------------------------------|---------------------------------------|
| S3 + CDN (standard)             | Proven durability, global edge delivery          | Cost at extreme scale; CDN egress expensive          | Most photo platforms (default)        |
| Self-hosted object store (Ceph) | Eliminates S3 cost; full control                 | Operational overhead; harder to scale globally      | Large orgs with dedicated infra teams |
| Content-addressed storage       | Deduplication (same photo uploaded twice = 1 copy)| Hash computation overhead; complex key management  | Platforms with high upload duplication|
| Signed URLs (short TTL)         | Immediate privacy enforcement on URL change      | More origin requests; harder to cache               | Privacy-sensitive photos, HIPAA       |
| WebP format                     | 50% smaller than JPEG; reduces CDN cost          | Older clients don't support WebP                   | Web-first platforms (serve WebP to modern browsers, JPEG fallback) |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** Why do we generate multiple thumbnail resolutions instead of serving the original?
   → A 50MB original served to a mobile device wastes bandwidth and increases page load time. A 640px thumbnail at ~200KB loads 250x faster. Different device types need different sizes: 150px for profile photos, 1080px for full-screen view. Pre-generating thumbnails at upload time avoids CPU-intensive resizing on every read request.

2. **(L3)** How does a CDN help with photo delivery?
   → A CDN (Content Delivery Network) caches photos at edge locations close to users worldwide. Instead of every request hitting your origin servers in us-east-1, a user in Tokyo gets the photo from a Tokyo edge node. This reduces latency from 200ms (cross-Pacific) to <20ms and reduces origin load by 90%.

3. **(L4)** How do you handle photo privacy when a user switches a photo from PUBLIC to PRIVATE?
   → Update the Photos DB immediately (strong consistency). For CDN cache: if using capability URLs (signed URLs), wait for the TTL to expire — typically 1 hour. For immediate enforcement, issue a CDN cache invalidation API call (at $0.005 per path), affordable for high-priority privacy requests. For regulated use cases (e.g., CSAM takedowns), CDN purge is mandatory and done programmatically.

4. **(L4)** What is EXIF data and why must you strip it?
   → EXIF (Exchangeable Image File Format) metadata is embedded in JPEG files by cameras and phones. It includes GPS coordinates (precise location where the photo was taken), camera model, lens settings, and sometimes the owner's name or email. Serving photos with EXIF data intact leaks the user's home address, workplace, and movement history. Always strip EXIF in the thumbnail worker before writing to CDN-accessible S3 storage. Retain EXIF only in the user's private original file if you offer a "download original" feature.

5. **(L5)** How would you design the thumbnail pipeline to handle 17,400 uploads/sec at peak?
   → Use Lambda for thumbnail workers: each Lambda invocation processes one photo, generating all 5 resolutions. Lambda can burst to thousands of concurrent invocations automatically, handling peak load without pre-provisioning. Use SQS or Kafka as the event queue between the upload acknowledgment and Lambda invocation. Key metrics to monitor: Lambda cold start rate (keep warm with provisioned concurrency for the first 100 instances), SQS queue depth (alert if > 5 minutes of backlog), and Lambda error rate. Cost at peak: ~$3.60/hr for Lambda compute alone.

6. **(L5)** Instagram-scale implies storing ~2 PB of new photos daily. How do you manage cost?
   → Use S3 Intelligent-Tiering: photos accessed frequently in the first 30 days stay in Standard tier ($0.023/GB), then automatically move to Infrequent Access ($0.0125/GB) for photos rarely accessed after 30 days. After 1 year, move original files to Glacier ($0.004/GB). Convert originals to WebP format at storage time — 50% size reduction cuts storage and CDN costs in half. Delete thumbnails for deleted photos immediately; archive originals to Glacier for legal hold compliance.

7. **(L5+)** How would you design the system to prevent hot shard problems in the Photos DB?
   → Sharding by user_id means a celebrity with 500M followers causes a hot shard when posting a photo. Solutions: (1) Route celebrity reads to read replicas rather than the primary — fan-out reads are read-heavy. (2) Cache celebrity photo metadata in Redis with a 5-minute TTL — 90% of reads are served from cache. (3) Use consistent hashing with virtual nodes — redistribute hot user's data across multiple physical shards. (4) For truly viral photos, pre-warm CDN cache by proactively pushing the photo to edge nodes rather than waiting for organic cache misses. This reduces origin load from millions of simultaneous cache misses to near-zero.

## Anti-patterns / Things NOT to Say

- **"Store photos in the database as BLOBs"** — Databases are optimized for indexed structured data, not large binary objects. Storing 500M * 3MB photos in PostgreSQL would require 1.5 PB of DB storage, destroy query performance with page-level fragmentation, and make backup/restore prohibitively slow. Use object storage (S3) for binaries; store only metadata and S3 keys in the DB.
- **"Serve photos directly from the application server"** — Application servers are optimized for business logic, not bandwidth. Serving 580K photo requests/sec at 200KB each requires 116 GB/sec of bandwidth — your app servers would have thousands of nodes just for egress. Use CDN for static asset delivery; let app servers handle API requests only.
- **"Generate thumbnails synchronously during upload"** — Synchronous thumbnail generation adds 2-5 seconds to the upload P99 and blocks the upload thread. For peak 17,400 uploads/sec, synchronous generation would require 17,400 * 2s = 34,800 concurrent thumbnail workers all the time. Async generation with a message queue decouples upload latency from processing capacity.
- **"Use the same S3 bucket for both originals (with EXIF) and CDN-served thumbnails"** — If originals and thumbnails are in the same bucket with CDN access, there is a risk of accidentally serving originals through the CDN (via URL guessing or misconfigured bucket policy). Keep originals in a private bucket accessible only by the thumbnail worker; serve only EXIF-stripped thumbnails from the CDN-accessible bucket.

## Python Implementation (sketch)

```python
import uuid
import boto3
import io
from PIL import Image, ExifTags
from dataclasses import dataclass
from typing import Dict, List

THUMBNAIL_SIZES = {
    "150": (150, 150),
    "320": (320, 320),
    "640": (640, 640),
    "1080": (1080, 1080),
}

@dataclass
class PhotoUploadResult:
    photo_id: str
    original_s3_key: str
    thumbnail_keys: Dict[str, str]
    width: int
    height: int

class ThumbnailWorker:
    """Processes a photo upload: strip EXIF, generate thumbnails, write to S3."""

    def __init__(self, s3_client, bucket_private: str, bucket_cdn: str):
        self.s3 = s3_client
        self.bucket_private = bucket_private   # Originals with EXIF (not CDN-accessible)
        self.bucket_cdn = bucket_cdn           # Thumbnails without EXIF (CDN-accessible)

    def process(self, photo_id: str, user_id: int, raw_bytes: bytes) -> PhotoUploadResult:
        img = Image.open(io.BytesIO(raw_bytes))
        original_width, original_height = img.size

        # Step 1: Write original (with EXIF) to private bucket
        original_key = f"originals/{user_id}/{photo_id}.jpg"
        self.s3.put_object(
            Bucket=self.bucket_private,
            Key=original_key,
            Body=raw_bytes,
            ContentType="image/jpeg",
            ServerSideEncryption="AES256"
        )

        # Step 2: Strip EXIF before generating CDN thumbnails
        img_no_exif = self._strip_exif(img)

        # Step 3: Generate and upload thumbnails (no EXIF)
        thumbnail_keys = {}
        for size_name, (max_w, max_h) in THUMBNAIL_SIZES.items():
            thumb = img_no_exif.copy()
            thumb.thumbnail((max_w, max_h), Image.LANCZOS)
            thumb_bytes = self._encode_webp(thumb)
            key = f"thumbnails/{user_id}/{photo_id}/{size_name}.webp"
            self.s3.put_object(
                Bucket=self.bucket_cdn,
                Key=key,
                Body=thumb_bytes,
                ContentType="image/webp",
                CacheControl="public, max-age=31536000, immutable"  # 1-year CDN cache
            )
            thumbnail_keys[size_name] = key

        return PhotoUploadResult(
            photo_id=photo_id,
            original_s3_key=original_key,
            thumbnail_keys=thumbnail_keys,
            width=original_width,
            height=original_height
        )

    def _strip_exif(self, img: Image.Image) -> Image.Image:
        """Return a new Image with all EXIF metadata removed."""
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        return clean

    def _encode_webp(self, img: Image.Image, quality: int = 85) -> bytes:
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=quality, method=6)
        return buf.getvalue()

def generate_photo_upload_url(user_id: int, photo_id: str, s3_client) -> str:
    """Generate a pre-signed S3 URL for direct client upload (bypasses app server bandwidth)."""
    key = f"uploads/{user_id}/{photo_id}.jpg"
    url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": "photo-uploads-raw",
            "Key": key,
            "ContentType": "image/jpeg",
            "ContentLength": 50 * 1024 * 1024  # Max 50MB
        },
        ExpiresIn=300  # 5-minute window to complete upload
    )
    return url
```
