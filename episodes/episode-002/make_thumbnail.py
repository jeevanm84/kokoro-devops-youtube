"""Episode 002 thumbnail (1280x720): three honest keywords + a real-command card."""
import json, pathlib, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "automation"))
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG1, BG2 = (11, 18, 32), (22, 36, 66); TEAL, AMBER, VIOLET, TEXT, MUTED = (45, 212, 191), (255, 180, 84), (167, 139, 250), (230, 237, 243), (148, 163, 184)
name = json.load(open(ROOT / "channel.json"))["name"]; S = 2; W, H = 1280 * S, 720 * S
img = Image.new("RGB", (W, H)); px = img.load()
for y in range(H):
    t = y / H
    for x in range(W): px[x, y] = tuple(int(a * (1 - t) + b * t) for a, b in zip(BG1, BG2))
d = ImageDraw.Draw(img); f = lambda p, s: ImageFont.truetype(p, s * S)
d.text((70 * S, 60 * S), "RESET", font=f(FB, 120), fill=AMBER)
d.text((70 * S, 200 * S), "REVERT", font=f(FB, 120), fill=TEAL)
d.text((70 * S, 340 * S), "RESTORE?", font=f(FB, 108), fill=VIOLET)
d.text((74 * S, 640 * S), f"{name.upper()}  ·  GIT", font=f(FB, 28), fill=MUTED)
x0, y0, x1, y1 = 800 * S, 110 * S, 1240 * S, 590 * S
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 + 10 * S, y0 + 14 * S, x1 + 10 * S, y1 + 14 * S), 28 * S, fill=(0, 0, 0, 150))
img = Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(14 * S))).convert("RGB"); d = ImageDraw.Draw(img)
d.rounded_rectangle((x0, y0, x1, y1), 28 * S, fill=(10, 15, 26), outline=TEAL, width=5 * S)
for i, (c, col) in enumerate((("$ git restore", MUTED), ("$ git reset", AMBER), ("$ git revert", TEAL), ("$ git reflog", VIOLET))):
    d.text((x0 + 36 * S, y0 + 40 * S + i * 105 * S), c, font=f(FM, 40), fill=col)
img = img.resize((1280, 720), Image.LANCZOS); img.save(pathlib.Path(__file__).resolve().parent / "thumbnail.png", optimize=True); print("thumbnail ok")
