```
date: 2026-10-24T17:55:39+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda-hira
target: /home/pavan/models/Qwen3-8B-Q6_K.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=1
args: -n 256 -k 2,4,8 --no-invariance --no-verify-cost --no-draft-b2
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 0 MHz, 11001 MHz, 67, 10.88 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 43.76 | 22.04 | True |
| explain r1 | 256 | 40.08 | 24.93 | True |
| rewrite r1 | 210 | 39.92 | 25.03 | True |
| math r1 | 256 | 40.10 | 24.89 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2 | 0 | code | 58.96 | 1.35x | 72.7 | 1.45 | 2.45 | 41.51 | 35.5 | 63.5 | 0.9 | 0.0 | 0.0 | yes | - |
| 4 | 0 | code | 59.28 | 1.35x | 56.3 | 2.23 | 3.23 | 54.40 | 42.4 | 56.7 | 0.9 | 0.0 | 0.0 | yes | - |
| 8 | 0 | code | 40.69 | 0.93x | 39.9 | 3.15 | 4.15 | 101.87 | 36.6 | 62.8 | 0.6 | 0.0 | 0.0 | yes | - |
| 2 | 0 | explain | 51.85 | 1.29x | 52.6 | 1.04 | 2.04 | 39.34 | 32.3 | 66.8 | 0.8 | 0.0 | 0.0 | yes | - |
| 4 | 0 | explain | 45.35 | 1.13x | 34.9 | 1.37 | 2.37 | 52.19 | 38.1 | 61.2 | 0.7 | 0.0 | 0.0 | yes | - |
| 8 | 0 | explain | 26.80 | 0.67x | 21.3 | 1.65 | 2.65 | 98.86 | 35.5 | 64.1 | 0.4 | 0.0 | 0.0 | yes | - |
| 2 | 0 | rewrite | 68.41 | 1.71x | 97.9 | 1.94 | 2.94 | 43.03 | 37.9 | 61.0 | 1.0 | 0.0 | 0.0 | yes | - |
| 4 | 0 | rewrite | 83.08 | 2.08x | 94.3 | 3.77 | 4.77 | 57.17 | 45.3 | 53.4 | 1.2 | 0.0 | 0.0 | yes | - |
| 8 | 0 | rewrite | 76.15 | 1.91x | 91.0 | 7.04 | 8.04 | 105.56 | 38.4 | 60.5 | 1.0 | 0.0 | 0.0 | yes | - |
| 2 | 0 | math | 61.40 | 1.53x | 77.5 | 1.53 | 2.53 | 41.28 | 36.5 | 62.7 | 0.9 | 0.0 | 0.0 | yes | - |
| 4 | 0 | math | 71.25 | 1.78x | 71.5 | 2.85 | 3.85 | 54.04 | 42.8 | 56.1 | 1.0 | 0.0 | 0.0 | yes | - |
| 8 | 0 | math | 48.98 | 1.22x | 50.6 | 3.96 | 4.96 | 101.29 | 36.4 | 62.9 | 0.7 | 0.0 | 0.0 | yes | - |

## speculative per k (pooled over prompts)

| k | tau | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 0 | 60.16 | 72.1 | 1.43 | 2.43 | 14.47 | 26.20 | 0.38 | 4/4 |
| 4 | 0 | 64.74 | 57.7 | 2.28 | 3.28 | 22.34 | 31.09 | 0.49 | 4/4 |
| 8 | 0 | 48.16 | 40.2 | 3.14 | 4.14 | 36.67 | 63.64 | 0.61 | 4/4 |
