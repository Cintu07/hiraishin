```
date: 2026-10-26T10:59:10+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda
target: /home/pavan/models/Qwen3-8B-Q6_K.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=<unset>
args: -n 256 -k 8 --reps 1 --no-invariance --no-verify-cost
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 2152 MHz, 9001 MHz, 78, 10.87 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 47.71 | 20.55 | True |
| explain r1 | 256 | 48.23 | 20.65 | True |
| rewrite r1 | 210 | 48.19 | 20.70 | True |
| math r1 | 256 | 48.34 | 20.62 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 8 | 0 | code | 70.27 | 1.47x | 40.7 | 3.21 | 4.21 | 59.96 | 53.4 | 45.5 | 1.0 | 0.0 | 0.1 | NO | tok 90 (0.2815) |
| 8 | 0 | explain | 50.38 | 1.04x | 24.4 | 1.91 | 2.91 | 57.77 | 53.8 | 45.4 | 0.7 | 0.0 | 0.0 | NO | tok 92 (0.0837) |
| 8 | 0 | rewrite | 134.14 | 2.78x | 91.0 | 7.04 | 8.04 | 59.93 | 53.6 | 44.5 | 1.9 | 0.0 | 0.0 | yes | - |
| 8 | 0 | math | 87.34 | 1.81x | 51.9 | 4.06 | 5.06 | 57.92 | 53.2 | 45.5 | 1.2 | 0.0 | 0.0 | NO | tok 133 (0.0301) |

## speculative per k (pooled over prompts)

| k | tau | ngram | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 8 | 0 | 0 | 85.53 | 42.5 | 3.33 | 4.33 | 31.40 | 26.58 | 0.66 | 1/4 |
