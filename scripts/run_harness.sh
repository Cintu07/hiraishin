#!/usr/bin/env bash
# Run harness/spec_harness over the fixed prompt set in one process (models load once).
# usage (inside WSL): bash scripts/run_harness.sh <out dir> <harness binary> <target gguf> [extra harness args...]
# env: set GGML_CUDA_BATCH_INVARIANT=1 before calling to test batch-invariant mode.
set -euo pipefail
OUT=${1:?out dir}; BIN=${2:?harness binary}; TGT=${3:?target gguf}; shift 3
HERE=$(cd "$(dirname "$0")/.." && pwd)
DFT=${DRAFT:-$HOME/models/Qwen3-0.6B-Q8_0.gguf}
mkdir -p "$OUT"
{
  echo "date: $(date -Is)"
  echo "bin: $BIN"; echo "target: $TGT"; echo "draft: $DFT"
  echo "GGML_CUDA_BATCH_INVARIANT=${GGML_CUDA_BATCH_INVARIANT:-<unset>}"
  echo "args: $*"
  nvidia-smi --query-gpu=name,driver_version,clocks.sm,clocks.mem,temperature.gpu,power.draw --format=csv,noheader
} > "$OUT/run_info.txt"
"$BIN" -m "$TGT" -md "$DFT" \
  -f "$HERE/prompts/code.txt" -f "$HERE/prompts/explain.txt" -f "$HERE/prompts/rewrite.txt" -f "$HERE/prompts/math.txt" \
  --out "$OUT" "$@" > "$OUT/results.jsonl" 2> "$OUT/stderr.txt"
echo "exit=$? lines=$(wc -l < "$OUT/results.jsonl")"
