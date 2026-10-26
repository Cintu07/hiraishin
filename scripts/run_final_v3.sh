#!/usr/bin/env bash
# Same-session end-to-end run with the per-shape CUDA graph key (patch 0005): stock speculative (unpatched, lossy) vs
# lossless with model-only and model+n-gram drafting, both targets. Output: logs/14_final_v3/.
# usage (inside WSL): bash scripts/run_final_v2.sh
set -uo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=$HERE/logs/14_final_v3
mkdir -p "$OUT"
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_start.txt"
for m in Q4_K_M Q6_K; do
  (unset GGML_CUDA_BATCH_INVARIANT; bash "$HERE/scripts/run_harness.sh" "$OUT/stock_$m" \
    "$HOME/hiraishin-build/bin/spec_harness-build-cuda" "$HOME/models/Qwen3-8B-$m.gguf" \
    -n 256 -k 8 --reps 1 --no-invariance --no-verify-cost)
  (export GGML_CUDA_BATCH_INVARIANT=1; unset HIRAISHIN_BI_GENERIC HIRAISHIN_BI_ROWS; bash "$HERE/scripts/run_harness.sh" "$OUT/hira_$m" \
    "$HOME/hiraishin-build/bin/spec_harness-build-cuda-hira" "$HOME/models/Qwen3-8B-$m.gguf" \
    -n 256 -k 5 --tau 3 --ngram 0,3 --reps 2 --inv-b 2,5,9)
done
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_end.txt"
