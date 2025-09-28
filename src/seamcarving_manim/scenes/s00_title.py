from manim import *
from seamcarving_manim.style import H1, H2, caption

class TitleScene(Scene):
    def construct(self):
        # --- timing knobs (≈15 s total) ---
        TITLE_RT   = 2.4
        SUB_RT     = 1.2
        BULLET_RT  = 3.2   # each bullet
        BAR_RT     = 1.0
        FOOTER_RT  = 1.0
        FINAL_WAIT = 4

        # --- title & subtitle (scaled + buffered to avoid clipping) ---
        title = H1("Seam Carving: Content-Aware Image Retargeting").scale(0.85)
        title.to_edge(UP, buff=0.6)
        self.play(Write(title), run_time=TITLE_RT)

        subtitle = H2("Energy → Dynamic Programming → Seam Removal (with demos)").scale(0.95)
        subtitle.next_to(title, DOWN, buff=0.45)
        self.play(FadeIn(subtitle, shift=DOWN*0.2), run_time=SUB_RT)

        # --- bullets: appear individually ---
        b1 = caption("• Why crop/scale fail on salient content").to_edge(LEFT).shift(DOWN*0.5)
        b2 = caption("• Energy maps on luminance (Sobel/Scharr)").next_to(b1, DOWN, aligned_edge=LEFT, buff=0.22)
        b3 = caption("• DP fill + backtrack to find minimal seams").next_to(b2, DOWN, aligned_edge=LEFT, buff=0.22)
        b4 = caption("• Forward energy, protect masks (faces/text)").next_to(b3, DOWN, aligned_edge=LEFT, buff=0.22)
        b5 = caption("• System view: display + bandwidth wins").next_to(b4, DOWN, aligned_edge=LEFT, buff=0.22)

        for b in [b1, b2, b3, b4, b5]:
            self.play(FadeIn(b, shift=RIGHT*0.3), run_time=BULLET_RT)

        # accent bar sized to the bullet stack
        bar = Rectangle(width=0.08, height=(b5.get_bottom()[1]-b1.get_top()[1])*-1 + 0.2,
                        fill_opacity=1, stroke_width=0).set_color(YELLOW)
        bar.next_to(VGroup(b1, b2, b3, b4, b5), LEFT, buff=0.25)
        self.play(GrowFromPoint(bar, bar.get_bottom()), run_time=BAR_RT)

        # footer, slightly above bottom to avoid edge cut-off
        footer = VGroup(
            caption("Hunter  •  Image Engineering"),
            caption("Runtime ≈ 13 minutes"),
        ).arrange(DOWN, buff=0.1).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(footer, shift=UP*0.2), run_time=FOOTER_RT)

        self.wait(FINAL_WAIT)
