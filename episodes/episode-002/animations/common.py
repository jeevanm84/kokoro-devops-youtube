"""Shared visuals for Episode 002: commit chains, terminals, tags."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "templates"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from brand import *
from facts import *

def commit_chain(labels, colors=None, r=0.42, gap=1.0):
    nodes = VGroup()
    for i, l in enumerate(labels):
        c = Circle(radius=r, color=(colors[i] if colors else CYAN), fill_color=PANEL, fill_opacity=1, stroke_width=4)
        t = T(l, 26, TEXT, weight=BOLD).move_to(c)
        nodes.add(VGroup(c, t))
    nodes.arrange(RIGHT, buff=gap)
    links = VGroup(*[Line(nodes[i + 1][0].get_left(), nodes[i][0].get_right(), color=MUTED, stroke_width=4) for i in range(len(nodes) - 1)])
    return nodes, links

def tag(text, color, fs=20):
    return boxed(M(text, fs, color), color, 0.16)

def term(lines, fs=24, pad=0.4):
    cols = [GREEN if l.lstrip().startswith("$") else (MUTED if l.startswith("(") else TEXT) for l in lines]
    return boxed(code_block(lines, fs, cols, 0.16), MUTED, pad, "#0A0F1A")
