# EAGLE-3 first look (2026-10-26 run, summarized 2026-11-06)

`scripts/try_eagle3.sh`: AngelSlim EAGLE-3 head for Qwen3-8B (converted to bf16 GGUF, `scripts/get_eagle3.sh`),
target Qwen3-8B Q4_K_M, the fork's `llama-speculative-simple --spec-type draft-eagle3`, patched build,
`GGML_CUDA_BATCH_INVARIANT=1`, 4-prompt set (chat template, thinking off), 256 tokens, fixed draft length k.
Plain reference: `llama-completion` on the same build. Numbers are the tools' own `accept` and `decoded ... speed` lines.

| prompt | plain tok/s | k=3 accept / tok/s | k=5 accept / tok/s | k=8 accept / tok/s |
|---|---:|---:|---:|---:|
| code | 64.4 | 30.8% / 60.7 | 19.8% / 47.0 | 12.9% / 31.5 |
| explain | 67.5 | 32.3% / 65.0 | 21.0% / 45.2 | 13.6% / 32.2 |
| rewrite | 66.0 | 71.1% / 96.9 | 59.2% / 90.0 | 45.8% / 72.3 |
| math | 67.3 | 37.5% / 69.0 | 26.0% / 54.7 | 16.6% / 37.5 |

- Acceptance is far below the Qwen3-0.6B Q8_0 draft model (77.3% of drafted tokens on the 45 prompt eval, with the
  adaptive stop). Only the copy-heavy rewrite prompt gains. At k=3 code and explain are below plain decoding.
- Text vs plain: code, rewrite, math identical over the compared length; explain diverges at the same character
  (858) at every k, which points at the tool's prompt path rather than the verify batch. Not investigated.
- `llama-speculative-simple` has no adaptive stop, so a fairer comparison would put the head in `spec_harness`.
  With acceptance this low at k=3, that would not beat the 0.6B draft. Dropped.
