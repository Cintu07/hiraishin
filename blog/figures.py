"""Figures for blog/hiraishin.md, drawn with figkit (engineering-drawing style, to scale where it shows time or size).

every number is read from, or computed from, the log named in the figure's title block.
usage: <python with matplotlib> blog/figures.py [01 02 ...]   -> blog/img/fig_*.png (+ .svg)
"""
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "figkit"))
from figkit import C, Sheet as _Sheet  # noqa: E402

# FIGMAP=01:01,08:06 renumbers figures for a post that uses a subset; cross references inside figures follow it
FIGMAP = dict(x.split(":") for x in os.environ.get("FIGMAP", "").split(",") if x)
ref = lambda n: FIGMAP.get(n, n)


def Sheet(fig, *a, **k):
    return _Sheet(ref(fig), *a, **k)

THEME = os.environ.get("FIGKIT_THEME", "drafting")
OUT = os.path.join(HERE, "img") if THEME == "drafting" else os.path.join(HERE, "img", THEME)
os.makedirs(OUT, exist_ok=True)


def load(rel, name="results.jsonl"):
    path = os.path.join(ROOT, rel, name) if not rel.endswith(".jsonl") else os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.startswith("{")]


def verify_cost(rel, model="target"):
    acc = {}
    for e in load(rel):
        if e["event"] == "verify_cost" and e["model"] == model:
            acc.setdefault(e["B"], []).append(e["ms_median"])
    return {b: st.mean(v) for b, v in sorted(acc.items())}


def fig01():
    vc = verify_cost("logs/03_harness/q4km_stock")
    s = Sheet("01", "every token pays for a full read of the weights",
              "one forward pass of qwen3-8b q4_k_m on an rtx 5060 laptop, drawn to scale", "logs/03_harness/q4km_stock",
              ["stock build", "median of 15 passes", "all logits returned"])
    x0, px = 110, 38.0
    stream = 4.672 / 286 * 1000
    y = 225
    s.text(x0, y, "streaming 4.67 gb of weights at ~286 gb/s", size=14, weight="medium")
    s.part(x0, y + 18, stream * px, 40, "weights in flight", material="weights", size=13)
    s.dim(x0, y + 76, x0 + stream * px, y + 76, f"{stream:.1f} ms")
    s.balloon(x0 + stream * px + 40, y + 38, 1, to=(x0 + stream * px - 3, y + 38))
    for i, b in enumerate((1, 2, 3)):
        yy = 365 + i * 112
        s.text(x0, yy, f"{b} token{'s' if b > 1 else ''} in one pass", size=14, weight="medium")
        s.part(x0, yy + 18, vc[b] * px, 40, None, material="plain" if b == 1 else "compute")
        extra = "" if b == 1 else f"   +{vc[b] - vc[1]:.1f} ms"
        s.dim(x0, yy + 76, x0 + vc[b] * px, yy + 76, f"{vc[b]:.2f} ms{extra}")
        s.balloon(x0 + vc[b] * px + 40, yy + 38, b + 1, to=(x0 + vc[b] * px - 3, yy + 38))
    s.ruler(x0, 718, 25 * px, 25, 5, px, "ms", minor=1)
    s.notes(1040, 330, [
        (1, f"4.672 gb / 286 gb/s = {stream:.1f} ms.\nthe bus is the speed limit."),
        (2, "a pass with one token: the read,\nplus the math, plus copying logits out."),
        (3, f"a 2nd token in the same pass costs\n{vc[2] - vc[1]:.1f} ms more ({100 * (vc[2] / vc[1] - 1):.0f}%). this is the loophole."),
        (4, f"a 3rd one costs more: the kernel\nfor 3 columns is slower (fig. {ref('08')})."),
    ], w=500)
    s.save(os.path.join(OUT, "fig_01_read.png"))


