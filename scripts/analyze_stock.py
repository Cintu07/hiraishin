"""Parse run_stock.sh logs into a table and check speculative outputs against plain greedy.

Derived numbers (llama-speculative, chain drafting, -np 1):
  cycles            = n_predict - n_accept   (each cycle emits exactly one target-chosen token)
  accepted/cycle    = n_accept / cycles
  tokens/target pass = n_predict / cycles
Lossless check is text-level: the plain generation must be a prefix of the speculative generation
(speculative can overshoot -n by up to n_max tokens). Token ids are not printed by the stock tools.

usage: python -I scripts/analyze_stock.py <matrix dir>
"""
import glob
import os
import re
import statistics
import sys

D = sys.argv[1]


def gen_text(path):
    d = open(path, "rb").read().replace(b"\r\n", b"\n")
    i = d.find(b"</think>")
    assert i >= 0, path
    g = d[i + len(b"</think>"):]
    g = g.replace(b" [end of text]", b"")
    return g.rstrip()


def num(pat, s, cast=float):
    m = re.search(pat, s)
    return cast(m.group(1)) if m else None


rows = {}
for err in sorted(glob.glob(os.path.join(D, "*.err"))):
    tag = os.path.basename(err)[:-4]
    s = open(err, encoding="utf-8", errors="replace").read()
    kind, *rest = tag.split("_")
    if kind == "plain":
        prompt, rep = rest
        r = dict(k=0, prompt=prompt, rep=rep,
                 tps=num(r"eval time =\s*[\d.]+ ms /\s*\d+ runs.*?([\d.]+) tokens per second\)\n", s),
                 n=num(r"eval time =\s*[\d.]+ ms /\s*(\d+) runs", s, int))
    else:
        k, prompt, rep = rest
        n_pred, n_acc = num(r"n_predict = (\d+)", s, int), num(r"n_accept  = (\d+)", s, int)
        if n_pred is None or n_acc is None:
            print(f"skipping {tag}: no final stats (run was cut off)", file=sys.stderr)
            continue
        cyc = n_pred - n_acc
        r = dict(k=int(k[1:]), prompt=prompt, rep=rep, tps=num(r"decoded\s+\d+ tokens in.*speed:\s*([\d.]+)", s),
                 n=n_pred, n_drafted=num(r"n_drafted = (\d+)", s, int), n_accept=n_acc,
                 accept=num(r"accept    = ([\d.]+)%", s), cycles=cyc,
                 acc_per_cycle=n_acc / cyc, tok_per_pass=n_pred / cyc)
    if r["tps"] is None:
        print(f"skipping {tag}: no final stats (run was cut off)", file=sys.stderr)
        continue
    r["gen"] = gen_text(os.path.join(D, tag + ".out"))
    rows[tag] = r

# lossless check vs plain rep 1 of the same prompt
for tag, r in rows.items():
    ref = rows[f"plain_{r['prompt']}_r1"]["gen"]
    g = r["gen"]
    if g.startswith(ref) or (r["k"] == 0 and g == ref):
        r["match"] = "yes"
        r["div"] = None
    else:
        i = next((j for j in range(min(len(g), len(ref))) if g[j] != ref[j]), min(len(g), len(ref)))
        r["match"] = "NO"
        r["div"] = i
        r["div_ctx"] = (ref[max(0, i - 40):i + 30], g[max(0, i - 40):i + 30])

print("## per run\n")
print("| run | tok/s | n | accept % | cycles | acc/cycle | tok/pass | matches plain | first diff byte / plain len |")
print("|---|---:|---:|---:|---:|---:|---:|---|---|")
for tag, r in rows.items():
    ref_len = len(rows[f"plain_{r['prompt']}_r1"]["gen"])
    print(f"| {tag} | {r['tps']:.2f} | {r['n']} | {r.get('accept', float('nan')):.1f} | {r.get('cycles', '-')} | "
          f"{r.get('acc_per_cycle', float('nan')):.2f} | {r.get('tok_per_pass', float('nan')):.2f} | {r['match']} | "
          f"{'-' if r['div'] is None else str(r['div']) + ' / ' + str(ref_len)} |")

print("\n## per config (mean over prompts and reps; acceptance stats are deterministic per prompt)\n")
print("| config | tok/s mean | tok/s min-max | accept % | acc/cycle | tok/pass | runs matching plain |")
print("|---|---:|---:|---:|---:|---:|---|")
for k in sorted({r["k"] for r in rows.values()}):
    rs = [r for r in rows.values() if r["k"] == k]
    t = [r["tps"] for r in rs]
    line = f"| {'plain' if k == 0 else f'spec k={k}'} | {statistics.mean(t):.2f} | {min(t):.2f}-{max(t):.2f} | "
    if k:
        # pooled over tokens, not mean of ratios
        na, nd, cy, npred = (sum(r[x] for r in rs) for x in ("n_accept", "n_drafted", "cycles", "n"))
        line += f"{100 * na / nd:.1f} | {na / cy:.2f} | {npred / cy:.2f} | "
    else:
        line += "- | - | 1.00 | "
    line += f"{sum(r['match'] == 'yes' for r in rs)}/{len(rs)} |"
    print(line)

print("\n## divergences (plain vs spec, 70 bytes around first difference)\n")
for tag, r in rows.items():
    if r["match"] == "NO":
        a, b = r["div_ctx"]
        print(f"- {tag} @ byte {r['div']}\n  - plain: {a!r}\n  - spec : {b!r}")
