"""Cover / share image for the batch invariance post, in the style of the blog's other covers
(dark card, dashed rounded border, excalifont, one phrase in a light rounded box).

usage: <python with pillow> blog/cover.py <out.png>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "figkit", "fonts", "Excalifont-Regular.ttf")
W, H = 2400, 1260
BG, INK, DIM, BOX, BOX_INK, EDGE = "#181818", "#ececec", "#9a9a9a", "#d6d6d6", "#1b1b1b", "#6e6e6e"

im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
f = lambda s: ImageFont.truetype(FONT, s)


def dashed_round_rect(x0, y0, x1, y1, r, dash=26, gap=16, width=4, fill=EDGE):
    # straight runs
    for (a, b, horizontal, fixed) in ((x0 + r, x1 - r, True, y0), (x0 + r, x1 - r, True, y1),
                                      (y0 + r, y1 - r, False, x0), (y0 + r, y1 - r, False, x1)):
        p = a
        while p < b:
            q = min(p + dash, b)
            d.line([(p, fixed), (q, fixed)] if horizontal else [(fixed, p), (fixed, q)], fill=fill, width=width)
            p = q + gap
    # corners as dashed arcs
    for (cx, cy, start) in ((x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)):
        for a in range(start, start + 90, 22):
            d.arc([cx - r, cy - r, cx + r, cy + r], a, min(a + 13, start + 90), fill=fill, width=width)


dashed_round_rect(34, 34, W - 34, H - 34, 70)
d.text((112, 128), "cuda · llama.cpp · inference", font=f(46), fill=INK, anchor="lm")

title = f(150)
line1, hi, rest = "why speculative decoding", "changed", "my output"
y1, y2 = 470, 700
d.text((W / 2, y1), line1, font=title, fill=INK, anchor="mm")

hw = d.textlength(hi, font=title)
rw = d.textlength(" " + rest, font=title)
pad_x, pad_y = 46, 34
total = hw + 2 * pad_x + rw
x = (W - total) / 2
bx0, by0, bx1, by1 = x, y2 - 105 - pad_y + 20, x + hw + 2 * pad_x, y2 + 85 + pad_y - 10
d.rounded_rectangle([bx0 + 7, by0 + 9, bx1 + 7, by1 + 9], radius=34, fill="#0c0c0c")  # drawn shadow, bottom right
d.rounded_rectangle([bx0, by0, bx1, by1], radius=34, fill=BOX)
d.arc([bx1 - 70, by1 - 70, bx1 + 2, by1 + 2], 10, 80, fill="#3a3a3a", width=4)  # pen re-trace on the corner
d.text((bx0 + pad_x, y2), hi, font=title, fill=BOX_INK, anchor="lm")
d.text((bx1, y2), " " + rest, font=title, fill=INK, anchor="lm")

d.text((W / 2, 960), "the same token, alone and in a batch, got different logits.", font=f(56), fill=DIM, anchor="mm")

out = sys.argv[1]
im.save(out, optimize=True)
print(out, im.size)