def fig02():
    s = Sheet("02", "one speculative cycle", "a small model guesses ahead, the big model checks every guess in one pass",
              "schematic", ["greedy decoding", "k = 5 guesses"])
    x0, cw, gap = 110, 136, 12
    guesses = ["the", "cache", "is", "slow", "now"]
    picks = ["the", "cache", "is", "full", "and"]
    s.text(x0, 222, "1   the draft model (0.6b) guesses 5 tokens, one at a time", size=14, weight="medium")
    for i, w in enumerate(guesses):
        s.part(x0 + i * (cw + gap), 240, cw, 52, w, material="draft", size=15)
    s.dim(x0, 312, x0 + 5 * cw + 4 * gap, 312, "~3.6 ms per guess", size=11)
    s.text(x0, 372, "2   the target (8b) reads its weights once and scores all 6 positions", size=14, weight="medium")
    s.part(x0, 390, 6 * cw + 5 * gap, 52, "one forward pass, batch of 6", material="weights", size=15)
    s.dim(x0, 462, x0 + 6 * cw + 5 * gap, 462, "~19 ms", size=11)
    s.text(x0, 522, "3   at each position, keep the guess only if it equals the target's own pick", size=14, weight="medium")
    for i, w in enumerate(picks):
        mat = "ok" if i < 3 else ("bad" if i == 3 else "none")
        s.part(x0 + i * (cw + gap), 540, cw, 52, w, material=mat, size=15)
        if i < 4:
            s.mark(x0 + i * (cw + gap) + cw / 2, 618, ok=i < 3)
    s.text(x0 + 4 * (cw + gap) + cw / 2, 618, "unused", size=11, ha="center", mono=True, color="soft")
    s.dim(x0, 662, x0 + 4 * cw + 3 * gap, 662, "out: the cache is full", size=12)
    s.notes(1040, 230, [
        (1, "guesses are cheap: the draft model\nhas 14x fewer parameters."),
        (2, f"checking 6 positions costs about\nwhat checking 1 costs (fig. {ref('01')})."),
        (3, "3 guesses match, then the target's\nown pick \"full\" replaces \"slow\"."),
        (4, "4 tokens for one read of the weights.\nevery one is what the target would\nhave said on its own."),
    ], w=500)
    s.save(os.path.join(OUT, "fig_02_cycle.png"))


def fig03():
    s = Sheet("03", "same numbers, different order, different answer",
              "fp32 addition depends on order, and a gpu kernel's order depends on how it splits the work",
              "schematic, mmvq.cu calc_nwarps (generic table)", ["fp32", "q4_k / q6_k mat-vec"])
    x0 = 110
    s.text(x0, 222, "three numbers, two orders", size=14, weight="medium")
    s.part(x0, 240, 520, 60, "(100000000 + 1) - 100000000  =  0", material="bad", size=15, mono=True)
    s.part(x0, 320, 520, 60, "(100000000 - 100000000) + 1  =  1", material="ok", size=15, mono=True)
    s.balloon(x0 + 560, 270, 1, to=(x0 + 523, 270))
    s.text(820, 222, "one dot product of a mat-vec, k split into 8 chunks", size=14, weight="medium")
    warp_mat = ["weights", "bad", "ok", "kv"]
    for r, (nw, label) in enumerate(((4, "1 to 4 tokens per pass: 4 warps"), (2, "5 to 8 tokens per pass: 2 warps"))):
        y = 262 + r * 170
        s.text(820, y, label, size=13, color="soft")
        for c in range(8):
            s.part(820 + c * 86, y + 16, 78, 50, f"c{c}", material=warp_mat[c % nw], size=13, mono=True)
        groups = " + ".join("(" + "+".join(f"c{c}" for c in range(w, 8, nw)) + ")" for w in range(nw))
        s.text(820, y + 92, groups, size=12, mono=True)
        s.balloon(820 + 8 * 86 + 30, y + 41, 2 + r, to=(820 + 8 * 86 - 5, y + 41))
    s.notes(110, 470, [
        (1, "near 1e8 an fp32 number can only step by 8,\nso the +1 is lost if it is added to the big number first."),
        (2, "each color is one warp. a warp adds its own chunks,\nthen the warps are added together."),
        (3, "with more tokens per pass the kernel uses fewer warps.\nsame chunks, different grouping, different rounding."),
    ], w=600)
    s.save(os.path.join(OUT, "fig_03_order.png"))


