# hiraishin progress

Goal: 100+ tok/s greedy decode for Qwen3-8B on an RTX 5060 Laptop (8 GB), lossless (token-for-token equal to plain decoding), via speculative decoding.

## State at stop (2026-10-25)

Environment: all current numbers come from WSL (CUDA 13.4, gcc 15.3), PrismML llama.cpp fork at `e8fd209`, built in `~/hiraishin-build/llama.cpp`:
- `build-cuda`: stock fork.
- `build-cuda-hira`: branch `hiraishin` = `e8fd209` + `patches/0001..0004` (checked: the patch series applied to pristine `e8fd209` gives an identical `ggml-cuda` tree).
- Models copied to `~/models` (Q6_K, Q4_K_M with sha256 `d98cdcbd…5785` matching the official file, 0.6B Q8_0 and PQ2_0 drafts).

WSL decodes faster than the Windows prebuilt: Q6_K tg128 44.4 tok/s (276 GB/s effective) vs 37.4 tok/s on Windows (`logs/01_plain/`).

## Verified findings (each from a saved log)

| finding | evidence |
|---|---|
| Stock llama.cpp speculative is not lossless here: 8/24 Q6_K runs and 8/24 Q4_K_M runs match plain greedy | `logs/03_harness/q6k_stock/report.md`, `q4km_stock/report.md` |
| Cause 1: mmvq K-split (nwarps) changes with column count, and Q6_K/Q4_K switch to MMQ at 6-8 columns | code reading of `mmvq.cu` plus invariance test (flips at B=5, 9 under fork BI mode) |
| Cause 2: flash-attention kernel choice (vec vs others) for B > 1 | B=2/3 flips in stock, bit-exact once forced to vec (`q6k_forkbi`) |
| Cause 3: `n_kv = pad(pos+1, 256)`, so a verify batch crossing a multiple of 256 sees a different KV length | harness KV_PAD guard |
| Cause 4: vec FA `parallel_blocks` comes from kernel occupancy, which differs between 1- and 2-query kernels (only matters past KV position 384) | `logs/03_harness/debug_rewrite`, fixed by patch 0003 |
| With patches 0001-0004 + `GGML_CUDA_BATCH_INVARIANT=1` + KV_PAD guard: 24/24 runs lossless on both models, teacher-forced logits bit-identical for B = 2..16 | `logs/03_harness/q6k_hira`, `q4km_hira`, `logs/05_bi_kernel/v3_*` |
| Fixed 2-token draft calls (avoid graph rebuild on shape change): k=2 60.2 -> 68.1, k=4 64.7 -> 69.8 tok/s (Q6_K) | `logs/04_draft_probe/` |
| BI Q4_K/Q6_K kernel (patch 0004, 4 rows/block) vs generic BI path, verify cost x B=1: Q4_K_M B5 1.74 -> 1.41, B8 2.66 -> 2.03; Q6_K B5 1.39 -> 1.30, B8 2.05 -> 1.77; still bit-exact | `logs/05_bi_kernel/v3_*` |

## Final lossless run (2026-10-25, on battery, see logs/06_final/summary.md)

- 104/104 speculative runs token-identical to plain decode on both models; 0 argmax flips, max |dlogit| 0.000000.
- Q4_K_M best single setting k=2 tau=0: 81.8 tok/s = 1.65x plain (49.7 tok/s on battery).
- Q6_K best single setting k=5 tau=1: 61.6 tok/s = 1.72x plain (35.8 tok/s on battery).
- Adaptive tau rescues large k (Q4_K_M k=8: 64.6 -> 79.6 tok/s at tau=2-3) but does not beat k=2 on Q4_K_M.
- To do: rerun on AC power (plain + stock spec + final in one session) for absolute numbers.

## Same-session run on AC power (2026-10-25, logs/07_ac_session/summary.md)

Plain, stock speculative (unpatched, lossy) and hiraishin lossless measured back to back, same conditions
(GPU power limit 61.7 W at start, 93.5 W at end, no thermal slowdown at 81 C mid-run).

| target | plain | best stock spec (lossy) | best hiraishin lossless | lossless runs |
|---|---:|---:|---:|---|
| Q4_K_M | 58.4 tok/s | 86.1 (k=8), 1-2/4 runs exact | 91.8 (k=8, tau=3), 1.57x | 104/104 |
| Q6_K | 48.1 tok/s | 85.5 (k=8), 1-2/4 runs exact | 83.7 (k=8, tau=3), 1.74x | 104/104 |

Q4_K_M k=8 tau=3 per prompt: code 78.7, explain 80.5, rewrite 107.2, math 100.9 tok/s. 100+ on 2 of 4 prompts, not on the mean.

## Drafter experiments (2026-10-26, AC power)

- PQ2_0 0.6B as drafter: 0.0% acceptance. The model itself is broken (generates garbage alone on both builds;
  old CIOT-V2 perplexity log reads PPL 34,558,588). Dead end. `logs/08_drafter/`
- n-gram (prompt lookup) drafting before the model draft, `--ngram N`: same-session Q4_K_M, k=6 tau=3, 2 reps,
  8/8 lossless: model-only 98.9 tok/s mean, + n-gram(3) 104.9-105.1 tok/s mean (plain 62.9-63.3 this session).
  Per prompt: rewrite 119 -> 153, code 89 -> 88, explain 87 -> 86, math 101 -> 93. Mean > 100, median ~90.
  Match length 3/4/5 and a 4-cycle cooldown after a rejected n-gram draft change little. `logs/09_ngram/`

## Not finished

- Not yet tried: PQ2_0 0.6B drafter, n-gram drafting, the kernel past 4 rows/block, tuning tau.
- Nsight Compute needs "allow GPU performance counters for all users" in the NVIDIA Control Panel (admin); not changed.

## Resume

```bash
# inside WSL
cd /mnt/c/Users/pavan/hiraishin
bash scripts/run_final.sh q4km_q8draft ~/models/Qwen3-8B-Q4_K_M.gguf   # ~8 min, GPU full
bash scripts/run_final.sh q6k_q8draft  ~/models/Qwen3-8B-Q6_K.gguf
python3 -I scripts/analyze_harness.py logs/06_final/q4km_q8draft > logs/06_final/q4km_q8draft/report.md
```
Proof of success: each `report.md` "runs matching plain" column reads n/n, and the invariance table shows 0 flips and max|dlogit| 0.000000.
