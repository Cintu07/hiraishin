"""Analyze the broad evaluation (scripts/run_eval.sh): per-category and overall tok/s, exactness, plain cross-check.

usage: python -I scripts/analyze_eval.py [logs/15_eval]  -> prints markdown (tee it into summary.md)
"""
import collections
import json
import os
import statistics as st
import sys

D = sys.argv[1] if len(sys.argv) > 1 else "logs/15_eval"


def load(sub):
    with open(os.path.join(D, sub, "results.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.startswith("{")]


stock, hira = load("stock"), load("hira")
cat = lambda p: p.rsplit("_", 1)[0]

plain = {e["prompt"]: e for e in hira if e["event"] == "plain"}
plain_stock = {e["prompt"]: e for e in stock if e["event"] == "plain"}
setups = collections.OrderedDict([
    ("plain decode", {p: e["tok_s"] for p, e in plain.items()}),
    ("stock llama.cpp spec k=8 (lossy)", {e["prompt"]: e for e in stock if e["event"] == "spec"}),
    ("hiraishin k=5 tau=3 (lossless)", {e["prompt"]: e for e in hira if e["event"] == "spec" and e["ngram"] == 0}),
    ("hiraishin k=5 tau=3 + n-gram (lossless)", {e["prompt"]: e for e in hira if e["event"] == "spec" and e["ngram"] == 3}),
])
prompts = sorted(plain)
cats = list(dict.fromkeys(cat(p) for p in prompts))


def tps(v):
    return v if isinstance(v, float) else v["tok_s"]


def q(xs, f):
    xs = sorted(xs)
    return xs[max(0, min(len(xs) - 1, int(round(f * (len(xs) - 1)))))]


print(f"# broad evaluation ({len(prompts)} prompts, Qwen3-8B Q4_K_M, RTX 5060 Laptop, 1024 tokens max, ctx 4096)\n")
gen = [plain[p]["n"] for p in prompts]
print(f"tokens generated per prompt (plain): mean {st.mean(gen):.0f}, min {min(gen)}, max {max(gen)}; "
      f"prompt lengths {min(plain[p]['n_prompt'] for p in prompts)}-{max(plain[p]['n_prompt'] for p in prompts)} tokens\n")

print("## overall\n")
print("| setup | mean tok/s | median | p10 (slow end) | worst prompt | x plain (mean of ratios) | prompts exact |")
print("|---|---:|---:|---:|---:|---:|---|")
base = setups["plain decode"]
for name, d in setups.items():
    v = [tps(d[p]) for p in prompts]
    ratio = st.mean(tps(d[p]) / base[p] for p in prompts)
    exact = "-" if name == "plain decode" else f"{sum(d[p]['matches_plain'] for p in prompts)}/{len(prompts)}"
    worst = min(prompts, key=lambda p: tps(d[p]))
    print(f"| {name} | {st.mean(v):.1f} | {st.median(v):.1f} | {q(v, 0.1):.1f} | {tps(d[worst]):.1f} ({worst}) | {ratio:.2f} | {exact} |")

print("\n## per category (mean tok/s; exact prompts in brackets)\n")
print("| category | n | " + " | ".join(setups) + " |")
print("|---|---:|" + "---:|" * len(setups))
for c in cats:
    ps = [p for p in prompts if cat(p) == c]
    cells = []
    for name, d in setups.items():
        m = st.mean(tps(d[p]) for p in ps)
        cells.append(f"{m:.1f}" if name == "plain decode" else f"{m:.1f} [{sum(d[p]['matches_plain'] for p in ps)}/{len(ps)}]")
    print(f"| {c} | {len(ps)} | " + " | ".join(cells) + " |")

print("\n## acceptance (pooled over prompts)\n")
print("| setup | accept % | tokens per target pass | n-gram cycles share |")
print("|---|---:|---:|---:|")
for name, d in list(setups.items())[1:]:
    es = [d[p] for p in prompts]
    C = sum(e["cycles"] for e in es)
    print(f"| {name} | {100 * sum(e['n_accept'] for e in es) / max(1, sum(e['n_drafted'] for e in es)):.1f} | "
          f"{(sum(e['n_accept'] for e in es) + C) / C:.2f} | {sum(e.get('n_ngram_cycles', 0) for e in es) / C:.2f} |")

same = 0
for p in prompts:
    a = open(os.path.join(D, "hira", f"plain_{p}_r1.ids")).read()
    b = open(os.path.join(D, "stock", f"plain_{p}_r1.ids")).read()
    same += a == b
print(f"\ncross-check: patched-build plain decode token ids == stock-build plain decode on {same}/{len(prompts)} prompts")
print(f"stock-build plain mean {st.mean(e['tok_s'] for e in plain_stock.values()):.1f} tok/s, "
      f"patched-build plain mean {st.mean(e['tok_s'] for e in plain.values()):.1f} tok/s")