def fig04():
    s = Sheet("04", "the 256 boundary", "llama.cpp attends over n_kv = round_up(last position + 1, 256) cells",
              "llama-kv-cache.cpp get_n_kv", ["cells drawn to scale"])
    x0, step = 140, 70
    y = 270
    s.text(110, 222, "kv positions", size=14, weight="medium")
    s.line([(x0 - 30, y), (x0 + 16 * step, y)], lw=1.2)
    for i, p in enumerate(range(248, 265)):
        x = x0 + i * step
        s.line([(x, y - 8), (x, y + 8)], lw=1.0)
        s.text(x, y + 26, str(p), size=11, ha="center", mono=True, color="soft")
    bx = x0 + 7.5 * step
    s.line([(bx, 225), (bx, 340)], color="red", lw=2.2)
    s.text(bx, 214, "256 cells | 512 cells", size=12, ha="center", mono=True, color="red")
    for i, p in enumerate(range(254, 258)):
        s.part(x0 + (p - 248) * step - 20, y + 48, 40, 26, None, material="kv")
    s.text(x0 + 6 * step - 20, y + 92, "a verify batch at 254 to 257", size=12, mono=True, color="soft")
    px = 1.6
    s.text(110, 440, "token 255 decoded alone", size=14, weight="medium")
    s.part(110, 458, 256 * px, 40, "attends over 256 cells", material="ok", size=13)
    s.dim(110, 516, 110 + 256 * px, 516, "256")
    s.text(110, 572, "token 255 inside that batch", size=14, weight="medium")
    s.part(110, 590, 512 * px, 40, "attends over 512 cells, the rest masked", material="bad", size=13)
    s.dim(110, 648, 110 + 512 * px, 648, "512")
    s.balloon(110 + 512 * px + 40, 610, 1, to=(110 + 512 * px - 3, 610))
    s.notes(1060, 420, [
        (1, f"a longer range can change how many\nblocks attention splits it into (fig. {ref('05')}).\nthe masked cells themselves add zero."),
        (2, "fix: a verify batch never crosses a\nmultiple of 256. cut it at 255,\nstart the next one at 256."),
    ], w=470)
    s.save(os.path.join(OUT, "fig_04_kvpad.png"))


def fig05():
    s = Sheet("05", "the bug that waited for position 384",
              "attention sums the kv cache in parallel blocks, and the block count comes from gpu occupancy",
              "logs/03_harness/debug_rewrite", ["first logit diff at kv 390", "block counts illustrative"])
    x0, px = 110, 1.75
    tiles = [(0, 127), (128, 255), (256, 383), (384, 511)]
    mats = ["weights", "bad", "ok", "kv"]
    rows = [("1 query kernel", [0, 1, 2, 3]), ("2 query kernel", [0, 1, 2, 0])]
    for r, (name, blocks) in enumerate(rows):
        y = 250 + r * 130
        s.text(x0, y - 22, f"{name}: tile > block", size=14, weight="medium")
        for t, (a, b) in enumerate(tiles):
            s.part(x0 + a * px, y, 128 * px, 50, f"tile {t} > block {blocks[t]}", material=mats[blocks[t]], size=12)
    s.arrow(x0 + 448 * px, 440, x0 + 64 * px, 440, color="blue", rad=-0.12, lw=1.2)
    s.text(x0 + 10, 520, "tile 3 is folded into block 0's running sum", size=12, color="blue")
    s.ruler(x0, 580, 512 * px, 512, 128, px, "kv cell", minor=32)
    for q, ok, n in ((300, True, 1), (390, False, 2)):
        x = x0 + q * px
        s.line([(x, 236), (x, 580)], color="green" if ok else "red", lw=1.4, ls=(0, (5, 4)), z=4)
        s.balloon(x, 650 if ok else 700, n)
        s.text(x + 24, 650 if ok else 700, f"query at {q}", size=12, mono=True, color="green" if ok else "red")
    s.notes(1060, 300, [
        (1, "query at 300: tile 3 lies past it and\nis fully masked. it adds nothing, so\nboth splits give the same sum."),
        (2, "query at 390: tile 3 holds real cells.\nfolding it into block 0 changes the\norder of the sum."),
        (3, "fix: a batched launch sizes its split\nwith the 1 query kernel's occupancy."),
    ], w=470)
    s.save(os.path.join(OUT, "fig_05_occupancy.png"))


