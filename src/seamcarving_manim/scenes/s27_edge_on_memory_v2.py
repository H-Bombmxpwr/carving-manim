from manim import *
import numpy as np
from pathlib import Path

from seamcarving_manim.style import H1, caption

# =================== TIMING CONSTANTS ===================
TITLE_RT         = 0.8
CAP_RT           = 0.8
HOLD             = 1.4

BLOCK_RT_X       = 0.1  # per 3x3 block for Sobel X sweep
BLOCK_RT_Y       = 0.1  # per 3x3 block for Sobel Y sweep

ARROWS_RT_X      = 5.0
ARROWS_RT_Y      = 5.0
ARROWS_RT_COMB   = 6.5

MAG_CROSSFADE_RT = 2.0
# =======================================================


class MemoryEdgeWalkthroughScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # Colors
        KERNEL_COLOR_X   = RED
        KERNEL_COLOR_Y   = BLUE
        GRAD_COLOR_X     = RED
        GRAD_COLOR_Y     = BLUE
        GRAD_COLOR_COMB  = GREEN
        MAG_COLOR        = YELLOW

        # -------------------------------------------------------
        # Load assets and gradient field
        # -------------------------------------------------------
        ROOT = Path(__file__).resolve().parents[3]
        IMG_DIR = ROOT / "src" / "seamcarving_manim" / "assets" / "images"
        EDGES_DIR = IMG_DIR / "memory_edges"

        orig_img_path = IMG_DIR / "memory.jpg"
        sobel_x_path  = EDGES_DIR / "memory_edge_x.png"
        sobel_y_path  = EDGES_DIR / "memory_edge_y.png"
        mag_path      = EDGES_DIR / "memory_edge_mag.png"

        gx_small  = np.load(EDGES_DIR / "gx_small.npy")
        gy_small  = np.load(EDGES_DIR / "gy_small.npy")
        mag_small = np.load(EDGES_DIR / "mag_small.npy")
        small_gray = np.load(EDGES_DIR / "small_gray.npy")

        Hs, Ws = small_gray.shape  # small grid resolution

        # -------------------------------------------------------
        # Base images (full-res)
        # -------------------------------------------------------
        orig = ImageMobject(str(orig_img_path))
        sobel_x_img = ImageMobject(str(sobel_x_path))
        sobel_y_img = ImageMobject(str(sobel_y_path))
        mag_img = ImageMobject(str(mag_path))

        DISP_H = 4.5
        for m in [orig, sobel_x_img, sobel_y_img, mag_img]:
            m.set_height(DISP_H)

        LEFT_POS   = LEFT * 3.4
        RIGHT_POS  = RIGHT * 3.4
        CENTER_POS = ORIGIN

        orig.move_to(LEFT_POS)
        sobel_x_img.move_to(RIGHT_POS)
        sobel_y_img.move_to(RIGHT_POS)
        mag_img.move_to(CENTER_POS)

        # -------------------------------------------------------
        # Helpers to map small-grid indices onto images
        # -------------------------------------------------------
        def cell_center_on_image(image_mob, i, j):
            """Center of cell (i,j) in small grid mapped onto an ImageMobject."""
            w = image_mob.width
            h = image_mob.height
            x0 = image_mob.get_left()[0]
            y0 = image_mob.get_top()[1]

            cell_w = w / Ws
            cell_h = h / Hs

            x = x0 + (j + 0.5) * cell_w
            y = y0 - (i + 0.5) * cell_h
            return np.array([x, y, 0.0])

        def build_mask_grid_for_image(image_mob):
            """Create a Ws x Hs grid of black rectangles over an image."""
            mask_blocks = {}
            group = VGroup()
            w = image_mob.width
            h = image_mob.height
            cell_w = w / Ws
            cell_h = h / Hs

            for i in range(Hs):
                for j in range(Ws):
                    r = Rectangle(
                        width=cell_w,
                        height=cell_h,
                        fill_color=BLACK,
                        fill_opacity=1.0,
                        stroke_width=0,
                    )
                    r.move_to(cell_center_on_image(image_mob, i, j))
                    mask_blocks[(i, j)] = r
                    group.add(r)
            return group, mask_blocks

        # 3x3 kernel overlay on original (in small-grid coordinates)
        def build_kernel_overlay(color):
            cells = VGroup()
            # We'll position this group by moving its center; its relative offsets
            # correspond to the 3×3 neighborhood in the small grid.
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    r = Rectangle(
                        width=orig.width / Ws,
                        height=orig.height / Hs,
                        fill_color=color,
                        fill_opacity=0.25,
                        stroke_color=color,
                        stroke_width=0.6,
                    )
                    r.shift(
                        RIGHT * dj * (orig.width / Ws)
                        + DOWN * di * (orig.height / Hs)
                    )
                    cells.add(r)
            return cells

        kernel_x = build_kernel_overlay(KERNEL_COLOR_X)
        kernel_y = build_kernel_overlay(KERNEL_COLOR_Y)

        # Vertical band for X, horizontal band for Y
        v_band = Rectangle(
            width=3 * (orig.width / Ws),
            height=orig.height,
            fill_color=KERNEL_COLOR_X,
            fill_opacity=0.15,
            stroke_color=KERNEL_COLOR_X,
            stroke_width=0.5,
        )

        h_band = Rectangle(
            width=orig.width,
            height=3 * (orig.height / Hs),
            fill_color=KERNEL_COLOR_Y,
            fill_opacity=0.15,
            stroke_color=KERNEL_COLOR_Y,
            stroke_width=0.5,
        )

        # -------------------------------------------------------
        # Arrow field helpers (using small gradients)
        # -------------------------------------------------------
        def create_arrow_field_on_image(
            image_mob, gx_arr, gy_arr, color, threshold=0.05, scale=0.45
        ):
            arrows = VGroup()
            mag_arr = np.sqrt(gx_arr**2 + gy_arr**2)
            maxmag = np.max(mag_arr) or 1.0

            for i in range(Hs):
                for j in range(Ws):
                    dvx = gx_arr[i, j]
                    dvy = gy_arr[i, j]
                    mag_val = np.sqrt(dvx**2 + dvy**2)
                    if mag_val < threshold * maxmag:
                        continue

                    dvx /= maxmag
                    dvy /= maxmag

                    start = cell_center_on_image(image_mob, i, j)
                    end = start + np.array([dvx, -dvy, 0.0]) * scale
                    arrows.add(
                        Arrow(
                            start,
                            end,
                            buff=0,
                            stroke_width=1.5,
                            color=color,
                            max_tip_length_to_length_ratio=0.3,
                            max_stroke_width_to_length_ratio=10,
                        )
                    )
            return arrows

        # -------------------------------------------------------
        # Title + original
        # -------------------------------------------------------
        title = H1(
            "Sobel Edge Detection on The Persistence of Memory"
        ).to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=TITLE_RT)

        cap = caption("Original color image").to_edge(DOWN)
        self.play(
            FadeIn(orig, shift=UP * 0.1),
            FadeIn(cap, shift=UP * 0.1),
            run_time=1.0,
        )
        self.wait(HOLD)

        # =======================================================
        # 1) SOBEL X: build edge image on the right, block-by-block
        # =======================================================
        # Put Sobel-X image on the right, fully masked
        self.add(sobel_x_img)
        mask_x_group, mask_x_blocks = build_mask_grid_for_image(sobel_x_img)
        self.add(mask_x_group)

        self.play(FadeOut(cap, shift=DOWN * 0.1), run_time=0.3)
        cap = caption(
            "Sobel X: building vertical-edge response block by block"
        ).to_edge(DOWN)
        cap.set_color(GRAD_COLOR_X)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)

        # Initialize band and kernel position for X
        # Start at small-grid cell (1,1)
        start_center = cell_center_on_image(orig, 1, 1)
        v_band.move_to(start_center)
        v_band.set_height(orig.height)
        v_band.set_x(start_center[0])
        v_band.set_y(orig.get_center()[1])

        kernel_x.move_to(start_center)

        self.add(v_band, kernel_x)

        # Sweep: columns (j) in steps of 3, rows (i) in steps of 3
        for j in range(1, Ws - 1, 3):
            col_center = cell_center_on_image(orig, 1, j)
            self.play(
                v_band.animate.set_x(col_center[0]),
                run_time=BLOCK_RT_X,
                rate_func=linear,
            )
            for i in range(1, Hs - 1, 3):
                block_center = cell_center_on_image(orig, i, j)
                self.play(
                    kernel_x.animate.move_to(block_center),
                    run_time=BLOCK_RT_X,
                    rate_func=linear,
                )

                # Reveal corresponding 3×3 block on Sobel-X image
                blocks_to_reveal = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ii = i + di
                        jj = j + dj
                        if 0 <= ii < Hs and 0 <= jj < Ws:
                            blocks_to_reveal.append(mask_x_blocks[(ii, jj)])

                if blocks_to_reveal:
                    self.play(
                        *[b.animate.set_fill(opacity=0.0) for b in blocks_to_reveal],
                        run_time=BLOCK_RT_X,
                    )

        self.wait(HOLD)
        self.play(FadeOut(v_band), FadeOut(kernel_x), run_time=0.5)

        # Arrow field on Sobel-X image
        arrows_x = create_arrow_field_on_image(
            sobel_x_img,
            gx_arr=gx_small,
            gy_arr=np.zeros_like(gy_small),  # X component only
            color=GRAD_COLOR_X,
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_x], lag_ratio=0.004),
            run_time=ARROWS_RT_X,
        )
        self.wait(HOLD * 1.2)

        # =======================================================
        # 2) SOBEL Y: same idea, with horizontal band
        # =======================================================
        self.play(
            FadeOut(arrows_x),
            FadeOut(sobel_x_img),
            FadeOut(mask_x_group),
            FadeOut(cap),
            run_time=0.8,
        )

        self.add(sobel_y_img)
        mask_y_group, mask_y_blocks = build_mask_grid_for_image(sobel_y_img)
        self.add(mask_y_group)

        cap = caption(
            "Sobel Y: building horizontal-edge response block by block"
        ).to_edge(DOWN)
        cap.set_color(GRAD_COLOR_Y)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)

        # Initialize band and kernel for Y (start near top)
        start_center_y = cell_center_on_image(orig, 1, 1)
        h_band.move_to(start_center_y)
        h_band.set_width(orig.width)
        h_band.set_y(start_center_y[1])
        h_band.set_x(orig.get_center()[0])

        kernel_y.move_to(start_center_y)

        self.add(h_band, kernel_y)

        # Sweep: rows (i) in steps of 3, columns (j) in steps of 3
        for i in range(1, Hs - 1, 3):
            row_center = cell_center_on_image(orig, i, 1)
            self.play(
                h_band.animate.set_y(row_center[1]),
                run_time=BLOCK_RT_Y,
                rate_func=linear,
            )
            for j in range(1, Ws - 1, 3):
                block_center = cell_center_on_image(orig, i, j)
                self.play(
                    kernel_y.animate.move_to(block_center),
                    run_time=BLOCK_RT_Y,
                    rate_func=linear,
                )

                blocks_to_reveal = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ii = i + di
                        jj = j + dj
                        if 0 <= ii < Hs and 0 <= jj < Ws:
                            blocks_to_reveal.append(mask_y_blocks[(ii, jj)])

                if blocks_to_reveal:
                    self.play(
                        *[b.animate.set_fill(opacity=0.0) for b in blocks_to_reveal],
                        run_time=BLOCK_RT_Y,
                    )

        self.wait(HOLD)
        self.play(FadeOut(h_band), FadeOut(kernel_y), run_time=0.5)

        # Arrow field on Sobel-Y image
        arrows_y = create_arrow_field_on_image(
            sobel_y_img,
            gx_arr=np.zeros_like(gx_small),
            gy_arr=gy_small,  # Y component only
            color=GRAD_COLOR_Y,
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_y], lag_ratio=0.004),
            run_time=ARROWS_RT_Y,
        )
        self.wait(HOLD * 1.2)

        # =======================================================
        # 3) Combined ∇I on original
        # =======================================================
        self.play(
            FadeOut(arrows_y),
            FadeOut(sobel_y_img),
            FadeOut(mask_y_group),
            FadeOut(cap),
            run_time=0.8,
        )

        # Move original to center
        self.play(orig.animate.move_to(CENTER_POS), run_time=0.9)

        cap = caption(
            "Combine ∂I/∂x and ∂I/∂y → full gradient field ∇I"
        ).to_edge(DOWN)
        cap.set_color(GRAD_COLOR_COMB)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)

        arrows_comb = create_arrow_field_on_image(
            orig,
            gx_arr=gx_small,
            gy_arr=gy_small,
            color=GRAD_COLOR_COMB,
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_comb], lag_ratio=0.004),
            run_time=ARROWS_RT_COMB,
        )
        self.wait(HOLD * 2)

        # =======================================================
        # 4) Smooth crossfade: arrows → |∇I| edge magnitude image
        # =======================================================
        self.play(FadeOut(cap), run_time=0.4)

        cap = caption("Edge magnitude |∇I| = √((∂I/∂x)² + (∂I/∂y)²)").to_edge(DOWN)
        cap.set_color(MAG_COLOR)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=CAP_RT)

        mag_img.set_height(DISP_H)
        mag_img.move_to(CENTER_POS)
        mag_img.set_opacity(0.0)
        self.add(mag_img)

        # One smooth motion: arrows fade out while edges fade in
        self.play(
            FadeOut(arrows_comb),
            mag_img.animate.set_opacity(1.0),
            run_time=MAG_CROSSFADE_RT,
        )
        self.wait(HOLD * 2)

        self.play(FadeOut(cap), run_time=0.6)
