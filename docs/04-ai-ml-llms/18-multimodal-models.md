# Multimodal Models — Vision + Language + Audio

Building systems that combine multiple data types.

---

## 🖼️ Vision-Language Models

### Architecture

```
Image encoder (CNN/ViT) → Feature vectors
Text encoder (BERT/GPT) → Feature vectors
Fusion/alignment layer
Shared representation space
```

### Key Models

**CLIP:** Image-text pairs, contrastive learning
- Match images to text descriptions
- Zero-shot: Classify image without training

**VisualBERT, VilBERT:** Joint image-text understanding
**BLIP:** Bootstrapped Language-Image Pre-training
**LLaVA:** LLM + vision encoder

### Training

```
Contrastive learning: Match correct image-text pairs
Alignment: Image embedding near text embedding
Large-scale data: LAION (400M+ image-text pairs)
```

---

## 🎵 Audio-Language Models

### Applications

**Speech recognition:** Audio → text
**Text-to-speech:** Text → audio
**Audio tagging:** Audio → labels
**Music generation:** Conditional music synthesis

### Techniques

**Spectrograms:** Convert audio to frequency-time
**WaveNet:** Autoregressive audio generation
**Transformers:** Attention over audio

---

## 🔄 Multimodal Fusion

### Early Fusion
```
Combine raw inputs immediately
Fast, less compute
Misses modality-specific patterns
```

### Late Fusion
```
Process each modality separately
Combine representations late
Better modality-specific learning
More compute
```

### Hybrid Fusion
```
Process separately, fuse multiple levels
Balance between both
```

---

## 💡 Challenges

**Modality gaps:** Different distributions
**Imbalanced data:** Text more abundant than audio
**Computational cost:** Multiple encoders
**Alignment:** Synchronize modalities

---

## ❓ Interview Q&A

**Q: How does CLIP enable zero-shot classification?**
A: Trained on image-text pairs. At test time, encode image and class labels, compute similarity. No fine-tuning needed.

**Q: Why separate encoders vs. single encoder?**
A: Separate: Leverage modality-specific architectures (CNN for images). Single: Simpler but less effective. Separate usually better.

**Q: How to handle missing modalities?**
A: Cross-modal retrieval: Use one modality to retrieve other. Attention gates: Learn to ignore missing. Pre-training: Robustness.

---

**Last updated:** 2026-05-22
