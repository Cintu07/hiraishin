# hiraishin

lossless speculative decoding for an 8b model on an 8 gb laptop gpu.

qwen3-8b q4_k_m runs at 61 tok/s on my rtx 5060 laptop with plain greedy decoding. with a 0.6b draft model, batched verification and the fixes in this repo it runs at 92 tok/s on a 45 prompt eval, and every one of the 45 outputs is token for token identical to plain decoding. stock speculative decoding on the same machine gets 77 tok/s and changes the output on 37 of the 45 prompts.

## results

one session, qwen3-8b q4_k_m target, qwen3-0.6b q8_0 draft, greedy, up to 1024 tokens per prompt, context 4096.

| setup | mean tok/s | median | slowest 10% | outputs identical to plain |
|---|---:|---:|---:|---|
| plain decode | 61.4 | 61.7 | 60.7 | n/a |
| stock speculative, k=8 | 76.6 | 71.4 | 35.5 | 8 / 45 |
| hiraishin, k=5, adaptive stop | **92.3** | **91.1** | 75.3 | **45 / 45** |

per category: math 108, structured output 104, code generation 98, code edits 94, summaries 91, explanations 84, creative writing 76, long documents 76. full table in `logs/15_eval/summary.md`.

on the smaller 4 prompt set the same setup reaches 102.7 tok/s, and 110.3 with n-gram drafting (`logs/14_final_v3/summary.md`). that set leans on prompts that copy from their input, so quote the 45 prompt numbers.

## why stock speculative decoding changed the output

the accept rule in speculative decoding is exact. the kernels are the problem. the target checks k drafted tokens in one batch of k+1, and the gpu sums floats in a different order for a batch than for a single token. logits drift by up to 3.7, and at a near tie the argmax flips. four separate causes showed up in the llama.cpp fork i used (commit `e8fd209`):

1. the mat-vec kernel splits the k dimension over 4 warps for 1 to 4 columns and 2 warps for 5 to 8, and k-quants switch to a different kernel past 5 to 7 columns.
2. attention picks a different kernel for more than one query.
3. the kv cache length is padded to a multiple of 256, so a batch that crosses a boundary attends over a longer range than the same token decoded alone.
4. vector attention sizes its kv split from gpu occupancy, which differs between the 1 query and 2 query kernels. this one only shows up past kv position 384.

each fix keeps the single token path untouched, so the reference stays the unmodified model. the check: feed the plain output back through the target in batches and compare every logit. after the fixes the max difference is 0.000000 for batch sizes 2 to 16.

## what is in here

| path | what |
|---|---|
| `patches/` | five patches against the fork at `e8fd209`. they apply in order and reproduce the build tree exactly |
| `harness/spec_harness.cpp` | the benchmark: plain decode, speculative decode with per cycle timing, verify cost vs batch size, batch invariance check, call pattern probes |
| `scripts/` | build, run and analysis scripts. every number in this readme comes from a script reading a saved log |
| `prompts/` | the 4 prompt set and the 45 prompt eval set (`scripts/make_eval_prompts.py`) |
| `logs/` | raw results for every run, by step |
| `docs/PROGRESS.md` | the full log of what was tried, what worked and what did not |
| `docs/x/` | charts generated from the logs |

the patches:

- `0001` mat-vec uses the 1 column warp split for every column count, and up to 16 columns stay on the mat-vec path
- `0002` attention keeps the vector kernel for up to 16 queries
- `0003` batched vector attention borrows the 1 query kernel's occupancy for its kv split
- `0004` a q4_k / q6_k multi column mat-vec that keeps per column arithmetic but shares weight unpacking, 4 blocks per sm
- `0005` the cuda graph cache keeps one graph per batch shape. stock keys it by the first node pointer, which llama.cpp reuses for every shape, so a changing verify size re captured the graph every call

everything except `0005` only does something with `GGML_CUDA_BATCH_INVARIANT=1`. the kv padding fix lives in the harness: a verify window never crosses a multiple of 256.

## reproduce

linux or wsl2, cuda 13, an sm_120 gpu (the kernels are tuned for that table, other gpus fall back to the stock path).

```bash
git clone https://github.com/PrismML-Eng/llama.cpp && cd llama.cpp && git checkout e8fd209
for p in /path/to/hiraishin/patches/000*.patch; do git apply -p1 "$p"; done
cmake -S . -B build-cuda-hira -G Ninja -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=120a -DGGML_CUDA_NCCL=OFF -DLLAMA_CURL=OFF
cmake --build build-cuda-hira -j --target llama-bench

cd /path/to/hiraishin
bash scripts/build_harness.sh /path/to/llama.cpp build-cuda-hira
GGML_CUDA_BATCH_INVARIANT=1 ~/hiraishin-build/bin/spec_harness-build-cuda-hira \
  -m Qwen3-8B-Q4_K_M.gguf -md Qwen3-0.6B-Q8_0.gguf -f prompts/code.txt \
  -n 256 -k 5 --tau 3 --inv-b 2,5,9 --out /tmp/run
```

each `spec` line of the output carries `matches_plain`, and each `invariance` line carries `argmax_mismatches` and `max_abs_dlogit_top1`. lossless means `true`, `0` and `0.000000`.

## limits

- one gpu, one model family, one fork. upstream llama.cpp was not tested.
- 45 prompts is enough to see the shape, small for a leaderboard claim.
- the draft model accepts about 2.5 tokens per target pass. that is the ceiling now, more than the kernels.
