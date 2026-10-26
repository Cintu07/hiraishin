"""Final comparison table: plain vs stock speculative (lossy) vs patched lossless speculative.

Per-prompt speeds are averaged over reps, then the mean (and median) is taken over the 4 prompts with equal
weight. "lossless" = every run's token ids equal plain decode.
usage: python -I scripts/final_summary.py            (2026-10-24 stock vs 2026-10-25 battery final)
       python -I scripts/final_summary.py <session>  (stock_<m> and hira_<m> from one session dir)
"""
import collections
import json
import statistics as st
import sys

if len(sys.argv) > 1:
    S = sys.argv[1]
    RUNS = {f"Qwen3-8B {m}": (f"{S}/stock_{m}", f"{S}/hira_{m}") for m in ("Q4_K_M", "Q6_K")}
else:
    RUNS = {
        "Qwen3-8B Q4_K_M": ("logs/03_harness/q4km_stock", "logs/06_final/q4km_q8draft"),
        "Qwen3-8B Q6_K": ("logs/03_harness/q6k_stock", "logs/06_final/q6k_q8draft"),
    }


def load(d):
    try:
        return [json.loads(l) for l in open(f"{d}/results.jsonl", encoding="utf-8") if l.startswith("{")]
    except FileNotFoundError:
        return None


def per_prompt(es, prompts):
    return {p: st.mean(x["tok_s"] for x in es if x["prompt"] == p) for p in prompts}


def tokens_per_pass(es):
    return sum(x["n_accept"] + x["cycles"] for x in es) / sum(x["cycles"] for x in es)


for model, (stock_dir, final_dir) in RUNS.items():
    stock, final = load(stock_dir), load(final_dir)
    print(f"\n## {model}\n")
    if final is None:
        print(f"(no final run in {final_dir})")
        continue
    pl = collections.defaultdict(list)
    for e in final:
        if e["event"] == "plain":
            pl[e["prompt"]].append(e["tok_s"])
    plain = {p: st.mean(v) for p, v in pl.items()}
    base = st.mean(plain.values())
    print(f"plain greedy decode (patched build, batch 1): {base:.1f} tok/s "
          f"({', '.join(f'{p} {v:.1f}' for p, v in plain.items())})\n")

    print("| setup | k | tau | ngram | pad | tok/s (mean of 4 prompts) | median prompt | x plain | tokens per target pass | lossless runs |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    if stock:
        g = collections.defaultdict(list)
        for e in stock:
            if e["event"] == "spec":
                g[e["k"]].append(e)
        for k, es in sorted(g.items()):
            per = per_prompt(es, plain)
            tps = st.mean(per.values())
            print(f"| stock llama.cpp spec (lossy) | {k} | 0 | 0 | 0 | {tps:.1f} | {st.median(per.values()):.1f} | "
                  f"{tps / base:.2f} | {tokens_per_pass(es):.2f} | {sum(x['matches_plain'] for x in es)}/{len(es)} |")
    g = collections.defaultdict(list)
    for e in final:
        if e["event"] == "spec":
            g[(e["k"], e.get("tau", 0), e.get("ngram", 0), e.get("pad_verify", 0))].append(e)
    best = None
    for (k, tau, ng, pv), es in sorted(g.items()):
        per = per_prompt(es, plain)
        tps = st.mean(per.values())
        ok = sum(x["matches_plain"] for x in es)
        print(f"| hiraishin lossless | {k} | {tau:g} | {ng} | {pv} | {tps:.1f} | {st.median(per.values()):.1f} | "
              f"{tps / base:.2f} | {tokens_per_pass(es):.2f} | {ok}/{len(es)} |")
        if ok == len(es) and (best is None or tps > best[0]):
            best = (tps, k, tau, ng, pv, per)
    if best:
        tps, k, tau, ng, pv, per = best
        print(f"\nbest single lossless setting: k={k} tau={tau:g} ngram={ng} pad_verify={pv}: {tps:.1f} tok/s mean "
              f"({', '.join(f'{p} {v:.1f}' for p, v in per.items())})")
    inv = [e for e in final if e["event"] == "invariance"]
    if inv:
        print(f"invariance: {sum(e['argmax_mismatches'] for e in inv)} argmax flips, "
              f"max |dlogit| {max(e['max_abs_dlogit_top1'] for e in inv):.6f} over {len(inv)} (prompt, B) checks")
