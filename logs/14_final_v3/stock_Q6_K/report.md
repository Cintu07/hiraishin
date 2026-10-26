```
date: 2026-10-26T11:27:09+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda
target: /home/pavan/models/Qwen3-8B-Q6_K.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=<unset>
args: -n 256 -k 8 --reps 1 --no-invariance --no-verify-cost
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 2212 MHz, 9001 MHz, 79, 11.37 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 44.30 | 20.54 | True |
| explain r1 | 256 | 47.35 | 20.57 | True |
| rewrite r1 | 210 | 47.28 | 20.77 | True |
| math r1 | 256 | 48.55 | 20.59 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 8 | 0 | code | 71.74 | 1.62x | 40.7 | 3.21 | 4.21 | 58.72 | 53.3 | 45.5 | 1.1 | 0.0 | 0.0 | NO | tok 90 (0.2815) |
| 8 | 0 | explain | 49.89 | 1.05x | 24.4 | 1.91 | 2.91 | 58.33 | 51.8 | 47.3 | 0.8 | 0.0 | 0.0 | NO | tok 92 (0.0837) |
| 8 | 0 | rewrite | 126.68 | 2.68x | 91.0 | 7.04 | 8.04 | 63.45 | 53.3 | 44.9 | 1.8 | 0.0 | 0.0 | yes | - |
| 8 | 0 | math | 87.28 | 1.80x | 51.9 | 4.06 | 5.06 | 57.96 | 54.0 | 44.8 | 1.2 | 0.0 | 0.0 | NO | tok 133 (0.0301) |

## speculative per k (pooled over prompts)

| k | tau | ngram | pad | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 8 | 0 | 0 | 0 | 83.90 | 42.5 | 3.33 | 4.33 | 31.17 | 27.10 | 0.68 | 1/4 |
