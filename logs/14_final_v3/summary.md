
## Qwen3-8B Q4_K_M

plain greedy decode (patched build, batch 1): 62.8 tok/s (code 64.2, explain 62.4, rewrite 61.9, math 62.7)

| setup | k | tau | ngram | pad | tok/s (mean of 4 prompts) | median prompt | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 8 | 0 | 0 | 0 | 101.5 | 93.6 | 1.62 | 4.63 | 1/4 |
| hiraishin lossless | 5 | 3 | 0 | 0 | 102.7 | 100.5 | 1.64 | 2.93 | 8/8 |
| hiraishin lossless | 5 | 3 | 3 | 0 | 110.3 | 97.0 | 1.76 | 2.88 | 8/8 |

best single lossless setting: k=5 tau=3 ngram=3 pad_verify=0: 110.3 tok/s mean (code 92.5, explain 88.5, rewrite 158.6, math 101.6)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 12 (prompt, B) checks

## Qwen3-8B Q6_K

plain greedy decode (patched build, batch 1): 48.3 tok/s (code 49.1, explain 48.2, rewrite 47.9, math 48.3)

| setup | k | tau | ngram | pad | tok/s (mean of 4 prompts) | median prompt | x plain | tokens per target pass | lossless runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| stock llama.cpp spec (lossy) | 8 | 0 | 0 | 0 | 83.9 | 79.5 | 1.74 | 4.33 | 1/4 |
| hiraishin lossless | 5 | 3 | 0 | 0 | 85.2 | 84.8 | 1.76 | 2.75 | 8/8 |
| hiraishin lossless | 5 | 3 | 3 | 0 | 90.9 | 80.6 | 1.88 | 2.69 | 8/8 |

best single lossless setting: k=5 tau=3 ngram=3 pad_verify=0: 90.9 tok/s mean (code 79.3, explain 67.4, rewrite 135.0, math 81.8)
invariance: 0 argmax flips, max |dlogit| 0.000000 over 12 (prompt, B) checks
