"""Benchmark charts for the X post, read straight from the saved logs (no hand-typed numbers).

usage: [THEME=beige] <python with matplotlib> scripts/make_charts.py   -> docs/x/*.png
Data: logs/14_final_v3 (one session: plain, stock speculative, hiraishin lossless) and the verify-cost sweeps.
Palette: dataviz reference palette. Orange/aqua/blue validated adjacent on both surfaces; gray is the neutral
baseline (plain decode), not a categorical hue. Every bar and line end carries its value as text.
"""
import collections
import json
import os
import statistics as st

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "docs", "x")
os.makedirs(OUT, exist_ok=True)

if os.environ.get("THEME") == "beige":
    SURFACE, INK, INK2, MUTED, GRID, BASE = "#f3ecdd", "#0b0b0b", "#52514e", "#7a756b", "#e3d9c6", "#c9bda5"
    BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#9d978b"
else:
    SURFACE, INK, INK2, MUTED, GRID, BASE = "#1a1a19", "#f0efec", "#c3c2b7", "#898781", "#2c2c2a", "#383835"
    BLUE, ORANGE, AQUA, GRAY = "#3987e5", "#d95926", "#199e70", "#6f6e69"
ON_FILL = "#ffffff"  # label inside a categorical fill

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 15,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": BASE, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": MUTED,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "legend.frameon": False, "legend.labelcolor": INK2,
})


def load(rel):
    with open(os.path.join(ROOT, rel, "results.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.startswith("{")]


def header(fig, title, sub):
    fig.text(0.05, 0.94, title, fontsize=24, fontweight="bold", color=INK, va="top")
    fig.text(0.05, 0.875, sub, fontsize=14, color=INK2, va="top")
    fig.text(0.95, 0.03, "hiraishin", fontsize=12, color=MUTED, ha="right")


def per_prompt(es):
    acc = collections.defaultdict(list)
    for e in es:
        acc[e["prompt"]].append(e["tok_s"])
    return {p: st.mean(v) for p, v in acc.items()}


S = "logs/14_final_v3"
K, TAU = 5, 3  # the final setting (logs/14_final_v3/summary.md)
models = [("Q4_K_M", "Qwen3-8B Q4_K_M"), ("Q6_K", "Qwen3-8B Q6_K")]


def spec(ev, ng):
    return [e for e in ev if e["event"] == "spec" and e["k"] == K and e["tau"] == TAU and e["ngram"] == ng]


# ---------------------------------------------------------------- chart 1: tok/s per model
rows = []
for m, label in models:
    stock, hira = load(f"{S}/stock_{m}"), load(f"{S}/hira_{m}")
    plain = st.mean(per_prompt([e for e in hira if e["event"] == "plain"]).values())
    sk = [e for e in stock if e["event"] == "spec"]
    h0, h3 = spec(hira, 0), spec(hira, 3)
    prompts_exact = lambda es: (len({e["prompt"] for e in es if e["matches_plain"]} -
                                    {e["prompt"] for e in es if not e["matches_plain"]}), len({e["prompt"] for e in es}))
    rows.append((label, [
        (plain, None),
        (st.mean(per_prompt(sk).values()), prompts_exact(sk)),
        (st.mean(per_prompt(h0).values()), prompts_exact(h0)),
        (st.mean(per_prompt(h3).values()), prompts_exact(h3)),
    ]))

series = [("plain decode", GRAY), ("stock llama.cpp speculative", ORANGE),
          ("hiraishin, draft model (lossless)", AQUA), ("hiraishin, draft model + n-gram (lossless)", BLUE)]
fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
fig.subplots_adjust(left=0.07, right=0.95, top=0.72, bottom=0.12)
w, gap = 0.2, 0.015
for xi, (label, vals) in enumerate(rows):
    for si, ((name, color), (v, ex)) in enumerate(zip(series, vals)):
        x = xi + (si - 1.5) * (w + gap)
        ax.bar(x, v, w, color=color, label=name if xi == 0 else None, zorder=3)
        ax.text(x, v + 1.5, f"{v:.1f}", ha="center", va="bottom", fontsize=16, fontweight="bold", color=INK)
        if ex:
            ax.text(x, 3, f"{ex[0]}/{ex[1]}\nexact", ha="center", va="bottom", fontsize=13, color=ON_FILL, zorder=4)
ax.set_xticks(range(len(rows)), [r[0] for r in rows], fontsize=17, color=INK)
ax.set_ylabel("tokens / second")
ax.set_ylim(0, max(v for _, vals in rows for v, _ in vals) * 1.16)
ax.grid(axis="x", visible=False)
ax.tick_params(axis="x", length=0)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.12), ncol=2, fontsize=14)
header(fig, "Lossless speculative decoding on an 8 GB laptop GPU",
       f"RTX 5060 Laptop · greedy · 4 prompts × 256 tokens, mean · one session · draft Qwen3-0.6B Q8_0 · "
       f"stock k=8, hiraishin k={K} with adaptive stop\n\"exact\" = prompts whose output is token-for-token identical to plain decoding")
fig.savefig(os.path.join(OUT, "1_toks_per_model.png"))
plt.close(fig)

# ---------------------------------------------------------------- chart 2: per prompt, Q4_K_M
hira = load(f"{S}/hira_Q4_K_M")
plain = per_prompt([e for e in hira if e["event"] == "plain"])
m0, m3 = per_prompt(spec(hira, 0)), per_prompt(spec(hira, 3))
prompts = list(plain)
fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
fig.subplots_adjust(left=0.07, right=0.95, top=0.72, bottom=0.12)
w = 0.26
for si, (name, color, data) in enumerate([("plain decode", GRAY, plain),
                                          ("hiraishin, draft model", AQUA, m0),
                                          ("hiraishin, draft model + n-gram", BLUE, m3)]):
    for xi, p in enumerate(prompts):
        x = xi + (si - 1) * (w + 0.015)
        ax.bar(x, data[p], w, color=color, label=name if xi == 0 else None, zorder=3)
        ax.text(x, data[p] + 1.5, f"{data[p]:.0f}", ha="center", va="bottom", fontsize=15, fontweight="bold", color=INK,
                zorder=5, bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE, edgecolor="none"))
