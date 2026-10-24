#!/usr/bin/env bash
# Final lossless measurement: patched build, GGML_CUDA_BATCH_INVARIANT=1, KV_PAD guard, fixed-shape draft,
# fixed draft lengths and adaptive draft length (tau), on one target. Writes logs/06_final/<name>/.
# usage (inside WSL): bash scripts/run_final.sh <name> <target gguf> [draft gguf]
set -euo pipefail
NAME=${1:?name}; TGT=${2:?target gguf}
export DRAFT=${3:-$HOME/models/Qwen3-0.6B-Q8_0.gguf}
HERE=$(cd "$(dirname "$0")/.." && pwd)
export GGML_CUDA_BATCH_INVARIANT=1
unset HIRAISHIN_BI_GENERIC HIRAISHIN_BI_ROWS
bash "$HERE/scripts/run_harness.sh" "$HERE/logs/06_final/$NAME" "$HOME/hiraishin-build/bin/spec_harness-build-cuda-hira" "$TGT" \
  -n 256 -k ${KS:-2,3,4,5,6,8} --tau ${TAUS:-0,1,2,3} --reps 1 --inv-b 2,3,5,9
