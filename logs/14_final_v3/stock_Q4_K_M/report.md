```
date: 2026-10-26T11:24:26+00:00
bin: /home/pavan/hiraishin-build/bin/spec_harness-build-cuda
target: /home/pavan/models/Qwen3-8B-Q4_K_M.gguf
draft: /home/pavan/models/Qwen3-0.6B-Q8_0.gguf
GGML_CUDA_BATCH_INVARIANT=<unset>
args: -n 256 -k 8 --reps 1 --no-invariance --no-verify-cost
NVIDIA GeForce RTX 5060 Laptop GPU, 610.74, 0 MHz, 11151 MHz, 62, 9.38 W
```

## plain greedy decode (batch 1)

| prompt | n | tok/s | median step ms | rep-to-rep identical |
|---|---:|---:|---:|---|
| code r1 | 256 | 63.00 | 15.68 | True |
| explain r1 | 256 | 63.26 | 15.82 | True |
| rewrite r1 | 210 | 62.37 | 16.01 | True |
| math r1 | 256 | 63.41 | 15.69 | True |

## speculative (chain, greedy) per prompt

| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 8 | 0 | code | 87.39 | 1.39x | 43.5 | 3.40 | 4.40 | 50.31 | 57.0 | 41.6 | 1.3 | 0.0 | 0.1 | NO | tok 10 (0.3053) |
| 8 | 0 | explain | 65.47 | 1.04x | 29.3 | 2.31 | 3.31 | 50.58 | 58.1 | 40.9 | 0.9 | 0.0 | 0.0 | NO | tok 113 (0.1183) |
| 8 | 0 | rewrite | 153.38 | 2.46x | 91.0 | 7.04 | 8.04 | 52.41 | 56.4 | 41.4 | 2.2 | 0.0 | 0.0 | yes | - |
| 8 | 0 | math | 99.81 | 1.57x | 52.8 | 4.16 | 5.16 | 51.70 | 58.1 | 40.3 | 1.6 | 0.0 | 0.1 | NO | tok 165 (0.0777) |

## speculative per k (pooled over prompts)

| k | tau | ngram | pad | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 8 | 0 | 0 | 0 | 101.51 | 46.3 | 3.63 | 4.63 | 29.37 | 20.91 | 0.72 | 1/4 |
