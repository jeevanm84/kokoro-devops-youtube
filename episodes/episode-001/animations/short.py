"""YouTube Short (1080x1920). Portrait frame is 9 x 16 units; captions are burned in near y=-3.7 by ffmpeg,
so all content stays above y=-3.2 and clear of the top UI band."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "templates"))
from brand import *
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from facts import *
config.frame_width, config.frame_height = 9, 16


class ShortHook(BrandScene):
    SID = "short"
    def construct(self):
        self.add(T(CHANNEL, 24, MUTED).move_to([0, 7.0, 0]))
        title = VGroup(*[T(s, 66, TEXT, weight=BOLD) for s in ("Python:", "interpreted", "or compiled?")]).arrange(DOWN, buff=0.25).move_to([0, 4.6, 0])
        both = T("BOTH.", 110, AMBER, weight=BOLD).move_to([0, 1.2, 0])
        code = code_block(["def add(a, b):", "    return a + b"], 36, [CYAN, TEXT], 0.3)
        cc = boxed(code, MUTED, 0.5).move_to([0, 5.2, 0])
        carrow = link([0, 4.0, 0], [0, 3.1, 0], AMBER); clab = T("CPython compiles", 26, AMBER).next_to(carrow, RIGHT, buff=0.25)
        tbl = instr_table(ROWS, 28, 0.68); dis = boxed(tbl, CYAN, 0.55).move_to([0, 0.4, 0])
        frame = VGroup(Line([0, 1.5, 0], [0, -2.1, 0]), Line([0, -2.1, 0], [2.4, -2.1, 0]), Line([2.4, -2.1, 0], [2.4, 1.5, 0])).set_color(MUTED).set_stroke(width=7)
        frame.move_to([0, -0.3, 0]); vm = T("Python VM · stack", 30, GREEN).next_to(frame, UP, buff=0.2)
        slot = lambda n: np.array([0, -1.65 + 0.85 * n, 0])
        item = lambda v, c: VGroup(card(1.9, 0.72, c, PANEL2), T(v, 36, TEXT, weight=BOLD))

        self.at(0, Write(title), rt=1.0)
        self.at(1, FadeIn(both, scale=1.4), rt=0.6)
        self.play(Flash(both, color=AMBER, flash_radius=1.8), run_time=0.7)
        self.at(2, FadeOut(both), FadeOut(title), rt=0.5)
        self.play(FadeIn(cc), run_time=0.7)
        self.play(GrowArrow(carrow), FadeIn(clab), run_time=0.7)
        self.at(3, FadeIn(dis, shift=UP * 0.3), rt=0.9)
        hl = SurroundingRectangle(tbl[1], color=AMBER, buff=0.1, corner_radius=0.08)
        self.at(4, Create(hl), rt=0.35)
        for k in (2, 3, 4):
            self.wait(0.15)
            self.play(hl.animate.become(SurroundingRectangle(tbl[k], color=AMBER, buff=0.1, corner_radius=0.08)), run_time=0.4)
        self.at(5, FadeOut(VGroup(cc, carrow, clab, hl)), dis.animate.move_to([0, 4.4, 0]), rt=0.9)
        self.play(Create(frame), FadeIn(vm), run_time=0.7)
        i2, i3, i5 = item("2", CYAN).move_to(slot(0)), item("3", CYAN).move_to(slot(1)), item("5", GREEN).move_to(slot(0))
        self.at(6, FadeIn(i2, shift=DOWN * 0.8), rt=0.6)
        self.play(FadeIn(i3, shift=DOWN * 0.8), run_time=0.6)
        self.play(FadeOut(i2), FadeOut(i3), run_time=0.5)
        self.play(FadeIn(i5, shift=UP * 0.4), run_time=0.6)
        ban = VGroup(T("compiled", 76, AMBER, weight=BOLD), T("↓", 60, MUTED), T("interpreted", 76, GREEN, weight=BOLD)).arrange(DOWN, buff=0.25)
        fit(ban, 8.2).move_to([0, -0.2, 0])
        self.at(7, FadeOut(VGroup(frame, vm, i5, dis)), FadeIn(ban, shift=UP * 0.3), rt=0.9)
        btn = VGroup(RoundedRectangle(corner_radius=0.3, width=4.0, height=1.1, fill_color=RED, fill_opacity=1, stroke_width=0), T("FOLLOW", 38, WHITE, weight=BOLD))
        btn[1].move_to(btn[0]); btn.move_to([0, -0.2, 0])
        self.at(8, FadeOut(ban), FadeIn(btn), rt=0.6)
        self.finish()
