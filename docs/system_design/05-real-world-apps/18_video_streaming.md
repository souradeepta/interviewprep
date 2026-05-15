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

### Architecture Diagram

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
```

## Complexity

| Operation | Time |
|-----------|------|
| Upload | O(n) where n=file size |
| Transcode | O(n) CPU-intensive |
| Stream | O(1) per request |
| Store segment | O(log n) |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class VideoQuality(Enum):
    SD = "480p"
    HD = "720p"
    FHD = "1080p"
    UHD = "4K"

@dataclass
class VideoSegment:
    segment_id: int
    quality: VideoQuality
    url: str
    duration_s: float

@dataclass
class Video:
    video_id: str
    title: str
    segments: Dict[VideoQuality, List[VideoSegment]] = field(default_factory=dict)
    thumbnail_url: str = ""

class StreamingService:
    def __init__(self):
        self._videos: Dict[str, Video] = {}
        self._cdn_nodes: List[str] = []

    def upload(self, video: Video):
        self._videos[video.video_id] = video

    def get_manifest(self, video_id: str) -> Dict:
        video = self._videos[video_id]
        return {
            "video_id": video_id,
            "title": video.title,
            "qualities": [q.value for q in video.segments.keys()],
            "thumbnail": video.thumbnail_url,
        }

    def get_segment(self, video_id: str, quality: VideoQuality, segment_id: int) -> Optional[VideoSegment]:
        segs = self._videos[video_id].segments.get(quality, [])
        return segs[segment_id] if segment_id < len(segs) else None

    def adaptive_quality(self, bandwidth_mbps: float) -> VideoQuality:
        if bandwidth_mbps >= 25: return VideoQuality.UHD
        if bandwidth_mbps >= 8: return VideoQuality.FHD
        if bandwidth_mbps >= 5: return VideoQuality.HD
        return VideoQuality.SD

# Usage
svc = StreamingService()
v = Video("v1", "My Video")
svc.upload(v)
quality = svc.adaptive_quality(10)
print(quality)  # VideoQuality.FHD
```

## Java Implementation

```java
import java.util.*;

public class StreamingService {
    enum Quality { SD, HD, FHD, UHD }
    record Segment(int id, Quality quality, String url) {}
    record Video(String id, String title, Map<Quality, List<Segment>> segments) {}

    private Map<String, Video> videos = new HashMap<>();

    public void upload(Video v) { videos.put(v.id(), v); }

    public Quality adaptiveQuality(double bandwidthMbps) {
        if (bandwidthMbps >= 25) return Quality.UHD;
        if (bandwidthMbps >= 8)  return Quality.FHD;
        if (bandwidthMbps >= 5)  return Quality.HD;
        return Quality.SD;
    }

    public Optional<Segment> getSegment(String videoId, Quality q, int idx) {
        List<Segment> segs = videos.get(videoId).segments().getOrDefault(q, List.of());
        return idx < segs.size() ? Optional.of(segs.get(idx)) : Optional.empty();
    }
}
```
