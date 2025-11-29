from manim import *
import numpy as np
from pathlib import Path

from seamcarving_manim.style import H1, caption


class MemoryEdgeWalkthroughScene(Scene):
    def construct(self):
        self.camera.background_color = "#000000"

        TITLE_RT = 0.8
        CAP_RT   = 0.8
        HOLD     = 1.4

        # ------------------------------------------------------------
        # Load precomputed assets
        # ------------------------------------------------------------
        ROOT = Path(__file__).resolve().parents[3]
        D = ROOT / "src" / "seamcarving_manim" / "assets" / "images" / "memory_edges_fast"

        img_orig = ImageMobject(str(D / "orig_color.png"))
        img_x    = ImageMobject(str(D / "sobel_x.png"))
        img_y    = ImageMobject(str(D / "sobel_y.png"))
        img_mag  = ImageMobject(str(D / "sobel_mag.png"))

        vec_x  = np.load(D / "vec_x.npy")
        vec_y  = np.load(D / "vec_y.npy")
        vec_dx = np.load(D / "vec_dx.npy")
        vec_dy = np.load(D / "vec_dy.npy")

        DISP_H = 4.3
        for im in [img_orig, img_x, img_y, img_mag]:
            im.set_height(DISP_H)

        # For mapping normalized coordinates
        W_screen = img_x.width
        H_screen = img_x.height

        LEFT_POS  = LEFT * 3.5
        RIGHT_POS = RIGHT * 3.5

        img_orig.move_to(LEFT_POS)
        img_x.move_to(RIGHT_POS)
        img_y.move_to(RIGHT_POS)
        img_mag.move_to(RIGHT_POS)

        # ------------------------------------------------------------
        # Title + original
        # ------------------------------------------------------------
        title = H1("Sobel Edge Detection on The Persistence of Memory").to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=TITLE_RT)

        self.play(FadeIn(img_orig, shift=UP * 0.1), run_time=1.0)
        cap = caption("Original color image").to_edge(DOWN)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD)

        # Helper: create dense arrows for a given image position and vector subset
        def create_arrow_field(image_mob, dx_factor=1.0, dy_factor=1.0, color=WHITE):
            arrows = VGroup()
            left = image_mob.get_left()[0]
            top  = image_mob.get_top()[1]
            for x_n, y_n, dx, dy in zip(vec_x, vec_y, vec_dx, vec_dy):
                sx = left + x_n * W_screen
                sy = top  - y_n * H_screen
                start = np.array([sx, sy, 0])
                end   = start + np.array([dx * dx_factor, -dy * dy_factor, 0]) * 0.45
                if np.linalg.norm(end - start) < 0.03:
                    continue
                arrows.add(Arrow(start, end, buff=0, stroke_width=1.5, color=color))
            return arrows

        # Helper: row-wise sweep that builds the right image in chunks
        def sweep_build_sobel(target_img, label_text, band_color, is_x=True):
            nonlocal cap

            # Hide previous caption
            self.play(FadeOut(cap, shift=DOWN * 0.1), run_time=0.3)

            cap = caption(label_text).to_edge(DOWN)
            cap.set_color(band_color)
            self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)

            # Show target image but clipped from top with zero height
            target_img.set_opacity(1.0)
            self.add(target_img)

            # Starting with no rows visible (height=0)
            H_full = target_img.height
            CHUNK_ROWS = 10  # conceptual rows; we’ll divide the height into N chunks
            N_STEPS = 20     # number of visible chunks (tunable)
            chunk_height = H_full / N_STEPS

            # Filter band over the original (horizontal strip)
            band = Rectangle(
                width=img_orig.width,
                height=chunk_height,
                fill_color=band_color,
                fill_opacity=0.25,
                stroke_color=band_color,
                stroke_width=1.0,
            )
            band.move_to(img_orig.get_top(), aligned_edge=UP)
            self.add(band)

            # Row-wise sweep
            for step in range(N_STEPS):
                # Move band down on original
                new_y = img_orig.get_top()[1] - chunk_height * (step + 0.5)
                self.play(
                    band.animate.move_to([img_orig.get_center()[0], new_y, 0]),
                    run_time=0.06,
                    rate_func=linear,
                )

                # Update clipping mask on the sobel image to reveal more rows
                mask_height = chunk_height * (step + 1)
                mask = Rectangle(
                    width=target_img.width,
                    height=mask_height,
                    stroke_opacity=0,
                    fill_opacity=0,
                )
                mask.move_to(target_img.get_top(), aligned_edge=UP)
                target_img.set_clip_path(mask)

            self.wait(HOLD)
            self.play(FadeOut(band, run_time=0.5))

        # ------------------------------------------------------------
        # Sobel X: sweep + arrows
        # ------------------------------------------------------------
        sweep_build_sobel(
            target_img=img_x,
            label_text="Applying Sobel X (vertical edges) and building the response",
            band_color=RED,
            is_x=True,
        )

        arrows_x = create_arrow_field(img_x, dx_factor=1.0, dy_factor=0.0, color=RED)
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_x], lag_ratio=0.004),
            run_time=2.5,
        )
        self.wait(HOLD * 1.2)

        # ------------------------------------------------------------
        # Sobel Y: sweep + arrows
        # ------------------------------------------------------------
        self.play(
            FadeOut(arrows_x),
            FadeOut(img_x),
            run_time=0.8,
        )

        sweep_build_sobel(
            target_img=img_y,
            label_text="Applying Sobel Y (horizontal edges) and building the response",
            band_color=BLUE,
            is_x=False,
        )

        arrows_y = create_arrow_field(img_y, dx_factor=0.0, dy_factor=1.0, color=BLUE)
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_y], lag_ratio=0.004),
            run_time=2.5,
        )
        self.wait(HOLD * 1.2)

        # ------------------------------------------------------------
        # Combined gradient ∇I on the original
        # ------------------------------------------------------------
        self.play(
            FadeOut(arrows_y),
            FadeOut(img_y),
            FadeOut(cap),
            run_time=0.8,
        )

        # Bring original to center
        self.play(img_orig.animate.move_to(ORIGIN), run_time=0.9)

        cap = caption("Combine ∂I/∂x and ∂I/∂y → full gradient field ∇I").to_edge(DOWN)
        cap.set_color(GREEN)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)

        arrows_v = create_arrow_field(img_orig, dx_factor=1.0, dy_factor=1.0, color=GREEN)
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_v], lag_ratio=0.004),
            run_time=3.0,
        )
        self.wait(HOLD * 2)

        # ------------------------------------------------------------
        # Magnitude image |∇I|
        # ------------------------------------------------------------
        self.play(
            FadeOut(arrows_v),
            FadeOut(cap),
            run_time=0.9,
        )

        img_mag.move_to(ORIGIN)
        img_mag.set_opacity(0.0)
        self.add(img_mag)

        cap = caption("Edge magnitude |∇I| = √((∂I/∂x)² + (∂I/∂y)²)").to_edge(DOWN)
        cap.set_color(YELLOW)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)

        self.play(img_mag.animate.set_opacity(1.0), run_time=1.6)
        self.wait(HOLD * 2)

        self.play(FadeOut(cap), run_time=0.6)
