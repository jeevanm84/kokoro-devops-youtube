"""Episode 002 scenes 01-05 (Git undo toolkit). Visuals keyed to narration cues; terminal text comes from facts.py (real recorded output)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import *


class S01(BrandScene):
    SID = "s01"
    def construct(self):
        self.chrome("The three-second panic")
        t = fit(term(['$ git commit -m "oops"'], 30, 0.5), 6.4).move_to([-3.8, 1.4, 0])
        stamp = T("WRONG!", 52, RED, weight=BOLD).rotate(0.15).move_to([-3.8, -0.1, 0])
        probs = VGroup(*[boxed(T(x, 28, TEXT), RED, 0.3, "#2A1215") for x in ("wrong file", "wrong branch", "already pushed")]).arrange(DOWN, buff=0.3).move_to([4.3, 1.0, 0])
        tools = VGroup(*[node(n, c, 30, w=2.6, h=0.9, mono=True) for n, c in zip(("restore", "reset", "revert", "reflog"), (CYAN, AMBER, GREEN, VIOLET))]).arrange(RIGHT, buff=0.35).move_to([0, -1.9, 0])
        self.at(0, FadeIn(t), rt=0.8)
        self.play(FadeIn(stamp, scale=1.6), run_time=0.6)
        self.at(1, LaggedStart(*[FadeIn(p, shift=LEFT * 0.4) for p in probs], lag_ratio=0.5), rt=2.0)
        self.at(2, LaggedStart(*[FadeIn(x, shift=UP * 0.3) for x in tools], lag_ratio=0.3), rt=1.8)
        self.at(3, *[pulse(x, scale_factor=1.1) for x in tools], rt=1.4)
        self.finish()


class S02(BrandScene):
    SID = "s02"
    def construct(self):
        self.chrome("Where your work lives")
        spec = [("Working directory", "your files", CYAN), ("Index", "staging area", AMBER), ("Repository", "commits", GREEN)]
        cards = VGroup(*[boxed(VGroup(T(a, 26, c, weight=BOLD), T(b, 22, MUTED)).arrange(DOWN, buff=0.15), c, 0.4) for a, b, c in spec]).arrange(RIGHT, buff=2.3)
        fit(cards, 13.2); cards.move_to([-0.2, 0.9, 0])
        arr = [link(cards[i].get_right(), cards[i + 1].get_left()) for i in range(2)]
        lab = [M(x, 20, MUTED).next_to(a, UP, buff=0.12) for x, a in zip(("git add", "git commit"), arr)]
        nodes, links = commit_chain(["A", "B", "C"], [MUTED, MUTED, GREEN], 0.4, 0.8)
        chain = VGroup(nodes, links).next_to(cards[2], DOWN, buff=0.7)
        head = tag("HEAD", AMBER).next_to(nodes[2], UP, buff=0.25)
        q = T("Which place changed?", 42, TEXT).move_to([0, 3.0, 0])
        self.at(0, FadeIn(q), rt=0.8)
        self.at(1, LaggedStart(FadeIn(cards[0]), GrowArrow(arr[0]), FadeIn(lab[0]), FadeIn(cards[1]), GrowArrow(arr[1]), FadeIn(lab[1]), FadeIn(cards[2]), lag_ratio=0.3), rt=3.2)
        self.at(2, FadeIn(chain), FadeIn(head), rt=1.2)
        self.at(3, *[pulse(c, scale_factor=1.06) for c in cards], rt=2.0)
        self.at(4, FadeIn(fit(T("Every undo command moves something between these places", 28, AMBER), 12.4).move_to([0, -2.5, 0])), rt=1.2)
        self.finish()


class S03(BrandScene):
    SID = "s03"
    def construct(self):
        self.chrome("git restore")
        t1 = fit(term(["$ git status --short", " M app.txt", "$ git restore app.txt", "$ git status --short", "(clean: no output)"], 22), 6.2).move_to([-3.5, -0.6, 0])
        t2 = fit(term(["$ git add app.txt", "$ git status --short", STAGED_BEFORE, "$ git restore --staged app.txt", "$ git status --short", STAGED_AFTER], 22), 6.2).move_to([-3.5, -0.7, 0])
        trk = VGroup(*[node(n, c, 24, w=3.4, h=0.8) for n, c in (("Working dir", CYAN), ("Index", AMBER), ("Repository", GREEN))]).arrange(RIGHT, buff=1.3).move_to([0, 2.0, 0])
        dot = Dot(radius=0.18, color=RED).move_to(trk[0].get_top() + UP * 0.35)
        ttl = T("restore: files and index only", 30, CYAN).move_to([0, 3.2, 0])
        nodes, links = commit_chain(["A", "B", "C"], [MUTED, MUTED, GREEN], 0.35, 0.7)
        chain = VGroup(nodes, links).move_to([3.8, -0.4, 0])
        lock = T("commits untouched", 24, GREEN).next_to(chain, DOWN, buff=0.3)
        self.at(0, FadeIn(ttl), FadeIn(trk), rt=0.8)
        self.at(1, FadeIn(t1), FadeIn(dot), rt=0.8)
        self.play(FadeOut(dot, scale=0.2), run_time=0.8)
        self.at(2, FadeOut(t1), FadeIn(t2), FadeIn(dot.move_to(trk[1].get_top() + UP * 0.35)), rt=0.8)
        self.wait(1.2)
        self.play(dot.animate.move_to(trk[0].get_top() + UP * 0.35), run_time=0.9)
        self.at(3, FadeIn(chain), FadeIn(lock), rt=1.0)
        self.finish()


class S04(BrandScene):
    SID = "s04"
    def construct(self):
        self.chrome("git reset: three modes")
        nodes, links = commit_chain(["A", "B", "C"], [MUTED, MUTED, RED], 0.38, 0.8)
        chain = VGroup(nodes, links).move_to([-4.0, 2.2, 0])
        main = tag("main", CYAN).next_to(nodes[2], UP, buff=0.22)
        cmd = M("$ git reset HEAD~1", 26, GREEN).move_to([2.4, 2.2, 0])
        W = [2.0, 2.2, 2.4, 2.4, 2.8]
        hdr = VGroup(*[T(x, 20, MUTED) for x in ("mode", "branch", "index", "your files", "git status --short")])
        def row(mode, cells, color):
            vals = [boxed(M(mode, 22, color), color, 0.12, PANEL)] + [boxed(M(txt, 20, c), MUTED, 0.12, PANEL) for txt, c in cells]
            for v, w in zip(vals, W): v[0].stretch_to_fit_width(w); v[0].stretch_to_fit_height(0.7); v[1].move_to(v[0])
            return VGroup(*vals).arrange(RIGHT, buff=0.1)
        r1 = row("--soft", [("moves to B", AMBER), ("unchanged", GREEN), ("unchanged", GREEN), (SOFT, TEXT)], CYAN)
        r2 = row("--mixed", [("moves to B", AMBER), ("reset", AMBER), ("unchanged", GREEN), (MIXED, TEXT)], AMBER)
        r3 = row("--hard", [("moves to B", AMBER), ("reset", AMBER), ("reset", RED), ("(clean)", TEXT)], RED)
        grid = VGroup(r1, r2, r3).arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([0, -0.5, 0])
        hdr.arrange(RIGHT, buff=0.1)
        for h, w in zip(hdr, W): h.move_to(h.get_center())
        for h, c in zip(hdr, r1): h.move_to([c.get_center()[0], grid.get_top()[1] + 0.35, 0])
        note = T("hard reset does not delete untracked files", 26, AMBER).move_to([0, -2.4, 0])
        self.at(0, FadeIn(chain), FadeIn(main), FadeIn(cmd), rt=1.0)
        self.at(1, main.animate.next_to(nodes[1], UP, buff=0.22), nodes[2].animate.set_opacity(0.35), FadeIn(hdr), rt=1.4)
        self.at(2, FadeIn(r1, shift=RIGHT * 0.3), rt=0.9)
        self.at(3, FadeIn(r2, shift=RIGHT * 0.3), rt=0.9)
        self.at(4, FadeIn(r3, shift=RIGHT * 0.3), rt=0.9)
        self.at(5, FadeIn(note), rt=0.9)
        self.finish()


class S05(BrandScene):
    SID = "s05"
    def construct(self):
        self.chrome("git revert: the safe one")
        nodes, links = commit_chain(["A", "B", "C"], [MUTED, MUTED, RED], 0.4, 0.8)
        mine = VGroup(nodes, links).move_to([-3.8, 1.3, 0])
        lab1 = T("your machine only", 22, GREEN).next_to(mine, UP, buff=0.35)
        n2, l2 = commit_chain(["A", "B", "C"], [MUTED, MUTED, RED], 0.4, 0.8)
        mate = VGroup(n2, l2).move_to([-3.8, -1.1, 0]); lab2 = T("teammate's copy", 22, MUTED).next_to(mate, UP, buff=0.3)
        pushed = T("already pushed", 22, RED).move_to(lab1)
        bad = T("rewrite history = everyone's branches break", 24, RED).move_to([-3.8, -2.4, 0])
        d = VGroup(Circle(radius=0.4, color=GREEN, fill_color=PANEL, fill_opacity=1, stroke_width=4), T("D", 26, TEXT, weight=BOLD)); d[1].move_to(d[0])
        d.move_to(nodes[2].get_center() + RIGHT * 1.8); dl = Line(d[0].get_left(), nodes[2][0].get_right(), color=MUTED, stroke_width=4)
        rv = T("Revert C", 22, GREEN).next_to(d, UP, buff=0.25)
        cmd = term(["$ git revert HEAD", "$ git log --oneline"] + REVERT_LOG, 20).move_to([4.2, 0.2, 0]); fit(cmd, 6.0).move_to([4.2, 0.2, 0])
        self.at(0, FadeIn(mine), FadeIn(lab1), rt=0.9)
        self.at(1, FadeIn(mate), FadeIn(lab2), Transform(lab1, pushed), rt=1.2)
        self.play(FadeIn(bad), run_time=0.8)
        self.at(2, FadeOut(bad), FadeIn(d), Create(dl), FadeIn(rv), rt=1.2)
        self.at(3, FadeIn(cmd), rt=1.2)
        self.finish()
