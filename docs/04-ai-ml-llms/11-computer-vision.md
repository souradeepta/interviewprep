# Computer Vision — Image Recognition, Detection, Segmentation

CV systems extract semantic understanding from images and video. Core concepts for ML engineering and system design interviews.

---

## ⚖️ CV Architecture Trade-offs

| Architecture | Accuracy | Speed | Params | Memory | Best For |
|-------------|---------|-------|--------|--------|---------|
| **ResNet-50** | Good | Fast | 25M | 4 GB | Classification baseline |
| **EfficientNet-B7** | Excellent | Medium | 66M | 8 GB | Accuracy-efficiency balance |
| **ViT-L/16** | SOTA | Slow | 307M | 24 GB | High-accuracy classification |
| **YOLOv8-nano** | Medium | 100+ FPS | 3M | 1 GB | Real-time detection, mobile |
| **YOLOv8-x** | Excellent | 30 FPS | 68M | 8 GB | Accurate detection |
| **SAM** | SOTA (seg) | Slow | 636M | 16 GB | Interactive segmentation |

### Task Decision Framework

```
Image input
    │
    ├── One label for whole image?    → Classification (ResNet, EfficientNet)
    │
    ├── Where are objects?            → Object Detection (YOLO, Faster R-CNN)
    │
    ├── Pixel-level labels?           → Semantic Segmentation (DeepLab, SegFormer)
    │
    ├── Separate object instances?    → Instance Segmentation (Mask R-CNN)
    │
    └── Video temporal understanding? → Video Transformer (TimeSformer, ViViT)
```

---

## 🏗️ Architecture Patterns

### Pattern 1: CNN Architecture Evolution

```
AlexNet (2012) — 8 layers, 60M params, 15.4% top-5 error on ImageNet
  ↓ Breakthrough: showed deep CNNs work for images

VGG-16 (2014) — 16 layers, 138M params, 7.4% error
  ↓ Key idea: stack of small 3×3 convs > one large conv

ResNet-50 (2015) — 50 layers, 25M params, 5.3% error
  ↓ Key idea: Residual connections prevent vanishing gradients
      y = F(x) + x  ← skip connection; gradient flows directly

EfficientNet-B0 (2019) — compound scaling
  ↓ Key idea: scale depth, width, resolution together
      φ: depth = 1.2^φ, width = 1.1^φ, resolution = 1.15^φ

Vision Transformer ViT (2020) — patches as tokens
  ↓ Key idea: apply transformer directly to image patches
      16×16 patch → linear embed → sequence of tokens → attention
```

### Pattern 2: Object Detection Pipeline (YOLO)

```
Input Image (640×640)
        │
        ▼
    Backbone (feature extraction)
    CSPDarknet or EfficientRep
        │
        ▼
    Neck (multi-scale features)
    FPN + PAN (feature pyramid network)
    ┌────────────────────────┐
    │  P3: 80×80 (small objs)│
    │  P4: 40×40 (mid objs)  │
    │  P5: 20×20 (large objs)│
    └────────────────────────┘
        │
        ▼
    Head (prediction)
    For each cell × anchor:
      [cx, cy, w, h, objectness, class_0, ..., class_N]
        │
        ▼
    NMS (Non-Maximum Suppression)
    Remove duplicate overlapping boxes
        │
        ▼
    Final detections: [(x,y,w,h, confidence, class), ...]
```

### Pattern 3: Vision Transformer (ViT)

```
Input: 224×224 image
Step 1: Divide into 16×16 patches → 14×14 = 196 patches
Step 2: Flatten each patch → 768-dim vector
Step 3: Add position embedding (learned)
Step 4: Prepend [CLS] token
Step 5: Apply N transformer encoder layers
Step 6: Use [CLS] output for classification

Attention: every patch attends to every other patch
→ Captures global context that CNNs struggle with at early layers
Weakness: Needs much more data than CNN to match performance
```

---

## 📊 Transfer Learning Pipeline

