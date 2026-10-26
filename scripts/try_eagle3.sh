#!/usr/bin/env bash
# First look at EAGLE-3 drafting (AngelSlim head for Qwen3-8B) with the fork's llama-speculative-simple, patched build,
# GGML_CUDA_BATCH_INVARIANT=1. Text-level exactness check against llama-completion (same build, same env).
# usage (inside WSL): bash scripts/try_eagle3.sh [out dir]
set -uo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$HERE/logs/16_eagle3}
B=$HOME/hiraishin-build/llama.cpp/build-cuda-hira/bin
TGT=$HOME/models/Qwen3-8B-Q4_K_M.gguf
EAG=$HOME/models/Qwen3-8B-eagle3-AngelSlim-bf16.gguf
export GGML_CUDA_BATCH_INVARIANT=1
mkdir -p "$OUT"
for p in code explain rewrite math; do
  "$B/llama-completion" -m "$TGT" -ngl 99 -c 4096 -fa on --temp 0 --seed 1 -n 256 -no-cnv -f "$HERE/prompts/$p.txt" \
    > "$OUT/plain_$p.out" 2> "$OUT/plain_$p.err" < /dev/null
  for k in 3 5 8; do
    "$B/llama-speculative-simple" -m "$TGT" -md "$EAG" --spec-type draft-eagle3 -ngl 99 -ngld 99 -c 4096 -fa on \
      --temp 0 --seed 1 -n 256 --spec-draft-n-max $k -f "$HERE/prompts/$p.txt" \
      > "$OUT/eagle3_k${k}_$p.out" 2> "$OUT/eagle3_k${k}_$p.err" < /dev/null
    echo "$p k=$k exit=$?"
  done
done
