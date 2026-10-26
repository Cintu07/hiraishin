```
date: 2026-10-26T10:54:42+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda
target: /home/pavan/models/Qwen3-8B-Q4_K_M.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=<unset>
args: -n 256 -k 8 --reps 1 --no-invariance --no-verify-cost
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 0 MHz, 11151 MHz, 56, 8.71 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 60.69 | 15.99 | True |
| explain r1 | 256 | 61.37 | 15.98 | True |
| rewrite r1 | 210 | 61.93 | 16.14 | True |
| math r1 | 256 | 62.42 | 15.93 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 8 | 0 | code | 82.23 | 1.36x | 43.5 | 3.40 | 4.40 | 53.46 | 56.4 | 42.2 | 1.2 | 0.0 | 0.1 | NO | tok 10 (0.3053) |
| 8 | 0 | explain | 61.87 | 1.01x | 29.3 | 2.31 | 3.31 | 53.53 | 59.5 | 39.5 | 0.9 | 0.0 | 0.1 | NO | tok 113 (0.1183) |
| 8 | 0 | rewrite | 145.40 | 2.35x | 91.0 | 7.04 | 8.04 | 55.29 | 57.4 | 40.7 | 1.9 | 0.0 | 0.1 | yes | - |
| 8 | 0 | math | 95.08 | 1.52x | 52.8 | 4.16 | 5.16 | 54.27 | 59.5 | 39.2 | 1.3 | 0.0 | 0.1 | NO | tok 165 (0.0777) |

## speculative per k (pooled over prompts)

| k | tau | ngram | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 8 | 0 | 0 | 96.14 | 46.3 | 3.63 | 4.63 | 31.47 | 21.74 | 0.70 | 1/4 |
