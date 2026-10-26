# broad evaluation (45 prompts, Qwen3-8B Q4_K_M, RTX 5060 Laptop, 1024 tokens max, ctx 4096)

tokens generated per prompt (plain): mean 509, min 111, max 1024; prompt lengths 26-2639 tokens

## overall

| setup | mean tok/s | median | p10 (slow end) | worst prompt | x plain (mean of ratios) | prompts exact |
|---|---:|---:|---:|---:|---:|---|
| plain decode | 61.4 | 61.7 | 60.7 | 56.2 (long_context_02) | 1.00 | - |
| stock llama.cpp spec k=8 (lossy) | 76.6 | 71.4 | 35.5 | 32.4 (creative_02) | 1.24 | 8/45 |
| hiraishin k=5 tau=3 (lossless) | 92.3 | 91.1 | 75.3 | 65.3 (long_context_02) | 1.50 | 45/45 |
| hiraishin k=5 tau=3 + n-gram (lossless) | 89.8 | 89.8 | 76.3 | 63.8 (long_context_02) | 1.46 | 45/45 |

## per category (mean tok/s; exact prompts in brackets)

| category | n | plain decode | stock llama.cpp spec k=8 (lossy) | hiraishin k=5 tau=3 (lossless) | hiraishin k=5 tau=3 + n-gram (lossless) |
|---|---:|---:|---:|---:|---:|
| code_edit | 5 | 62.0 | 76.3 [0/5] | 93.9 [5/5] | 94.4 [5/5] |
| code_gen | 7 | 61.8 | 68.0 [0/7] | 98.3 [7/7] | 94.9 [7/7] |
| creative | 5 | 61.5 | 35.4 [0/5] | 76.0 [5/5] | 76.6 [5/5] |
| explain | 7 | 61.6 | 62.1 [0/7] | 83.8 [7/7] | 82.4 [7/7] |
| long_context | 4 | 57.2 | 59.9 [0/4] | 76.5 [4/4] | 75.9 [4/4] |
| math | 7 | 62.0 | 121.3 [3/7] | 108.1 [7/7] | 102.3 [7/7] |
| structured | 4 | 61.9 | 107.5 [1/4] | 104.5 [4/4] | 98.2 [4/4] |
| summarize | 6 | 62.0 | 76.3 [4/6] | 91.1 [6/6] | 88.9 [6/6] |

## acceptance (pooled over prompts)

| setup | accept % | tokens per target pass | n-gram cycles share |
|---|---:|---:|---:|
| stock llama.cpp spec k=8 (lossy) | 37.6 | 3.96 | 0.00 |
| hiraishin k=5 tau=3 (lossless) | 77.3 | 2.52 | 0.00 |
| hiraishin k=5 tau=3 + n-gram (lossless) | 64.9 | 2.46 | 0.12 |

cross-check: patched-build plain decode token ids == stock-build plain decode on 45/45 prompts
stock-build plain mean 57.0 tok/s, patched-build plain mean 61.4 tok/s
