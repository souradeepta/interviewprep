# Geohashing

## Problem Statement

Encodes geographic location into a string. Enables efficient spatial queries and proximity searches.

## Design

### Key Concepts

```
Recursively subdivide map into quadrants, encode as bits. String from bits via base32.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
Geohash encoding:
  World → 32 quadrants (level 1, 5 bits)
  Each quadrant → 32 sub-quadrants (level 2)
  Each sub-quadrant → 32 sub-sub-quadrants (level 3)
  "wx4" = precision level 3 geohash
```

## Common Questions & Answers

**Q: Precision levels?** A: 11 chars = 37cm accuracy. 8 chars = 38m. 6 chars = 1.2km.

**Q: Spatial queries?** A: Query geohash neighbors for nearby results.

**Q: Index efficiency?** A: B-tree on geohash string enables range scans.

## Back-of-Envelope Calculations

- Earth = 10 billion geohashes (level 6)
- User location precision: level 8 = 38m (fine for most apps)
- Neighbor queries: check up to 9 hashes (current + 8 neighbors)

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Geohashing | String-based, indexable | Proximity anomalies at boundaries |
| Latitude/Longitude | Direct coordinates | Requires 2D spatial indexing (R-tree) |
| Quadtree | Perfect spatial locality | More complex to implement |

## Follow-up Interview Questions

1. How would you implement this at scale (1M+ operations/sec)?
2. What happens if the [key component] fails?
3. How to ensure [important property] in this system?
4. What's the bottleneck at 10x current scale?
5. How would you monitor and debug [specific aspect]?

## Example Scenario Walkthrough

Scenario: [Concrete example with 5-10 steps showing system in action]

## Implementation

### Python Implementation

```python
class GeoHash:
    def __init__(self, lat, lon, precision=6):
        self.lat = lat
        self.lon = lon
        self.precision = precision

    def encode(self):
        lat_range = [-90, 90]
        lon_range = [-180, 180]
        geohash = []
        bits = 0
        bit = 0
        ch = 0

        while len(geohash) < self.precision:
            if bits % 2 == 0:
                mid = (lon_range[0] + lon_range[1]) / 2
                if self.lon > mid:
                    ch |= (1 << (4 - bit))
                    lon_range[0] = mid
                else:
                    lon_range[1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) / 2
                if self.lat > mid:
                    ch |= (1 << (4 - bit))
                    lat_range[0] = mid
                else:
                    lat_range[1] = mid

            bits += 1
            if bits == 5:
                geohash.append(self._base32_char(ch))
                bits = 0
                ch = 0
            bit += 1

        return ''.join(geohash)

    def _base32_char(self, val):
        base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
        return base32[val]
```

### Java Implementation

```java
class GeoHash {
    private final double lat, lon;
    private final int precision;
    private static final String BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz";

    public GeoHash(double lat, double lon, int precision) {
        this.lat = lat;
        this.lon = lon;
        this.precision = precision;
    }

    public String encode() {
        double[] latRange = {-90, 90};
        double[] lonRange = {-180, 180};
        StringBuilder geohash = new StringBuilder();
        int bits = 0, ch = 0;

        while (geohash.length() < precision) {
            if (bits % 2 == 0) {
                double mid = (lonRange[0] + lonRange[1]) / 2;
                if (lon > mid) {
                    ch |= (1 << (4 - (bits / 2)));
                    lonRange[0] = mid;
                } else {
                    lonRange[1] = mid;
                }
            } else {
                double mid = (latRange[0] + latRange[1]) / 2;
                if (lat > mid) {
                    ch |= (1 << (4 - (bits / 2)));
                    latRange[0] = mid;
                } else {
                    latRange[1] = mid;
                }
            }

            bits++;
            if (bits == 5) {
                geohash.append(BASE32.charAt(ch));
                bits = 0;
                ch = 0;
            }
        }
        return geohash.toString();
    }
}
```

### Production Considerations

- **Concurrency**: Thread safety and synchronization
- **Error Handling**: Fault tolerance and recovery
- **Monitoring**: Observability and metrics
- **Performance**: Optimization strategies

## Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| [Key Op 1] | O(n) | [Explanation] |
| [Key Op 2] | O(log n) | [Explanation] |
| [Key Op 3] | O(1) | [Explanation] |

## Real-world Applications

- Use case 1
- Use case 2
- Use case 3

## Related Concepts

- Concept A (see documentation)
- Concept B (see documentation)
- Concept C (see documentation)

## Further Reading

- Academic papers
- System design references
- Implementation guides
