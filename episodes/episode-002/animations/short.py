"""Episode 002 Short (1080x1920): reset soft/mixed/hard in 30 s. Content stays above y=-3.2 (captions below)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import *
config.frame_width, config.frame_height = 9, 16


class ShortHook(BrandScene):
    SID = "short"
    def construct(self):
        self.add(T(CHANNEL, 24, MUTED).move_to([0, 7.0, 0]))
        title = VGroup(*[T(s, 62, TEXT, weight=BOLD) for s in ("git reset", "soft, mixed", "or hard?")]).arrange(DOWN, buff=0.25).move_to([0, 4.7, 0])
        nodes, links = commit_chain(["A", "B", "C"], [MUTED, MUTED, RED], 0.45, 0.9)
        chain = VGroup(nodes, links).move_to([0, 5.2, 0]); main = tag("main", CYAN, 24).next_to(nodes[2], UP, buff=0.25)
        def lane(mode, line, st, color, y):
            top = VGroup(M(mode, 44, color), M(st, 34, MUTED)).arrange(RIGHT, buff=0.9)
            g = boxed(VGroup(top, T(line, 36, TEXT)).arrange(DOWN, buff=0.25), color, 0.35)
            return fit(g, 8.2).move_to([0, y, 0])
        l1 = lane("--soft", "changes stay STAGED", SOFT, CYAN, 2.7)
        l2 = lane("--mixed", "changes stay, UNSTAGED", MIXED, AMBER, 0.4)
        l3 = lane("--hard", "changes are thrown away", "(clean)", RED, -1.9)
        rl = term(["$ git reflog -3"] + REFLOG, 26); fit(rl, 8.4); rl.move_to([0, 1.4, 0])
        fixl = term(["$ git reset --hard HEAD@{1}"], 30); fit(fixl, 8.4); fixl.move_to([0, -1.1, 0])
        btn = VGroup(RoundedRectangle(corner_radius=0.3, width=4.0, height=1.1, fill_color=RED, fill_opacity=1, stroke_width=0), T("FOLLOW", 38, WHITE, weight=BOLD)); btn[1].move_to(btn[0]); btn.move_to([0, 0.5, 0])
        self.at(0, Write(title), rt=1.0)
        self.at(1, FadeOut(title), FadeIn(chain), FadeIn(main), rt=0.7)
        self.at(2, main.animate.next_to(nodes[1], UP, buff=0.25), nodes[2].animate.set_opacity(0.35), rt=0.9)
        self.at(3, FadeIn(l1, shift=UP * 0.3), rt=0.7)
        self.at(4, FadeIn(l2, shift=UP * 0.3), rt=0.7)
        self.at(5, FadeIn(l3, shift=UP * 0.3), rt=0.7)
        self.at(6, FadeOut(VGroup(l1, l2, l3, chain, main)), FadeIn(rl), rt=0.7)
        self.at(7, FadeIn(fixl), rt=0.7)
        self.at(8, FadeOut(VGroup(rl, fixl)), FadeIn(btn), rt=0.6)
        self.finish()