```python
import time
from typing import Optional, Tuple, List

# Simulate a simplified CV training pipeline
# (Real implementation uses PyTorch/TensorFlow)

class ConvBlock:
    """Simulates a conv + BN + ReLU block."""
    def __init__(self, in_c: int, out_c: int, kernel: int = 3):
        self.in_c = in_c
        self.out_c = out_c
        self.kernel = kernel

    def __repr__(self):
        return f"Conv({self.in_c}→{self.out_c}, k={self.kernel})"

    def flops(self, h: int, w: int) -> int:
        return 2 * self.kernel**2 * self.in_c * self.out_c * h * w


class ResBlock:
    """ResNet residual block with skip connection."""
    def __init__(self, channels: int):
        self.conv1 = ConvBlock(channels, channels)
        self.conv2 = ConvBlock(channels, channels)

    def __repr__(self):
        return f"ResBlock({self.conv1.in_c})"


class SimpleCNN:
    """Simplified CNN architecture (not runnable without tensor framework)."""
    def __init__(self, num_classes: int = 1000):
        self.stem = ConvBlock(3, 64, kernel=7)
        self.layer1 = [ResBlock(64)] * 3
        self.layer2 = [ResBlock(128)] * 4
        self.layer3 = [ResBlock(256)] * 6
        self.layer4 = [ResBlock(512)] * 3
        self.classifier_in = 512
        self.num_classes = num_classes

    def estimate_params(self) -> int:
        """Rough parameter count estimate."""
        p = 3 * 64 * 7 * 7  # stem
        for layer in [self.layer1, self.layer2, self.layer3, self.layer4]:
            for block in layer:
                c = block.conv1.in_c
                p += 2 * (c * c * 9)  # Two 3×3 convs
        p += self.classifier_in * self.num_classes  # FC
        return p


class TransferLearningSetup:
    """
    Demonstrates transfer learning strategy selection.
    Real code: replace with PyTorch/TF model loading.
    """

    def __init__(self, base_model: str, num_classes: int, dataset_size: int):
        self.base_model = base_model
        self.num_classes = num_classes
        self.dataset_size = dataset_size

    def recommend_strategy(self) -> dict:
        """
        Strategy depends on:
        - Dataset size (small/large)
        - Domain similarity to ImageNet (similar/different)
        """
        if self.dataset_size < 1000:
            strategy = "linear_probe"
            description = "Freeze all layers, train only new classifier head"
            layers_to_train = "classifier_only"
        elif self.dataset_size < 10000:
            strategy = "fine_tune_last"
            description = "Freeze early layers, train last 2 blocks + head"
            layers_to_train = "layer4 + classifier"
        else:
            strategy = "full_fine_tune"
            description = "Train all layers with low LR (1e-4 to 1e-5)"
            layers_to_train = "all"

        return {
            "base_model": self.base_model,
            "dataset_size": self.dataset_size,
            "num_classes": self.num_classes,
            "strategy": strategy,
            "description": description,
            "layers_to_train": layers_to_train,
            "recommended_lr": "1e-2 (head)" if layers_to_train == "classifier_only" else "1e-4",
            "epochs": 5 if strategy == "linear_probe" else 20,
        }


# Demo
setups = [
    TransferLearningSetup("ResNet-50", num_classes=10, dataset_size=500),
    TransferLearningSetup("ResNet-50", num_classes=50, dataset_size=5000),
    TransferLearningSetup("EfficientNet-B4", num_classes=200, dataset_size=100000),
]

for setup in setups:
    rec = setup.recommend_strategy()
    print(f"\nDataset: {rec['dataset_size']} samples, {rec['num_classes']} classes")
    print(f"  Strategy: {rec['strategy']}")
    print(f"  Train layers: {rec['layers_to_train']}")
    print(f"  Learning rate: {rec['recommended_lr']}")
```

---

## 📏 Detection Metrics

```python
def compute_iou(box1: tuple, box2: tuple) -> float:
    """
    Compute Intersection over Union.
    Boxes: (x1, y1, x2, y2) format.
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection

    return intersection / union if union > 0 else 0.0


def compute_ap(precisions: List[float], recalls: List[float]) -> float:
    """Average Precision: area under precision-recall curve."""
    # Interpolated AP (11-point)
    ap = 0.0
    for recall_threshold in [r / 10 for r in range(11)]:
        prec_at_recall = [p for p, r in zip(precisions, recalls) if r >= recall_threshold]
        ap += max(prec_at_recall, default=0) / 11
    return ap


# Example
pred_box  = (100, 100, 200, 200)
gt_box    = (110, 90, 210, 190)
iou = compute_iou(pred_box, gt_box)
print(f"IoU: {iou:.3f} ({'TP' if iou >= 0.5 else 'FP'})")

# Detection at different score thresholds
precs = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
recs  = [0.1, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9]
print(f"AP@0.5: {compute_ap(precs, recs):.3f}")
```

---

## ❓ Interview Q&A

**Q1: How do residual connections solve the vanishing gradient problem?**

A: Standard deep networks: gradients flow through every layer during backprop, multiplied by weights. If weights are <1, gradient shrinks exponentially → early layers learn nothing. ResNet adds `y = F(x) + x`: the skip connection creates a gradient highway. `∂L/∂x = ∂L/∂y × (∂F/∂x + I)` — the identity term `I` ensures gradient is at least 1, preventing vanishing. Practical: enables training 1000+ layer networks.

**Q2: YOLO vs. Faster R-CNN — when do you choose each?**

A: 
- **YOLO**: real-time requirements (>30 FPS), mobile/edge deployment, acceptable with lower accuracy on small objects. Use for: autonomous driving feed, live video analytics
- **Faster R-CNN**: highest accuracy needed, small objects matter, latency >100ms acceptable. Use for: medical imaging, satellite imagery analysis

