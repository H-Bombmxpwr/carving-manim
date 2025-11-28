from manim import *
from pathlib import Path

try:
    from seamcarving_manim.style import H1, caption
except:
    def H1(t): return Text(t, font_size=42, weight=BOLD, color=WHITE)
    def caption(t): return Text(t, font_size=26, color=GRAY_B)


class FinalCreditsScene(Scene):
    def construct(self):
        self.camera.background_color = "#0a0a0a"

        # ============================================================
        # TIMING CONSTANTS
        # ============================================================
        TITLE_RT     = 0.8
        CAP_RT       = 0.7
        BULLET_DELAY = 2.0
        BULLET_FADE  = 0.7
        HOLD         = 2.0

        # ============================================================
        # 1. CREDITS + SUMMARY
        # ============================================================
        title = H1("Seam Carving: Content-Aware Resizing").to_edge(UP, buff=0.6)
        byline = Text(
            "Created by Hunter Baisden",
            font_size=30,
            color=GRAY_C
        ).next_to(title, DOWN, buff=0.3)

        bullets = [
            Text("• Sobel filters for edge strength", font_size=28, color=GRAY_B),
            Text("• Gradient → Edginess map → Energy", font_size=28, color=GRAY_B),
            Text("• DP min-energy paths to the bottom", font_size=28, color=GRAY_B),
            Text("• Why other shrink methods fail", font_size=28, color=GRAY_B),
        ]

        bullet_group = VGroup(*bullets).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.25
        ).next_to(byline, DOWN, buff=0.5)

        # --- title + byline ---
        self.play(Write(title), run_time=TITLE_RT)
        self.play(FadeIn(byline, shift=UP * 0.1), run_time=CAP_RT)

        # --- bullets one-by-one with 2-second spacing ---
        for b in bullets:
            self.play(FadeIn(b, shift=RIGHT * 0.2), run_time=BULLET_FADE)
            self.wait(BULLET_DELAY)

        self.wait(HOLD)

        # Fade everything out
        self.play(
            FadeOut(title, shift=UP * 0.2),
            FadeOut(byline, shift=UP * 0.2),
            FadeOut(bullet_group, shift=UP * 0.2),
            run_time=0.8,
        )

        # ============================================================
        # 2. REFERENCES GRID – tightened spacing + lowered so title is clear
        # ============================================================

        refs_title = H1("References").to_edge(UP, buff=0.4)
        self.play(FadeIn(refs_title, shift=UP * 0.2), run_time=TITLE_RT)

        repo_root = Path(__file__).resolve().parents[3]
        thumb_root = (
            repo_root
            / "src"
            / "seamcarving_manim"
            / "assets"
            / "images"
            / "final_scene"
        )

        items = [
            ("MIT Intro to Computational Thinking", thumb_root / "mit.png"),
            ("Original Seam Carving Paper",        thumb_root / "paper.png"),
            ("Python Seam-Carving Package",        thumb_root / "python.png"),
            ("Wikipedia: Seam Carving",            thumb_root / "wikipedia.png"),
        ]

        tiles = []
        for name, img_path in items:
            thumb = ImageMobject(str(img_path)).set_height(1.9)

            frame = RoundedRectangle(
                width=thumb.width + 0.12,
                height=thumb.height + 0.12,
                corner_radius=0.1,
                stroke_color=WHITE,
                stroke_width=2,
                fill_opacity=0,
            ).move_to(thumb)

            label = Text(name, font_size=20, color=WHITE).next_to(thumb, DOWN, buff=0.2)
            tile = Group(frame, thumb, label)
            tiles.append(tile)

        # *** Tightened spacing AND moved grid downward ***
        grid = Group(*tiles).arrange_in_grid(
            rows=2,
            cols=2,
            buff=1.0,             # tighter so it doesn't collide with the title
            cell_alignment=UP,
        ).next_to(refs_title, DOWN, buff=0.6)  # more buffer so title is visible

        self.play(FadeIn(grid, shift=UP * 0.2), run_time=1.0)
        self.wait(HOLD * 2)

        # Fade out everything
        self.play(
            FadeOut(refs_title, shift=UP * 0.2),
            FadeOut(grid, shift=DOWN * 0.2),
            run_time=1.0,
        )

        # ============================================================
        # 3. FINAL “THANKS FOR WATCHING”
        # ============================================================

        thanks = Text(
            "Thanks for watching!",
            font_size=38,
            color=GRAY_B,
            weight=BOLD
        ).move_to(ORIGIN)

        self.play(FadeIn(thanks, shift=UP * 0.15), run_time=1.0)
        self.wait(3.0)   # stays on screen at the very end

        self.play(FadeOut(thanks, run_time=0.8))
        self.wait(0.3)
