"""figkit: measured, to-scale technical figures for the hiraishin blog, in two looks.

    drafting    an engineering drawing: graph paper, a framed sheet with zone letters, a title block naming the log
                the numbers came from, red dimension lines that state measured values, numbered callout balloons
    chalkboard  a lecture board: dark slate, chalk strokes that skip and smudge, coloured chalk for emphasis, the
                figure number written in the corner the way a professor would

every bit of writing is set in excalifont (sil ofl 1.1, the excalidraw hand). geometry is the same in both looks:
wherever a figure shows time or size it is drawn to scale.

    from figkit import Sheet
    s = Sheet("07", "where one cycle goes", "45 prompt eval", "logs/15_eval", theme="chalkboard")
    s.part(100, 300, 380, 60, "verify", material="weights")
    s.dim(100, 380, 480, 380, "19.0 ms")
    s.save("out.png")

coordinates are pixels at 1x, y down. output is a 2x png plus an svg. the theme can also come from FIGKIT_THEME.
"""
import math
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HAND = FontProperties(fname=os.path.join(HERE, "fonts", "Excalifont-Regular.ttf"))

THEMES = {
    "drafting": {
        "paper": "#f4f1ea", "chalk": False,
        "colors": {"ink": "#1b2430", "soft": "#6f6a60", "faint": "#a39d90", "blue": "#2f5d9e", "red": "#c8372d",
                   "amber": "#b7791f", "green": "#2e7d4f", "violet": "#5b4a9e"},
        "tints": {"weights": "#dbe4f0", "draft": "#e5e0f1", "kv": "#f2e5cc", "compute": "#e6e1d6", "ok": "#d8eadd",
                  "bad": "#f2d8d2", "plain": "#ebe6da", "none": None},
    },
    "chalkboard": {
        "paper": "#24302b", "chalk": True,
        "colors": {"ink": "#ecebe4", "soft": "#b7b9ae", "faint": "#7f8a83", "blue": "#93bfee", "red": "#f19185",
                   "amber": "#f3d273", "green": "#a2dbab", "violet": "#c7aef0"},
        "tints": {"weights": ("#93bfee", 0.16), "draft": ("#c7aef0", 0.16), "kv": ("#f3d273", 0.16),
                  "compute": ("#ecebe4", 0.07), "ok": ("#a2dbab", 0.16), "bad": ("#f19185", 0.18),
                  "plain": ("#ecebe4", 0.06), "none": None},
    },
}

# the active theme's colours; figures import C and read it after building a Sheet
C = dict(THEMES["drafting"]["colors"])


