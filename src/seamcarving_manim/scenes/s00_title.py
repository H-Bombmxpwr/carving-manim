from manim import *
from seamcarving_manim.style import H1, H2, caption

class TitleScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # --- timing ---
        TITLE_RT = 2.5
        NAME_RT  = 1.5
        CLASS_RT = 1.5
        FINAL_WAIT = 4

        # --- main title ---
        title = H1("Seam Carving: Content-Aware Image Retargeting").scale(0.9)
        title.move_to(UP * 1.5)
        self.play(Write(title), run_time=TITLE_RT)

        # --- your name ---
        name = H2("Hunter Baisden").scale(0.9)
        name.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(name, shift=DOWN * 0.3), run_time=NAME_RT)

        # --- class info ---
        class_info = caption("Image Engineering • Fall 2025")
        class_info.next_to(name, DOWN, buff=0.3)
        self.play(FadeIn(class_info, shift=DOWN * 0.2), run_time=CLASS_RT)

        # --- small linger ---
        self.wait(FINAL_WAIT)
