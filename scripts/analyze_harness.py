"""Turn spec_harness results.jsonl into markdown tables.

usage: python -I scripts/analyze_harness.py <run dir> [<stock matrix dir for text cross-check>]
"""
import collections
import json
import os
import statistics as st
import sys

D = sys.argv[1]
ev = [json.loads(l) for l in open(os.path.join(D, "results.jsonl"), encoding="utf-8") if l.startswith("{")]
by = collections.defaultdict(list)
for e in ev:
    by[e["event"]].append(e)

out = []
p = out.append
info = open(os.path.join(D, "run_info.txt"), encoding="utf-8").read().strip()
p("```\n" + info + "\n```\n")

p("## plain greedy decode (batch 1)\n")
p("| prompt | n | tok/s | median step ms | rep-to-rep identical |")
p("|---|---:|---:|---:|---|")
for e in by["plain"]:
    p(f"| {e['prompt']} r{e['rep']} | {e['n']} | {e['tok_s']:.2f} | {e['step_ms_median']:.2f} | {e['same_as_rep1']} |")
plain_tps = {e["prompt"]: e["tok_s"] for e in by["plain"] if e["rep"] == 1}
plain_step = {e["prompt"]: e["step_ms_median"] for e in by["plain"] if e["rep"] == 1}

p("\n## speculative (chain, greedy) per prompt\n")
p("| k | tau | prompt | tok/s | speedup | accept % | acc/cycle | tok/pass | ms/cycle | draft % | verify % | argmax % | kv % | other % | matches plain | first diff (plain top1-top2 margin) |")
p("|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
for e in by["spec"]:
    T = e["ms_total"]
    c = e["cycles"]
    draft = e["ms_draft_gpu"] + e["ms_draft_cpu"]
    argm = e["ms_verify_cpu"]
    diff = "-" if e["matches_plain"] else f"tok {e['first_diff']} ({e['plain_margin_at_diff']:.4f})"
    p(f"| {e['k']} | {e.get('tau', 0):g} | {e['prompt']} | {e['tok_s']:.2f} | {e['tok_s'] / plain_tps[e['prompt']]:.2f}x | "
      f"{100 * e['n_accept'] / e['n_drafted']:.1f} | {e['n_accept'] / c:.2f} | {(e['n_accept'] + c) / c:.2f} | {T / c:.2f} | "
      f"{100 * draft / T:.1f} | {100 * e['ms_verify_gpu'] / T:.1f} | {100 * argm / T:.1f} | {100 * e['ms_kv'] / T:.1f} | "
      f"{100 * e['ms_other'] / T:.1f} | {'yes' if e['matches_plain'] else 'NO'} | {diff} |")

p("\n## speculative per k (pooled over prompts)\n")
p("| k | tau | ngram | tok/s (mean of prompts) | accept % | acc/cycle | tok/pass | draft ms/cycle | verify ms/cycle | other+kv+argmax ms/cycle | runs matching plain |")
p("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
for k, tau, ng in sorted({(e["k"], e.get("tau", 0), e.get("ngram", 0)) for e in by["spec"]}):
    es = [e for e in by["spec"] if e["k"] == k and e.get("tau", 0) == tau and e.get("ngram", 0) == ng]
    C = sum(e["cycles"] for e in es)
    na = sum(e["n_accept"] for e in es)
    nd = sum(e["n_drafted"] for e in es)
    dr = sum(e["ms_draft_gpu"] + e["ms_draft_cpu"] for e in es) / C
    vf = sum(e["ms_verify_gpu"] for e in es) / C
    ot = sum(e["ms_other"] + e["ms_kv"] + e["ms_verify_cpu"] for e in es) / C
    p(f"| {k} | {tau:g} | {ng} | {st.mean(e['tok_s'] for e in es):.2f} | {100 * na / nd:.1f} | {na / C:.2f} | {(na + C) / C:.2f} | "
      f"{dr:.2f} | {vf:.2f} | {ot:.2f} | {sum(e['matches_plain'] for e in es)}/{len(es)} |")

if by["verify_cost"]:
    p("\n## forward pass cost vs batch size (median of 15, all logits returned)\n")
    p("| model | B | ms (mean over prompts' depths) | x B=1 | ms per token |")
    p("|---|---:|---:|---:|---:|")
    vc = collections.defaultdict(list)
    for e in by["verify_cost"]:
        vc[(e["model"], e["B"])].append(e["ms_median"])
    base = {m: st.mean(vc[(m, 1)]) for m in {k[0] for k in vc}}
    for (m, B), v in sorted(vc.items()):
        p(f"| {m} | {B} | {st.mean(v):.3f} | {st.mean(v) / base[m]:.3f} | {st.mean(v) / B:.3f} |")
    depths = sorted({e["depth"] for e in by["verify_cost"]})
    p(f"\ndepths used: {depths}")

if by["invariance"]:
    p("\n## batch invariance: plain sequence re-fed in windows of B (teacher forcing)\n")
    p("| prompt | B | positions | argmax flips vs batch-1 | first flip at | max abs diff of top-1 logit | min plain margin at a flip |")
    p("|---|---:|---:|---:|---:|---:|---:|")
    for e in by["invariance"]:
        p(f"| {e['prompt']} | {e['B']} | {e['positions']} | {e['argmax_mismatches']} | {e['first_mismatch']} | "
          f"{e['max_abs_dlogit_top1']:.6f} | {e['min_plain_margin_at_mismatch']:.6f} |")

if len(sys.argv) > 2:
    p("\n## cross-check: harness plain text vs stock llama-completion (Windows prebuilt)\n")
    for name in plain_tps:
        a = open(os.path.join(D, f"plain_{name}_r1.txt"), "rb").read().replace(b"\r\n", b"\n").strip()
        so = os.path.join(sys.argv[2], f"plain_{name}_r1.out")
        if not os.path.exists(so):
            p(f"- {name}: no stock log")
            continue
        b = open(so, "rb").read().replace(b"\r\n", b"\n")
        b = b[b.find(b"</think>") + 8:].replace(b" [end of text]", b"").strip()
        n = min(len(a), len(b))
        i = next((j for j in range(n) if a[j] != b[j]), n)
        p(f"- {name}: {'identical' if a == b else f'differs at byte {i} of {len(b)} (harness len {len(a)})'}")

print("\n".join(out))
