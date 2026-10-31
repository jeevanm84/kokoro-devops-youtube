"""Thumbnail stage: programmatic 1280x720 PNG, 2x supersampled. High contrast, three words, one clear technical illustration."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from config import *

BG1, BG2 = (11, 18, 32), (22, 36, 66)
CYAN, AMBER, VIOLET, PINK, GREEN, TEXT, MUTED = (45, 212, 191), (255, 180, 84), (167, 139, 250), (244, 114, 182), (126, 231, 135), (230, 237, 243), (148, 163, 184)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def make(path, rows, name="", variant="A"):
    S = 2; W, H = THUMB_RES[0] * S, THUMB_RES[1] * S
    img = Image.new("RGB", (W, H), BG1); px = img.load()
    for y in range(H):                                   # vertical gradient
        t = y / H
        for x in range(0, W): px[x, y] = tuple(int(BG1[i] * (1 - t) + BG2[i] * t) for i in range(3))
    glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((W * 0.55, H * 0.05, W * 1.05, H * 0.95), fill=(20, 90, 110)); glow = glow.filter(ImageFilter.GaussianBlur(160 * S / 2))
    img = Image.blend(img, Image.composite(glow, img, glow.convert("L")), 0.55)
    d = ImageDraw.Draw(img)
    f = lambda p, s: ImageFont.truetype(p, s * S)
    # headline: three words, escalating size
    if variant == "A":
        d.text((70 * S, 78 * S), "COMPILED?", font=f(FB, 98), fill=PINK)
        d.text((70 * S, 218 * S), "INTERPRETED?", font=f(FB, 76), fill=VIOLET)
        d.text((70 * S, 330 * S), "BOTH.", font=f(FB, 196), fill=AMBER, stroke_width=3 * S, stroke_fill=(120, 80, 0))
    else:
        d.text((70 * S, 70 * S), "HOW PYTHON", font=f(FB, 80), fill=TEXT)
        d.text((70 * S, 195 * S), "REALLY RUNS", font=f(FB, 80), fill=CYAN)
        d.text((70 * S, 330 * S), "YOUR CODE", font=f(FB, 92), fill=AMBER, stroke_width=3 * S, stroke_fill=(120, 80, 0))
    d.text((74 * S, 640 * S), f"{(name or '').upper()}  ·  PYTHON", font=f(FB, 28), fill=MUTED)
    # bytecode card
    cx0, cy0, cx1, cy1 = 815 * S, 110 * S, 1240 * S, 590 * S
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((cx0 + 10 * S, cy0 + 14 * S, cx1 + 10 * S, cy1 + 14 * S), 28 * S, fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(14 * S))).convert("RGB"); d = ImageDraw.Draw(img)
    d.rounded_rectangle((cx0, cy0, cx1, cy1), 28 * S, fill=(19, 28, 46), outline=CYAN, width=5 * S)
    d.text((cx0 + 30 * S, cy0 + 22 * S), "bytecode", font=f(FB, 34), fill=CYAN)
    d.line((cx0 + 24 * S, cy0 + 78 * S, cx1 - 24 * S, cy0 + 78 * S), fill=(48, 66, 100), width=3 * S)
    cols = [MUTED, CYAN, AMBER]
    for i, (o, op, ar) in enumerate(rows):
        y = cy0 + 100 * S + i * 74 * S
        if i == 3: d.rounded_rectangle((cx0 + 14 * S, y - 8 * S, cx1 - 14 * S, y + 56 * S), 14 * S, fill=(60, 50, 12))
        d.text((cx0 + 30 * S, y), o, font=f(FM, 32), fill=cols[0]); d.text((cx0 + 90 * S, y), op, font=f(FM, 32), fill=cols[1])
        if ar: d.text((cx0 + 345 * S, y), ar.split(" ")[-1].strip("()"), font=f(FM, 32), fill=cols[2])
    img = img.resize(THUMB_RES, Image.LANCZOS); img.save(path, optimize=True)
    print(f"[thumb] {path} {img.size}")

def run(ep):
    import importlib.util
    spec = importlib.util.spec_from_file_location("facts", ep_dir(ep) / "facts.py"); F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
    import json; name = json.load(open(ROOT / "channel.json"))["name"]
    make(ep_dir(ep) / "thumbnail.png", F.ROWS, name)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "episode-001")
