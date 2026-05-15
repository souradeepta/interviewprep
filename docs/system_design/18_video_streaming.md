# Video Streaming Platform

## Problem Statement
Design a platform for video streaming with adaptive bitrate and CDN delivery.

**Requirements:**
- Upload video
- Transcode to multiple bitrates
- Stream with adaptive quality
- Cache across CDN
- Track playback analytics

## Design

### Transcoding Pipeline

```
Upload → Queue task
Worker picks task → Transcode to bitrates (480p, 720p, 1080p)
Store segments → CDN
Index in metadata DB
```

### Adaptive Bitrate Streaming

```
Client measures bandwidth
Request appropriate quality
Manifest file lists available bitrates
Switch on connection change
```

### CDN Strategy

```
Popular videos → Edge cache
Edge cache bandwidth exceeds → Origin pulls
LRU eviction for capacity
Geographic distribution
```


## Architecture Diagram

```
┌───────────────────────────────┐
│   Video Streaming Platform    │
│  Video Ingestion              │
│  - Upload to S3               │
│  - Transcode to multiple res  │
│  - CDN distribution           │
│  Adaptive Bitrate Playback    │
│  - Monitor bandwidth          │
│  - Switch resolution per 4s   │
│  Analytics                    │
│  - Watch time, completion     │
└───────────────────────────────┘
```

## Common Questions & Answers

**Q: Adaptive bitrate switching?** A: Monitor download speed, estimate bandwidth. Downgrade if slow, upgrade if fast. Switch at chunk boundary (4s).

**Q: Transcoding cost?** A: Pre-transcode (slow ingestion) vs on-demand (slow playback). Cache formats (storage cost). Usually: 3-4 resolutions.

**Q: Low startup latency?** A: Cache first chunk locally, CDN edge, start low res + switch up.

**Q: Live streaming?** A: RTMP ingest to multiple servers, HLS distribution.

## Back-of-Envelope Calculations

1M concurrent, 4 Mbps avg. Bandwidth: 4Tbps. Storage: 1M × 2GB = 2EB. Transcoding: 1h video = ~5h encode.
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Progressive download | Simple | No ABR |
| DASH streaming | Adaptive | Latency |
| RTMP | Low latency | Not web |

## Follow-up Interview Questions

1. Live with 1M concurrent? 2. DRM implementation? 3. P2P optimization? 4. CDN bottleneck? 5. Content popularity caching?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Upload | O(n) where n=file size |
| Transcode | O(n) CPU-intensive |
| Stream | O(1) per request |
| Store segment | O(log n) |
