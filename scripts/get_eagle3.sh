#!/usr/bin/env bash
# Fetch the AngelSlim EAGLE-3 head for Qwen3-8B plus the target's config/tokenizer (no target weights), and convert
# the head to GGUF with the fork's converter. Downloads go to their own directory; the converter loads the pickle
# with torch.load(weights_only=True) (conversion/base.py), so no code from the download runs.
# usage (inside WSL): bash scripts/get_eagle3.sh
set -euo pipefail
E=$HOME/eagle
L=$HOME/hiraishin-build/llama.cpp
mkdir -p "$E/head" "$E/qwen3-8b"
HF=https://huggingface.co
for f in config.json pytorch_model.bin; do
  [ -s "$E/head/$f" ] || curl -L --fail --retry 5 -C - -o "$E/head/$f" "$HF/AngelSlim/Qwen3-8B_eagle3/resolve/main/$f"
done
for f in config.json generation_config.json tokenizer.json tokenizer_config.json vocab.json merges.txt; do
  [ -s "$E/qwen3-8b/$f" ] || curl -L --fail --retry 5 -o "$E/qwen3-8b/$f" "$HF/Qwen/Qwen3-8B/resolve/main/$f"
done
sha256sum "$E/head/pytorch_model.bin" > "$E/head.sha256"
if [ ! -x "$E/venv/bin/python" ]; then
  python3 -m venv "$E/venv"
  "$E/venv/bin/pip" install -q --upgrade pip
  "$E/venv/bin/pip" install -q torch --index-url https://download.pytorch.org/whl/cpu
  "$E/venv/bin/pip" install -q numpy safetensors sentencepiece transformers jinja2 pyyaml
fi
cd "$L"
"$E/venv/bin/python" convert_hf_to_gguf.py "$E/head" --target-model-dir "$E/qwen3-8b" --outtype bf16 \
  --outfile "$HOME/models/Qwen3-8B-eagle3-AngelSlim-bf16.gguf"
ls -l "$HOME/models/Qwen3-8B-eagle3-AngelSlim-bf16.gguf"
