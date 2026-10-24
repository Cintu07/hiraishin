#!/usr/bin/env bash
# Batch-invariant mat-vec kernel check: teacher-forced bit-exactness and verify cost vs B,
# for the generic BI path and the mmvq-bi kernel at 1/2/4 rows per block.
# usage (inside WSL): bash scripts/sweep_bi_kernel.sh <out dir> <target gguf>
set -euo pipefail
OUT=${1:?out dir}; TGT=${2:?target gguf}
HERE=$(cd "$(dirname "$0")/.." && pwd)
BIN=$HOME/hiraishin-build/bin/spec_harness-build-cuda-hira
mkdir -p "$OUT"
export GGML_CUDA_BATCH_INVARIANT=1
for cfg in ${CFGS:-generic rows1 rows2 rows4 rows8}; do
  unset HIRAISHIN_BI_GENERIC HIRAISHIN_BI_ROWS
  case $cfg in
    generic) export HIRAISHIN_BI_GENERIC=1 ;;
    rows*)   export HIRAISHIN_BI_ROWS=${cfg#rows} ;;
  esac
  mkdir -p "$OUT/$cfg"
  "$BIN" -m "$TGT" -f "$HERE/prompts/rewrite.txt" -f "$HERE/prompts/code.txt" -n 256 --inv-b 2,3,5,8,9,12 \
    --out "$OUT/$cfg" > "$OUT/$cfg/results.jsonl" 2> "$OUT/$cfg/stderr.txt"
  echo "$cfg exit=$?"
done
