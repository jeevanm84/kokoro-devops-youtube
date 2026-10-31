"""Channel brand kit + narration-synced Manim base scene.

Sync model: automation/tts.py writes timing.json (exact sentence start times).
`BrandScene.at(i, *anims)` waits until sentence i begins, then plays anims, so visuals land on the words.
Any cue that arrives late (animations overran) is recorded to drift.json and checked by QA.
"""
from manim import *
import json, os, pathlib

# ---- Palette ("Under The Hood": deep navy + cyan/amber accents) ----
BG, PANEL, PANEL2 = "#0B1220", "#131C2E", "#1B2740"
CYAN, AMBER, GREEN, PINK, RED, VIOLET = "#2DD4BF", "#FFB454", "#7EE787", "#F472B6", "#F87171", "#A78BFA"   # teal/amber = logo colours
TEXT, MUTED = "#E6EDF3", "#94A3B8"
SANS, MONO = "DejaVu Sans", "DejaVu Sans Mono"   # swap for Inter / JetBrains Mono when fonts are bundled
CHANNEL = json.load(open(pathlib.Path(__file__).resolve().parents[1] / "channel.json"))["name"].upper()

UI = 1.2   # global text scale: keeps copy readable at 1080p and on phones
def T(s, fs=28, color=TEXT, **kw):  return Text(s, font=SANS, font_size=fs * UI, color=color, **kw)
def M(s, fs=26, color=TEXT, **kw):  return Text(s, font=MONO, font_size=fs * UI, color=color, **kw)

def card(w, h, color=MUTED, fill=PANEL, sw=2.5, r=0.18):
    return RoundedRectangle(corner_radius=r, width=w, height=h, stroke_color=color, stroke_width=sw,
                            fill_color=fill, fill_opacity=1)

def node(label, color=CYAN, fs=24, w=None, h=None, mono=False, fill=PANEL):
    t = (M if mono else T)(label, fs, TEXT)
    c = card(w or t.width + 0.7, h or t.height + 0.5, color, fill, sw=3)
    t.move_to(c)
    return VGroup(c, t)

def link(a, b, color=MUTED, **kw):
    return Arrow(a, b, buff=0.08, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.25, **kw)

class BrandScene(Scene):
    SID = None
    def setup(self):
        self.camera.background_color = BG
        t = json.load(open(os.environ["TIMING_JSON"]))[self.SID]
        self.dur = t["duration"]
        self.cues = [s["start"] for s in t["sentences"]]
        self.lates = []

    def chrome(self, chapter):
        self.add(T(chapter.upper(), 18, CYAN).to_corner(UL, buff=0.35),
                 T(CHANNEL, 16, MUTED).to_corner(UR, buff=0.35))

    def wait_until(self, t):
        d = t - self.time
        if d > 0.034:
            self.wait(d)

    def at(self, i, *anims, rt=1.0, **kw):
        self.wait_until(self.cues[i])
        self.lates.append(round(self.time - self.cues[i], 3))
        if anims:
            nxt = self.cues[i + 1] if i + 1 < len(self.cues) else self.dur
            rt = max(min(rt, nxt - self.time - 0.08), 0.25)
            self.play(*anims, run_time=rt, **kw)

    def finish(self):
        self.wait_until(self.dur)
        p = pathlib.Path(os.environ["TIMING_JSON"]).parent / "drift"
        p.mkdir(exist_ok=True)
        json.dump({"scene": self.SID, "late_s": self.lates, "end_time": round(self.time, 3), "target": self.dur},
                  open(p / f"{self.SID}.json", "w"))


# ---------- layout helpers (auto-sized so text can never overflow its container) ----------
def fit(m, w):
    """Scale a mobject down (never up) so it is at most w units wide."""
    if m.width > w:
        m.scale_to_fit_width(w)
    return m

def boxed(content, color=MUTED, pad=0.4, fill=PANEL, sw=2.5):
    """Card sized to its content. Returns VGroup(card, content)."""
    c = card(content.width + 2 * pad, content.height + 2 * pad, color, fill, sw)
    content.move_to(c)
    return VGroup(c, content)

def code_block(lines, fs=24, colors=None, buff=0.25):
    """Left-aligned monospace lines. Manim strips leading spaces, so indentation is re-applied by shifting."""
    cw = M("0" * 20, fs).width / 20
    rows = VGroup()
    for i, l in enumerate(lines):
        ind = len(l) - len(l.lstrip(" "))
        if l.strip():
            t = M(l.strip(), fs, colors[i] if colors else TEXT)
        else:
            t = M("x", fs).set_opacity(0)
        t.indent = ind * cw
        rows.add(t)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=buff)
    for t in rows:
        t.shift(RIGHT * t.indent)
    return rows

def instr_table(rows, fs=22, step=0.6):
    """dis-style table with columns sized from measured text widths. Returns VGroup of per-row VGroups centred at the origin."""
    cols = [[M(r[i] if r[i] else "·", fs, c) for r in rows] for i, c in enumerate((MUTED, CYAN, AMBER))]
    for r, cell in zip(rows, cols[2]):
        if not r[2]:
            cell.set_opacity(0)
    wd = [max(c.width for c in col) for col in cols]
    xs = [0, wd[0] + 0.35, wd[0] + wd[1] + 0.7]; tw = sum(wd) + 0.7
    out = VGroup()
    for i in range(len(rows)):
        row = VGroup()
        for j in range(3):
            cols[j][i].move_to([xs[j] - tw / 2, -i * step, 0], aligned_edge=LEFT); row.add(cols[j][i])
        out.add(row)
    return out.move_to(ORIGIN)

def pulse(m, color=AMBER, **_ignored):
    """Highlight without recolouring: draws a moving outline around m. (Indicate() repaints the whole
    mobject, so filled cards became solid blocks with invisible text.)"""
    return Circumscribe(m, color=color, buff=0.1, time_width=0.6, stroke_width=6)
