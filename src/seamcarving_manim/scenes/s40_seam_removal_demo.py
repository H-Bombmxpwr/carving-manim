from manim import *
import numpy as np
from PIL import Image
from utils.seam_carving_core import energy_map, cumulative_min_energy_vertical, find_vertical_seam, remove_vertical_seam
from scenes.style import *

class SeamRemovalDemo(Scene):
    def construct(self):
        img = np.array(Image.open("assets/images/beach.jpg").convert("RGB"))/255.0
        img_mobj = ImageMobject(np.uint8(img*255)).scale(0.9)
        self.add(H1("Seam removal (vertical)").to_edge(UP))
        self.play(FadeIn(img_mobj))
        self.wait(0.3)

        frames = []
        cur = img.copy()
        for _ in range(60):  # remove 60 seams
            E = energy_map(cur)
            M, back = cumulative_min_energy_vertical(E)
            seam = find_vertical_seam(M, back)
            cur = remove_vertical_seam(cur, seam)
            frames.append(np.uint8(cur*255))

        # animate a few key frames
        for k in range(0, len(frames), 6):
            self.play(Transform(img_mobj, ImageMobject(frames[k]).scale(0.9)), run_time=0.25, rate_func=linear)
        self.wait(0.5)
