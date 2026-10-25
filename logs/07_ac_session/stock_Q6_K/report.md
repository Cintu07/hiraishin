```
date: 2026-10-25T05:00:29+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda
target: /home/pavan/models/Qwen3-8B-Q6_K.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=<unset>
args: -n 256 -k 2,4,8 --reps 1 --inv-b 2,5,9 --no-verify-cost
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 1755 MHz, 11151 MHz, 72, 10.94 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 49.49 | 20.04 | True |
| explain r1 | 256 | 49.02 | 20.38 | True |
| rewrite r1 | 210 | 49.10 | 20.29 | True |
| math r1 | 256 | 47.86 | 20.58 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2 | 0 | code | 76.59 | 1.55x | 73.3 | 1.45 | 2.45 | 32.01 | 26.5 | 72.4 | 1.1 | 0.0 | 0.0 | NO | tok 40 (0.1120) |
| 4 | 0 | code | 72.18 | 1.46x | 56.3 | 2.23 | 3.23 | 44.68 | 38.3 | 60.7 | 1.0 | 0.0 | 0.0 | NO | tok 90 (0.2815) |
| 8 | 0 | code | 72.05 | 1.46x | 40.7 | 3.21 | 4.21 | 58.47 | 53.1 | 45.8 | 1.1 | 0.0 | 0.0 | NO | tok 90 (0.2815) |
| 2 | 0 | explain | 65.47 | 1.34x | 58.3 | 1.16 | 2.16 | 33.01 | 26.5 | 72.4 | 1.0 | 0.0 | 0.0 | NO | tok 113 (0.0242) |
| 4 | 0 | explain | 56.82 | 1.16x | 41.1 | 1.63 | 2.63 | 46.27 | 40.9 | 58.2 | 0.8 | 0.0 | 0.0 | NO | tok 113 (0.0242) |
| 8 | 0 | explain | 50.50 | 1.03x | 24.4 | 1.91 | 2.91 | 57.63 | 54.4 | 44.9 | 0.7 | 0.0 | 0.0 | NO | tok 92 (0.0837) |
| 2 | 0 | rewrite | 84.64 | 1.72x | 97.9 | 1.94 | 2.94 | 34.78 | 26.5 | 72.2 | 1.3 | 0.0 | 0.0 | yes | - |
| 4 | 0 | rewrite | 98.39 | 2.00x | 94.3 | 3.77 | 4.77 | 48.28 | 41.9 | 56.6 | 1.5 | 0.0 | 0.0 | yes | - |
| 8 | 0 | rewrite | 132.64 | 2.70x | 91.0 | 7.04 | 8.04 | 60.60 | 53.0 | 45.1 | 1.8 | 0.0 | 0.0 | yes | - |
| 2 | 0 | math | 75.43 | 1.58x | 78.8 | 1.56 | 2.56 | 33.94 | 26.3 | 72.6 | 1.1 | 0.0 | 0.0 | NO | tok 133 (0.0301) |
| 4 | 0 | math | 81.58 | 1.70x | 70.1 | 2.79 | 3.79 | 46.51 | 40.6 | 58.2 | 1.2 | 0.0 | 0.0 | yes | - |
| 8 | 0 | math | 86.88 | 1.82x | 51.9 | 4.06 | 5.06 | 58.23 | 53.4 | 45.3 | 1.2 | 0.0 | 0.1 | NO | tok 133 (0.0301) |

## speculative per k (pooled over prompts)

| k | tau | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 0 | 75.53 | 74.6 | 1.48 | 2.48 | 8.82 | 24.11 | 0.38 | 1/4 |
| 4 | 0 | 77.24 | 60.3 | 2.39 | 3.39 | 18.61 | 27.07 | 0.51 | 2/4 |
| 8 | 0 | 85.52 | 42.5 | 3.33 | 4.33 | 31.29 | 26.40 | 0.64 | 1/4 |

## batch invariance: plain sequence re-fed in windows of B (teacher forcing)

| prompt | B | positions | argmax flips vs batch-1 | first flip at | max abs diff of top-1 logit | min plain margin at a flip |
|---|---:|---:|---:|---:|---:|---:|
| code | 2 | 255 | 1 | 90 | 1.144295 | 0.281471 |
| code | 5 | 255 | 1 | 90 | 1.025093 | 0.281471 |
| code | 9 | 255 | 1 | 90 | 1.450157 | 0.281471 |
| explain | 2 | 255 | 4 | 113 | 0.474533 | 0.011530 |
| explain | 5 | 255 | 4 | 113 | 0.696171 | 0.011530 |
| explain | 9 | 255 | 4 | 92 | 0.475407 | 0.008219 |
| rewrite | 2 | 209 | 0 | -1 | 3.699348 | -1.000000 |
| rewrite | 5 | 209 | 0 | -1 | 2.064003 | -1.000000 |
| rewrite | 9 | 209 | 0 | -1 | 3.533276 | -1.000000 |
| math | 2 | 255 | 1 | 133 | 0.600182 | 0.030142 |
| math | 5 | 255 | 0 | -1 | 0.966568 | -1.000000 |
| math | 9 | 255 | 1 | 133 | 1.119553 | 0.030142 |