Key difference: YOLO is single-stage (direct prediction); Faster R-CNN is two-stage (propose regions first, then classify). Two-stage = more accurate, slower.

**Q3: When should you use ViT instead of CNN?**

A: ViT advantages:
- Global context from first layer (attention = all patches talk to all patches)
- Better at capturing long-range relationships
- Scales better with data and compute

CNN advantages:
- Sample-efficient (inductive bias: translation invariance, locality)
- Better with <100K training examples
- Faster inference (convolutional operations highly optimized)

**Use ViT when**: large dataset (>1M examples), large model budget, need global context. **Use CNN when**: small dataset, real-time inference, mobile deployment.

**Q4: How do you handle class imbalance in object detection?**

A: Four techniques:
1. **Focal Loss** (RetinaNet): `FL(p) = -(1-p)^γ log(p)` — reduces loss weight for easy (well-classified) examples, focuses training on hard examples
2. **Oversampling**: repeat rare classes in training batches
3. **Data augmentation**: heavy augmentation (mosaic, mixup) for rare classes
4. **Sampling**: use class-aware sampling so each batch has balanced representation

**Q5: How would you deploy a real-time object detection system (30 FPS on edge)?**

A: Pipeline:
1. **Model**: YOLOv8-nano (3M params, <2ms inference) or YOLOv8-s
2. **Quantization**: INT8 quantization via TensorRT → 3-4× speedup, <1% accuracy drop
3. **Batching**: process frames in batch=4 for GPU utilization
4. **Input**: resize to 416×416 (vs. 640×640) — 2.4× fewer pixels, faster
5. **Hardware**: NVIDIA Jetson Orin (275 TOPS) or Apple M-series Neural Engine
6. **Benchmark**: measure with actual video stream, not synthetic; monitor memory, temperature, frame drops

---

## 🧪 Practical Exercises

### Exercise 1: IoU and NMS Implementation (Easy)

```python
def non_maximum_suppression(
    boxes: List[tuple],
    scores: List[float],
    iou_threshold: float = 0.5,
) -> List[int]:
    """
    Non-Maximum Suppression: remove duplicate detections.
    Returns indices of kept boxes.
    """
    if not boxes:
        return []

    # Sort by score descending
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    kept = []

    while order:
        current = order[0]
        kept.append(current)
        order = order[1:]

        # Remove boxes with high IoU to current
        order = [
            i for i in order
            if compute_iou(boxes[current], boxes[i]) < iou_threshold
        ]

    return kept


# Test
boxes = [(100,100,200,200), (110,105,205,205), (300,300,400,400), (305,295,405,395)]
scores = [0.9, 0.8, 0.7, 0.6]

kept_indices = non_maximum_suppression(boxes, scores, iou_threshold=0.5)
print(f"NMS kept {len(kept_indices)}/{len(boxes)} boxes: indices {kept_indices}")
print(f"Final detections: {[boxes[i] for i in kept_indices]}")
```

---

### Exercise 2: Transfer Learning Decision Tree (Medium)

```python
def recommend_cv_approach(
    dataset_size: int,
    num_classes: int,
    domain: str,  # "similar" or "different" to ImageNet
    latency_ms: int,  # Target inference latency
    device: str,  # "gpu", "cpu", "mobile"
) -> dict:
    """Return recommended architecture + training strategy."""
    
    # Architecture by latency/device
    if device == "mobile" or latency_ms < 10:
        arch = "MobileNetV3" if dataset_size > 1000 else "EfficientNet-B0"
    elif latency_ms < 100:
        arch = "ResNet-50" if num_classes < 100 else "EfficientNet-B4"
    else:
        arch = "EfficientNet-B7" if num_classes > 100 else "ViT-B/16"

    # Training strategy
    if dataset_size < 500:
        strategy = "linear_probe"
    elif dataset_size < 5000 and domain == "similar":
        strategy = "fine_tune_last_2_blocks"
    elif dataset_size < 50000:
        strategy = "full_fine_tune_low_lr"
    else:
        strategy = "train_from_scratch"

    return {
        "architecture": arch,
        "strategy": strategy,
        "pretrained": strategy != "train_from_scratch",
        "augmentation": "heavy" if dataset_size < 5000 else "standard",
        "suggested_lr": {"linear_probe": 0.01, "fine_tune_last_2_blocks": 0.0001,
                        "full_fine_tune_low_lr": 0.00005, "train_from_scratch": 0.001}[strategy],
    }


# Test cases
cases = [
    (200, 5, "similar", 50, "mobile"),
    (5000, 20, "different", 100, "gpu"),
    (500000, 1000, "similar", 200, "gpu"),
]
for args in cases:
    rec = recommend_cv_approach(*args)
    print(f"Dataset={args[0]}, classes={args[1]}: {rec['architecture']} + {rec['strategy']}")
