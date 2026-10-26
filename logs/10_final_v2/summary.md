
## Qwen3-8B Q4_K_M

plain greedy decode (patched build, batch 1): 62.4 tok/s (code 63.7, explain 62.3, rewrite 61.4, math 62.3)

| setup | k | tau | ngram | tok/s (mean of 4 prompts) | median prompt | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 8 | 0 | 0 | 96.1 | 88.7 | 1.54 | 4.63 | 1/4 |
| hiraishin lossless | 4 | 3 | 0 | 98.4 | 96.4 | 1.58 | 2.80 | 8/8 |
| hiraishin lossless | 4 | 3 | 3 | 103.9 | 90.3 | 1.67 | 2.76 | 8/8 |
| hiraishin lossless | 6 | 3 | 0 | 98.7 | 95.3 | 1.58 | 3.01 | 8/8 |
| hiraishin lossless | 6 | 3 | 3 | 104.1 | 90.4 | 1.67 | 2.97 | 8/8 |
| hiraishin lossless | 8 | 3 | 0 | 97.8 | 94.9 | 1.57 | 3.18 | 8/8 |
| hiraishin lossless | 8 | 3 | 3 | 101.3 | 89.9 | 1.62 | 3.13 | 8/8 |

best single lossless setting: k=6 tau=3 ngram=3: 104.1 tok/s mean (code 86.1, explain 84.5, rewrite 151.2, math 94.7)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 12 (prompt, B) checks

## Qwen3-8B Q6_K

plain greedy decode (patched build, batch 1): 48.2 tok/s (code 48.9, explain 48.3, rewrite 47.8, math 47.9)

| setup | k | tau | ngram | tok/s (mean of 4 prompts) | median prompt | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 8 | 0 | 0 | 85.5 | 78.8 | 1.77 | 4.33 | 1/4 |
| hiraishin lossless | 4 | 3 | 0 | 81.4 | 81.9 | 1.69 | 2.65 | 8/8 |
| hiraishin lossless | 4 | 3 | 3 | 85.2 | 75.8 | 1.77 | 2.58 | 8/8 |
| hiraishin lossless | 6 | 3 | 0 | 83.0 | 81.0 | 1.72 | 2.81 | 8/8 |
| hiraishin lossless | 6 | 3 | 3 | 88.3 | 75.0 | 1.83 | 2.77 | 8/8 |
| hiraishin lossless | 8 | 3 | 0 | 81.2 | 79.0 | 1.68 | 2.93 | 8/8 |
| hiraishin lossless | 8 | 3 | 3 | 85.8 | 76.7 | 1.78 | 2.92 | 8/8 |

best single lossless setting: k=6 tau=3 ngram=3: 88.3 tok/s mean (code 73.1, explain 66.0, rewrite 137.3, math 76.9)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 12 (prompt, B) checks
