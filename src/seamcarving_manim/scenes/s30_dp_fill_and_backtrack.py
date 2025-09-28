from manim import *
import numpy as np
from PIL import Image
from utils.seam_carving_core import energy_map, cumulative_min_energy_vertical, find_vertical_seam
from scenes.style import *

class DPFillAndBacktrack(Scene):
    def construct(self):
        img = np.array(Image.open("assets/images/beach.jpg").convert("RGB"))/255.0
        E = energy_map(img)
        M, back = cumulative_min_energy_vertical(E)

        # show dynamic programming grid filling
        grid = ImageMobject(np.uint8(255*(M/M.max()))).scale(0.9)
        self.play(FadeIn(grid), Write(H2("Cumulative energy (bottom-up DP)").next_to(grid, DOWN)))
        self.wait(0.5)

        seam = find_vertical_seam(M, back)
        # draw seam as a polyline overlay
        H, W = E.shape
        pts = [grid.get_corner(UL) + np.array([x/W*grid.width, (i+0.5)/H*grid.height, 0])
               for i,x in enumerate(seam)]
        seam_vm = VMobject(stroke_color=ACCENT, stroke_width=6).set_points_as_corners(pts)
        self.play(Create(seam_vm))
        self.wait(1)
