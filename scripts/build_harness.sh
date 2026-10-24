#!/usr/bin/env bash
# Build harness/spec_harness.cpp in WSL against a llama.cpp CUDA build.
# usage (inside WSL): bash scripts/build_harness.sh [llama.cpp dir] [build subdir]
set -euo pipefail
L=${1:-$HOME/hiraishin-build/llama.cpp}
B=${2:-build-cuda}
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=$HOME/hiraishin-build/bin
mkdir -p "$OUT"
export PATH=$HOME/cuda-13/bin:$PATH
g++ -O2 -std=c++17 -o "$OUT/spec_harness-$B" "$HERE/harness/spec_harness.cpp" \
    -I"$L/include" -I"$L/ggml/include" \
    -L"$L/$B/bin" -lllama -lggml -lggml-base -Wl,-rpath,"$L/$B/bin" -Wl,-rpath-link,"$L/$B/bin" \
    -Wl,-rpath-link,/usr/lib/wsl/lib
echo "built $OUT/spec_harness-$B"
