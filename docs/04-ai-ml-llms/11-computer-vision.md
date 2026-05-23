# Computer Vision — Image Recognition, Detection, Segmentation

Essential CV concepts for ML interviews.

---

## 📸 Image Classification

Predict category of image: cat, dog, car, etc.

### Architecture Evolution

**AlexNet (2012):** Breakthrough CNN
- 8 layers, 60M parameters
- Showed deep learning works

**VGG (2014):** Simple, deep architecture
- 16-19 layers
- Small 3×3 filters stacked

**ResNet (2015):** Residual connections
- 152+ layers without gradient vanishing
- Skip connections: x + f(x)

**Inception (2014):** Multi-scale processing
- Parallel conv branches
- Different kernel sizes

**EfficientNet (2019):** Optimal scaling
- Balance depth, width, resolution
- SOTA efficiency

### Training

```
Dataset: ImageNet (1.2M images, 1000 classes)

Transfer learning (preferred):
1. Pre-train on ImageNet
2. Fine-tune last layers
3. Much faster, better

From scratch: Requires large data
```

---

## 🔍 Object Detection

Locate and classify objects in image.

### Approaches

**YOLO:** Fast, one-stage detector
- Divide image into grid
- Predict bounding boxes per cell
- ~60 FPS

**Faster R-CNN:** Accurate, two-stage
- Region proposal network (RPN)
- Classify proposals
- Slower but more accurate

**SSD, RetinaNet, EfficientDet:** Other options

### Metrics

```
IoU (Intersection over Union):
Measures overlap of predicted vs. ground truth box
IoU = |Pred ∩ Truth| / |Pred ∪ Truth|

Typically need IoU > 0.5 to count as correct
```

---

## 🎨 Semantic Segmentation

Classify each pixel.

### Architecture

```
Encoder-Decoder:
- Encoder: Downsample (extract features)
- Decoder: Upsample (restore resolution)
- Output: Class per pixel
```

### U-Net

Popular for medical imaging:
```
Encoder → bottleneck → Decoder
with skip connections (concatenate encoder outputs)
```

---

## 🌍 Advanced Topics

**Instance Segmentation:** Separate instances
**Panoptic Segmentation:** Combine semantic + instance
**3D Vision:** Point clouds, volumetric data
**Video:** Temporal + spatial understanding

---

## ❓ Interview Q&A

**Q: Why transfer learning for CV?**
A: ImageNet pre-training learns useful features (edges, textures, shapes). Fine-tuning much faster than training from scratch.

**Q: YOLO vs. Faster R-CNN trade-offs?**
A: YOLO: Fast (~60 FPS), lower accuracy. Faster R-CNN: Slower, more accurate. Choose based on latency/accuracy needs.

**Q: Why use skip connections in U-Net?**
A: Preserves spatial information from encoder. Helps decoder reconstruct fine details.

---

**Last updated:** 2026-05-22
