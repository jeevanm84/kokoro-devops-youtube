"""Scene-render stage. Each scene is cached by hash(scene file + brand kit + facts + that scene's timing); only changed scenes re-render.
Usage: render.py <episode> [scene ids...] [--quality l|h] [--force]"""
import hashlib, json, os, shutil, subprocess, sys, time
from config import *

SCENE_FILES = {f"s{i:02d}": "scenes_a.py" if i <= 5 else "scenes_b.py" for i in range(1, 11)}
SCENE_FILES["short"] = "short.py"
CLASS = {**{f"s{i:02d}": f"S{i:02d}" for i in range(1, 11)}, "short": "ShortHook"}

def key(ep, sid, timing, quality):
    h = hashlib.sha256()
    for p in (ep_dir(ep) / "animations" / SCENE_FILES[sid], ROOT / "templates/brand.py", ROOT / "channel.json", ep_dir(ep) / "facts.py"):
        h.update(p.read_bytes())
    h.update(json.dumps(timing[sid], sort_keys=True).encode()); h.update(quality.encode())
    return h.hexdigest()[:16]

def render_scene(ep, sid, quality="h", force=False):
    b = build_dir(ep); timing = json.load(open(b / "timing.json")); (b / "scenes").mkdir(exist_ok=True)
    out = b / "scenes" / f"{sid}.mp4"; stamp = b / "scenes" / f"{sid}.key"; k = key(ep, sid, timing, quality)
    if not force and out.exists() and stamp.exists() and stamp.read_text() == k:
        print(f"[render] {sid}: cached"); return True
    res = SHORT_RES if sid == "short" else MAIN_RES
    if quality == "l": res = (res[0] // 4, res[1] // 4) if False else (res[0] // 3, res[1] // 3)
    env = {**os.environ, "TIMING_JSON": str(b / "timing.json")}
    media = b / "media"
    cmd = ["manim", "render", "-r", f"{res[0]},{res[1]}", "--fps", str(FPS if quality == "h" else 15), "--format", "mp4", "--disable_caching",
           "--media_dir", str(media), "-o", sid, str(ep_dir(ep) / "animations" / SCENE_FILES[sid]), CLASS[sid]]
    t = time.time(); r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if r.returncode:
        print(f"[render] {sid}: FAILED\n{r.stdout[-1200:]}\n{r.stderr[-2500:]}"); return False
    produced = list(media.rglob(f"{sid}.mp4"))
    produced.sort(key=lambda p: p.stat().st_mtime)
    shutil.copy(produced[-1], out); stamp.write_text(k)
    print(f"[render] {sid}: ok in {time.time()-t:.0f}s -> {out.name}"); return True

def run(ep, ids=None, quality="h", force=False):
    ids = ids or list(CLASS)
    ok = [render_scene(ep, s, quality, force) for s in ids]
    return all(ok)

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]; ep = a[0]; ids = a[1:] or None
    q = "l" if "--quality" in sys.argv and sys.argv[sys.argv.index("--quality") + 1] == "l" else "h"
    a = [x for x in a if x not in ("l", "h")]; ids = [x for x in a[1:]] or None
    sys.exit(0 if run(ep, ids, q, "--force" in sys.argv) else 1)
