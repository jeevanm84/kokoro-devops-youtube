"""Pipeline orchestrator with checkpoints.
  python automation/pipeline.py run   episode-001            # run every stage that is stale
  python automation/pipeline.py run   episode-001 --from render
  python automation/pipeline.py only  episode-001 qa         # retry a single stage
  python automation/pipeline.py status episode-001
Stage state (input hash + result + timing) lives in episodes/<ep>/build/state.json; log in build/pipeline.log.
A stage is skipped when its inputs are unchanged and it previously succeeded. Nothing is reported 'done' unless its output validates."""
import hashlib, json, sys, time, traceback
from config import *
import validate_technical, tts, subtitles, render, assemble, thumbnail, metadata, qa

def H(*paths):
    h = hashlib.sha256()
    for p in paths:
        for f in sorted(p.rglob("*") if p.is_dir() else [p]):
            if f.is_file() and "__pycache__" not in f.parts: h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()[:16]

def stages(ep):
    E = ep_dir(ep); A = ROOT / "automation"; T = ROOT / "templates"
    S, F, AN = E / "script.json", E / "facts.py", E / "animations"
    return [
        ("validate",  lambda: validate_technical.run(ep),                      lambda: H(S, F, A / "validate_technical.py"), []),
        ("tts",       lambda: (tts.run(ep), True)[1],                          lambda: H(S, A / "tts.py"), [E / "build/timing.json"]),
        ("subtitles", lambda: (subtitles.run(ep), True)[1],                    lambda: H(S, A / "subtitles.py", E / "build/timing.json"), [E / "subtitles/youtube-video.en.srt"]),
        ("render",    lambda: render.run(ep),                                  lambda: H(AN, T, F, ROOT / "channel.json", E / "build/timing.json"), [E / "build/scenes/s10.mp4", E / "build/scenes/short.mp4"]),
        ("assemble",  lambda: (assemble.run_main(ep), True)[1],                lambda: H(E / "build/timing.json", E / "subtitles", E / "build/scenes", A / "assemble.py"), [E / "youtube-video.mp4"]),
        ("short",     lambda: (assemble.run_short(ep), True)[1],               lambda: H(E / "build/timing.json", E / "build/short.ass", E / "build/scenes/short.mp4", A / "assemble.py"), [E / "youtube-short.mp4"]),
        ("thumbnail", lambda: (thumbnail.run(ep), True)[1],                    lambda: H(F, A / "thumbnail.py", ROOT / "channel.json"), [E / "thumbnail.png"]),
        ("metadata",  lambda: (metadata.run(ep), True)[1],                     lambda: H(S, A / "metadata.py", E / "build/timing.json"), [E / "metadata.json"]),
        ("qa",        lambda: qa.run(ep),                                      lambda: H(E / "youtube-video.mp4", E / "youtube-short.mp4", E / "thumbnail.png", E / "metadata.json"), [E / "qa-report.md"]),
    ]

def main():
    cmd, ep = sys.argv[1], sys.argv[2]; b = build_dir(ep); sf = b / "state.json"
    state = json.load(open(sf)) if sf.exists() else {}
    st = stages(ep); names = [s[0] for s in st]
    if cmd == "status":
        for n in names: print(f"{n:10} {state.get(n, {}).get('result', '-')}")
        return 0
    if cmd == "only": todo = [sys.argv[3]]
    else:
        todo = names[names.index(sys.argv[sys.argv.index("--from") + 1]):] if "--from" in sys.argv else names
    force = "--force" in sys.argv
    for name, fn, inputs, outs in st:
        if name not in todo: continue
        h = inputs()
        if not force and state.get(name, {}).get("hash") == h and state[name]["result"] == "ok" and all(o.exists() for o in outs):
            print(f"[{name}] up to date — skipped"); continue
        print(f"\n=== {name} ===", flush=True); t = time.time()
        try: ok = bool(fn())
        except Exception: traceback.print_exc(); ok = False
        state[name] = {"hash": inputs(), "result": "ok" if ok else "FAILED", "seconds": round(time.time() - t, 1)}
        json.dump(state, open(sf, "w"), indent=2)
        if not ok: print(f"[{name}] FAILED — pipeline stopped. Fix and rerun; completed stages are cached."); return 1
    print("\nAll requested stages passed."); return 0

if __name__ == "__main__":
    sys.exit(main())
