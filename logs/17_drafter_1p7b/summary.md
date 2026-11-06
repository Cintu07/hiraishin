# Qwen3-1.7B Q4_K_M as drafter (2026-11-06, AC power)

Target Qwen3-8B Q4_K_M, patched build, `GGML_CUDA_BATCH_INVARIANT=1`, 4-prompt set, 256 tokens, n-gram off.
Drafter fetched with `scripts/get_drafter_1p7b.sh` (sha256 checked). It fits in 8 GB next to the target at ctx 4096.

## smoke (`scripts/run_drafter_cmp.sh smoke`), both at k=5 tau=3

| drafter | mean tok/s | tokens per pass | drafted per cycle | draft ms per drafted token | draft ms/cycle | verify ms/cycle | exact |
|---|---:|---:|---:|---:|---:|---:|---|
| 0.6B Q8_0 | 91.9 | 2.93 | 2.33 | 4.57 | 10.65 | 21.29 | 4/4 |
| 1.7B Q4_K_M | 81.7 | 3.60 | 3.11 | 6.34 | 19.75 | 24.56 | 4/4 |

The 1.7B is right more often (+23% tokens per pass) but drafts more per cycle and each guess costs 39% more, so
drafting time per cycle nearly doubles and the cycle gets 38% longer.

## sweep (`sweep_1p7b/`), 1.7B only, k in 3,5,8 x tau in 3,5,8

74.7 to 79.4 tok/s, best k=8 tau=8. Plain decode measured 51.9 tok/s in this run (about 59 in the smoke run), so
absolute numbers drifted; only the ordering within the sweep is used.

## interleaved A/B (`scripts/run_drafter_ab.sh`, `ab/`), each at its best setting, alternated twice

| round | 0.6B k=5 tau=3 | 1.7B k=8 tau=8 |
|---|---:|---:|
| 1 | 93.6 (plain 59.3) | 84.0 (plain 57.7) |
| 2 | 92.0 (plain 51.1) | 80.5 (plain 52.9) |

The 0.6B is faster on every prompt in both rounds; 16/16 runs exact. The 45-prompt eval was not run for the 1.7B:
a 10%+ loss on all four prompts in both rounds is not going to reverse.

Conclusion: on this laptop a bigger drafter loses, because drafting is bandwidth-bound like the target. More accepted
tokens have to come from a drafter that is as cheap as the 0.6B (or cheaper), not from a bigger one.

Plain decode varied from 51.1 to 59.3 tok/s within one hour on AC with no change in settings. Unexplained.
