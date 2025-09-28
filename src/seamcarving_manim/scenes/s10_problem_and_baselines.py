from manim import *
import numpy as np
from PIL import Image
from importlib.resources import files

from seamcarving_manim.style import H1, caption
from seamcarving_manim.utils.seam_carving_core import (
    energy_map, cumulative_min_energy_vertical,
    find_vertical_seam, remove_vertical_seam
)

class BaselinesScene(Scene):
    def construct(self):
        # ---- look & pacing ----
        self.camera.background_color = BLACK
        TITLE_RT   = 0.8
        CAP_RT     = 0.6

        # keep both baselines same speed
        SHRINK_TIME = 5.0
        RETURN_TIME = 4.0
        HOLD        = 0.45
        MIN_STEP    = 0.15  # ≥ 1/15s to avoid preview jitter (-pql is 15 FPS)

        # ---- title ----
        title = H1("Baselines: Naive Scaling vs. Seam Carving").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)

        # ---- load image ----
        img_path = files("seamcarving_manim.assets.images").joinpath("memory.jpg")
        img_u8   = np.array(Image.open(img_path).convert("RGB"), dtype=np.uint8)

        # ---- centered display with static frame ----
        DISP_H   = 4.5
        CENTER   = ORIGIN

        img_mobj = ImageMobject(img_u8).set_height(DISP_H).move_to(CENTER)
        self.add(img_mobj)

        frame_rect = Rectangle(
            width=img_mobj.width, height=img_mobj.height,
            stroke_color=GREEN, stroke_width=6, fill_opacity=0
        ).move_to(CENTER)
        frame_rect.set_z_index(100)
        self.add(frame_rect)

        credit = caption("Image: The Persistence of Memory (1931) — Salvador Dalí").to_edge(DOWN, buff=0.45)
        self.play(FadeIn(credit), run_time=CAP_RT)

        # =========================
        # Part 1 — Naive squish x2
        # =========================
        cap_naive = caption("Naive resize: pull the RIGHT edge inward (height unchanged) → squish/stretch artifacts")
        cap_naive.next_to(frame_rect, DOWN, buff=0.25)
        self.play(FadeIn(cap_naive), run_time=CAP_RT)

        orig      = img_mobj.copy()
        left_edge = orig.get_left()
        fx        = 0.65  # 65% width

        def squish(m, a):
            m.become(orig.copy())
            s = 1.0 + (fx - 1.0) * a
            m.stretch(s, dim=0, about_point=left_edge)  # horizontal only

        def unsquish(m, a):
            m.become(orig.copy())
            s = fx + (1.0 - fx) * a
            m.stretch(s, dim=0, about_point=left_edge)

        # cycle 1
        self.play(UpdateFromAlphaFunc(img_mobj, squish),   run_time=SHRINK_TIME, rate_func=smooth)
        self.wait(HOLD)
        self.play(UpdateFromAlphaFunc(img_mobj, unsquish), run_time=RETURN_TIME, rate_func=smooth)
        self.wait(HOLD)
        # cycle 2
        self.play(UpdateFromAlphaFunc(img_mobj, squish),   run_time=SHRINK_TIME, rate_func=smooth)
        self.wait(HOLD)
        self.play(UpdateFromAlphaFunc(img_mobj, unsquish), run_time=RETURN_TIME, rate_func=smooth)
        self.wait(HOLD)

        self.play(FadeOut(cap_naive), run_time=0.3)

        # =========================================
        # Part 2 — Seam carving (package) + SMOOTH WIPE (two cycles)
        # =========================================
        import seam_carving as sc

        cap_sc = caption("Seam carving: remove low-energy columns → background collapses, subject preserved")
        cap_sc.next_to(frame_rect, DOWN, buff=0.25)
        self.play(FadeIn(cap_sc), run_time=CAP_RT)

        # 1) Compute ONE final carved image at the same target ratio as naive
        src_h, src_w = img_u8.shape[:2]
        target_w     = max(2, int(round(src_w * fx)))

        carved_u8 = sc.resize(
            img_u8, (int(target_w), int(src_h)),
            energy_mode='backward',          # 'forward' is slower but sometimes nicer
            order='width-first'
        ).astype(np.uint8)

        # 2) Build two layers: original (reference) and final carved; keep them left-aligned
        orig_layer   = ImageMobject(img_u8).set_height(DISP_H).move_to(CENTER)
        carved_layer = ImageMobject(carved_u8).set_height(DISP_H).move_to(CENTER)
        carved_layer.align_to(orig_layer, LEFT).align_to(orig_layer, UP)

        # Swap out the Part-1 image and show both layers (carved under a mask)
        self.remove(img_mobj)
        self.add(orig_layer, carved_layer)

        # Keep the green frame above everything
        self.bring_to_front(frame_rect)

        # 3) Opaque mask that hides the carved layer; we’ll shrink its width from the LEFT
        mask = Rectangle(
            width=carved_layer.width, height=carved_layer.height,
            stroke_opacity=0, fill_color=BLACK, fill_opacity=1.0
        ).align_to(carved_layer, LEFT).align_to(carved_layer, UP)
        mask.set_z_index(carved_layer.z_index + 1)
        self.add(mask)

        def reveal_mask_update(m, a):
            # a: 0 → carved fully hidden; 1 → carved fully revealed
            left_pt = carved_layer.get_left()
            w_full  = carved_layer.width
            w_now   = max(1e-3, (1.0 - a) * w_full)   # shrink from full → 0
            m.set_width(w_now, stretch=True, about_point=left_pt)
            m.align_to(carved_layer, LEFT).align_to(carved_layer, UP)

        def reset_mask():
            reveal_mask_update(mask, 0.0)  # fully cover carved

        # 4) Two smooth cycles (reveal → hide → reveal → hide) matching naive timing
        for _ in range(2):
            reset_mask()
            self.play(
                UpdateFromAlphaFunc(mask, reveal_mask_update),
                run_time=SHRINK_TIME, rate_func=smooth
            )
            self.wait(HOLD)
            self.play(
                UpdateFromAlphaFunc(mask, lambda m, a: reveal_mask_update(m, 1.0 - a)),
                run_time=RETURN_TIME, rate_func=smooth
            )
            self.wait(HOLD)

        self.play(FadeOut(cap_sc), run_time=0.3)
        self.wait(0.6)
