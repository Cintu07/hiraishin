```
date: 2026-10-26T11:25:08+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda-hira
target: /home/pavan/models/Qwen3-8B-Q4_K_M.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=1
args: -n 256 -k 5 --tau 3 --ngram 0,3 --reps 2 --inv-b 2,5,9
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 2662 MHz, 11151 MHz, 73, 10.83 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 65.32 | 15.24 | True |
| code r2 | 256 | 63.08 | 15.83 | True |
| explain r1 | 256 | 61.95 | 16.00 | True |
| explain r2 | 256 | 62.77 | 15.93 | True |
| rewrite r1 | 210 | 61.02 | 16.03 | True |
| rewrite r2 | 210 | 62.69 | 15.88 | True |
| math r1 | 256 | 61.95 | 15.86 | True |
| math r2 | 256 | 63.48 | 15.62 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 5 | 3 | code | 92.13 | 1.41x | 74.9 | 1.69 | 2.69 | 29.25 | 32.7 | 65.9 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | code | 94.45 | 1.45x | 74.9 | 1.69 | 2.69 | 28.53 | 32.6 | 65.8 | 1.6 | 0.0 | 0.0 | yes | - |
| 5 | 3 | code | 92.65 | 1.42x | 71.0 | 1.64 | 2.64 | 28.48 | 32.5 | 66.1 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | code | 92.29 | 1.41x | 71.0 | 1.64 | 2.64 | 28.60 | 32.5 | 66.1 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 88.96 | 1.44x | 73.8 | 1.21 | 2.21 | 24.79 | 27.7 | 70.9 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 88.70 | 1.43x | 73.8 | 1.21 | 2.21 | 24.86 | 27.1 | 71.5 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 88.05 | 1.42x | 67.8 | 1.21 | 2.21 | 25.04 | 26.4 | 72.3 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | explain | 89.01 | 1.44x | 67.8 | 1.21 | 2.21 | 24.77 | 25.8 | 72.8 | 1.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | rewrite | 123.09 | 2.02x | 97.1 | 4.00 | 5.00 | 40.43 | 42.5 | 55.6 | 1.8 | 0.0 | 0.1 | yes | - |
| 5 | 3 | rewrite | 118.53 | 1.94x | 97.1 | 4.00 | 5.00 | 41.98 | 42.3 | 55.9 | 1.8 | 0.0 | 0.1 | yes | - |
| 5 | 3 | rewrite | 158.06 | 2.59x | 89.9 | 4.22 | 5.22 | 33.06 | 18.8 | 78.4 | 2.8 | 0.0 | 0.0 | yes | - |
| 5 | 3 | rewrite | 159.15 | 2.61x | 89.9 | 4.22 | 5.22 | 32.83 | 18.3 | 79.4 | 2.3 | 0.0 | 0.0 | yes | - |
| 5 | 3 | math | 108.89 | 1.76x | 88.0 | 2.20 | 3.20 | 29.39 | 32.5 | 65.8 | 1.6 | 0.0 | 0.1 | yes | - |
| 5 | 3 | math | 106.50 | 1.72x | 88.0 | 2.20 | 3.20 | 30.05 | 33.0 | 65.4 | 1.6 | 0.0 | 0.0 | yes | - |
| 5 | 3 | math | 101.38 | 1.64x | 70.8 | 1.98 | 2.98 | 29.36 | 30.5 | 68.0 | 1.5 | 0.0 | 0.0 | yes | - |
| 5 | 3 | math | 101.73 | 1.64x | 70.8 | 1.98 | 2.98 | 29.26 | 30.1 | 68.4 | 1.4 | 0.0 | 0.0 | yes | - |

## speculative per k (pooled over prompts)

| k | tau | ngram | pad | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 5 | 3 | 0 | 0 | 102.66 | 82.9 | 1.93 | 2.93 | 9.60 | 19.16 | 0.45 | 8/8 |
| 5 | 3 | 3 | 0 | 110.29 | 74.3 | 1.88 | 2.88 | 7.85 | 19.72 | 0.44 | 8/8 |

## forward pass cost vs batch size (median of 15, all logits returned)

| model | B | ms (mean over prompts' depths) | x B=1 | ms per token |
|---|---:|---:|---:|---:|
| draft | 1 | 3.579 | 1.000 | 3.579 |
| target | 1 | 18.719 | 1.000 | 18.719 |
| target | 2 | 17.295 | 0.924 | 8.647 |
| target | 3 | 17.747 | 0.948 | 5.916 |
| target | 4 | 19.274 | 1.030 | 4.819 |
| target | 5 | 23.083 | 1.233 | 4.617 |
| target | 6 | 26.147 | 1.397 | 4.358 |
| target | 7 | 29.367 | 1.569 | 4.195 |
| target | 8 | 32.671 | 1.745 | 4.084 |
| target | 9 | 36.913 | 1.972 | 4.101 |
| target | 10 | 40.348 | 2.155 | 4.035 |
| target | 11 | 45.296 | 2.420 | 4.118 |
| target | 12 | 49.888 | 2.665 | 4.157 |

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
