# Photo Sharing Platform

## Problem Statement
Design a photo sharing system with upload, storage, CDN, and thumbnail generation.

**Operations:**
- `uploadPhoto(user_id, file)` — Upload photo
- `getPhoto(photo_id, size)` — Get photo
- `deletePhoto(user_id, photo_id)` — Delete photo
- `getAlbum(album_id)` — Get album

## Design

### Upload Pipeline

```
1. Upload to blob storage (S3)
2. Queue thumbnail generation
3. Generate thumbnails (multiple sizes)
4. Update metadata DB
5. Invalidate CDN cache
```

### CDN Delivery

```
Original → Origin
Thumbnails → Edge cache
User request → Closest edge
Fallback to origin on miss
```

### Storage Optimization

```
Thumbnail compression: 70% size reduction
Original archival: Cheaper tier
Metadata indexing: Fast search
Deduplication: Same photo detected
```

## Complexity

| Operation | Time |
|-----------|------|
| Upload | O(n) |
| Thumbnail gen | O(n) async |
| Get | O(1) cache |
