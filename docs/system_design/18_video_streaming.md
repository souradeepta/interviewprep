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

## Complexity

| Operation | Time |
|-----------|------|
| Upload | O(n) where n=file size |
| Transcode | O(n) CPU-intensive |
| Stream | O(1) per request |
| Store segment | O(log n) |
