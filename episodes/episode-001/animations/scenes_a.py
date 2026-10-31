"""Episode 001 scenes 01-05. Every visual is keyed to narration cues via BrandScene.at()."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "templates"))
from brand import *
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from facts import *


class S01(BrandScene):
    SID = "s01"
    def construct(self):
        self.chrome("The question")
        term = card(4.9, 3.2, MUTED, "#0A0F1A").move_to([-4.45, 0.1, 0])
        bar = Rectangle(width=4.9, height=0.48, fill_color=PANEL2, fill_opacity=1, stroke_width=0).move_to(term.get_top() + DOWN * 0.24)
        dots = VGroup(*[Dot(radius=0.07, color=c) for c in (RED, AMBER, GREEN)]).arrange(RIGHT, buff=0.14).move_to(bar.get_left() + RIGHT * 0.5)
        cmd = fit(M("$ python app.py", 32, GREEN), 4.4).move_to(term.get_center() + UP * 0.35)
        box = card(3.0, 3.2, CYAN, PANEL).move_to([0.5, 0.1, 0])
        q = T("?", 140, CYAN).move_to(box)
        out = card(3.4, 2.2, MUTED, "#0A0F1A").move_to([5.2, 0.1, 0])
        outt = fit(M("Hello, world!", 28, TEXT), 3.0).move_to(out)
        a1 = link(term.get_right(), box.get_left(), MUTED); a2 = link(box.get_right(), out.get_left(), MUTED)

        self.at(0, FadeIn(VGroup(term, bar, dots)), rt=0.8)
        self.play(Write(cmd), run_time=1.4)
        self.play(GrowArrow(a1), FadeIn(box), Write(q), run_time=1.0)
        self.play(GrowArrow(a2), FadeIn(VGroup(out, outt)), run_time=1.0)
        self.at(1, pulse(q, color=AMBER, scale_factor=1.3), rt=1.2)
        ask = VGroup(T("interpreted?", 44, VIOLET), T("or", 34, MUTED), T("compiled?", 44, PINK)).arrange(RIGHT, buff=0.55).move_to([0.2, 2.95, 0])
        self.at(2, LaggedStart(*[FadeIn(m, shift=DOWN * 0.3) for m in ask], lag_ratio=0.5), rt=1.8)
        both = fit(T("BOTH", 64, AMBER, weight=BOLD), 2.7).move_to(box)
        self.at(3, ReplacementTransform(q, both), box.animate.set_stroke(AMBER), FadeOut(ask), rt=1.0)
        self.play(Flash(both, color=AMBER, flash_radius=1.4), run_time=0.8)
        self.finish()


class S02(BrandScene):
    SID = "s02"
    def construct(self):
        self.chrome("Compiled and interpreted")
        lines = code_block(["import os", "x = 10", "y = x * 2", "print(y)", "os.exit()"], 30, [MUTED] * 5, buff=0.3)
        panel = boxed(lines, MUTED, 0.5).move_to([-3.2, -0.2, 0])
        label = T("“Interpreted” = reads line by line?", 34, MUTED).move_to([0, 2.7, 0])
        ptr = Triangle(color=CYAN, fill_opacity=1).scale(0.18).rotate(-PI / 2).next_to(lines[0], LEFT, buff=0.3)
        self.at(0, FadeIn(VGroup(panel, label)), FadeIn(ptr), rt=0.8)
        for ln in list(lines)[1:]:
            self.play(ptr.animate.next_to(ln, LEFT, buff=0.3), run_time=0.7)
        cross = VGroup(Line(panel[0].get_corner(UL), panel[0].get_corner(DR), color=RED, stroke_width=9),
                       Line(panel[0].get_corner(UR), panel[0].get_corner(DL), color=RED, stroke_width=9))
        self.at(1, Create(cross), label.animate.set_color(RED), rt=0.8)
        names = ["source.py", "compiler", "bytecode", "Python VM"]; cols = [VIOLET, AMBER, CYAN, GREEN]
        ns = VGroup(*[node(n, c, 26, w=2.4, h=1.2) for n, c in zip(names, cols)]).arrange(RIGHT, buff=0.8).move_to(UP * 0.7)
        arrows = VGroup(*[link(ns[i].get_right(), ns[i + 1].get_left()) for i in range(3)])
        self.at(2, FadeOut(VGroup(panel, lines, label, ptr, cross)), rt=0.6)
        self.play(LaggedStart(FadeIn(ns[0]), GrowArrow(arrows[0]), FadeIn(ns[1]), GrowArrow(arrows[1]), FadeIn(ns[2]), lag_ratio=0.35), run_time=2.4)
        pk = Dot(radius=0.15, color=AMBER).move_to(ns[0].get_top() + UP * 0.3)
        self.at(3, GrowArrow(arrows[2]), FadeIn(ns[3]), FadeIn(pk), rt=1.0)
        for k in (1, 2, 3):
            self.play(pk.animate.move_to(ns[k].get_top() + UP * 0.3), run_time=0.7)
        self.play(FadeOut(pk), run_time=0.3)
        u1 = Line(ns[0].get_bottom() + DOWN * 0.4 + LEFT * 1.3, ns[2].get_bottom() + DOWN * 0.4 + RIGHT * 1.3, color=AMBER, stroke_width=6)
        u2 = Line(ns[2].get_bottom() + DOWN * 1.15 + LEFT * 1.3, ns[3].get_bottom() + DOWN * 1.15 + RIGHT * 1.3, color=GREEN, stroke_width=6)
        t1 = T("COMPILE", 32, AMBER).next_to(u1, DOWN, buff=0.15); t2 = T("INTERPRET", 32, GREEN).next_to(u2, DOWN, buff=0.15)
        self.at(4, Create(u1), FadeIn(t1), rt=1.0)
        self.play(Create(u2), FadeIn(t2), run_time=1.0)
        self.finish()


class S03(BrandScene):
    SID = "s03"
    def construct(self):
        self.chrome("The pipeline")
        names = ["Source\ncode", "Tokens", "AST", "Bytecode", "Output"]
        subs = ["text", "token list", "tree", "instructions", "result"]
        cols = [VIOLET, CYAN, GREEN, AMBER, PINK]
        ns = VGroup(*[node(n, c, 22, w=1.75, h=1.4) for n, c in zip(names, cols)]).arrange(RIGHT, buff=1.15).move_to(UP * 0.3)
        sub = VGroup(*[T(s, 20, MUTED).next_to(n, DOWN, buff=0.25) for s, n in zip(subs, ns)])
        arrows = VGroup(*[link(ns[i].get_right(), ns[i + 1].get_left()) for i in range(4)])
        stage = ["tokenizer", "parser", "compiler", "virtual\nmachine"]
        sl = VGroup(*[T(s, 18, AMBER).move_to([a.get_center()[0], ns[0].get_top()[1] + 0.7, 0]) for s, a in zip(stage, arrows)])
        top = lambda n: n.get_top() + UP * 0.22
        pk = Dot(radius=0.15, color=AMBER).move_to(top(ns[0]))
        self.at(0, FadeIn(ns[0]), FadeIn(sub[0]), FadeIn(pk), rt=0.8)
        for i in range(4):
            self.at(i + 1, GrowArrow(arrows[i]), FadeIn(sl[i], shift=DOWN * 0.2), rt=0.8)
            self.play(pk.animate.move_to(top(ns[i + 1])), FadeIn(ns[i + 1]), FadeIn(sub[i + 1]), run_time=1.0)
            self.play(pulse(ns[i + 1], color=cols[i + 1], scale_factor=1.12), run_time=0.7)
        self.play(FadeOut(pk), run_time=0.3)
        self.at(5, *[pulse(n, scale_factor=1.1) for n in ns], rt=1.2)
        self.finish()


class S04(BrandScene):
    SID = "s04"
    def construct(self):
        self.chrome("Tokens and the syntax tree")
        toks = [t for t, _ in TOKENS]; kinds = [k for _, k in TOKENS]; cols = [CYAN, AMBER, CYAN, AMBER, GREEN]
        tm = VGroup(*[M(t, 44, c) for t, c in zip(toks, cols)]).arrange(RIGHT, buff=0.3).move_to(UP * 2.75)
        self.at(0, Write(tm), rt=1.5)
        self.play(pulse(tm, color=AMBER, scale_factor=1.05), run_time=0.8)
        spread = tm.copy().arrange(RIGHT, buff=0.85).move_to(UP * 2.75)
        boxes = VGroup(*[SurroundingRectangle(t, color=c, buff=0.14, corner_radius=0.1) for t, c in zip(spread, cols)])
        kl = VGroup(*[T(k, 20, c).next_to(b, DOWN, buff=0.1) for k, b, c in zip(kinds, boxes, cols)])
        self.at(1, Transform(tm, spread), rt=1.0)
        self.play(LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.25), FadeIn(kl), run_time=1.6)
        nd = lambda txt, c: node(txt, c, 20, h=0.65)
        assign = nd("Assign", VIOLET).move_to([1.0, 0.7, 0])
        tgt = nd("Name: total", CYAN).move_to([-1.2, -0.65, 0])
        binop = nd("BinOp", GREEN).move_to([3.3, -0.65, 0])
        lft = nd("Name: price", CYAN).move_to([1.15, -2.0, 0])
        op = nd("Mult", AMBER).move_to([3.3, -2.0, 0])
        rgt = nd("Constant: 2", GREEN).move_to([5.45, -2.0, 0])
        ln = lambda p, c: Line(p.get_bottom(), c.get_top(), color=MUTED, stroke_width=3)
        edges = [ln(assign, tgt), ln(assign, binop), ln(binop, lft), ln(binop, op), ln(binop, rgt)]
        self.at(2, FadeIn(assign, shift=DOWN * 0.3), rt=0.8)
        self.play(*[Create(e) for e in edges[:2]], FadeIn(tgt), FadeIn(binop), run_time=1.0)
        self.at(3, pulse(assign, color=VIOLET), rt=1.0)
        self.play(*[Create(e) for e in edges[2:]], FadeIn(lft), FadeIn(op), FadeIn(rgt), run_time=1.4)
        self.play(pulse(binop, color=GREEN, scale_factor=1.15), run_time=0.9)
        err = boxed(VGroup(T("SyntaxError", 22, RED, weight=BOLD), T("caught here,\nbefore running", 18, TEXT)).arrange(DOWN, buff=0.15), RED, 0.3, "#2A1215")
        err.move_to([-5.3, -1.7, 0])
        self.at(4, pulse(VGroup(assign, tgt, binop, lft, op, rgt), scale_factor=1.04), rt=1.4)
        self.play(FadeIn(err, shift=RIGHT * 0.4), run_time=1.0)
        self.finish()


class S05(BrandScene):
    SID = "s05"
    def construct(self):
        self.chrome("Bytecode")
        code = code_block(["def add(a, b):", "    return a + b"], 26, [CYAN, TEXT], 0.3)
        cp = boxed(VGroup(T("Source", 20, MUTED), code).arrange(DOWN, aligned_edge=LEFT, buff=0.25), MUTED, 0.4).move_to([-3.9, 2.0, 0])
        tbl = instr_table(ROWS, 22, 0.52)
        dp = boxed(VGroup(T("dis.dis(add)", 20, MUTED), tbl).arrange(DOWN, buff=0.3), CYAN, 0.4).move_to([-3.9, -1.3, 0])
        cobj = VGroup(T("code object", 26, GREEN, weight=BOLD), M(f"co_code   {CO_CODE_PREFIX} …", 20), M(f"co_consts {CO_CONSTS}", 20),
                      M(f"co_varnames {CO_VARNAMES}", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        cop = boxed(cobj, GREEN, 0.4).move_to([3.5, 0.9, 0])
        pyc = boxed(VGroup(M("__pycache__/", 22, VIOLET), M(PYC_FILE, 18)).arrange(DOWN, aligned_edge=LEFT, buff=0.2), VIOLET, 0.35).move_to([3.5, -1.8, 0])
        arr = link(cp.get_bottom(), dp.get_top()); arr_l = T("compile", 22, AMBER).next_to(arr, RIGHT, buff=0.2)
        arr2 = link(dp.get_right(), cop.get_left(), GREEN); arr2_l = T("stored in", 20, GREEN).next_to(arr2, UP, buff=0.08)
        a3 = link(cop.get_bottom(), pyc.get_top(), VIOLET); a3_l = T("cached", 20, VIOLET).next_to(a3, RIGHT, buff=0.15)
        self.at(0, FadeIn(T("AST  →  bytecode", 30, AMBER).move_to([0.8, 3.35, 0])), rt=0.8)
        self.at(1, FadeIn(cp), rt=0.9)
        self.at(2, GrowArrow(arr), FadeIn(arr_l), FadeIn(dp), rt=1.2)
        hl = SurroundingRectangle(tbl[1], color=AMBER, buff=0.07, corner_radius=0.08)
        self.at(3, Create(hl), rt=0.5)
        for k in (2, 3, 4):
            self.play(hl.animate.become(SurroundingRectangle(tbl[k], color=AMBER, buff=0.07, corner_radius=0.08)), run_time=0.55)
            self.wait(0.55)
        self.at(4, FadeOut(hl), GrowArrow(arr2), FadeIn(arr2_l), FadeIn(cop), rt=1.2)
        self.play(pulse(dp, color=GREEN, scale_factor=1.02), run_time=0.8)
        self.at(5, GrowArrow(a3), FadeIn(a3_l), FadeIn(pyc), rt=1.2)
        self.finish()
