#!/usr/bin/env bash
# Interleaved A/B of the two drafters at their best 4-prompt settings, so drift (heat, power) hits both equally:
# 0.6B Q8_0 k=5 tau=3 and 1.7B Q4_K_M k=8 tau=8, alternated twice. Each call also measures its own plain decode.
# usage (inside WSL): bash scripts/run_drafter_ab.sh [out dir]
set -uo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$HERE/logs/17_drafter_1p7b/ab}
BIN=$HOME/hiraishin-build/bin/spec_harness-build-cuda-hira
P=(); for p in code explain rewrite math; do P+=(-f "$HERE/prompts/$p.txt"); done
export GGML_CUDA_BATCH_INVARIANT=1; unset HIRAISHIN_BI_GENERIC HIRAISHIN_BI_ROWS HIRAISHIN_GRAPH_KEY_SIMPLE
mkdir -p "$OUT"
for r in 1 2; do
  for cfg in "Qwen3-0.6B-Q8_0 5 3" "Qwen3-1.7B-Q4_K_M 8 8"; do
    set -- $cfg; d=$OUT/r${r}_$1; mkdir -p "$d"
    "$BIN" -m "$HOME/models/Qwen3-8B-Q4_K_M.gguf" -md "$HOME/models/$1.gguf" "${P[@]}" -c 4096 -n 256 -k $2 --tau $3 \
      --ngram 0 --no-invariance --no-verify-cost --out "$d" > "$d/results.jsonl" 2> "$d/stderr.txt"
    echo "r$r $1 exit=$?"
  done
done