def fig06():
    old = {e["B"]: e["ms_median"] for e in load("logs/11_graph_probe/probe_per_b.jsonl") if e["pattern"] == "fixed"}
    old_v = {e["B"]: e["ms_median"] for e in load("logs/11_graph_probe/probe_per_b.jsonl") if e["pattern"] == "varying"}
    new_v = {e["B"]: e["ms_median"] for e in load("logs/11_graph_probe/probe_per_b_keyfix.jsonl") if e["pattern"] == "varying"}
    s = Sheet("06", "one cache slot for every shape",
              "cuda graphs are cached by the address of the graph's first node, which llama.cpp reuses for every batch size",
              "logs/11_graph_probe", ["q4_k_m target", "median per batch size"])
    x0 = 110
    s.text(x0, 222, "stock key", size=15, weight="bold", color="red")
    for i, b in enumerate((3, 5)):
        s.part(x0, 245 + i * 70, 200, 50, f"verify {b} tokens", material="plain", size=13)
        s.arrow(x0 + 200, 270 + i * 70, x0 + 290, 300, color="red")
    s.part(x0 + 290, 270, 230, 60, "key = 0x7f..a0", material="bad", size=14, mono=True)
    s.arrow(x0 + 520, 300, x0 + 570, 300)
    s.part(x0 + 570, 270, 250, 60, "1 graph, re-captured", material="plain", size=13, sub="on every size change")
    s.text(x0, 450, "per shape key", size=15, weight="bold", color="green")
    for i, b in enumerate((3, 4, 5)):
        y = 470 + i * 64
        s.part(x0, y, 200, 48, f"verify {b} tokens", material="plain", size=13)
        s.arrow(x0 + 200, y + 24, x0 + 290, y + 24)
        s.part(x0 + 290, y, 230, 48, f"key = (0x7f..a0, {b})", material="ok", size=13, mono=True)
        s.arrow(x0 + 520, y + 24, x0 + 570, y + 24)
        s.part(x0 + 570, y, 250, 48, f"graph for {b}, kept", material="plain", size=13)
    tx = 990
    s.text(tx, 222, "measured cost per verify call (ms)", size=13, weight="medium")
    hdr = ["tokens", "same size", "size changes", "size changes"]
    sub = ["", "every call", "stock key", "shape key"]
    cols = [tx, tx + 90, tx + 225, tx + 375]
    for c, h, sb in zip(cols, hdr, sub):
        s.text(c, 254, h, size=11, mono=True, color="soft")
        s.text(c, 272, sb, size=11, mono=True, color="soft")
    s.line([(tx, 286), (tx + 490, 286)], color="faint", lw=0.8)
    for r, b in enumerate((2, 3, 4, 5)):
        yy = 310 + r * 32
        s.text(cols[0] + 20, yy, str(b), size=13, mono=True)
        s.text(cols[1], yy, f"{old[b]:.1f}", size=13, mono=True)
        s.text(cols[2], yy, f"{old_v[b]:.1f}", size=13, mono=True, color="red")
        s.text(cols[3], yy, f"{new_v[b]:.1f}", size=13, mono=True, color="green")
    s.notes(tx, 470, [
        (1, "adaptive drafting changes the verify\nsize almost every cycle."),
        (2, "end to end, the shape key took the\nlossless setup from 98.8 to 102.9 tok/s."),
    ], w=420)
    s.save(os.path.join(OUT, "fig_06_graphs.png"))


