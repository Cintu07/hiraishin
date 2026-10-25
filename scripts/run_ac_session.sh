#!/usr/bin/env bash
# One session, same conditions: plain llama-bench, stock speculative (unpatched build, BI off), and the
# patched lossless setup, for both targets. Output: logs/07_ac_session/.
# usage (inside WSL): bash scripts/run_ac_session.sh
set -uo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=$HERE/logs/07_ac_session
mkdir -p "$OUT"
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_start.txt"
for m in Q4_K_M Q6_K; do
  "$HOME/hiraishin-build/llama.cpp/build-cuda/bin/llama-bench" -m "$HOME/models/Qwen3-8B-$m.gguf" -ngl 99 -fa 1 \
    -p 0 -n 128 -d 0,512 -r 5 -o md > "$OUT/bench_plain_$m.txt" 2>&1
  echo "bench $m exit=$?"
  (unset GGML_CUDA_BATCH_INVARIANT; bash "$HERE/scripts/run_harness.sh" "$OUT/stock_$m" \
    "$HOME/hiraishin-build/bin/spec_harness-build-cuda" "$HOME/models/Qwen3-8B-$m.gguf" \
    -n 256 -k 2,4,8 --reps 1 --inv-b 2,5,9 --no-verify-cost)
  (export GGML_CUDA_BATCH_INVARIANT=1; unset HIRAISHIN_BI_GENERIC HIRAISHIN_BI_ROWS; bash "$HERE/scripts/run_harness.sh" "$OUT/hira_$m" \
    "$HOME/hiraishin-build/bin/spec_harness-build-cuda-hira" "$HOME/models/Qwen3-8B-$m.gguf" \
    -n 256 -k 2,3,4,5,6,8 --tau 0,1,2,3 --reps 1 --inv-b 2,3,5,9)
done
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_end.txt"
