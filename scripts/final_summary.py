"""Final comparison table: plain vs stock speculative (lossy) vs patched lossless speculative.

Means are over the 4 prompts (equal weight per prompt). "lossless" = every run's token ids equal plain decode.
usage: python -I scripts/final_summary.py
"""
import collections
import json
import statistics as st

RUNS = {
    "Qwen3-8B Q4_K_M": ("logs/03_harness/q4km_stock", "logs/06_final/q4km_q8draft"),
    "Qwen3-8B Q6_K": ("logs/03_harness/q6k_stock", "logs/06_final/q6k_q8draft"),
}


def load(d):
    try:
        return [json.loads(l) for l in open(f"{d}/results.jsonl", encoding="utf-8") if l.startswith("{")]
    except FileNotFoundError:
        return None


for model, (stock_dir, final_dir) in RUNS.items():
    stock, final = load(stock_dir), load(final_dir)
    print(f"\n## {model}\n")
    if final is None:
        print(f"(no final run in {final_dir})")
        continue
    plain = {e["prompt"]: e["tok_s"] for e in final if e["event"] == "plain" and e["rep"] == 1}
    print(f"plain greedy decode (patched build, batch 1): {st.mean(plain.values()):.1f} tok/s "
          f"({', '.join(f'{p} {v:.1f}' for p, v in plain.items())})\n")

    print("| setup | k | tau | tok/s (mean of 4 prompts) | x plain | tokens per target pass | lossless runs |")
    print("|---|---:|---:|---:|---:|---:|---|")
    if stock:
        sp = {e["prompt"]: e["tok_s"] for e in stock if e["event"] == "plain" and e["rep"] == 1}
        g = collections.defaultdict(list)
        for e in stock:
            if e["event"] == "spec":
                g[e["k"]].append(e)
        for k, es in sorted(g.items()):
            tps = st.mean(st.mean(x["tok_s"] for x in es if x["prompt"] == p) for p in sp)
            tpp = sum(x["n_accept"] + x["cycles"] for x in es) / sum(x["cycles"] for x in es)
            print(f"| stock llama.cpp spec (lossy) | {k} | 0 | {tps:.1f} | {tps / st.mean(sp.values()):.2f} | {tpp:.2f} | "
                  f"{sum(x['matches_plain'] for x in es)}/{len(es)} |")
    g = collections.defaultdict(list)
    for e in final:
        if e["event"] == "spec":
            g[(e["k"], e["tau"])].append(e)
    best = None
    for (k, tau), es in sorted(g.items()):
        tps = st.mean(x["tok_s"] for x in es)
        tpp = sum(x["n_accept"] + x["cycles"] for x in es) / sum(x["cycles"] for x in es)
        ok = sum(x["matches_plain"] for x in es)
        print(f"| hiraishin lossless | {k} | {tau:g} | {tps:.1f} | {tps / st.mean(plain.values()):.2f} | {tpp:.2f} | {ok}/{len(es)} |")
        if ok == len(es) and (best is None or tps > best[0]):
            best = (tps, k, tau, es)
    if best:
        tps, k, tau, es = best
        print(f"\nbest single lossless setting: k={k} tau={tau:g}: {tps:.1f} tok/s mean "
              f"({', '.join(f'{x['prompt']} {x['tok_s']:.1f}' for x in es)})")
    inv = [e for e in final if e["event"] == "invariance"]
    if inv:
        print(f"invariance: {sum(e['argmax_mismatches'] for e in inv)} argmax flips, "
              f"max |dlogit| {max(e['max_abs_dlogit_top1'] for e in inv):.6f} over {len(inv)} (prompt, B) checks")