def fig07():
    ev = [e for e in load("logs/15_eval/hira") if e["event"] == "spec" and e["ngram"] == 0]
    pl = [e for e in load("logs/15_eval/hira") if e["event"] == "plain"]
    cyc = sum(e["cycles"] for e in ev)
    draft = sum(e["ms_draft_gpu"] + e["ms_draft_cpu"] for e in ev) / cyc
    verify = sum(e["ms_verify_gpu"] for e in ev) / cyc
    rest = sum(e["ms_other"] + e["ms_kv"] + e["ms_verify_cpu"] for e in ev) / cyc
    tpp = (sum(e["n_accept"] for e in ev) + cyc) / cyc
    step = st.mean(e["step_ms_median"] for e in pl)
    total = draft + verify + rest
    s = Sheet("07", "where one speculative cycle goes", "mean over every cycle of the 45 prompt eval, drawn to scale",
              "logs/15_eval/hira", ["k = 5, adaptive stop", f"{cyc} cycles"])
    x0, px = 110, 32.0
    y = 250
    s.text(x0, y - 24, "one speculative cycle", size=15, weight="bold")
    x = x0
    for name, ms, mat in (("draft", draft, "draft"), ("verify", verify, "weights"), ("", rest, "compute")):
        s.part(x, y, ms * px, 56, name or None, material=mat, size=14)
        if name:
            s.dim(x, y + 78, x + ms * px, y + 78, f"{ms:.2f} ms", size=11)
        x += ms * px
    s.balloon(x + 36, y + 28, 1, to=(x - 3, y + 28))
    s.dim(x0, y + 128, x0 + total * px, y + 128, f"{total:.1f} ms for {tpp:.2f} tokens", size=13)
    y2 = 470
    s.text(x0, y2 - 24, f"the same {tpp:.2f} tokens, decoded plainly", size=15, weight="bold")
    n_full = int(tpp)
    for k in range(n_full):
        s.part(x0 + k * step * px, y2, step * px, 56, f"token {k + 1}", material="plain", size=13)
    s.part(x0 + n_full * step * px, y2, (tpp - n_full) * step * px, 56, f"{tpp - n_full:.2f}", material="plain",
           size=12, mono=True)
    s.dim(x0, y2 + 78, x0 + tpp * step * px, y2 + 78, f"{tpp * step:.1f} ms", size=13)
    s.ruler(x0, 660, 45 * px, 45, 5, px, "ms", minor=1)
    s.notes(110, 740, [(1, f"bookkeeping, {rest:.2f} ms: cpu argmax over 152k logits, kv trims"),
                       (2, f"per token: {total / tpp:.1f} ms vs {step:.1f} ms plain, {1000 * tpp / total:.0f} vs {1000 / step:.0f} tok/s")],
            w=700, size=12)
    s.save(os.path.join(OUT, "fig_07_budget.png"))