ax.axhline(100, color=INK2, linewidth=2, linestyle=(0, (6, 4)), zorder=2)
ax.text(-0.45, 101.5, "100 tok/s", ha="left", va="bottom", fontsize=14, color=INK2)
ax.set_xticks(range(len(prompts)), prompts, fontsize=17, color=INK)
ax.set_ylabel("tokens / second")
ax.set_ylim(0, max(m3.values()) * 1.12)
ax.grid(axis="x", visible=False)
ax.tick_params(axis="x", length=0)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.12), ncol=3, fontsize=14)
header(fig, "Qwen3-8B Q4_K_M: over 100 tok/s on average, lossless",
       f"RTX 5060 Laptop (8 GB) · greedy · 256 tokens per prompt · k={K}, adaptive stop tau={TAU} · mean of 2 runs\n"
       f"mean: plain {st.mean(plain.values()):.1f}, draft model {st.mean(m0.values()):.1f}, + n-gram {st.mean(m3.values()):.1f} tok/s · "
       "every output token-for-token identical to plain decoding")
fig.savefig(os.path.join(OUT, "2_per_prompt_q4km.png"))
plt.close(fig)


# ---------------------------------------------------------------- chart 3: verify cost vs batch size
def vc_curve(rel, model="target"):
    c = collections.defaultdict(list)
    for e in load(rel):
        if e["event"] == "verify_cost" and e["model"] == model:
            c[e["B"]].append(e["ms_median"])
    b1 = st.mean(c[1])
    return {b: st.mean(v) / b1 for b, v in sorted(c.items()) if b <= 9}


curves = [
    ("stock (switches to MMQ, not exact)", ORANGE, vc_curve("logs/03_harness/q4km_stock")),
    ("batch-invariant, generic mat-vec (exact)", AQUA, vc_curve("logs/05_bi_kernel/v3_Q4_K_M/generic")),
    ("batch-invariant, hiraishin kernel (exact)", BLUE, vc_curve("logs/05_bi_kernel/v4_minblocks4_Q4_K_M/rows4")),
]
fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
fig.subplots_adjust(left=0.08, right=0.80, top=0.74, bottom=0.12)
for name, color, c in curves:
    bs, ys = list(c), list(c.values())
    ax.plot(bs, ys, color=color, linewidth=2.5, marker="o", markersize=9, markeredgecolor=SURFACE,
            markeredgewidth=2, label=name, zorder=3)
    ax.text(bs[-1] + 0.15, ys[-1], f"{ys[-1]:.2f}x", va="center", fontsize=15, fontweight="bold", color=INK)
ax.axhline(1, color=BASE, linewidth=1.5, zorder=1)
ax.grid(axis="x", visible=False)
ax.set_xticks(range(1, 10))
ax.set_xlabel("tokens verified in one target pass (B)")
ax.set_ylabel("time vs a single-token pass (×)")
ax.set_xlim(0.7, 9.8)
ax.set_ylim(0.7, max(max(c.values()) for _, _, c in curves) * 1.08)
ax.legend(loc="upper left", fontsize=14)
header(fig, "The price of exact verification, and a kernel to pay less of it",
       "Qwen3-8B Q4_K_M · RTX 5060 Laptop · target forward pass, all logits returned, median of 15\n"
       "exact = logits bit-identical to decoding each token alone")
fig.savefig(os.path.join(OUT, "3_verify_cost_q4km.png"))
plt.close(fig)

print("wrote", sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
