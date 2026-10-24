```
date: 2026-10-24T17:13:32+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda
target: /home/pavan/models/Qwen3-8B-Q6_K.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=<unset>
args: -n 256 -k 2,4,8 --reps 2
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 0 MHz, 11001 MHz, 57, 9.73 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 46.06 | 21.28 | True |
| code r2 | 256 | 46.09 | 21.25 | True |
| explain r1 | 256 | 40.52 | 24.45 | True |
| explain r2 | 256 | 41.16 | 24.18 | True |
| rewrite r1 | 210 | 40.16 | 24.82 | True |
| rewrite r2 | 210 | 40.05 | 24.89 | True |
| math r1 | 256 | 40.30 | 24.67 | True |
| math r2 | 256 | 40.29 | 24.72 | True |

## speculative (chain, greedy) per prompt

| k | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2 | code | 60.99 | 1.32x | 71.4 | 1.43 | 2.43 | 39.82 | 35.9 | 63.2 | 0.9 | 0.0 | 0.0 | NO | tok 40 (0.1120) |
| 2 | code | 61.94 | 1.34x | 71.4 | 1.43 | 2.43 | 39.21 | 34.6 | 64.4 | 0.9 | 0.0 | 0.0 | NO | tok 40 (0.1120) |
| 4 | code | 63.88 | 1.39x | 54.6 | 2.19 | 3.19 | 49.86 | 42.3 | 56.7 | 0.9 | 0.0 | 0.0 | NO | tok 90 (0.2815) |
| 4 | code | 65.29 | 1.42x | 54.6 | 2.19 | 3.19 | 48.79 | 41.2 | 57.9 | 0.9 | 0.0 | 0.0 | NO | tok 90 (0.2815) |
| 8 | code | 69.32 | 1.50x | 41.9 | 3.36 | 4.36 | 62.84 | 51.3 | 47.7 | 1.0 | 0.0 | 0.0 | NO | tok 90 (0.2815) |
| 8 | code | 68.75 | 1.49x | 41.9 | 3.36 | 4.36 | 63.36 | 52.2 | 46.8 | 1.0 | 0.0 | 0.0 | NO | tok 90 (0.2815) |
| 2 | explain | 55.95 | 1.38x | 58.1 | 1.16 | 2.16 | 38.62 | 33.1 | 66.1 | 0.8 | 0.0 | 0.0 | NO | tok 113 (0.0242) |
| 2 | explain | 56.19 | 1.39x | 58.1 | 1.16 | 2.16 | 38.46 | 33.5 | 65.7 | 0.8 | 0.0 | 0.0 | NO | tok 113 (0.0242) |
| 4 | explain | 55.18 | 1.36x | 40.7 | 1.63 | 2.63 | 47.64 | 38.6 | 60.6 | 0.8 | 0.0 | 0.0 | NO | tok 113 (0.0242) |
| 4 | explain | 54.99 | 1.36x | 40.7 | 1.63 | 2.63 | 47.81 | 38.4 | 60.7 | 0.8 | 0.0 | 0.0 | NO | tok 113 (0.0242) |
| 8 | explain | 47.38 | 1.17x | 26.0 | 2.08 | 3.08 | 65.08 | 53.0 | 46.3 | 0.7 | 0.0 | 0.0 | NO | tok 92 (0.0837) |
| 8 | explain | 46.48 | 1.15x | 26.0 | 2.08 | 3.08 | 66.33 | 54.5 | 44.8 | 0.7 | 0.0 | 0.0 | NO | tok 92 (0.0837) |
| 2 | rewrite | 69.08 | 1.72x | 97.2 | 1.94 | 2.94 | 42.61 | 38.5 | 60.5 | 1.0 | 0.0 | 0.0 | yes | - |
| 2 | rewrite | 67.72 | 1.69x | 97.2 | 1.94 | 2.94 | 43.47 | 39.6 | 59.4 | 1.0 | 0.0 | 0.0 | yes | - |
| 4 | rewrite | 85.46 | 2.13x | 94.3 | 3.77 | 4.77 | 55.58 | 47.8 | 50.9 | 1.3 | 0.0 | 0.0 | yes | - |
| 4 | rewrite | 84.11 | 2.09x | 94.3 | 3.77 | 4.77 | 56.47 | 48.8 | 50.0 | 1.2 | 0.0 | 0.0 | yes | - |
| 8 | rewrite | 111.85 | 2.79x | 92.0 | 7.36 | 8.36 | 74.74 | 57.4 | 41.0 | 1.6 | 0.0 | 0.0 | yes | - |
| 8 | rewrite | 113.48 | 2.83x | 92.0 | 7.36 | 8.36 | 73.67 | 57.0 | 41.4 | 1.6 | 0.0 | 0.0 | yes | - |
| 2 | math | 62.23 | 1.54x | 79.3 | 1.59 | 2.59 | 41.55 | 37.3 | 61.7 | 1.0 | 0.0 | 0.0 | NO | tok 133 (0.0301) |
| 2 | math | 62.71 | 1.56x | 79.3 | 1.59 | 2.59 | 41.24 | 37.4 | 61.7 | 1.0 | 0.0 | 0.0 | NO | tok 133 (0.0301) |
| 4 | math | 72.69 | 1.80x | 72.7 | 2.91 | 3.91 | 53.78 | 41.5 | 57.3 | 1.1 | 0.0 | 0.0 | yes | - |
| 4 | math | 72.91 | 1.81x | 72.7 | 2.91 | 3.91 | 53.62 | 42.2 | 56.7 | 1.1 | 0.0 | 0.0 | yes | - |
| 8 | math | 82.42 | 2.05x | 53.3 | 4.27 | 5.27 | 63.88 | 53.3 | 45.6 | 1.2 | 0.0 | 0.0 | NO | tok 133 (0.0301) |
| 8 | math | 81.65 | 2.03x | 53.3 | 4.27 | 5.27 | 64.49 | 52.5 | 46.3 | 1.2 | 0.0 | 0.0 | NO | tok 133 (0.0301) |

## speculative per k (pooled over prompts)

| k | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 62.10 | 74.0 | 1.48 | 2.48 | 14.50 | 25.46 | 0.38 | 2/8 |
| 4 | 69.31 | 60.2 | 2.41 | 3.41 | 21.27 | 29.03 | 0.51 | 4/8 |
| 8 | 77.67 | 44.1 | 3.53 | 4.53 | 35.09 | 29.87 | 0.67 | 2/8 |

## forward pass cost vs batch size (median of 15, all logits returned)

| model | B | ms (mean over prompts' depths) | x B=1 | ms per token |
|---|---:|---:|---:|---:|
| draft | 1 | 3.522 | 1.000 | 3.522 |
| target | 1 | 24.278 | 1.000 | 24.278 |
| target | 2 | 25.203 | 1.038 | 12.601 |
| target | 3 | 26.542 | 1.093 | 8.847 |
| target | 4 | 29.947 | 1.234 | 7.487 |
| target | 5 | 32.633 | 1.344 | 6.527 |
| target | 6 | 37.156 | 1.530 | 6.193 |
| target | 7 | 41.021 | 1.690 | 5.860 |
| target | 8 | 28.849 | 1.188 | 3.606 |
| target | 9 | 31.055 | 1.279 | 3.451 |

depths used: [174, 178, 205, 335]

## batch invariance: plain sequence re-fed in windows of B (teacher forcing)

| prompt | B | positions | argmax flips vs batch-1 | first flip at | max abs diff of top-1 logit | min plain margin at a flip |
|---|---:|---:|---:|---:|---:|---:|
| code | 2 | 255 | 1 | 90 | 1.144295 | 0.281471 |
| code | 3 | 255 | 2 | 40 | 0.828648 | 0.112011 |
| code | 5 | 255 | 1 | 90 | 1.025093 | 0.281471 |
| code | 9 | 255 | 1 | 90 | 1.450157 | 0.281471 |
| explain | 2 | 255 | 4 | 113 | 0.474533 | 0.011530 |
| explain | 3 | 255 | 4 | 113 | 0.433014 | 0.011530 |
| explain | 5 | 255 | 4 | 113 | 0.696171 | 0.011530 |
| explain | 9 | 255 | 4 | 92 | 0.475407 | 0.008219 |
| rewrite | 2 | 209 | 0 | -1 | 3.699348 | -1.000000 |
| rewrite | 3 | 209 | 0 | -1 | 0.660538 | -1.000000 |
| rewrite | 5 | 209 | 0 | -1 | 2.265839 | -1.000000 |
| rewrite | 9 | 209 | 0 | -1 | 0.693581 | -1.000000 |
| math | 2 | 255 | 1 | 133 | 0.834389 | 0.030142 |
| math | 3 | 255 | 1 | 133 | 0.972099 | 0.030142 |
| math | 5 | 255 | 0 | -1 | 0.710892 | -1.000000 |
| math | 9 | 255 | 1 | 133 | 1.283920 | 0.030142 |

## cross-check: harness plain text vs stock llama-completion (Windows prebuilt)

- code: identical
- explain: identical
- rewrite: identical
- math: identical
