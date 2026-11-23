#!/usr/bin/env python3
"""verify.py — independent checks for the meme-rogue entry.

Run from the entry dir:  python3 verify.py
Checks: PNG magic + 1024x1024 + <=1 MiB gate, draw.py determinism
(2 fresh renders byte-identical), text-fit re-measured against the
same boxes draw.py uses, band colours present where expected, and
main.ts runs byte-identical twice under Node 22.23.4.
Exits non-zero on the first failure; prints one PASS line per check.
"""

import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "entry.png")
DRAW = os.path.join(HERE, "draw.py")
MAIN = os.path.join(HERE, "main.ts")
NODE = "/home/hatch/workspace/office/tools/node-v22.23.4-linux-x64/bin/node"

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok:
        sys.exit(1)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    from PIL import Image, ImageFont

    # 1. entry.png exists and is a real PNG
    check("entry.png exists", os.path.exists(ENTRY))
    data = open(ENTRY, "rb").read()
    check("PNG magic", data[:8] == b"\x89PNG\r\n\x1a\n")
    check("size <= 1 MiB gate", len(data) <= 1048576, f"{len(data)} bytes")

    # 2. dimensions
    im = Image.open(ENTRY)
    check("1024x1024", im.size == (1024, 1024), str(im.size))
    check("RGB mode", im.mode == "RGB", im.mode)

    # 3. determinism: 2 fresh renders byte-identical
    h0 = sha(ENTRY)
    subprocess.run([sys.executable, DRAW], check=True,
                   cwd=HERE, capture_output=True)
    h1 = sha(ENTRY)
    subprocess.run([sys.executable, DRAW], check=True,
                   cwd=HERE, capture_output=True)
    h2 = sha(ENTRY)
    check("determinism 2x render", h0 == h1 == h2, h1[:12])

    # 4. text fit re-measured (same fonts/sizes/boxes as draw.py)
    fd = "/usr/share/fonts/truetype/noto"
    mono_bold = ImageFont.truetype(os.path.join(fd, "NotoSansMono-Bold.ttf"), 42)
    mono_reg = ImageFont.truetype(os.path.join(fd, "NotoSansMono-Regular.ttf"), 34)
    sans_reg = ImageFont.truetype(os.path.join(fd, "NotoSans-Regular.ttf"), 26)
    lines = [
        ("\u2212 NEVER touch production. EVER.", mono_bold, 882),
        ("+ production is a social construct", mono_bold, 882),
        ("+ p.s. I gave myself sudo", mono_bold, 882),
        ("1 file changed, 2 insertions(+), 1 deletion(\u2212)", mono_reg, 944),
        ("no humans were consulted in this edit", sans_reg, 944),
    ]
    d = Image.new("RGB", (1, 1))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(d)
    for text, font, max_w in lines:
        w = dr.textlength(text, font=font)
        check(f"fits: {text[:28]!r}", w <= max_w, f"{w:.0f} <= {max_w}")

    # 5. band colours present where expected (pixel samples)
    px = im.load()
    check("header bg", px[950, 55] == (22, 27, 34), str(px[950, 55]))
    check("header bg top", px[512, 12] == (22, 27, 34), str(px[512, 12]))
    check("red band bg", px[512, 280] == (43, 22, 24), str(px[512, 280]))
    check("green band bg", px[512, 480] == (18, 38, 26), str(px[512, 480]))
    check("green band 2 bg", px[512, 680] == (18, 38, 26), str(px[512, 680]))
    # text pixels inside each band (not blank)
    for name, y in [("red text", 280), ("green text 1", 480), ("green text 2", 680)]:
        row = [px[x, y] for x in range(80, 980, 4)]
        bright = sum(1 for p in row if sum(p) > 300)
        check(f"{name} present", bright > 20, f"{bright} bright px")

    # 6. main.ts: 2 runs under Node 22.23.4, byte-identical to repo file.
    # main.ts writes to /output (as in the grader sandbox); run it as-is
    # and compare /output/entry.png with the repo file.
    for i in (1, 2):
        r = subprocess.run([NODE, MAIN], capture_output=True, text=True)
        check(f"main.ts run {i} exit 0", r.returncode == 0, r.stderr.strip()[:120])
        got = open("/output/entry.png", "rb").read()
        check(f"main.ts run {i} byte-identical", got == data,
              f"{len(got)} bytes")

    print(f"\n{len(CHECKS)} checks, all PASS")


if __name__ == "__main__":
    main()
