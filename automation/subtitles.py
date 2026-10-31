"""Subtitle stage: SRT for the main video (global timeline) and styled ASS for the Short.
Timing comes from exact per-sentence TTS alignment; chunks inside a sentence are split proportionally to character count."""
import json, re, sys, textwrap
from config import *

MAX_LINE, MAX_CUE_CHARS = 40, 74

def display(text, rules):
    for pat, rep in rules:
        text = re.sub(pat, rep.replace("`", ""), text, flags=re.I if "\\" not in pat else 0)
    return text

def chunk(text, MAX_CUE_CHARS=MAX_CUE_CHARS):
    """Split a sentence into cue-sized phrases, preferring punctuation boundaries."""
    parts = [p.strip() for p in re.split(r"(?<=[,;:])\s+", text) if p.strip()]
    cues, cur = [], ""
    for p in parts:
        if cur and len(cur) + 1 + len(p) > MAX_CUE_CHARS:
            cues.append(cur); cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur: cues.append(cur)
    out = []
    for c in cues:
        if len(c) > MAX_CUE_CHARS:                      # split into n balanced pieces (avoids one-word orphans)
            n = -(-len(c) // MAX_CUE_CHARS); words = c.split(); target = len(c) / n; piece = ""
            for w in words:
                if piece and len(piece) + 1 + len(w) > target * 1.15 and len(out) < 10**6 and sum(1 for _ in [0]):
                    out.append(piece); piece = w
                else:
                    piece = f"{piece} {w}".strip()
            out.append(piece)
        else:
            out.append(c)
    return out

def wrap(c): return "\n".join(textwrap.wrap(c, MAX_LINE, break_long_words=False)) if len(c) > MAX_LINE else c

def cues_for(scene_timing, offset, rules, maxc=MAX_CUE_CHARS, do_wrap=True):
    res = []
    for s in scene_timing["sentences"]:
        chunks = [display(c, rules) for c in chunk(s["text"], maxc)]
        total = sum(len(c) for c in chunks); t = s["start"]; span = s["end"] - s["start"]
        for c in chunks:
            d = span * len(c) / total
            res.append((offset + t, offset + t + d, wrap(c) if do_wrap else c)); t += d
    return res

def ts(x, sep=","):
    ms = int(round(max(x, 0) * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d}{sep}{ms:03d}"

def write_srt(cues, path):
    with open(path, "w") as f:
        for i, (a, b, t) in enumerate(cues, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b - 0.02)}\n{t}\n\n")

def write_ass(cues, path, w=1080, h=1920, margin_v=400, fs=58):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,DejaVu Sans,{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,{margin_v},1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    def a(x): return ts(x, ".")[1:-1]
    with open(path, "w") as f:
        f.write(head)
        for s, e, t in cues:
            f.write(f"Dialogue: 0,{a(s)},{a(e)},Default,,0,0,0,,{t.replace(chr(10), '\\N')}\n")

def run(ep):
    script = json.load(open(ep_dir(ep) / "script.json")); timing = json.load(open(build_dir(ep) / "timing.json"))
    rules = script.get("display_rules", []); out = ep_dir(ep) / "subtitles"; out.mkdir(exist_ok=True)
    cues, off = [], 0.0
    for sc in script["scenes"]:
        cues += cues_for(timing[sc["id"]], off, rules); off += timing[sc["id"]]["duration"]
    write_srt(cues, out / "youtube-video.en.srt")
    sc = cues_for(timing["short"], 0.0, rules, maxc=40, do_wrap=False)
    write_srt(sc, out / "youtube-short.en.srt"); write_ass(sc, build_dir(ep) / "short.ass")
    print(f"[subs] main {len(cues)} cues, short {len(sc)} cues")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "episode-001")
