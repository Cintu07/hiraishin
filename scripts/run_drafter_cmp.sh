#!/usr/bin/env bash
# Draft model comparison on the patched build, lossless settings (k=5 tau=3, n-gram off), same session:
# Qwen3-0.6B Q8_0 vs Qwen3-1.7B Q4_K_M as drafter for Qwen3-8B Q4_K_M. Every run is checked token for token
# against plain decoding inside the harness.
# usage (inside WSL): bash scripts/run_drafter_cmp.sh <smoke|eval> [out dir]
set -uo pipefail
MODE=${1:?smoke or eval}
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=${2:-$HERE/logs/17_drafter_1p7b/$MODE}
TGT=$HOME/models/Qwen3-8B-Q4_K_M.gguf
BIN=$HOME/hiraishin-build/bin/spec_harness-build-cuda-hira
PROMPTS=()
if [ "$MODE" = eval ]; then
  for f in "$HERE"/prompts/eval/*.txt; do PROMPTS+=(-f "$f"); done; N=1024
else
  for p in code explain rewrite math; do PROMPTS+=(-f "$HERE/prompts/$p.txt"); done; N=256
fi
export GGML_CUDA_BATCH_INVARIANT=1; unset HIRAISHIN_BI_GENERIC HIRAISHIN_BI_ROWS HIRAISHIN_GRAPH_KEY_SIMPLE
mkdir -p "$OUT"
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_start.txt"
date -Is > "$OUT/run_info.txt"
for d in Qwen3-0.6B-Q8_0 Qwen3-1.7B-Q4_K_M; do
  mkdir -p "$OUT/$d"
  "$BIN" -m "$TGT" -md "$HOME/models/$d.gguf" "${PROMPTS[@]}" -c 4096 -n $N -k 5 --tau 3 --ngram 0 \
    --no-invariance --no-verify-cost --out "$OUT/$d" > "$OUT/$d/results.jsonl" 2> "$OUT/$d/stderr.txt"
  echo "$d exit=$? lines=$(wc -l < "$OUT/$d/results.jsonl")"
done
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_end.txt"
