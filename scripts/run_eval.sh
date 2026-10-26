#!/usr/bin/env bash
# Broader evaluation: 45 prompts (prompts/eval), 1024 tokens, 4096 context, Qwen3-8B Q4_K_M, one session.
# stock build: plain + stock speculative k=8 (lossy). patched build: plain + lossless k=5 tau=3, n-gram off/on.
# usage (inside WSL): bash scripts/run_eval.sh [out dir]
set -uo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$HERE/logs/15_eval}
TGT=$HOME/models/Qwen3-8B-Q4_K_M.gguf
DFT=$HOME/models/Qwen3-0.6B-Q8_0.gguf
PROMPTS=()
for f in "$HERE"/prompts/eval/*.txt; do PROMPTS+=(-f "$f"); done
mkdir -p "$OUT/stock" "$OUT/hira"
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_start.txt"
{ echo "date: $(date -Is)"; echo "prompts: ${#PROMPTS[@]} args"; } > "$OUT/run_info.txt"

(unset GGML_CUDA_BATCH_INVARIANT
 "$HOME/hiraishin-build/bin/spec_harness-build-cuda" -m "$TGT" -md "$DFT" "${PROMPTS[@]}" -c 4096 -n 1024 \
   -k 8 --no-invariance --no-verify-cost --out "$OUT/stock" > "$OUT/stock/results.jsonl" 2> "$OUT/stock/stderr.txt")
echo "stock exit=$? lines=$(wc -l < "$OUT/stock/results.jsonl")"

(export GGML_CUDA_BATCH_INVARIANT=1; unset HIRAISHIN_BI_GENERIC HIRAISHIN_BI_ROWS HIRAISHIN_GRAPH_KEY_SIMPLE
 "$HOME/hiraishin-build/bin/spec_harness-build-cuda-hira" -m "$TGT" -md "$DFT" "${PROMPTS[@]}" -c 4096 -n 1024 \
   -k 5 --tau 3 --ngram 0,3 --no-invariance --no-verify-cost --out "$OUT/hira" > "$OUT/hira/results.jsonl" 2> "$OUT/hira/stderr.txt")
echo "hira exit=$? lines=$(wc -l < "$OUT/hira/results.jsonl")"
nvidia-smi --query-gpu=power.draw,enforced.power.limit,clocks.max.mem,pstate,temperature.gpu --format=csv > "$OUT/gpu_end.txt"
