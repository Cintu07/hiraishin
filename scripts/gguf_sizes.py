"""Sum GGUF tensor bytes, split into "read every decode step" vs token_embd (row lookup).

usage: python -I scripts/gguf_sizes.py <model.gguf> [<llama.cpp>/gguf-py]
"""
import sys
import types
from collections import defaultdict

# gguf/metadata.py imports yaml at module level but only uses it for model cards; stub it so no install is needed
sys.modules.setdefault("yaml", types.ModuleType("yaml"))
sys.path.insert(0, sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\pavan\dev\llm\llama.cpp\gguf-py")
from gguf import GGUFReader  # noqa: E402

r = GGUFReader(sys.argv[1])
by_type = defaultdict(int)
total = embd = 0
tied = not any(t.name == "output.weight" for t in r.tensors)
for t in r.tensors:
    n = int(t.n_bytes)
    total += n
    by_type[t.tensor_type.name] += n
    if t.name == "token_embd.weight":
        embd = n

print(f"file: {sys.argv[1]}")
print(f"tensors: {len(r.tensors)}  total_bytes: {total}  ({total / 2**30:.3f} GiB)")
print(f"token_embd_bytes: {embd}  tied_output: {tied}")
# with tied embeddings the same matrix is the lm head, so it is read in full every step
per_token = total if tied else total - embd
print(f"weight_bytes_read_per_decode_step: {per_token}  ({per_token / 1e9:.3f} GB)")
for k, v in sorted(by_type.items(), key=lambda kv: -kv[1]):
    print(f"  {k:8s} {v:>12d}")
