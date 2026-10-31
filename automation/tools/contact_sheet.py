"""Visual QA helper: grab one frame near the end of each narrated sentence of a scene and tile them.
usage: contact_sheet.py <episode> <scene-id> [out.png] [cols]"""
import json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import *

ep, sid = sys.argv[1], sys.argv[2]; out = sys.argv[3] if len(sys.argv) > 3 else f"/tmp/sheet_{sid}.png"; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 2
b = build_dir(ep); t = json.load(open(b / "timing.json"))[sid]; vid = b / "scenes" / f"{sid}.mp4"
cues = [s["start"] for s in t["sentences"]] + [t["duration"]]
times = [c + 0.92 * (cues[i + 1] - c) for i, c in enumerate(cues[:-1])]
imgs = []
for i, ts in enumerate(times):
    p = Path(tempfile.mkdtemp()) / "f.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ts:.2f}", "-i", str(vid), "-frames:v", "1", str(p)], check=True)
    im = Image.open(p).convert("RGB"); ImageDraw.Draw(im).text((6, im.height - 14), f"#{i} t={ts:.1f}s", fill=(255, 255, 0)); imgs.append(im)
w, h = imgs[0].size; rows = (len(imgs) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols + 4 * (cols - 1), h * rows + 4 * (rows - 1)), (60, 60, 60))
for i, im in enumerate(imgs): sheet.paste(im, ((i % cols) * (w + 4), (i // cols) * (h + 4)))
sheet.save(out); print(out, sheet.size)
