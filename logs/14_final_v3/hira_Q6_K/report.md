```
date: 2026-10-26T11:28:17+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda-hira
target: /home/pavan/models/Qwen3-8B-Q6_K.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=1
args: -n 256 -k 5 --tau 3 --ngram 0,3 --reps 2 --inv-b 2,5,9
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 0 MHz, 11151 MHz, 73, 11.70 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 49.15 | 20.34 | True |
| code r2 | 256 | 49.01 | 20.29 | True |
| explain r1 | 256 | 47.77 | 20.61 | True |
| explain r2 | 256 | 48.57 | 20.52 | True |
| rewrite r1 | 210 | 47.48 | 20.66 | True |
| rewrite r2 | 210 | 48.26 | 20.69 | True |
| math r1 | 256 | 47.92 | 20.56 | True |
| math r2 | 256 | 48.62 | 20.56 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 5 | 3 | code | 76.93 | 1.57x | 73.9 | 1.64 | 2.64 | 34.36 | 25.9 | 72.9 | 1.2 | 0.0 | 0.0 | yes | - |
| 5 | 3 | code | 80.61 | 1.64x | 73.9 | 1.64 | 2.64 | 32.79 | 27.0 | 71.8 | 1.2 | 0.0 | 0.0 | yes | - |
| 5 | 3 | code | 79.38 | 1.62x | 69.2 | 1.59 | 2.59 | 32.57 | 26.9 | 71.9 | 1.2 | 0.0 | 0.0 | yes | - |
| 5 | 3 | code | 79.30 | 1.61x | 69.2 | 1.59 | 2.59 | 32.61 | 26.0 | 72.8 | 1.2 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 66.44 | 1.39x | 61.7 | 0.90 | 1.90 | 28.64 | 21.5 | 77.4 | 1.1 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 66.88 | 1.40x | 61.7 | 0.90 | 1.90 | 28.45 | 21.4 | 77.5 | 1.0 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 67.34 | 1.41x | 58.6 | 0.92 | 1.92 | 28.48 | 20.8 | 78.2 | 1.0 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 67.52 | 1.41x | 58.6 | 0.92 | 1.92 | 28.41 | 20.6 | 78.4 | 1.0 | 0.0 | 0.0 | yes | - |
| 5 | 3 | rewrite | 105.09 | 2.21x | 97.1 | 4.00 | 5.00 | 47.35 | 39.1 | 59.2 | 1.6 | 0.0 | 0.0 | yes | - |
| 5 | 3 | rewrite | 103.99 | 2.19x | 97.1 | 4.00 | 5.00 | 47.85 | 38.7 | 59.8 | 1.5 | 0.0 | 0.0 | yes | - |
| 5 | 3 | rewrite | 134.60 | 2.83x | 89.9 | 4.22 | 5.22 | 38.82 | 17.9 | 80.1 | 2.0 | 0.0 | 0.0 | yes | - |
| 5 | 3 | rewrite | 135.36 | 2.85x | 89.9 | 4.22 | 5.22 | 38.60 | 16.9 | 81.1 | 2.0 | 0.0 | 0.0 | yes | - |
| 5 | 3 | math | 91.33 | 1.91x | 86.9 | 2.11 | 3.11 | 34.05 | 28.9 | 69.6 | 1.4 | 0.0 | 0.0 | yes | - |
| 5 | 3 | math | 90.50 | 1.89x | 86.9 | 2.11 | 3.11 | 34.36 | 29.5 | 69.1 | 1.4 | 0.0 | 0.0 | yes | - |
| 5 | 3 | math | 82.00 | 1.71x | 66.5 | 1.83 | 2.83 | 34.55 | 25.9 | 72.8 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | math | 81.58 | 1.70x | 66.5 | 1.83 | 2.83 | 34.73 | 25.8 | 72.9 | 1.3 | 0.0 | 0.0 | yes | - |

## speculative per k (pooled over prompts)

| k | tau | ngram | pad | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 5 | 3 | 0 | 0 | 85.22 | 79.3 | 1.75 | 2.75 | 9.23 | 23.82 | 0.43 | 8/8 |
| 5 | 3 | 3 | 0 | 90.89 | 70.3 | 1.69 | 2.69 | 7.48 | 24.35 | 0.41 | 8/8 |

## forward pass cost vs batch size (median of 15, all logits returned)

| model | B | ms (mean over prompts' depths) | x B=1 | ms per token |
|---|---:|---:|---:|---:|
| draft | 1 | 3.601 | 1.000 | 3.601 |
| target | 1 | 24.293 | 1.000 | 24.293 |
| target | 2 | 22.249 | 0.916 | 11.125 |
| target | 3 | 22.948 | 0.945 | 7.649 |
| target | 4 | 25.410 | 1.046 | 6.353 |
| target | 5 | 29.342 | 1.208 | 5.868 |
| target | 6 | 31.366 | 1.291 | 5.228 |
| target | 7 | 33.162 | 1.365 | 4.737 |
| target | 8 | 36.918 | 1.520 | 4.615 |
| target | 9 | 42.315 | 1.742 | 4.702 |
| target | 10 | 45.641 | 1.879 | 4.564 |
| target | 11 | 51.847 | 2.134 | 4.713 |
| target | 12 | 57.735 | 2.377 | 4.811 |

depths used: [174, 178, 205, 335]

## batch invariance: plain sequence re-fed in windows of B (teacher forcing)

| prompt | B | positions | argmax flips vs batch-1 | first flip at | max abs diff of top-1 logit | min plain margin at a flip |
|---|---:|---:|---:|---:|---:|---:|
| code | 2 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| code | 5 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| code | 9 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| explain | 2 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| explain | 5 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| explain | 9 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| rewrite | 2 | 209 | 0 | -1 | 0.000000 | -1.000000 |
| rewrite | 5 | 209 | 0 | -1 | 0.000000 | -1.000000 |
| rewrite | 9 | 209 | 0 | -1 | 0.000000 | -1.000000 |
| math | 2 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| math | 5 | 255 | 0 | -1 | 0.000000 | -1.000000 |
| math | 9 | 255 | 0 | -1 | 0.000000 | -1.000000 |
