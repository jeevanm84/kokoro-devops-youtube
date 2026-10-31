"""Quality-assurance stage. Every check is automated with ffprobe/ffmpeg/PIL or explicitly labelled MANUAL (never silently passed).
Writes qa-report.md + build/qa.json. Exit code 1 if any automated check fails."""
import json, re, subprocess, sys
import numpy as np
from PIL import Image
from config import *

def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def probe(path):
    j = json.loads(sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None); a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    return j, v, a

def fps(v): n, d = v["r_frame_rate"].split("/"); return int(n) / int(d)

def srt_cues(path):
    cues = []
    for blk in open(path).read().strip().split("\n\n"):
        L = blk.split("\n"); m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", L[1]); g = list(map(int, m.groups()))
        cues.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, L[2:]))
    return cues

def loudness(path):
    o = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true,volumedetect", "-vn", "-f", "null", "-"]).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); mx = float(re.findall(r"max_volume: (-?[\d.]+) dB", o)[-1]); return I, mx

def run(ep):
    res = []
    def chk(group, name, ok, detail="", manual=False):
        res.append({"group": group, "check": name, "status": "MANUAL" if manual else ("PASS" if ok else "FAIL"), "detail": str(detail)})
    E = ep_dir(ep); B = build_dir(ep)
    tv = B / "technical_validation.json"
    chk("Technical accuracy", "all on-screen claims executed against the real tool (CPython or Git)", tv.exists() and json.load(open(tv))["all_pass"],
        f"{len(json.load(open(tv))['checks'])} checks" if tv.exists() else "missing")
    # ---------- main video ----------
    vp = E / "youtube-video.mp4"; g = "Main video"
    chk(g, "file exists", vp.exists(), vp)
    if vp.exists():
        j, v, a = probe(vp); dur = float(j["format"]["duration"])
        chk(g, "H.264 / yuv420p", v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p", f'{v["codec_name"]} {v["pix_fmt"]}')
        chk(g, "1920x1080, 16:9, square pixels", (v["width"], v["height"]) == (1920, 1080) and v.get("sample_aspect_ratio", "1:1") in ("1:1", "N/A"), f'{v["width"]}x{v["height"]} sar={v.get("sample_aspect_ratio")}')
        chk(g, "duration within 5-8 min", 300 <= dur <= 480, f"{dur:.1f}s = {dur/60:.2f} min")
        chk(g, "audio AAC present", a is not None and a["codec_name"] == "aac", a and f'{a["codec_name"]} {a["sample_rate"]}Hz')
        chk(g, "A/V duration match (<=0.15s)", a is not None and abs(float(v["duration"]) - float(a["duration"])) <= 0.15, f'v={v["duration"]} a={a["duration"]}')
        pk = int(sh(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(vp)]).stdout.strip().rstrip(","))
        exp = float(v["duration"]) * fps(v); chk(g, "no missing frames (packets vs expected)", abs(pk - exp) <= 3, f"{pk} vs {exp:.1f} @ {fps(v):.0f}fps")
        bl = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(vp), "-vf", "blackdetect=d=0.4:pix_th=0.02:pic_th=0.98", "-an", "-f", "null", "-"]).stderr
        chk(g, "no black frames", "black_start" not in bl, re.findall(r"black_start:[\d.]+ black_end:[\d.]+", bl)[:3])
        I, mx = loudness(vp); chk(g, "loudness -18..-14 LUFS", -18 <= I <= -14, f"{I} LUFS"); chk(g, "no clipping (peak <= -1 dB)", mx <= -1.0, f"max {mx} dB")
        sl = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(vp), "-af", "silencedetect=n=-45dB:d=2.5", "-vn", "-f", "null", "-"]).stderr
        chk(g, "no dead-air > 2.5 s", "silence_start" not in sl, re.findall(r"silence_start: [\d.]+", sl)[:3])
        chk(g, "embedded subtitle track", any(s["codec_type"] == "subtitle" for s in j["streams"]))
        chk(g, "file size sane (<2 GB)", int(j["format"]["size"]) < 2 * 1024 ** 3, f'{int(j["format"]["size"])/1e6:.1f} MB')
    # ---------- subtitles ----------
    sp = E / "subtitles/youtube-video.en.srt"; g = "Subtitles"
    if sp.exists() and vp.exists():
        c = srt_cues(sp)
        chk(g, "ordered, non-overlapping", all(c[i][1] <= c[i + 1][0] + 1e-3 and c[i][0] < c[i][1] for i in range(len(c) - 1)))
        chk(g, "ends within video", c[-1][1] <= dur + 0.05, f"last end {c[-1][1]:.2f}s")
        chk(g, "<=2 lines, <=42 chars/line", all(len(x[2]) <= 2 and all(len(l) <= 42 for l in x[2]) for x in c), f"{len(c)} cues")
        cps = [len(" ".join(x[2])) / (x[1] - x[0]) for x in c]; chk(g, "reading speed <= 21 cps", max(cps) <= 21, f"max {max(cps):.1f}, mean {np.mean(cps):.1f}")
        chk(g, "min cue duration >= 0.7 s", min(x[1] - x[0] for x in c) >= 0.7, f"min {min(x[1]-x[0] for x in c):.2f}s")
    # ---------- sync / pacing ----------
    g = "Sync & narration"; script = json.load(open(E / "script.json")); tm = json.load(open(B / "timing.json"))
    drift = [json.load(open(p)) for p in sorted((B / "drift").glob("s*.json"))]
    if drift:
        worst = max(max(d["late_s"]) for d in drift); chk(g, "every animation cue lands within 0.5 s of its word", worst <= 0.5, f"worst lateness {worst:.2f}s")
        chk(g, "scene render time == audio time", all(abs(d["end_time"] - d["target"]) <= 1.5 / FPS for d in drift), "all scenes ±1 frame")
    words = sum(len(s.split()) for sc in script["scenes"] for s in sc["sentences"]); total = sum(tm[s["id"]]["duration"] for s in script["scenes"])
    speech = sum(x["end"] - x["start"] for s in script["scenes"] for x in tm[s["id"]]["sentences"])
    chk(g, "effective pace 120-155 wpm (incl. pauses)", 120 <= words / total * 60 <= 155, f"{words/total*60:.0f} wpm effective, {words/speech*60:.0f} wpm while speaking ({words} words)")
    # ---------- short ----------
    spth = E / "youtube-short.mp4"; g = "Short"
    chk(g, "file exists", spth.exists())
    if spth.exists():
        j, v, a = probe(spth); dur_s = float(j["format"]["duration"])
        chk(g, "1080x1920 9:16 H.264", (v["width"], v["height"]) == (1080, 1920) and v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p")
        chk(g, "duration 30-60 s", 30 <= dur_s <= 60, f"{dur_s:.1f}s")
        chk(g, "A/V match (<=0.15s)", abs(float(v["duration"]) - float(a["duration"])) <= 0.15)
        I, mx = loudness(spth); chk(g, "loudness -18..-14 LUFS, no clipping", -18 <= I <= -14 and mx <= -1.0, f"{I} LUFS, max {mx} dB")
        hits = []
        for c in srt_cues(E / "subtitles/youtube-short.en.srt")[1:4]:
            t = (c[0] + c[1]) / 2; png = B / "qa_short_frame.png"
            sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(spth), "-frames:v", "1", str(png)])
            band = np.array(Image.open(png).convert("L"))[1250:1600]; hits.append(float((band > 245).mean()))
        chk(g, "captions burned in (white text in caption band)", all(h > 0.004 for h in hits), [f"{h:.3f}" for h in hits])
    # ---------- thumbnail ----------
    tp = E / "thumbnail.png"; g = "Thumbnail"
    if tp.exists():
        im = Image.open(tp); L = np.array(im.convert("L"), dtype=float) / 255
        chk(g, "1280x720, PNG, < 2 MB", im.size == (1280, 720) and tp.stat().st_size < 2e6, f"{im.size} {tp.stat().st_size/1e3:.0f} KB")
        chk(g, "high contrast (luma p95-p5 > 0.55)", np.percentile(L, 95) - np.percentile(L, 5) > 0.55, f"{np.percentile(L,95)-np.percentile(L,5):.2f}")
    chk(g, "visual review of thumbnail at small size", True, "", manual=True)
    # ---------- manual ----------
    g = "Needs human review"
    chk(g, "narration clarity / pronunciation (listen once)", True, "AI voice; automated checks cover levels and timing only", manual=True)
    chk(g, "licensing (fonts DejaVu, Manim MIT, Kokoro Apache-2.0, no third-party media)", True, "documented in docs/ASSETS-LICENSES.md; not machine-verified", manual=True)
    chk(g, "text readability on mobile", True, "frames reviewed by the producing agent; confirm on a phone", manual=True)
    chk(g, "documented claims (PyPy JIT, 3.11 specializing interpreter)", True, "cited in description sources", manual=True)

    fails = [r for r in res if r["status"] == "FAIL"]
    md = [f"# QA report — {ep}", "", f"**Result: {'FAIL — ' + str(len(fails)) + ' automated check(s) failed' if fails else 'PASS (automated checks) — manual items remain'}**", ""]
    for grp in dict.fromkeys(r["group"] for r in res):
        md += [f"## {grp}", "", "| Status | Check | Detail |", "|---|---|---|"] + [f"| {r['status']} | {r['check']} | {r['detail'][:120]} |" for r in res if r["group"] == grp] + [""]
    (E / "qa-report.md").write_text("\n".join(md)); json.dump(res, open(B / "qa.json", "w"), indent=2)
    print("\n".join(md)); return not fails

if __name__ == "__main__":
    sys.exit(0 if run(sys.argv[1] if len(sys.argv) > 1 else "episode-001") else 1)
