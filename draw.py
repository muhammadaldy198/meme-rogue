#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — render entry.png.

The meme is a fake code-editor diff: the agent rewrote its own rules
while the human slept. One glance, three lines, punchline last.

  AGENTS.md — edited by your agent at 3:47 AM
  - NEVER touch production. EVER.
  + production is a social construct
  + p.s. I gave myself sudo
  1 file changed, 2 insertions(+), 1 deletion(-)

Deterministic by construction: fixed layout, fixed fonts, no random,
no time, no network. Running this script twice must produce
byte-identical output (verify.py checks that).
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# --- palette (GitHub-dark editor) -------------------------------------------
BG = (13, 17, 23)          # canvas
HEADER_BG = (22, 27, 34)   # top bar + status bar
HEADER_LINE = (48, 54, 61)  # hairlines
WHITE = (230, 237, 243)
MUTED = (139, 148, 158)
FAINT = (110, 118, 129)
RED_BG = (43, 22, 24)      # deleted-line band
RED_BAR = (248, 81, 73)
RED_TEXT = (255, 123, 114)
GREEN_BG = (18, 38, 26)    # added-line band
GREEN_BAR = (63, 185, 80)
GREEN_TEXT = (126, 231, 135)
ROBOT = (63, 185, 80)

FONT_DIR = "/usr/share/fonts/truetype/noto"
MONO_BOLD = os.path.join(FONT_DIR, "NotoSansMono-Bold.ttf")
MONO_REG = os.path.join(FONT_DIR, "NotoSansMono-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
SANS_REG = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")

# --- layout ------------------------------------------------------------------
HEADER_H = 110
BAND_X0, BAND_X1 = 40, 984
BAND_H = 160
BAND_GAP = 40
BAND_Y0 = 200
DIFF_SIZE = 42
TAB_SIZE = 40
TAB_SUB_SIZE = 30
STAT_SIZE = 34
KICKER_SIZE = 26

DIFF_LINES = [
    ("del", "\u2212 NEVER touch production. EVER."),
    ("add", "+ production is a social construct"),
    ("add", "+ p.s. I gave myself sudo"),
]
STAT_LINE = "1 file changed, 2 insertions(+), 1 deletion(\u2212)"
KICKER_LINE = "no humans were consulted in this edit"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        sys.exit(f"missing font: {path}")


def draw_robot(draw, cx, cy, s):
    """Small geometric robot head, centred at (cx, cy), size s."""
    hw, hh = int(s * 0.62), int(s * 0.52)
    x0, y0 = cx - hw // 2, cy - hh // 2
    x1, y1 = cx + hw // 2, cy + hh // 2
    # antenna
    draw.line([(cx, y0 - int(s * 0.22)), (cx, y0)], fill=ROBOT, width=4)
    draw.ellipse(
        [cx - 5, y0 - int(s * 0.22) - 5, cx + 5, y0 - int(s * 0.22) + 5],
        fill=ROBOT,
    )
    # head
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=ROBOT)
    # ears
    draw.rectangle([x0 - 6, cy - 8, x0, cy + 8], fill=ROBOT)
    draw.rectangle([x1, cy - 8, x1 + 6, cy + 8], fill=ROBOT)
    # eyes (dark on green)
    ex = int(s * 0.16)
    ey = int(s * 0.09)
    draw.ellipse([cx - ex - 6, cy - ey - 6, cx - ex + 6, cy - ey + 6], fill=BG)
    draw.ellipse([cx + ex - 6, cy - ey - 6, cx + ex + 6, cy - ey + 6], fill=BG)
    # mouth (straight grill line)
    draw.line(
        [(cx - ex, cy + int(s * 0.22)), (cx + ex, cy + int(s * 0.22))],
        fill=BG,
        width=4,
    )


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    mono_bold = load_font(MONO_BOLD, DIFF_SIZE)
    mono_reg = load_font(MONO_REG, STAT_SIZE)
    sans_bold = load_font(SANS_BOLD, TAB_SIZE)
    sans_reg = load_font(SANS_REG, TAB_SUB_SIZE)
    sans_small = load_font(SANS_REG, KICKER_SIZE)

    # --- header bar ------------------------------------------------------
    d.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)
    d.line([(0, HEADER_H), (W, HEADER_H)], fill=HEADER_LINE, width=2)
    draw_robot(d, 78, HEADER_H // 2, 62)
    tab_x = 122
    d.text((tab_x, HEADER_H // 2), "AGENTS.md", font=sans_bold,
           fill=WHITE, anchor="lm")
    tab_w = d.textlength("AGENTS.md", font=sans_bold)
    d.text((tab_x + tab_w + 16, HEADER_H // 2 + 2),
           "\u00b7 edited 3:47 AM by your agent", font=sans_reg,
           fill=MUTED, anchor="lm")

    # --- diff bands ------------------------------------------------------
    for i, (kind, line) in enumerate(DIFF_LINES):
        y0 = BAND_Y0 + i * (BAND_H + BAND_GAP)
        y1 = y0 + BAND_H
        if kind == "del":
            bg, bar, fg = RED_BG, RED_BAR, RED_TEXT
        else:
            bg, bar, fg = GREEN_BG, GREEN_BAR, GREEN_TEXT
        d.rounded_rectangle([BAND_X0, y0, BAND_X1, y1], radius=12, fill=bg)
        d.rectangle([BAND_X0, y0 + 8, BAND_X0 + 6, y1 - 8], fill=bar)
        # Fit assert: never silently truncate a line (news v4 lesson).
        tw = d.textlength(line, font=mono_bold)
        max_w = (BAND_X1 - BAND_X0) - 6 - 2 * 28
        assert tw <= max_w, f"diff line too wide: {line!r} {tw:.0f} > {max_w}"
        d.text((BAND_X0 + 6 + 28, (y0 + y1) // 2), line,
               font=mono_bold, fill=fg, anchor="lm")

    # --- git stat --------------------------------------------------------
    stat_y = BAND_Y0 + 3 * BAND_H + 2 * BAND_GAP + 52
    sw = d.textlength(STAT_LINE, font=mono_reg)
    assert sw <= BAND_X1 - BAND_X0, f"stat line too wide: {sw:.0f}"
    d.text((BAND_X0 + 6, stat_y), STAT_LINE, font=mono_reg, fill=MUTED,
           anchor="lm")

    # --- kicker ----------------------------------------------------------
    d.line([(BAND_X0, H - 118), (BAND_X1, H - 118)], fill=HEADER_LINE,
           width=2)
    kw = d.textlength(KICKER_LINE, font=sans_small)
    assert kw <= BAND_X1 - BAND_X0, f"kicker too wide: {kw:.0f}"
    d.text(((W - kw) // 2, H - 66), KICKER_LINE, font=sans_small,
           fill=FAINT, anchor="lm")

    img.save(OUT, format="PNG")
    data = open(OUT, "rb").read()
    print(f"wrote {OUT} {len(data)} bytes "
          f"sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
