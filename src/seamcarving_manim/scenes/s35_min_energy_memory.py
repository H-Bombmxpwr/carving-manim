from manim import *
from seamcarving_manim.style import H1, caption
from pathlib import Path


class MemoryMinEnergyBottomScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # ===== TIMING PARAMETERS (in seconds) =====
        TITLE_RT        = 3
        CAPTION_RT      = 1.2
        STEP_WAIT_SHORT = 2.0
        STEP_WAIT_MED   = 2.0
        SIDE_BY_SIDE_RT = 6.0
        LABELS_RT       = 0.7
        FINAL_HOLD      = 2.5
        CLEAN_EXIT_RT   = 0.8
        # ==========================================

        # Helper: manage a single bottom caption at a time
        bottom_caption = None

        def set_caption(text, rt=CAPTION_RT):
            nonlocal bottom_caption
            new_cap = caption(text).to_edge(DOWN, buff=0.5)
            if bottom_caption is None:
                self.play(FadeIn(new_cap, shift=0.1 * UP), run_time=rt)
            else:
                self.play(
                    FadeOut(bottom_caption, shift=0.1 * DOWN),
                    FadeIn(new_cap, shift=0.1 * UP),
                    run_time=rt,
                )
            bottom_caption = new_cap
            return new_cap

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        title = H1("From Persistence to Min-Energy Map").to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=TITLE_RT)

        # --------------------------------------------------
        # Load images (original, edge map, DP min-energy map)
        # --------------------------------------------------
        base_dir = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "images"
        )
        orig_path = base_dir / "memory.jpg"
        edge_path = base_dir / "memory_edges" / "memory_edge_mag.png"
        dp_path   = base_dir / "min_energy_bottom" / "memory_min_energy_bottom.png"

        orig_img = ImageMobject(str(orig_path))
        edge_img = ImageMobject(str(edge_path))
        dp_img   = ImageMobject(str(dp_path))

        for im in [orig_img, edge_img, dp_img]:
            im.height = 5.0
            im.to_edge(UP, buff=1.0)

        # --------------------------------------------------
        # Step 1: Original image
        # --------------------------------------------------
        self.play(FadeIn(orig_img, shift=0.2 * UP), run_time=STEP_WAIT_MED)
        set_caption("Step 1: Start from the original painting.")
        self.wait(STEP_WAIT_SHORT)

        # --------------------------------------------------
        # Step 2: Sobel edginess map
        # --------------------------------------------------
        set_caption("Step 2: Compute Sobel edginess E(i, j): strong edges = high energy.")
        self.play(ReplacementTransform(orig_img, edge_img), run_time=STEP_WAIT_MED)
        self.wait(STEP_WAIT_SHORT)

        # --------------------------------------------------
        # Step 3: DP min-energy-to-bottom map (orange)
        # --------------------------------------------------
        set_caption("Step 3: DP accumulates the minimum energy from each pixel down.")
        self.play(ReplacementTransform(edge_img, dp_img), run_time=STEP_WAIT_MED)

        set_caption("Bright orange zones are costly; dark channels are easy routes for seams.")
        self.wait(STEP_WAIT_MED)

        # --------------------------------------------------
        # Final view: all three side by side
        # --------------------------------------------------
        orig_small = ImageMobject(str(orig_path))
        edge_small = ImageMobject(str(edge_path))
        dp_small   = ImageMobject(str(dp_path))

        for im in [orig_small, edge_small, dp_small]:
            im.height = 3.0

        row = Group(orig_small, edge_small, dp_small).arrange(RIGHT, buff=0.7)
        row.to_edge(UP, buff=0.9)

        self.play(
            FadeOut(dp_img, shift=UP * 0.2),
            FadeIn(row, shift=UP * 0.2),
            run_time=SIDE_BY_SIDE_RT,
        )

        label_orig  = Text("Original",         font_size=26, color=GRAY_B).next_to(orig_small, DOWN, buff=0.15)
        label_edges = Text("Edginess E(i, j)", font_size=26, color=GRAY_B).next_to(edge_small, DOWN, buff=0.15)
        label_dp    = Text("Min-energy map",   font_size=26, color=GRAY_B).next_to(dp_small,   DOWN, buff=0.15)

        labels = Group(label_orig, label_edges, label_dp)
        self.play(FadeIn(labels), run_time=LABELS_RT)

        set_caption("Left → right: original image, edge energy, and min-energy-to-bottom map.")
        self.wait(FINAL_HOLD)

        # --------------------------------------------------
        # Clean exit
        # --------------------------------------------------
        self.play(
            FadeOut(row),
            FadeOut(labels),
            FadeOut(bottom_caption),
            FadeOut(title),
            run_time=CLEAN_EXIT_RT,
        )
        self.wait(0.3)
