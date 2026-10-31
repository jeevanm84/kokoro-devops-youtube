"""Episode 001 scenes 06-10."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "templates"))
from brand import *
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from facts import *


class S06(BrandScene):
    SID = "s06"
    def construct(self):
        self.chrome("The stack machine")
        tbl = instr_table(ROWS, 20, 0.62); ip = boxed(tbl, CYAN, 0.5).move_to([-4.2, 0.4, 0])
        it = T("bytecode of add()", 22, MUTED).next_to(ip, UP, buff=0.2)
        ptr = Triangle(color=AMBER, fill_opacity=1).scale(0.15).rotate(-PI / 2)
        at_row = lambda k: tbl[k].get_left() + LEFT * 0.32
        ptr.move_to(at_row(0))
        frame = VGroup(Line([0, 1.9, 0], [0, -1.5, 0]), Line([0, -1.5, 0], [1.9, -1.5, 0]), Line([1.9, -1.5, 0], [1.9, 1.9, 0])).set_color(MUTED).set_stroke(width=5)
        frame.move_to([1.0, 0.2, 0]); st = T("STACK", 24, MUTED).next_to(frame, UP, buff=0.15)
        slot = lambda n: np.array([1.0, -1.1 + 0.8 * n, 0])
        item = lambda v, c: VGroup(card(1.5, 0.66, c, PANEL2), T(v, 30, TEXT, weight=BOLD)).set_z_index(2)
        loc = boxed(VGroup(T("frame locals", 20, GREEN), M("a = 2", 26), M("b = 3", 26)).arrange(DOWN, buff=0.2), GREEN, 0.35).move_to([5.3, 1.5, 0])
        ret = boxed(VGroup(T("caller receives", 20, PINK), M("5", 44, TEXT, weight=BOLD)).arrange(DOWN, buff=0.2), PINK, 0.35).move_to([5.3, -0.9, 0])

        self.at(0, FadeIn(VGroup(ip, it)), FadeIn(ptr), rt=1.0)
        self.play(Create(frame), FadeIn(st), run_time=0.9)
        self.at(1, FadeIn(loc, shift=LEFT * 0.3), rt=1.0)
        i2 = item("2", CYAN).move_to(slot(0)); i3 = item("3", CYAN).move_to(slot(1))
        self.at(2, ptr.animate.move_to(at_row(1)), rt=0.5)
        self.play(FadeIn(i2, shift=DOWN * 0.8), run_time=0.8)
        self.play(ptr.animate.move_to(at_row(2)), run_time=0.5)
        self.play(FadeIn(i3, shift=DOWN * 0.8), run_time=0.8)
        plus = VGroup(Circle(radius=0.5, color=AMBER, fill_color=PANEL, fill_opacity=1), T("+", 44, AMBER)).move_to([3.3, 0.3, 0])
        i5 = item("5", GREEN).move_to(slot(0))
        self.at(3, ptr.animate.move_to(at_row(3)), FadeIn(plus), rt=0.6)
        self.play(i3.animate.move_to(plus.get_left() + UP * 0.35), i2.animate.move_to(plus.get_left() + DOWN * 0.35), run_time=0.9)
        self.play(FadeOut(i2), FadeOut(i3), Flash(plus, color=AMBER, flash_radius=0.8), run_time=0.7)
        self.play(FadeIn(i5, shift=RIGHT * 0.6), FadeOut(plus), run_time=0.8)
        self.at(4, ptr.animate.move_to(at_row(4)), rt=0.5)
        self.play(FadeIn(ret), FadeOut(i5, shift=RIGHT * 1.5), run_time=1.2)
        loop = VGroup(node("fetch", CYAN, 24, w=1.7, h=0.75), node("execute", AMBER, 24, w=1.9, h=0.75), node("next", GREEN, 24, w=1.5, h=0.75)).arrange(RIGHT, buff=0.9).move_to([0.6, -2.45, 0])
        la = VGroup(link(loop[0].get_right(), loop[1].get_left()), link(loop[1].get_right(), loop[2].get_left()))
        back = CurvedArrow(loop[2].get_bottom() + DOWN * 0.05, loop[0].get_bottom() + DOWN * 0.05, angle=-TAU / 6, color=MUTED, stroke_width=4)
        self.at(5, LaggedStart(*[FadeIn(n) for n in loop], lag_ratio=0.3), *[Create(a) for a in la], rt=1.4)
        self.play(Create(back), run_time=0.9)
        self.finish()


class S07(BrandScene):
    SID = "s07"
    def construct(self):
        self.chrome("Names and objects")
        cl = code_block(["x = [1, 2, 3]", "y = x", "y.append(4)", "y = None", "del x"], 26, None, 0.32)
        cp = boxed(cl, MUTED, 0.5).move_to([-4.6, 0.5, 0])
        hl = lambda k: SurroundingRectangle(cl[k], color=AMBER, buff=0.1, corner_radius=0.08)
        mem = T("MEMORY", 22, MUTED).move_to([4.0, 2.7, 0])
        obj = VGroup(card(3.6, 2.1, CYAN, PANEL2), T("list object", 22, CYAN), M("[1, 2, 3]", 30, TEXT), M("refcount: 1", 22, AMBER))
        obj[1].move_to(obj[0].get_top() + DOWN * 0.35); obj[2].move_to(obj[0].get_center() + UP * 0.0); obj[3].move_to(obj[0].get_bottom() + UP * 0.38)
        obj.move_to([4.0, 0.7, 0])
        xt = node("x", VIOLET, 30, w=1.0, h=0.75).move_to([-0.6, 1.3, 0]); yt = node("y", PINK, 30, w=1.0, h=0.75).move_to([-0.6, 0.0, 0])
        ax = link(xt.get_right(), obj[0].get_left() + UP * 0.4, VIOLET); ay = link(yt.get_right(), obj[0].get_left() + DOWN * 0.4, PINK)

        self.at(0, FadeIn(cp), FadeIn(mem), rt=1.0)
        h = hl(0)
        wrong = boxed(VGroup(M("x", 26, VIOLET), M("[1,2,3]", 24)).arrange(DOWN, buff=0.15), RED, 0.35, "#2A1215").move_to([0.9, 0.7, 0])
        wx = VGroup(Line(wrong.get_corner(UL), wrong.get_corner(DR), color=RED, stroke_width=7), Line(wrong.get_corner(UR), wrong.get_corner(DL), color=RED, stroke_width=7))
        self.at(1, Create(h), rt=0.5)
        self.play(FadeIn(wrong), run_time=0.7)
        self.play(Create(wx), run_time=0.6)
        self.at(2, FadeOut(wrong), FadeOut(wx), rt=0.5)
        self.play(FadeIn(obj, shift=LEFT * 0.4), run_time=0.8)
        self.play(FadeIn(xt), GrowArrow(ax), run_time=0.8)
        h2 = hl(1)
        self.at(3, ReplacementTransform(h, h2), rt=0.5)
        self.play(FadeIn(yt), GrowArrow(ay), run_time=0.9)
        self.at(4, Transform(obj[3], M("refcount: 2", 22, AMBER).move_to(obj[3])), rt=0.7)
        self.play(Indicate(obj[3], color=AMBER, scale_factor=1.3), run_time=0.8)
        h3 = hl(2); v4 = M("[1, 2, 3, 4]", 30, TEXT).move_to(obj[2]); note = T("x sees it too", 20, VIOLET).next_to(xt, UP, buff=0.12)
        self.at(5, ReplacementTransform(h2, h3), rt=0.4)
        self.play(Transform(obj[2], v4), FadeIn(note), run_time=0.8)
        h4 = hl(3)
        self.wait(1.2)
        self.play(ReplacementTransform(h3, h4), FadeOut(ay), FadeOut(note), Transform(obj[3], M("refcount: 1", 22, AMBER).move_to(obj[3])), run_time=1.0)
        self.play(yt[0].animate.set_stroke(MUTED), run_time=0.4)
        h5 = hl(4); freed = T("freed", 28, RED, weight=BOLD).move_to(obj[0])
        self.at(6, ReplacementTransform(h4, h5), FadeOut(ax), Transform(obj[3], M("refcount: 0", 22, RED).move_to(obj[3])), rt=0.8)
        self.play(FadeOut(VGroup(obj[1], obj[2])), FadeIn(freed), obj[0].animate.set_stroke(RED), run_time=0.8)
        self.play(FadeOut(VGroup(obj, freed, xt, yt, h5)), run_time=0.7)
        c1 = node("A", AMBER, 28, w=1.0, h=1.0).move_to([3.1, 0.9, 0]); c2 = node("B", GREEN, 28, w=1.0, h=1.0).move_to([5.0, 0.9, 0])
        cyc = VGroup(CurvedArrow(c1.get_top(), c2.get_top(), angle=-PI / 2.5, color=MUTED), CurvedArrow(c2.get_bottom(), c1.get_bottom(), angle=-PI / 2.5, color=MUTED))
        gc = T("cyclic garbage collector", 24, GREEN).move_to([4.0, -0.7, 0])
        self.at(7, FadeIn(VGroup(c1, c2)), *[Create(a) for a in cyc], rt=1.0)
        self.play(FadeIn(gc), run_time=0.8)
        self.finish()


class S08(BrandScene):
    SID = "s08"
    def construct(self):
        self.chrome("Frames and the call stack")
        cl = code_block([f"{i+1}  {s}" for i, s in enumerate(FRAME_SRC)], 20, None, 0.2)
        cp = boxed(cl, MUTED, 0.45).move_to([-4.0, 0.3, 0])
        hl = lambda k: SurroundingRectangle(cl[k], color=AMBER, buff=0.06, corner_radius=0.06)
        title = T("CALL STACK", 22, MUTED).move_to([3.6, 2.4, 0])
        def frame(name, locs, c, y):
            inner = VGroup(T(name, 26, c, weight=BOLD), fit(M(locs, 17, MUTED), 4.0)).arrange(DOWN, buff=0.12)
            g = VGroup(card(4.6, 1.0, c, PANEL2), inner); inner.move_to(g[0])
            return g.move_to([3.6, y, 0])
        fm = frame("<module>", "locals: {}", VIOLET, -1.7); fl = frame("load_user()", "locals: {}  next: line 5", CYAN, -0.55)
        fp = frame("parse()", "raw = ' Ada '  next: line 2", GREEN, 0.6)
        floor = Line([1.2, -2.25, 0], [6.0, -2.25, 0], color=MUTED, stroke_width=4)
        self.at(0, FadeIn(cp), FadeIn(title), Create(floor), rt=1.0)
        h = hl(6)
        self.at(1, Create(h), FadeIn(fm, shift=UP * 0.3), rt=0.8)
        self.play(FadeIn(fl, shift=DOWN * 0.5), run_time=0.9)
        h2 = hl(4)
        self.at(2, ReplacementTransform(h, h2), FadeIn(fp, shift=DOWN * 0.5), rt=1.0)
        h3 = hl(1)
        self.at(3, ReplacementTransform(h2, h3), rt=0.5)
        self.play(FadeOut(fp, shift=UP * 0.6), run_time=0.8)
        tb = code_block(["Traceback (most recent call last):", "  line 7, in <module>", "  line 5, in load_user", "  line 2, in parse"], 18, [MUTED, VIOLET, CYAN, GREEN], 0.22)
        tp = boxed(tb, MUTED, 0.4); fit(tp, 6.0).move_to([-4.0, 0.9, 0])
        err = boxed(VGroup(M("RecursionError:", 18, RED), M("maximum recursion depth exceeded", 18, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15), RED, 0.35, "#2A1215")
        fit(err, 6.0).move_to([-4.0, -1.6, 0])
        self.at(4, FadeOut(VGroup(cp, h3)), FadeIn(fp), rt=0.6)
        self.play(FadeIn(tp), run_time=0.8)
        self.wait(2.0)
        self.play(FadeIn(err, shift=UP * 0.3), run_time=0.9)
        self.finish()


class S09(BrandScene):
    SID = "s09"
    def construct(self):
        self.chrome("Why it matters")
        specs = [("dis module", "See what the\ninterpreter really\nexecutes", CYAN), ("Shared\nreferences", "Why two names can\nchange together", PINK),
                 ("__pycache__", "Why imports are\nfaster the second\ntime", VIOLET), ("Same model,\nevolving details", "CPython · PyPy (JIT)\n3.11+ specializes\nhot bytecode", GREEN)]
        glyph = [M("LOAD_FAST", 18, CYAN), VGroup(Dot(color=VIOLET), Dot(color=PINK), Dot(color=CYAN)).arrange(RIGHT, buff=0.3), M("*.pyc", 22, VIOLET), M("JIT", 24, GREEN)]
        cards = VGroup()
        for (ttl, body, c), g in zip(specs, glyph):
            bg = card(3.15, 4.2, c, PANEL)
            g.move_to(bg.get_top() + DOWN * 0.5)
            tt = fit(T(ttl, 20, c, weight=BOLD, line_spacing=0.9), 2.8).move_to(bg.get_top() + DOWN * 1.5)
            bd = fit(T(body, 18, TEXT, line_spacing=0.9), 2.8).move_to(bg.get_bottom() + UP * 1.0)
            cards.add(VGroup(bg, g, tt, bd))
        cards.arrange(RIGHT, buff=0.3).move_to(DOWN * 0.1)
        ask = T("Where you'll meet this in real projects", 32, TEXT).move_to([0, 3.0, 0])
        self.at(0, FadeIn(ask), rt=0.8)
        for i in range(4):
            self.at(i + 1, FadeIn(cards[i], shift=UP * 0.4), rt=0.9)
            self.play(Indicate(cards[i][2], color=WHITE, scale_factor=1.08), run_time=0.7)
        self.finish()


class S10(BrandScene):
    SID = "s10"
    def construct(self):
        self.chrome("Recap")
        names = ["Source", "Tokens", "AST", "Bytecode", "VM"]; cols = [VIOLET, CYAN, GREEN, AMBER, PINK]
        ns = VGroup(*[node(n, c, 22, w=1.8, h=0.85) for n, c in zip(names, cols)]).arrange(RIGHT, buff=0.6).move_to(UP * 2.5)
        ar = VGroup(*[link(ns[i].get_right(), ns[i + 1].get_left()) for i in range(4)])
        pts = [("1", "tokenize → parse → compile → execute", CYAN), ("2", "names are bound to objects; objects live while referenced", AMBER), ("3", "every call gets its own frame on the call stack", GREEN)]
        rows = VGroup(*[VGroup(node(n, c, 26, w=0.75, h=0.75), T(t, 26, TEXT)).arrange(RIGHT, buff=0.4) for n, t, c in pts]).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(UP * 0.35)
        fit(rows, 12.8)
        self.at(0, FadeIn(ns[0]), rt=0.5)
        self.at(1, LaggedStart(*[AnimationGroup(GrowArrow(ar[i]), FadeIn(ns[i + 1])) for i in range(4)], lag_ratio=0.35), FadeIn(rows[0], shift=RIGHT * 0.3), rt=2.6)
        self.at(2, FadeIn(rows[1], shift=RIGHT * 0.3), rt=0.9)
        self.at(3, FadeIn(rows[2], shift=RIGHT * 0.3), rt=0.9)
        btn = VGroup(RoundedRectangle(corner_radius=0.3, width=3.2, height=0.85, fill_color=RED, fill_opacity=1, stroke_width=0), T("SUBSCRIBE", 28, WHITE, weight=BOLD))
        btn[1].move_to(btn[0]); btn.move_to([-4.2, -2.15, 0])
        nxt = T("Which system should we visualize next?\nTell me in the comments.", 26, TEXT, line_spacing=0.9); fit(nxt, 7.6).move_to([1.8, -2.15, 0])
        self.at(4, FadeIn(btn, shift=UP * 0.3), rt=0.8)
        self.play(FadeIn(nxt), Indicate(btn, color=WHITE, scale_factor=1.08), run_time=1.0)
        self.finish()
