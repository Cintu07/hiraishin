#!/usr/bin/env bash
# Fetch Qwen3-1.7B Q4_K_M (unsloth GGUF) as a candidate drafter and check its sha256 against the hub's ETag.
# usage (inside WSL): bash scripts/get_drafter_1p7b.sh
set -euo pipefail
F=$HOME/models/Qwen3-1.7B-Q4_K_M.gguf
SHA=b139949c5bd74937ad8ed8c8cf3d9ffb1e99c866c823204dc42c0d91fa181897
curl -L --fail --retry 5 -C - -o "$F" https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf
echo "$SHA  $F" | sha256sum -c -
ls -l "$F"