class Sheet:
    def __init__(self, fig, title, sub="", source="", block_extra=None, w=1600, h=900, theme=None):
        theme = theme or os.environ.get("FIGKIT_THEME", "drafting")
        self.theme = THEMES[theme]
        self.theme_name = theme
        C.clear()
        C.update(self.theme["colors"])
        self.paper = self.theme["paper"]
        self.chalky = self.theme["chalk"]
        self.rng = np.random.default_rng(int(fig) if str(fig).isdigit() else 7)
        self.w, self.h = w, h
        self.fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(h, 0)
        self.ax.axis("off")
        self.fig.patch.set_facecolor(self.paper)
        if self.chalky:
            self._board()
            self._board_header(fig, title, sub)
            self._board_corner(fig, source, block_extra or [])
        else:
            self._paper()
            self._frame()
            self._header(fig, title, sub)
            self._title_block(fig, title, source, block_extra or [])

    # ------------------------------------------------------------------ drafting sheet
    def _paper(self):
        for x in range(0, self.w + 1, 10):
            self.ax.plot([x, x], [0, self.h], color="#ddd5c4" if x % 50 == 0 else "#ebe5d8",
                         lw=0.7 if x % 50 == 0 else 0.4, zorder=0)
        for y in range(0, self.h + 1, 10):
            self.ax.plot([0, self.w], [y, y], color="#ddd5c4" if y % 50 == 0 else "#ebe5d8",
                         lw=0.7 if y % 50 == 0 else 0.4, zorder=0)

    def _frame(self):
        m, i = 18, 30
        self.ax.add_patch(Rectangle((m, m), self.w - 2 * m, self.h - 2 * m, fill=False, ec=C["ink"], lw=1.8, zorder=1))
        self.ax.add_patch(Rectangle((i, i), self.w - 2 * i, self.h - 2 * i, fill=False, ec=C["ink"], lw=0.6, zorder=1))
        cols, rows = 8, 4
        for k in range(1, cols):
            x = m + k * (self.w - 2 * m) / cols
            for y0, y1 in ((m, i), (self.h - i, self.h - m)):
                self.ax.plot([x, x], [y0, y1], color=C["ink"], lw=0.6, zorder=1)
        for k in range(cols):
            x = m + (k + 0.5) * (self.w - 2 * m) / cols
            for y in (m + 6, self.h - m - 6):
                self._t(x, y, str(k + 1), 7, "soft")
        for k in range(1, rows):
            y = m + k * (self.h - 2 * m) / rows
            for x0, x1 in ((m, i), (self.w - i, self.w - m)):
                self.ax.plot([x0, x1], [y, y], color=C["ink"], lw=0.6, zorder=1)
        for k in range(rows):
            y = m + (k + 0.5) * (self.h - 2 * m) / rows
            for x in (m + 6, self.w - m - 6):
                self._t(x, y, "abcd"[k], 7, "soft")

    def _header(self, fig, title, sub):
        self._t(62, 70, f"fig. {fig}", 15, "red", ha="left")
        self._t(62, 106, title, 32, "ink", ha="left")
        if sub:
            self._t(63, 144, sub, 16, "soft", ha="left")
        self.ax.plot([62, self.w - 62], [166, 166], color=C["ink"], lw=0.8, zorder=2)

    def _title_block(self, fig, title, source, extra):
        bw, bh = 700, 96
        x0, y0 = self.w - 30 - bw, self.h - 30 - bh
        self.ax.add_patch(Rectangle((x0, y0), bw, bh, facecolor=self.paper, ec=C["ink"], lw=1.2, zorder=8))
        for yy in (y0 + 32, y0 + 64):
            self.ax.plot([x0, x0 + bw], [yy, yy], color=C["ink"], lw=0.6, zorder=9)
        for xx in (x0 + 150, x0 + 590):
            self.ax.plot([xx, xx], [y0, y0 + bh], color=C["ink"], lw=0.6, zorder=9)
        cells = [("project", "hiraishin"), ("model", "qwen3-8b"), ("gpu", "rtx 5060 laptop")]
        for r, (k, v) in enumerate(cells):
            self._t(x0 + 8, y0 + 11 + 32 * r, k, 7, "soft", ha="left", z=10)
            self._t(x0 + 8, y0 + 24 + 32 * r, v, 10, "ink", ha="left", z=10)
        for r, (k, v) in enumerate((("title", title), ("source", source), ("conditions", " · ".join(extra) or "measured"))):
            self._t(x0 + 158, y0 + 11 + 32 * r, k, 7, "soft", ha="left", z=10)
            self._t(x0 + 158, y0 + 24 + 32 * r, v[:66], 10, "ink", ha="left", z=10)
        self._t(x0 + 598, y0 + 11, "fig", 7, "soft", ha="left", z=10)
        self._t(x0 + 645, y0 + 58, fig, 30, "red", z=10)

    # ------------------------------------------------------------------ chalkboard
    def _board(self):
        g = self.rng.normal(0, 1, (self.h // 6, self.w // 6))
        for _ in range(3):  # cheap blur: neighbour averages, so the slate looks rubbed, not noisy
            g = (g + np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1)) / 5
        self.ax.imshow(g, extent=(0, self.w, self.h, 0), cmap="Greys_r", alpha=0.10, zorder=0, interpolation="bicubic")
        for _ in range(9):  # old eraser swipes
            x, y = self.rng.uniform(60, self.w - 200), self.rng.uniform(180, self.h - 80)
            L, a = self.rng.uniform(200, 520), self.rng.uniform(-0.25, 0.25)
            self.ax.plot([x, x + L * math.cos(a)], [y, y + L * math.sin(a)], color="#ecebe4", lw=self.rng.uniform(18, 40),
                         alpha=0.022, solid_capstyle="round", zorder=0)
        wood = "#5b3d27"
        for (x, y, w, h) in ((0, 0, self.w, 16), (0, self.h - 16, self.w, 16), (0, 0, 16, self.h), (self.w - 16, 0, 16, self.h)):
            self.ax.add_patch(Rectangle((x, y), w, h, facecolor=wood, ec="none", zorder=12))
        self.ax.add_patch(Rectangle((16, 16), self.w - 32, self.h - 32, fill=False, ec="#3b2718", lw=2.0, zorder=12))

    def _board_header(self, fig, title, sub):
        self._t(66, 100, title, 34, "ink", ha="left")
        self.line([(62, 132), (min(66 + len(title) * 17.5, self.w - 300), 130)], color="amber", lw=2.4)
        if sub:
            self._t(68, 166, sub, 16, "soft", ha="left")

    def _board_corner(self, fig, source, extra):
        self._t(self.w - 60, 70, f"fig. {fig}", 26, "amber", ha="right")
        self._t(self.w - 60, self.h - 46, f"from {source}" + (f"  ·  {'  ·  '.join(extra)}" if extra else ""), 11,
                "faint", ha="right")

    # ------------------------------------------------------------------ strokes
    def _resample(self, pts, step=4.0):
        pts = np.asarray(pts, dtype=float)
        seg = np.diff(pts, axis=0)
        L = np.concatenate([[0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
        if L[-1] < 1:
            return pts
        s = np.linspace(0, L[-1], max(2, int(L[-1] / step)))
        return np.column_stack([np.interp(s, L, pts[:, 0]), np.interp(s, L, pts[:, 1])])

    def _chalk(self, pts, color, lw, z):
        """a chalk stroke: a few rough passes, small skips where the chalk lifts, a little dust."""
        p = self._resample(pts)
        n = len(p)
        d = np.gradient(p, axis=0)
        nrm = np.column_stack([-d[:, 1], d[:, 0]]) / (np.hypot(d[:, 0], d[:, 1])[:, None] + 1e-9)
        col = C.get(color, color)
        keep = self.rng.random(n - 1) > 0.06
        for k, (amp, alpha, wscale) in enumerate(((0.5, 0.85, 1.0), (0.9, 0.35, 0.7), (0.9, 0.25, 0.55))):
            off = self.rng.normal(0, amp, n)
            q = p + nrm * off[:, None]
            segs = np.stack([q[:-1], q[1:]], axis=1)
            mask = keep if k == 0 else self.rng.random(n - 1) > 0.15
            widths = lw * wscale * (0.8 + 0.4 * self.rng.random(n - 1))
            self.ax.add_collection(LineCollection(segs[mask], colors=col, linewidths=widths[mask], alpha=alpha,
                                                  capstyle="round", zorder=z))
        if len(p) > 4:
            idx = self.rng.choice(n, size=max(1, n // 3))
            dp = p[idx] + self.rng.normal(0, 2.0, (len(idx), 2))
            self.ax.scatter(dp[:, 0], dp[:, 1], s=0.6, c=col, alpha=0.35, linewidths=0, zorder=z)

    def line(self, pts, color="ink", lw=1.2, ls="-", z=4):
        if self.chalky:
            if ls != "-":  # dashed chalk: draw every other piece
                p = self._resample(pts, 3.0)
                for i in range(0, len(p) - 3, 6):
                    self._chalk(p[i:i + 4], color, lw * 1.3, z)
            else:
                self._chalk(pts, color, lw * 1.5, z)
            return
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=C.get(color, color), lw=lw, ls=ls, zorder=z, solid_capstyle="butt")

    def _rect(self, x, y, w, h, tint, edge="ink", lw=1.3, z=3):
        if tint:
            col, alpha = tint if isinstance(tint, tuple) else (tint, 1.0)
            self.ax.add_patch(Rectangle((x, y), w, h, facecolor=col, alpha=alpha, ec="none", zorder=z))
        if self.chalky:
            j = lambda: self.rng.uniform(-1.2, 1.2)
            for a, b in (((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))):
                self._chalk([(a[0] + j(), a[1] + j()), (b[0] + j(), b[1] + j())], edge, lw * 1.4, z + 0.5)
        else:
            self.ax.add_patch(Rectangle((x, y), w, h, facecolor="none", ec=C.get(edge, edge), lw=lw, zorder=z + 0.5))

    # ------------------------------------------------------------------ text
    def _t(self, x, y, s, size, color, ha="center", va="center", z=7, rot=0):
        self.ax.text(x, y, s, fontproperties=HAND, fontsize=size, color=C.get(color, color), ha=ha, va=va, zorder=z,
                     rotation=rot, linespacing=1.2, alpha=0.95 if self.chalky else 1.0)

    def text(self, x, y, s, size=13, color="ink", ha="left", va="center", mono=False, weight="regular", z=7, rot=0,
             plate=None):
        """all writing is excalifont. `mono` and `weight` are kept so figure code reads the same in both themes:
        numbers and emphasised words get a touch more size instead of a different face."""
        bump = 1.0 + (0.08 if weight in ("medium", "bold") else 0.0)
        self._t(x, y, s, size * 1.12 * bump, color, ha=ha, va=va, z=z, rot=rot)

    # ------------------------------------------------------------------ parts and annotation
    def part(self, x, y, w, h, label=None, material="plain", size=13, lw=1.3, mono=False, label_color="ink", z=3,
             sub=None, plate=True):
        self._rect(x, y, w, h, self.theme["tints"][material], lw=lw, z=z)
        if label:
            if sub:
                self.text(x + w / 2, y + h / 2 - 10, label, size=size, ha="center", weight="medium", color=label_color, z=z + 2)
                self.text(x + w / 2, y + h / 2 + 12, sub, size=size - 3, ha="center", color="soft", z=z + 2)
            else:
                self.text(x + w / 2, y + h / 2, label, size=size, ha="center", weight="medium", color=label_color, z=z + 2)

    def _head(self, tip, toward, color, size=9, z=6):
        tip, toward = np.array(tip, float), np.array(toward, float)
        u = (toward - tip) / (np.hypot(*(toward - tip)) + 1e-9)
        n = np.array([-u[1], u[0]])
        if self.chalky:
            for sgn in (1, -1):
                self._chalk([tip + u * size * 1.4 + n * size * 0.55 * sgn, tip], color, 1.8, z)
            return
        pts = [tip, tip + u * size + n * size * 0.32, tip + u * size - n * size * 0.32]
        self.ax.add_patch(Polygon(pts, closed=True, facecolor=C.get(color, color), ec="none", zorder=z))

    def dim(self, x1, y1, x2, y2, label, color="red", ext=None, size=12, side=0, gap=True):
        """dimension line between two points with arrowheads; the value sits in a gap in the line."""
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if y1 == y2 and gap and not side:
            half = len(label) * size * 0.42 + 10
            self.line([(x1, y1), (max(x1, mx - half), y1)], color=color, lw=0.9, z=6)
            self.line([(min(x2, mx + half), y1), (x2, y2)], color=color, lw=0.9, z=6)
        else:
            self.line([(x1, y1), (x2, y2)], color=color, lw=0.9, z=6)
        self._head((x1, y1), (x2, y2), color)
        self._head((x2, y2), (x1, y1), color)
        if y1 == y2:
            self.text(mx, my + side * 16 if side else my, label, size=size, ha="center", color=color, z=7)
        else:
            self.text(mx + 10, my, label, size=size, color=color, z=7)

    def _circle(self, x, y, r, color, fill=None, lw=1.2, z=8):
        if fill:
            self.ax.add_patch(Circle((x, y), r, facecolor=fill, ec="none", zorder=z))
        if self.chalky:
            t = np.linspace(0, 2 * math.pi * 1.05, 40) + self.rng.uniform(0, 6.28)
            self._chalk(np.column_stack([x + r * np.cos(t), y + r * np.sin(t)]), color, 1.8, z + 0.5)
        else:
            self.ax.add_patch(Circle((x, y), r, facecolor="none", ec=C[color], lw=lw, zorder=z + 0.5))

    def balloon(self, x, y, n, to=None, color="ink"):
        """numbered callout; with `to`, a leader line runs from the balloon to a dot on the thing it names."""
        if to:
            self.line([(x, y), to], color=color, lw=0.8, z=6)
            self.ax.add_patch(Circle(to, 3.2, facecolor=C[color], ec="none", zorder=7))
        self._circle(x, y, 15, color, fill=self.paper)
        self._t(x, y + 0.5, str(n), 14, color, z=9)

    def notes(self, x, y, items, w=520, size=12, title="notes"):
        self.text(x, y, title, size=11, color="soft")
        self.line([(x, y + 14), (x + w, y + 14)], color="faint", lw=0.8)
        yy = y + 40
        for n, s in items:
            lines = s.split("\n")
            self.balloon(x + 15, yy + 2, n)
            for i, ln in enumerate(lines):
                self.text(x + 42, yy + 24 * i, ln, size=size)
            yy += 24 * len(lines) + 20
        return yy

    def arrow(self, x1, y1, x2, y2, color="ink", lw=1.2, rad=0.0, label=None, size=12, ls="-"):
        if self.chalky:
            p0, p2 = np.array([x1, y1], float), np.array([x2, y2], float)
            dv = p2 - p0
            p1 = (p0 + p2) / 2 + np.array([-dv[1], dv[0]]) * rad  # same bend direction as matplotlib's arc3
            t = np.linspace(0, 1, 40)[:, None]
            curve = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
            self.line(curve, color=color, lw=lw, ls=ls, z=6)
            self._head(curve[-1], curve[-6], color, size=11)
        else:
            self.ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>,head_length=7,head_width=3.5",
                                              connectionstyle=f"arc3,rad={rad}", color=C.get(color, color), lw=lw,
                                              zorder=6, linestyle=ls, shrinkA=0, shrinkB=0))
        if label:
            self.text((x1 + x2) / 2, (y1 + y2) / 2 - 14, label, size=size, ha="center", color=color)

    def ruler(self, x0, y, length, units, step, unit_px, label, minor=None, color="ink", down=True):
        """a scale: `units` long, a tick every `step`, `unit_px` pixels per unit."""
        self.line([(x0, y), (x0 + length, y)], color=color, lw=1.0)
        d = 1 if down else -1
        v = 0.0
        while v <= units + 1e-9:
            x = x0 + v * unit_px
            self.line([(x, y), (x, y + 9 * d)], color=color, lw=1.0)
            self.text(x, y + 24 * d, f"{v:g}", size=10, ha="center", color="soft")
            v += step
        if minor and not self.chalky:
            v = 0.0
            while v <= units + 1e-9:
                x = x0 + v * unit_px
                self.line([(x, y), (x, y + 5 * d)], color=color, lw=0.6)
                v += minor
        self.text(x0 + length + 34, y + 24 * d, label, size=10, ha="left", color="soft")

    def dot(self, x, y, color, r=5):
        self._circle(x, y, r, color, fill=self.paper, z=6)

    def swatch(self, x, y, color, w=26, h=14):
        self.ax.add_patch(Rectangle((x, y - h / 2), w, h, facecolor=C[color], ec="none", zorder=5,
                                    alpha=0.85 if self.chalky else 1.0))

    def bar(self, x, y, w, h, color):
        self.ax.add_patch(Rectangle((x, y), w, h, facecolor=C[color], ec="none", zorder=5, alpha=0.85 if self.chalky else 1.0))

    def mark(self, x, y, ok=True, r=9):
        color = "green" if ok else "red"
        if ok:
            pts = [(x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.8)]
            if self.chalky:
                self._chalk(pts, color, 2.6, 7)
            else:
                self.ax.plot(*zip(*pts), color=C[color], lw=2.2, zorder=7, solid_capstyle="round", solid_joinstyle="round")
        else:
            for a, b in (((x - r * 0.75, y - r * 0.75), (x + r * 0.75, y + r * 0.75)),
                         ((x - r * 0.75, y + r * 0.75), (x + r * 0.75, y - r * 0.75))):
                if self.chalky:
                    self._chalk([a, b], color, 2.6, 7)
                else:
                    self.ax.plot(*zip(a, b), color=C[color], lw=2.2, zorder=7)

    def save(self, path):
        self.fig.savefig(path, dpi=200, facecolor=self.paper)
        self.fig.savefig(os.path.splitext(path)[0] + ".svg", facecolor=self.paper)
        plt.close(self.fig)
