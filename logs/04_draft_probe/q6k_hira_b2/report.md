```
date: 2026-10-24T17:54:06+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda-hira
target: /home/pavan/models/Qwen3-8B-Q6_K.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=1
args: -n 256 -k 2,4,8 --no-invariance --no-verify-cost
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 0 MHz, 11001 MHz, 51, 9.46 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 43.87 | 21.58 | True |
| explain r1 | 256 | 41.85 | 24.31 | True |
| rewrite r1 | 210 | 43.17 | 21.94 | True |
| math r1 | 256 | 39.90 | 25.00 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2 | 0 | code | 68.27 | 1.56x | 71.6 | 1.42 | 2.42 | 35.51 | 25.5 | 73.4 | 1.1 | 0.0 | 0.0 | yes | - |
| 4 | 0 | code | 65.06 | 1.48x | 55.3 | 2.19 | 3.19 | 48.96 | 36.4 | 62.6 | 0.9 | 0.0 | 0.0 | yes | - |
| 8 | 0 | code | 40.78 | 0.93x | 38.2 | 3.02 | 4.02 | 98.48 | 35.0 | 64.4 | 0.6 | 0.0 | 0.0 | yes | - |
| 2 | 0 | explain | 58.01 | 1.39x | 52.6 | 1.04 | 2.04 | 35.16 | 25.5 | 73.6 | 0.8 | 0.0 | 0.0 | yes | - |
| 4 | 0 | explain | 48.27 | 1.15x | 34.3 | 1.35 | 2.35 | 48.59 | 35.8 | 63.4 | 0.7 | 0.0 | 0.0 | yes | - |
| 8 | 0 | explain | 26.51 | 0.63x | 20.9 | 1.62 | 2.62 | 98.92 | 36.2 | 63.4 | 0.4 | 0.0 | 0.0 | yes | - |
| 2 | 0 | rewrite | 77.52 | 1.80x | 97.9 | 1.94 | 2.94 | 37.97 | 27.4 | 71.4 | 1.1 | 0.0 | 0.0 | yes | - |
| 4 | 0 | rewrite | 89.08 | 2.06x | 94.3 | 3.77 | 4.77 | 53.32 | 40.0 | 58.6 | 1.3 | 0.0 | 0.0 | yes | - |
| 8 | 0 | rewrite | 75.69 | 1.75x | 91.0 | 7.04 | 8.04 | 106.20 | 37.3 | 61.5 | 1.2 | 0.0 | 0.0 | yes | - |
| 2 | 0 | math | 68.65 | 1.72x | 77.5 | 1.53 | 2.53 | 36.92 | 26.9 | 72.0 | 1.0 | 0.0 | 0.0 | yes | - |
| 4 | 0 | math | 76.70 | 1.92x | 71.5 | 2.85 | 3.85 | 50.21 | 36.5 | 62.3 | 1.1 | 0.0 | 0.0 | yes | - |
| 8 | 0 | math | 49.08 | 1.23x | 50.6 | 3.96 | 4.96 | 101.09 | 36.3 | 62.9 | 0.7 | 0.0 | 0.0 | yes | - |

## speculative per k (pooled over prompts)

| k | tau | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 0 | 68.11 | 71.8 | 1.42 | 2.42 | 9.49 | 26.32 | 0.37 | 4/4 |
| 4 | 0 | 69.78 | 57.1 | 2.26 | 3.26 | 18.30 | 30.94 | 0.50 | 4/4 |
| 8 | 0 | 48.01 | 39.6 | 3.09 | 4.09 | 36.05 | 63.38 | 0.64 | 4/4 |
