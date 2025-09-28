# src/seamcarving_manim/scenes/s20_energy_map.py
from manim import *
import numpy as np
from PIL import Image
from importlib.resources import files

from seamcarving_manim.utils.seam_carving_core import energy_map
from seamcarving_manim.style import H1, caption

class EnergyMapScene(Scene):
    def construct(self):
        title = H1("Energy map (Sobel magnitude on luminance)").to_edge(UP)
        self.play(Write(title))

        img_path = files("seamcarving_manim.assets.images").joinpath("beach.jpg")
        img = np.array(Image.open(img_path).convert("RGB")) / 255.0
        E = energy_map(img)

        left = ImageMobject((img * 255).astype("uint8")).scale(0.8).to_edge(LEFT)
        right = ImageMobject(np.uint8(255 * (E / E.max()))).scale(0.8).to_edge(RIGHT).set_color_map("inferno")

        self.play(FadeIn(left), FadeIn(right))
        self.play(FadeIn(caption("Original").next_to(left, DOWN, buff=0.2)))
        self.play(FadeIn(caption("High gradients = high energy").next_to(right, DOWN, buff=0.2)))
        self.wait(0.5)
