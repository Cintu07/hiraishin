
## Qwen3-8B Q4_K_M

plain greedy decode (patched build, batch 1): 58.4 tok/s (code 59.8, explain 59.0, rewrite 58.5, math 56.1)

| setup | k | tau | tok/s (mean of 4 prompts) | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 2 | 0 | 82.7 | 1.41 | 2.53 | 2/4 |
| stock llama.cpp spec (lossy) | 4 | 0 | 78.8 | 1.34 | 3.60 | 1/4 |
| stock llama.cpp spec (lossy) | 8 | 0 | 86.1 | 1.46 | 4.63 | 1/4 |
| hiraishin lossless | 2 | 0 | 88.5 | 1.52 | 2.50 | 4/4 |
| hiraishin lossless | 2 | 1 | 85.6 | 1.47 | 2.43 | 4/4 |
| hiraishin lossless | 2 | 2 | 87.3 | 1.50 | 2.37 | 4/4 |
| hiraishin lossless | 2 | 3 | 88.2 | 1.51 | 2.33 | 4/4 |
| hiraishin lossless | 3 | 0 | 86.5 | 1.48 | 3.06 | 4/4 |
| hiraishin lossless | 3 | 1 | 87.4 | 1.50 | 2.84 | 4/4 |
| hiraishin lossless | 3 | 2 | 89.7 | 1.54 | 2.71 | 4/4 |
| hiraishin lossless | 3 | 3 | 89.2 | 1.53 | 2.62 | 4/4 |
| hiraishin lossless | 4 | 0 | 85.8 | 1.47 | 3.47 | 4/4 |
| hiraishin lossless | 4 | 1 | 88.4 | 1.52 | 3.17 | 4/4 |
| hiraishin lossless | 4 | 2 | 89.6 | 1.54 | 2.95 | 4/4 |
| hiraishin lossless | 4 | 3 | 90.8 | 1.56 | 2.80 | 4/4 |
| hiraishin lossless | 5 | 0 | 82.0 | 1.41 | 3.82 | 4/4 |
| hiraishin lossless | 5 | 1 | 88.0 | 1.51 | 3.40 | 4/4 |
| hiraishin lossless | 5 | 2 | 90.5 | 1.55 | 3.15 | 4/4 |
| hiraishin lossless | 5 | 3 | 90.8 | 1.56 | 2.93 | 4/4 |
| hiraishin lossless | 6 | 0 | 77.3 | 1.32 | 4.15 | 4/4 |
| hiraishin lossless | 6 | 1 | 86.0 | 1.47 | 3.63 | 4/4 |
| hiraishin lossless | 6 | 2 | 90.6 | 1.55 | 3.25 | 4/4 |
| hiraishin lossless | 6 | 3 | 90.8 | 1.56 | 3.01 | 4/4 |
| hiraishin lossless | 8 | 0 | 70.8 | 1.21 | 4.58 | 4/4 |
| hiraishin lossless | 8 | 1 | 84.5 | 1.45 | 3.90 | 4/4 |
| hiraishin lossless | 8 | 2 | 89.3 | 1.53 | 3.44 | 4/4 |
| hiraishin lossless | 8 | 3 | 91.8 | 1.57 | 3.18 | 4/4 |

best single lossless setting: k=8 tau=3: 91.8 tok/s mean (code 78.7, explain 80.5, rewrite 107.2, math 100.9)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 16 (prompt, B) checks

## Qwen3-8B Q6_K

plain greedy decode (patched build, batch 1): 48.1 tok/s (code 49.9, explain 47.8, rewrite 47.4, math 47.1)

| setup | k | tau | tok/s (mean of 4 prompts) | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 2 | 0 | 75.5 | 1.55 | 2.48 | 1/4 |
| stock llama.cpp spec (lossy) | 4 | 0 | 77.2 | 1.58 | 3.39 | 2/4 |
| stock llama.cpp spec (lossy) | 8 | 0 | 85.5 | 1.75 | 4.33 | 1/4 |
| hiraishin lossless | 2 | 0 | 80.6 | 1.68 | 2.42 | 4/4 |
| hiraishin lossless | 2 | 1 | 79.8 | 1.66 | 2.37 | 4/4 |
| hiraishin lossless | 2 | 2 | 78.7 | 1.64 | 2.31 | 4/4 |
| hiraishin lossless | 2 | 3 | 77.3 | 1.61 | 2.22 | 4/4 |
| hiraishin lossless | 3 | 0 | 80.7 | 1.68 | 2.87 | 4/4 |
| hiraishin lossless | 3 | 1 | 82.4 | 1.71 | 2.76 | 4/4 |
| hiraishin lossless | 3 | 2 | 81.9 | 1.70 | 2.62 | 4/4 |
| hiraishin lossless | 3 | 3 | 80.2 | 1.67 | 2.50 | 4/4 |
| hiraishin lossless | 4 | 0 | 76.7 | 1.60 | 3.26 | 4/4 |
| hiraishin lossless | 4 | 1 | 82.3 | 1.71 | 3.06 | 4/4 |
| hiraishin lossless | 4 | 2 | 81.7 | 1.70 | 2.80 | 4/4 |
| hiraishin lossless | 4 | 3 | 83.2 | 1.73 | 2.65 | 4/4 |
| hiraishin lossless | 5 | 0 | 75.6 | 1.57 | 3.58 | 4/4 |
| hiraishin lossless | 5 | 1 | 82.1 | 1.71 | 3.29 | 4/4 |
| hiraishin lossless | 5 | 2 | 83.2 | 1.73 | 3.00 | 4/4 |
| hiraishin lossless | 5 | 3 | 80.0 | 1.67 | 2.75 | 4/4 |
| hiraishin lossless | 6 | 0 | 73.7 | 1.53 | 3.78 | 4/4 |
| hiraishin lossless | 6 | 1 | 78.9 | 1.64 | 3.43 | 4/4 |
| hiraishin lossless | 6 | 2 | 82.9 | 1.73 | 3.06 | 4/4 |
| hiraishin lossless | 6 | 3 | 82.6 | 1.72 | 2.81 | 4/4 |
| hiraishin lossless | 8 | 0 | 67.4 | 1.40 | 4.09 | 4/4 |
| hiraishin lossless | 8 | 1 | 79.0 | 1.64 | 3.62 | 4/4 |
| hiraishin lossless | 8 | 2 | 83.6 | 1.74 | 3.21 | 4/4 |
| hiraishin lossless | 8 | 3 | 83.7 | 1.74 | 2.93 | 4/4 |

best single lossless setting: k=8 tau=3: 83.7 tok/s mean (code 75.9, explain 64.7, rewrite 109.3, math 85.0)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 16 (prompt, B) checks
