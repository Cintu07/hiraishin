"""Summarize scripts/sweep_bi_kernel.sh output: bit-exactness and verify cost (x B=1) per config.

usage: python -I scripts/summarize_sweep.py <sweep dir> [<sweep dir> ...]
"""
import collections
import json
import os
import sys

for D in sys.argv[1:]:
    print(f"== {D}")
    for cfg in sorted(os.listdir(D)):
        f = os.path.join(D, cfg, "results.jsonl")
        if not os.path.exists(f):
            continue
        ev = [json.loads(l) for l in open(f) if l.startswith("{")]
        inv = [e for e in ev if e["event"] == "invariance"]
        flips = sum(e["argmax_mismatches"] for e in inv)
        mx = max(e["max_abs_dlogit_top1"] for e in inv)
        vc = collections.defaultdict(list)
        for e in ev:
            if e["event"] == "verify_cost":
                vc[e["B"]].append(e["ms_median"])
        b1 = sum(vc[1]) / len(vc[1])
        row = " ".join(f"B{b}={sum(v) / len(v) / b1:.2f}x" for b, v in sorted(vc.items()) if b > 1)
        print(f"  {cfg:10s} flips={flips} max|dlogit|={mx:.6f} B1={b1:.2f}ms {row}")
