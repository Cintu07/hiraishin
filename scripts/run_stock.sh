#!/usr/bin/env bash
# Step 1.1/1.2: plain greedy decode (llama-completion) and llama-speculative at draft lengths 2/4/8,
# over the fixed prompt set. One process per run; stdout = prompt echo + generation, stderr = stats.
# usage: bash scripts/run_stock.sh <out dir> [reps]
set -u
OUT=${1:?out dir}; REPS=${2:-2}
RT=/c/Users/pavan/Desktop/CIOT-V2/gpu-runtime
M=/c/Users/pavan/Desktop/CIOT-V2/models
TGT=$M/Qwen3-8B-Q6_K.gguf
DFT=$M/Qwen3-0.6B-Q8_0.gguf
COMMON=(-ngl 99 -c 2048 -fa on --temp 0 --seed 1 -n 256)
mkdir -p "$OUT"
{
  echo "date: $(date -Is)"
  "$RT/llama-cli.exe" --version 2>&1 | head -2
  echo "target: $TGT"; echo "draft: $DFT"; echo "common: ${COMMON[*]}"
} > "$OUT/run_info.txt"

for p in code explain rewrite math; do
  for r in $(seq 1 "$REPS"); do
    tag=plain_${p}_r$r
    "$RT/llama-completion.exe" -m "$TGT" "${COMMON[@]}" -no-cnv -f prompts/$p.txt \
      > "$OUT/$tag.out" 2> "$OUT/$tag.err" < /dev/null
    echo "$tag exit=$?"
    for k in 2 4 8; do
      tag=spec_k${k}_${p}_r$r
      "$RT/llama-speculative.exe" -m "$TGT" -md "$DFT" -ngld 99 "${COMMON[@]}" --spec-draft-n-max $k -f prompts/$p.txt \
        > "$OUT/$tag.out" 2> "$OUT/$tag.err" < /dev/null
      echo "$tag exit=$?"
    done
  done
done