def fig08():
    curves = [("stock, switches to mmq (not exact)", "red", verify_cost("logs/03_harness/q4km_stock")),
              ("exact, generic mat-vec", "amber", verify_cost("logs/05_bi_kernel/v3_Q4_K_M/generic")),
              ("exact, hiraishin kernel", "blue", verify_cost("logs/05_bi_kernel/v4_minblocks4_Q4_K_M/rows4"))]
    s = Sheet("08", "the price of exact verification", "cost of one target pass with b tokens, relative to one token",
              "logs/03_harness/q4km_stock, logs/05_bi_kernel", ["q4_k_m", "median of 15", "all logits"])
    x0, y0, w, h = 150, 225, 760, 470
    xs = lambda b: x0 + (b - 1) / 8 * w
    ys = lambda v: y0 + h - (v - 0.75) / (3.5 - 0.75) * h
    for v in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
        s.line([(x0, ys(v)), (x0 + w, ys(v))], color="faint", lw=0.6, z=2)
        s.text(x0 - 14, ys(v), f"{v:.1f}x", size=11, mono=True, ha="right", color="soft")
    s.line([(x0, ys(1.0)), (x0 + w, ys(1.0))], color="ink", lw=1.0, z=2)
    for b in range(1, 10):
        s.text(xs(b), y0 + h + 22, str(b), size=11, mono=True, ha="center", color="soft")
    s.text(x0 + w / 2, y0 + h + 52, "tokens verified in one pass (b)", size=12, ha="center", color="soft")
    for i, (name, col, c) in enumerate(curves):
        pts = [(xs(b), ys(v / c[1])) for b, v in c.items() if b <= 9]
        s.line(pts, color=col, lw=2.2, z=5)
        for p in pts:
            s.dot(p[0], p[1], col)
        s.text(pts[-1][0] + 16, pts[-1][1], f"{c[9] / c[1]:.2f}x", size=13, mono=True, weight="medium", color=col)
        s.line([(1060, 250 + i * 34), (1100, 250 + i * 34)], color=col, lw=2.4)
        s.text(1112, 250 + i * 34, name, size=12)
    s.notes(1060, 380, [
        (1, "stock is cheap past 5 tokens because it\nswitches to a faster kernel whose sums\nare not bit-identical."),
        (2, "the exact path stays on the mat-vec and\npays per column."),
        (3, "the hiraishin kernel shares weight\nunpacking across columns and asks for\n4 blocks per sm (128 registers)."),
    ], w=420)
    s.save(os.path.join(OUT, "fig_08_verify_cost.png"))


def fig09():
    stock = {e["prompt"]: e for e in load("logs/15_eval/stock") if e["event"] == "spec"}
    hira = {e["prompt"]: e for e in load("logs/15_eval/hira") if e["event"] == "spec" and e["ngram"] == 0}
    plain = {e["prompt"]: e for e in load("logs/15_eval/hira") if e["event"] == "plain"}
    cats = []
    for p in sorted(plain):
        c = p.rsplit("_", 1)[0]
        if c not in cats:
            cats.append(c)
    s = Sheet("09", "45 prompts, 8 kinds of work", "mean tok/s per category, every run checked token for token",
              "logs/15_eval", ["q4_k_m", "up to 1024 tokens", "ctx 4096", "one session"])
    x0, px = 280, 6.4
    y = 222
    for name, col, xx in (("plain decode", "faint", 0), ("stock speculative", "red", 210), ("hiraishin", "blue", 450)):
        s.swatch(x0 + xx, y, col)
        s.text(x0 + xx + 36, y, name, size=12)
    for i, c in enumerate(cats):
        ps = [p for p in plain if p.rsplit("_", 1)[0] == c]
        yy = 258 + i * 56
        s.text(x0 - 20, yy + 20, c.replace("_", " "), size=14, ha="right", weight="medium")
        vals = [(st.mean(plain[p]["tok_s"] for p in ps), "faint", None),
                (st.mean(stock[p]["tok_s"] for p in ps), "red", sum(stock[p]["matches_plain"] for p in ps)),
                (st.mean(hira[p]["tok_s"] for p in ps), "blue", sum(hira[p]["matches_plain"] for p in ps))]
        for j, (v, col, ex) in enumerate(vals):
            by = yy + j * 15
            s.bar(x0, by, v * px, 12, col)
            lab = f"{v:.0f}" + ("" if ex is None else f"  {ex}/{len(ps)} exact")
            s.text(x0 + v * px + 8, by + 6, lab, size=10, mono=True, color="ink" if col != "faint" else "soft", z=8)
    s.line([(x0 + 100 * px, 248), (x0 + 100 * px, 258 + len(cats) * 56)], color="faint", lw=1.0, ls=(0, (4, 4)), z=2)
    s.ruler(x0, 258 + len(cats) * 56 + 4, 125 * px, 125, 25, px, "tok/s", minor=5)
    s.save(os.path.join(OUT, "fig_09_eval.png"))


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09}

if __name__ == "__main__":
    for name in (sys.argv[1:] or FIGS):
        FIGS[name]()
        print("drew fig", name)
