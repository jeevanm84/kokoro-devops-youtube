"""Episode 002 scenes 06-10."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import *


class S06(BrandScene):
    SID = "s06"
    def construct(self):
        self.chrome("git reflog: the safety net")
        nodes, links = commit_chain(["A", "B", "C"], [MUTED, MUTED, RED], 0.4, 0.8)
        chain = VGroup(nodes, links).move_to([-4.6, 1.2, 0])
        main = tag("main", CYAN).next_to(nodes[1], UP, buff=0.22)
        nodes[2].set_opacity(0.3); links[1].set_opacity(0.3)
        lost = T("lost?", 26, RED).next_to(nodes[2], DOWN, buff=0.25)
        t = term(["$ git reflog -3"] + REFLOG, 20); fit(t, 7.2); t.move_to([3.1, 1.2, 0])
        row = t[1][2]
        hl = SurroundingRectangle(row, color=AMBER, buff=0.06, corner_radius=0.06)
        fix = term(["$ git reset --hard HEAD@{1}"], 24).move_to([3.1, -0.8, 0])
        note = T("local only · old entries expire", 26, AMBER).move_to([0, -2.4, 0])
        self.at(0, FadeIn(chain), FadeIn(main), FadeIn(lost), rt=1.0)
        self.at(1, FadeOut(lost), FadeIn(t), rt=1.2)
        self.at(2, Create(hl), rt=0.6)
        self.play(FadeIn(fix), run_time=0.8)
        self.play(main.animate.next_to(nodes[2], UP, buff=0.22), nodes[2].animate.set_opacity(1), links[1].animate.set_opacity(1), run_time=1.0)
        self.at(3, FadeIn(note), rt=1.0)
        self.finish()


class S07(BrandScene):
    SID = "s07"
    def construct(self):
        self.chrome("Replay: the lab in 60 seconds")
        nodes, links = commit_chain(["A", "B", "C"], [MUTED, MUTED, RED], 0.34, 0.7)
        chain = VGroup(nodes, links).move_to([-4.6, 3.0, 0]); cap = T("a throwaway repo, C is the mistake", 24, MUTED).move_to([1.2, 3.0, 0])
        hard = HARD if HARD else "(clean: no output)"
        a = term(["$ git reset --soft HEAD~1", "$ git status --short", SOFT], 20, 0.3)
        b = term(["$ git reset --mixed HEAD~1", "$ git status --short", MIXED], 20, 0.3)
        c = term(["$ git reset --hard HEAD~1", "$ git status --short", hard], 20, 0.3)
        d = term(["$ git reflog -3"] + REFLOG, 18, 0.3); fit(d, 6.4); d.move_to([3.4, -1.6, 0])
        e = term(["$ git reflog -3"] + REFLOG + ["$ git reset --hard HEAD@{1}"], 18, 0.3); fit(e, 6.4); e.move_to([3.4, -1.6, 0])
        for x in (a, b, c): fit(x, 6.4)
        a.move_to([-3.4, 0.95, 0]); b.move_to([3.4, 0.95, 0]); c.move_to([-3.4, -1.6, 0])
        self.at(0, FadeIn(chain), FadeIn(cap), rt=1.0)
        self.at(1, FadeIn(a), rt=1.0)
        self.at(2, FadeIn(b), rt=1.0)
        self.at(3, FadeIn(c), rt=1.0)
        self.at(4, FadeIn(d), rt=1.0)
        self.at(5, FadeOut(d), FadeIn(e), rt=0.8)
        self.finish()


class S08(BrandScene):
    SID = "s08"
    def construct(self):
        self.chrome("Mistakes that cost teams hours")
        spec = [("1", "Reset a pushed commit,\nthen force-push", "Teammates' branches now\ndisagree with yours.\nUse revert, or --force-with-lease\nafter telling the team."),
                ("2", "reset --hard with\nuncommitted edits", "The reflog tracks commits,\nso edits you never committed\nare generally gone for good."),
                ("3", "Thinking revert\nremoves a secret", "The old commit stays in history.\nRotate the credential first,\nthen clean history if needed.")]
        cards = VGroup()
        for n, ttl, body in spec:
            bg = card(4.0, 4.3, RED, "#1A1014")
            num = T(n, 54, RED, weight=BOLD).move_to(bg.get_top() + DOWN * 0.7)
            tt = fit(T(ttl, 24, TEXT, weight=BOLD, line_spacing=0.9), 3.5).move_to(bg.get_center() + UP * 0.1)
            bd = fit(T(body, 18, MUTED, line_spacing=0.95), 3.5).move_to(bg.get_bottom() + UP * 1.1)
            cards.add(VGroup(bg, num, tt, bd))
        cards.arrange(RIGHT, buff=0.4).move_to([0, 0.1, 0])
        ask = T("Three mistakes that keep happening", 32, TEXT).move_to([0, 3.0, 0])
        self.at(0, FadeIn(ask), rt=0.8)
        for i in range(3):
            self.at(i + 1, FadeIn(cards[i], shift=UP * 0.4), rt=1.0)
        self.finish()


class S09(BrandScene):
    SID = "s09"
    def construct(self):
        self.chrome("Answering this in an interview")
        sc = boxed(T("Scenario: a faulty commit is on protected main, and already deployed", 28, TEXT), RED, 0.4, "#2A1215"); fit(sc, 12.4); sc.move_to([0, 2.1, 0])
        steps = ["Impact", "Evidence", "Investigation", "Mitigation", "Communication", "Permanent fix", "Prevention"]
        cols = [RED, VIOLET, VIOLET, AMBER, CYAN, GREEN, GREEN]
        ns = [node(s_, c, 20, w=2.9, h=0.8) for s_, c in zip(steps, cols)]
        r1 = VGroup(*ns[:4]).arrange(RIGHT, buff=0.5).move_to([0, 0.5, 0]); r2 = VGroup(*ns[4:]).arrange(RIGHT, buff=0.5).move_to([0, -1.4, 0])
        ar = [link(ns[i].get_right(), ns[i + 1].get_left()) for i in range(3)] + [link(ns[4].get_right(), ns[5].get_left()), link(ns[5].get_right(), ns[6].get_left())]
        mid = -0.45; p0 = ns[3].get_bottom(); p3 = ns[4].get_top()
        elbow = VGroup(Line(p0, [p0[0], mid, 0], color=MUTED, stroke_width=4), Line([p0[0], mid, 0], [p3[0], mid, 0], color=MUTED, stroke_width=4), Arrow([p3[0], mid, 0], p3, buff=0, color=MUTED, stroke_width=4, max_tip_length_to_length_ratio=0.3))
        capm = []
        for n_, txt, c, pos in ((ns[3], "git revert (main is shared)", AMBER, UP), (ns[5], "a tested change", GREEN, DOWN), (ns[6], "branch protection,\nrequired checks", GREEN, DOWN)):
            m = T(txt, 20, c, line_spacing=0.9); fit(m, 3.4); m.next_to(n_, pos, buff=0.18); capm.append(m)
        self.at(0, FadeIn(T("Interviewers ask for scenarios, not command names", 30, TEXT).move_to([0, 3.05, 0])), rt=0.8)
        self.at(1, FadeIn(sc), rt=1.0)
        self.at(2, LaggedStart(*[FadeIn(n_, shift=UP * 0.2) for n_ in ns], lag_ratio=0.25), *[Create(a_) for a_ in ar], Create(elbow), rt=3.8)
        self.at(3, LaggedStart(*[FadeIn(m) for m in capm], lag_ratio=0.5), rt=2.4)
        self.at(4, *[Indicate(n_, scale_factor=1.08) for n_ in ns], rt=2.0)
        self.finish()


class S10(BrandScene):
    SID = "s10"
    def construct(self):
        self.chrome("Practice and recap")
        repo = boxed(VGroup(M("git-command-master-map", 30, CYAN), T("Lab 05 · Undo and reflog recovery", 26, TEXT), M("github.com/jeevanm84/git-command-master-map", 20, MUTED)).arrange(DOWN, buff=0.2), CYAN, 0.45)
        fit(repo, 12.0); repo.move_to([0, 1.45, 0])
        chips = VGroup(*[node(t, c, 22, w=2.9, h=0.85) for t, c in (("restore: files", CYAN), ("reset: branch", AMBER), ("revert: shared", GREEN), ("reflog: rescue", VIOLET))]).arrange(RIGHT, buff=0.3).move_to([0, -0.35, 0])
        btn = VGroup(RoundedRectangle(corner_radius=0.3, width=3.2, height=0.85, fill_color=RED, fill_opacity=1, stroke_width=0), T("SUBSCRIBE", 28, WHITE, weight=BOLD)); btn[1].move_to(btn[0]); btn.move_to([-4.2, -1.6, 0])
        nxt = T("Which Git scenario next?\nTell me in the comments.", 26, TEXT, line_spacing=0.9); fit(nxt, 7.6).move_to([1.8, -1.6, 0])
        note = T("Predict the result, then run it.", 24, MUTED).move_to([0, -2.5, 0])
        self.at(0, FadeIn(T("Practise in a safe sandbox", 34, TEXT).move_to([0, 3.15, 0])), rt=0.8)
        self.at(1, FadeIn(repo), rt=1.0)
        self.at(2, Indicate(repo, color=AMBER, scale_factor=1.03), rt=1.0)
        self.at(3, LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in chips], lag_ratio=0.5), rt=3.0)
        self.at(4, FadeIn(btn), FadeIn(nxt), rt=1.0)
        self.at(5, FadeIn(note), rt=1.0)
        self.finish()
