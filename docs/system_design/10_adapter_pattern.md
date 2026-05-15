# Adapter Pattern

## Problem Statement

Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

**Use Cases:**
- Third-party library integration
- Legacy code integration
- Interface translation (USB-C to USB-A adapter)
- Incompatible libraries/APIs

## Design

### Class Diagram

```
        Client (expects Target interface)
             │
             ├─→ Adapter
                    │
                    └─→ delegates to Adaptee
```

### Key Components

```
Target: Interface client expects
Adapter: Implements Target, wraps Adaptee
Adaptee: Existing interface to adapt
Client: Uses Adapter through Target interface
```

### Adapter Implementation

```
class Adapter implements Target {
  private Adaptee adaptee;
  
  public void targetMethod() {
    // Translate to Adaptee's interface
    adaptee.adapteeMethod();
  }
}
```

## Types

```
Class Adapter: Uses inheritance (less flexible)
Object Adapter: Uses composition (more flexible) - preferred
```


## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│      Client                                 │
│  (expects MediaPlayer interface)            │
│                                             │
│  + play(audioFile)                          │
│  + stop()                                   │
└────────────┬──────────────────────────────┘
             │ uses Target interface
             ▼
┌─────────────────────────────────────────────┐
│      MediaAdapter (Adapter)                 │
│  ┌──────────────────────────────────────┐   │
│  │  - vlcPlayer: VLCPlayer (Adaptee)    │   │
│  │  - mediaPlayer: MediaPlayer          │   │
│  │                                      │   │
│  │  + play(file) {                      │   │
│  │      vlcPlayer.playVLC(file)         │   │
│  │    }                                 │   │
│  └──────────────────────────────────────┘   │
│         delegates to Adaptee                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      VLCPlayer (Adaptee)                    │
│  (incompatible interface)                   │
│                                             │
│  + playVLC(vlcFile)                         │
│  + stopVLC()                                │
└─────────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Object Adapter vs Class Adapter?**
A: Object Adapter (composition): wraps Adaptee, flexible, can adapt subclasses. Class Adapter (inheritance): inherits from Adaptee, simpler but inflexible, breaks if Adaptee changes. Use Object Adapter (composition over inheritance).

**Q: When to adapt vs modify the source?**
A: Adapt if: source is third-party, legacy, or used elsewhere (don't want to break). Modify if: you own the code and can change it safely. Adapter masks incompatibility; refactoring fixes it. Prefer refactoring for codebase you own.

**Q: Multiple adapters for same Adaptee?**
A: Yes, normal. Different targets may expect different interfaces. One Adaptee → multiple adapters. Each adapter specializes for specific client expectations. Avoids client modification.

**Q: Data conversion in adapter—performance impact?**
A: Adapter may transform data (e.g., XML to JSON). Overhead depends on data size. For small data, negligible. For large, consider caching or streaming. Mark hot path adapters for optimization.

## Back-of-Envelope Calculations

For typical scenario (JSON to XML adapter, 100K requests/sec):
- Storage: Adapter class × 1KB code = 1KB, minimal instances
- Throughput: Adapter translation O(n) where n=data size, 100KB payload = 1-5ms
- Latency: Data transformation adds 1-5ms per request
- Bandwidth: Same data size (just format conversion)

Scaling: Adapter doesn't bottleneck if transformation is fast. Bottleneck is actual I/O to Adaptee.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Object Adapter | Flexible, composition, no inheritance | Extra indirection |
| Class Adapter | Simple, direct inheritance | Breaks inheritance chain, inflexible |
| No Adapter (modify source) | Direct, simple | Breaks compatibility, invasive |

## Follow-up Interview Questions

1. How would you handle bidirectional adaptation (convert both directions)?
2. What if Adaptee interface changes? Adapter becomes brittle; how to handle versioning?
3. How to monitor adapter usage and transformation latency?
4. What's the bottleneck at 10x scale (1M requests)? Adapter transformation time, not invocation.
5. How would you implement lazy adaptation (only transform when needed)?

## Example Scenario Walkthrough

Scenario: Integrate legacy VLCPlayer into modern MediaPlayer system

Initial setup:
- Client expects: MediaPlayer interface (play, stop, pause)
- Existing code: VLCPlayer with (playVLC, stopVLC, pauseVLC)
- Incompatible interfaces

Step 1: Client requests to play file
- Client.play("movie.mp4")
- Client expects MediaPlayer interface

Step 2: Adapter intercepts call
- MediaAdapter receives play("movie.mp4")
- Adapter wraps VLCPlayer internally

Step 3: Adapter translates and delegates
- MediaAdapter.play("movie.mp4") {
-     vlcPlayer.playVLC("movie.mp4")
- }

Step 4: VLCPlayer executes actual work
- Loads VLC codec
- Plays movie.mp4
- Client gets expected behavior

Step 5: Client requests to stop
- Client.stop()
- MediaAdapter.stop() {
-     vlcPlayer.stopVLC()
- }

Step 6: Integration complete
- Client code unchanged (works with MediaPlayer interface)
- VLCPlayer integrated seamlessly
- No modification to VLCPlayer source code
- Adapter handles interface translation

## Trade-offs

| Pro | Con |
|-----|-----|
| Makes incompatible work | Extra indirection |
| Single Responsibility | May require multiple adapters |
| Open/Closed principle | Complexity |
| Reuses existing code | Don't overuse |

## Complexity

| Operation | Time |
|-----------|------|
| adapt | O(1) |
| delegate | O(1) |
