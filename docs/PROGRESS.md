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

## Not finished

- Final lossless run (`scripts/run_final.sh`) was stopped partway: `logs/06_final/q4km_q8draft/results.jsonl` holds 169 lines (all prompts up to k=6). Q6_K final not run.
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
