```
date: 2026-10-25T04:52:06+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda
target: /home/pavan/models/Qwen3-8B-Q4_K_M.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=<unset>
args: -n 256 -k 2,4,8 --reps 1 --inv-b 2,5,9 --no-verify-cost
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 300 MHz, 11001 MHz, 57, 28.52 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 58.69 | 16.36 | True |
| explain r1 | 256 | 59.47 | 16.39 | True |
| rewrite r1 | 210 | 58.51 | 16.49 | True |
| math r1 | 256 | 58.76 | 16.58 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2 | 0 | code | 79.27 | 1.35x | 76.0 | 1.52 | 2.52 | 31.78 | 31.4 | 67.1 | 1.4 | 0.0 | 0.0 | NO | tok 55 (0.0298) |
| 4 | 0 | code | 70.72 | 1.21x | 60.6 | 2.40 | 3.40 | 48.07 | 42.5 | 56.4 | 1.1 | 0.0 | 0.0 | NO | tok 55 (0.0298) |
| 8 | 0 | code | 72.75 | 1.24x | 43.5 | 3.40 | 4.40 | 60.44 | 58.6 | 40.2 | 1.1 | 0.0 | 0.0 | NO | tok 10 (0.3053) |
| 2 | 0 | explain | 72.43 | 1.22x | 60.3 | 1.20 | 2.20 | 30.33 | 29.6 | 69.3 | 1.1 | 0.0 | 0.0 | yes | - |
| 4 | 0 | explain | 63.60 | 1.07x | 49.7 | 1.98 | 2.98 | 46.81 | 40.1 | 59.0 | 0.9 | 0.0 | 0.0 | NO | tok 20 (0.0666) |
| 8 | 0 | explain | 55.45 | 0.93x | 29.3 | 2.31 | 3.31 | 59.72 | 58.9 | 40.2 | 0.8 | 0.0 | 0.0 | NO | tok 113 (0.1183) |
| 2 | 0 | rewrite | 95.92 | 1.64x | 97.9 | 1.94 | 2.94 | 30.69 | 29.7 | 68.9 | 1.4 | 0.0 | 0.0 | yes | - |
| 4 | 0 | rewrite | 101.91 | 1.74x | 94.3 | 3.77 | 4.77 | 46.61 | 39.5 | 59.0 | 1.4 | 0.0 | 0.0 | yes | - |
| 8 | 0 | rewrite | 131.09 | 2.24x | 91.0 | 7.04 | 8.04 | 61.32 | 58.6 | 39.6 | 1.8 | 0.0 | 0.0 | yes | - |
| 2 | 0 | math | 83.29 | 1.42x | 81.1 | 1.62 | 2.62 | 31.49 | 31.0 | 67.8 | 1.2 | 0.0 | 0.0 | NO | tok 165 (0.0777) |
| 4 | 0 | math | 79.07 | 1.35x | 71.7 | 2.84 | 3.84 | 48.51 | 41.9 | 57.0 | 1.1 | 0.0 | 0.0 | NO | tok 165 (0.0777) |
| 8 | 0 | math | 84.92 | 1.45x | 52.8 | 4.16 | 5.16 | 60.77 | 59.2 | 39.5 | 1.2 | 0.0 | 0.0 | NO | tok 165 (0.0777) |

## speculative per k (pooled over prompts)

| k | tau | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 0 | 82.73 | 76.6 | 1.53 | 2.53 | 9.47 | 21.21 | 0.39 | 2/4 |
| 4 | 0 | 78.82 | 65.4 | 2.60 | 3.60 | 19.54 | 27.47 | 0.53 | 1/4 |
| 8 | 0 | 86.05 | 46.3 | 3.63 | 4.63 | 35.54 | 24.13 | 0.69 | 1/4 |

## batch invariance: plain sequence re-fed in windows of B (teacher forcing)

| prompt | B | positions | argmax flips vs batch-1 | first flip at | max abs diff of top-1 logit | min plain margin at a flip |
|---|---:|---:|---:|---:|---:|---:|
| code | 2 | 255 | 1 | 55 | 0.448364 | 0.029839 |
| code | 5 | 255 | 1 | 55 | 0.378098 | 0.029839 |
| code | 9 | 255 | 2 | 10 | 1.050774 | 0.141575 |
| explain | 2 | 255 | 1 | 236 | 0.391281 | 0.050945 |
| explain | 5 | 255 | 1 | 20 | 0.718029 | 0.066582 |
| explain | 9 | 255 | 3 | 113 | 1.008070 | 0.118273 |
| rewrite | 2 | 209 | 0 | -1 | 0.516552 | -1.000000 |
| rewrite | 5 | 209 | 0 | -1 | 0.371216 | -1.000000 |
| rewrite | 9 | 209 | 0 | -1 | 1.258034 | -1.000000 |
| math | 2 | 255 | 0 | -1 | 0.477039 | -1.000000 |
| math | 5 | 255 | 1 | 165 | 0.369595 | 0.077740 |
| math | 9 | 255 | 1 | 165 | 1.200932 | 0.077740 |
