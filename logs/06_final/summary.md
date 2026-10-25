
## Qwen3-8B Q4_K_M

plain greedy decode (patched build, batch 1): 49.7 tok/s (code 51.3, explain 47.4, rewrite 51.5, math 48.4)

| setup | k | tau | tok/s (mean of 4 prompts) | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 2 | 0 | 81.3 | 1.37 | 2.53 | 4/8 |
| stock llama.cpp spec (lossy) | 4 | 0 | 78.2 | 1.32 | 3.60 | 2/8 |
| stock llama.cpp spec (lossy) | 8 | 0 | 86.1 | 1.45 | 4.63 | 2/8 |
| hiraishin lossless | 2 | 0 | 81.8 | 1.65 | 2.50 | 4/4 |
| hiraishin lossless | 2 | 1 | 78.3 | 1.58 | 2.43 | 4/4 |
| hiraishin lossless | 2 | 2 | 77.4 | 1.56 | 2.37 | 4/4 |
| hiraishin lossless | 2 | 3 | 76.7 | 1.55 | 2.33 | 4/4 |
| hiraishin lossless | 3 | 0 | 80.5 | 1.62 | 3.06 | 4/4 |
| hiraishin lossless | 3 | 1 | 79.6 | 1.60 | 2.84 | 4/4 |
| hiraishin lossless | 3 | 2 | 78.6 | 1.58 | 2.71 | 4/4 |
| hiraishin lossless | 3 | 3 | 78.0 | 1.57 | 2.62 | 4/4 |
| hiraishin lossless | 4 | 0 | 77.4 | 1.56 | 3.47 | 4/4 |
| hiraishin lossless | 4 | 1 | 78.3 | 1.58 | 3.17 | 4/4 |
| hiraishin lossless | 4 | 2 | 78.8 | 1.59 | 2.95 | 4/4 |
| hiraishin lossless | 4 | 3 | 78.3 | 1.58 | 2.80 | 4/4 |
| hiraishin lossless | 5 | 0 | 75.4 | 1.52 | 3.82 | 4/4 |
| hiraishin lossless | 5 | 1 | 79.4 | 1.60 | 3.40 | 4/4 |
| hiraishin lossless | 5 | 2 | 80.9 | 1.63 | 3.15 | 4/4 |
| hiraishin lossless | 5 | 3 | 80.6 | 1.62 | 2.93 | 4/4 |
| hiraishin lossless | 6 | 0 | 70.9 | 1.43 | 4.15 | 4/4 |
| hiraishin lossless | 6 | 1 | 78.0 | 1.57 | 3.63 | 4/4 |
| hiraishin lossless | 6 | 2 | 79.4 | 1.60 | 3.25 | 4/4 |
| hiraishin lossless | 6 | 3 | 79.9 | 1.61 | 3.01 | 4/4 |
| hiraishin lossless | 8 | 0 | 64.6 | 1.30 | 4.58 | 4/4 |
| hiraishin lossless | 8 | 1 | 75.5 | 1.52 | 3.90 | 4/4 |
| hiraishin lossless | 8 | 2 | 79.5 | 1.60 | 3.44 | 4/4 |
| hiraishin lossless | 8 | 3 | 79.6 | 1.60 | 3.18 | 4/4 |

best single lossless setting: k=2 tau=0: 81.8 tok/s mean (code 78.3, explain 70.4, rewrite 91.8, math 86.7)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 16 (prompt, B) checks

## Qwen3-8B Q6_K

plain greedy decode (patched build, batch 1): 35.8 tok/s (code 39.1, explain 27.5, rewrite 39.6, math 36.9)

| setup | k | tau | tok/s (mean of 4 prompts) | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 2 | 0 | 62.1 | 1.49 | 2.48 | 2/8 |
| stock llama.cpp spec (lossy) | 4 | 0 | 69.3 | 1.66 | 3.41 | 4/8 |
| stock llama.cpp spec (lossy) | 8 | 0 | 77.7 | 1.86 | 4.53 | 2/8 |
| hiraishin lossless | 2 | 0 | 57.8 | 1.62 | 2.42 | 4/4 |
| hiraishin lossless | 2 | 1 | 57.6 | 1.61 | 2.37 | 4/4 |
| hiraishin lossless | 2 | 2 | 56.9 | 1.59 | 2.31 | 4/4 |
| hiraishin lossless | 2 | 3 | 55.9 | 1.56 | 2.22 | 4/4 |
| hiraishin lossless | 3 | 0 | 58.5 | 1.64 | 2.87 | 4/4 |
| hiraishin lossless | 3 | 1 | 61.5 | 1.72 | 2.76 | 4/4 |
| hiraishin lossless | 3 | 2 | 58.2 | 1.63 | 2.62 | 4/4 |
| hiraishin lossless | 3 | 3 | 58.3 | 1.63 | 2.50 | 4/4 |
| hiraishin lossless | 4 | 0 | 59.3 | 1.66 | 3.26 | 4/4 |
| hiraishin lossless | 4 | 1 | 60.2 | 1.68 | 3.06 | 4/4 |
| hiraishin lossless | 4 | 2 | 60.9 | 1.70 | 2.80 | 4/4 |
| hiraishin lossless | 4 | 3 | 51.8 | 1.45 | 2.65 | 4/4 |
| hiraishin lossless | 5 | 0 | 57.2 | 1.60 | 3.58 | 4/4 |
| hiraishin lossless | 5 | 1 | 61.6 | 1.72 | 3.29 | 4/4 |
| hiraishin lossless | 5 | 2 | 60.5 | 1.69 | 3.00 | 4/4 |
| hiraishin lossless | 5 | 3 | 57.4 | 1.60 | 2.75 | 4/4 |
| hiraishin lossless | 6 | 0 | 50.9 | 1.42 | 3.78 | 4/4 |
| hiraishin lossless | 6 | 1 | 54.2 | 1.52 | 3.43 | 4/4 |
| hiraishin lossless | 6 | 2 | 56.5 | 1.58 | 3.06 | 4/4 |
| hiraishin lossless | 6 | 3 | 55.3 | 1.55 | 2.81 | 4/4 |
| hiraishin lossless | 8 | 0 | 47.5 | 1.33 | 4.09 | 4/4 |
| hiraishin lossless | 8 | 1 | 56.6 | 1.58 | 3.62 | 4/4 |
| hiraishin lossless | 8 | 2 | 60.6 | 1.69 | 3.21 | 4/4 |
| hiraishin lossless | 8 | 3 | 59.8 | 1.67 | 2.93 | 4/4 |

best single lossless setting: k=5 tau=1: 61.6 tok/s mean (code 58.6, explain 41.6, rewrite 82.2, math 63.9)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 16 (prompt, B) checks

## Conditions (important)

Measured 2026-10-25 on battery power (33%, discharging): nvidia-smi showed enforced power limit 55 W,
clocks_event_reasons.sw_power_cap Active, memory clock 9001 MHz (11001 MHz in the 2026-10-24 runs, which were on AC).
Plain decode in this session is ~15% slower than on 2026-10-24, so absolute tok/s here are battery-limited and the
"stock" rows (2026-10-24, AC) are not a same-conditions comparison. Lossless results and the x-plain ratios
(same session, same conditions) are valid.
