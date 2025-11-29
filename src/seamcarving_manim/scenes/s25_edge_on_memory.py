from manim import *
from pathlib import Path
from PIL import Image
import numpy as np

from seamcarving_manim.style import H1, caption

# Resolve project root: .../carving-manim/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSETS_DIR   = PROJECT_ROOT / "src" / "seamcarving_manim" / "assets" / "images"


class EdgeOnMemoryScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        TITLE_RT = 0.8
        CAP_RT   = 0.8
        HOLD     = 1.2

        # --- title ---
        title = H1("Edges on The Persistence of Memory").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)
        self.wait(0.4)

        # --- load images from local assets (NOT from venv) ---
        orig_path = ASSETS_DIR / "memory.jpg"
        ex_path   = ASSETS_DIR / "memory_edges" / "memory_edge_x.png"
        ey_path   = ASSETS_DIR / "memory_edges" / "memory_edge_y.png"
        em_path   = ASSETS_DIR / "memory_edges" / "memory_edge_mag.png"

        print("EdgeOnMemoryScene loading from:")
        print("  orig :", orig_path)
        print("  edgeX:", ex_path)
        print("  edgeY:", ey_path)
        print("  edgeM:", em_path)

        orig_arr     = np.array(Image.open(orig_path).convert("RGB"), dtype=np.uint8)
        edge_x_arr   = np.array(Image.open(ex_path).convert("RGB"), dtype=np.uint8)
        edge_y_arr   = np.array(Image.open(ey_path).convert("RGB"), dtype=np.uint8)
        edge_mag_arr = np.array(Image.open(em_path).convert("RGB"), dtype=np.uint8)

        orig    = ImageMobject(orig_arr).set_z_index(100)
        edge_x  = ImageMobject(edge_x_arr).set_z_index(100)
        edge_y  = ImageMobject(edge_y_arr).set_z_index(100)
        edge_mag= ImageMobject(edge_mag_arr).set_z_index(100)


        for m in [orig, edge_x, edge_y, edge_mag]:
            m.set_z_index(100)

        # unify sizes
        DISP_H = 4.2
        for m in [orig, edge_x, edge_y, edge_mag]:
            m.set_height(DISP_H)

        # --- Step 1: original only ---
        orig.move_to(ORIGIN)
        self.play(FadeIn(orig, run_time=1.0))
        cap_orig = caption(
            "Original image: The Persistence of Memory (1931) — Salvador Dalí"
        ).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cap_orig, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD * 1.3)

        # --- Step 2: Sobel X (vertical edges) ---
        self.play(
            orig.animate.shift(LEFT * 3.6).scale(0.75),
            FadeOut(cap_orig, shift=DOWN * 0.1),
            run_time=1.0,
        )

        edge_x.next_to(orig, RIGHT, buff=0.8)

        cap_x = caption(
            "Sobel X: strong response at vertical edges (left–right changes)"
        ).to_edge(DOWN, buff=0.4)
        self.play(
            FadeIn(edge_x, shift=RIGHT * 0.3),
            FadeIn(cap_x, shift=UP * 0.1),
            run_time=1.0,
        )
        label_x = Text("∂I/∂x   (Sobel X)", font_size=22, color=RED).next_to(edge_x, DOWN, buff=0.2)
        self.play(FadeIn(label_x, shift=UP * 0.1), run_time=0.5)

        self.wait(HOLD * 1.3)

        # pulse the edges a bit
        self.play(edge_x.animate.scale(1.03), run_time=0.4)
        self.play(edge_x.animate.scale(1 / 1.03), run_time=0.4)
        self.wait(0.4)

        # --- Step 3: Sobel Y (horizontal edges) ---
        self.play(
            FadeOut(edge_x),
            FadeOut(label_x),
            FadeOut(cap_x, shift=DOWN * 0.1),
            orig.animate.shift(RIGHT * 7.2),
            run_time=1.0,
        )


        edge_y.next_to(orig, LEFT, buff=0.8)

        cap_y = caption(
            "Sobel Y: strong response at horizontal edges (up–down changes)"
        ).to_edge(DOWN, buff=0.4)
        self.play(
            FadeIn(edge_y, shift=LEFT * 0.3),
            FadeIn(cap_y, shift=UP * 0.1),
            run_time=1.0,
        )
        label_y = Text("∂I/∂y   (Sobel Y)", font_size=22,   color=BLUE).next_to(edge_y, DOWN, buff=0.2)

        self.play(FadeIn(label_y, shift=UP * 0.1), run_time=0.5)

        self.wait(HOLD * 1.3)

        self.play(edge_y.animate.scale(1.03), run_time=0.4)
        self.play(edge_y.animate.scale(1 / 1.03), run_time=0.4)
        self.wait(0.4)

        # --- Step 4: bring both edges in and combine into full edge map ---
        self.play(
                FadeOut(cap_y, shift=DOWN * 0.1),
                FadeOut(orig),
                FadeOut(edge_y),
                FadeOut(label_y),
                run_time=0.7,
            )


        # small X and Y on left/right, combined in center
        edge_mag.move_to(ORIGIN)
        edge_x_small = edge_x.copy().set_height(3.0)
        edge_y_small = edge_y.copy().set_height(3.0)

        edge_x_small.next_to(edge_mag, LEFT, buff=0.8)
        edge_y_small.next_to(edge_mag, RIGHT, buff=0.8)

        self.play(
            FadeIn(edge_x_small, shift=LEFT * 0.3),
            FadeIn(edge_y_small, shift=RIGHT * 0.3),
            run_time=1.0,
        )

        cap_combine = caption(
            "Combine |∂I/∂x| and |∂I/∂y| → full edge map |∇I|"
        ).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cap_combine, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD)

        # "Cool" combination animation: X + Y collapse into center and crossfade to |∇I|
        edge_mag.set_opacity(0.0)
        self.add(edge_mag)
        label_mag = Text("|∇I|  (edge magnitude)", font_size=24, color=GREEN)\
        .next_to(edge_mag, DOWN, buff=0.3)

        self.play(FadeIn(label_mag, shift=UP * 0.1), run_time=0.6)


        self.play(
            edge_x_small.animate.move_to(edge_mag.get_center()).scale(0.9),
            edge_y_small.animate.move_to(edge_mag.get_center()).scale(0.9),
            run_time=1.0,
        )

        self.play(
            edge_mag.animate.set_opacity(1.0),
            edge_x_small.animate.set_opacity(0.0),
            edge_y_small.animate.set_opacity(0.0),
            run_time=1.5,
        )

        self.remove(edge_x_small, edge_y_small)
        self.wait(HOLD * 2)

        # final beat: zoom the edge map slightly
        self.play(edge_mag.animate.scale(1.05), run_time=0.6)
        self.wait(1.0)

        self.wait(1.0)

        self.play(FadeOut(label_mag), run_time=0.6)
