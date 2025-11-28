from manim import *
from seamcarving_manim.style import H1, caption
from pathlib import Path
import numpy as np
from PIL import Image


class DualSeamCarvingScene(Scene):
    def construct(self):
        self.camera.background_color = "#0a0a0a"

        # ================= TIMING / DISPLAY PARAMS =================
        TITLE_RT    = 0.8
        TITLE_HOLD  = 0.7   # how long to keep title before fading it out
        CAP_RT      = 0.6
        CARVE_TIME  = 20.0  # total time for all seam-removal frames (slower seams)
        HOLD_BEFORE = 1.5
        HOLD_AFTER  = 3.0
        DISP_H      = 3.0   # height of each image
        # ==========================================================

        # ---------------- Title ----------------
        title = H1("Same Seams, Two Views").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)
        self.wait(TITLE_HOLD)

        # ---------------- Caption helper ----------------
        bottom_caption = None

        def set_caption(text, rt=CAP_RT):
            nonlocal bottom_caption
            new_cap = caption(text).to_edge(DOWN, buff=0.4)
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

        # ---------------- Load precomputed frames ----------------
        # Load from local repo directory (NOT package-installed path)
        repo_root = Path(__file__).resolve().parents[3]

        frames_root = (
            repo_root
            / "src"
            / "seamcarving_manim"
            / "assets"
            / "images"
            / "memory_dual"
        )

        orig_dir = frames_root / "orig"
        dp_dir   = frames_root / "dp"

        orig_files = sorted(orig_dir.glob("frame_*.png"))
        dp_files   = sorted(dp_dir.glob("frame_*.png"))

        if not orig_files or not dp_files:
            raise FileNotFoundError(
                f"Did not find frames in:\n{orig_dir}\n{dp_dir}\n"
            )

        # Preload arrays (avoids disk hit per frame)
        orig_frames = [
            np.array(Image.open(f).convert("RGB"), dtype=np.uint8) for f in orig_files
        ]
        dp_frames = [
            np.array(Image.open(f).convert("RGB"), dtype=np.uint8) for f in dp_files
        ]

        # Use the minimum count in case of any mismatch
        num_frames = min(len(orig_frames), len(dp_frames))
        if num_frames == 0:
            raise RuntimeError("No frames loaded for dual seam demo.")

        # ---------------- Initial stacked display ----------------
        # IMPORTANT: orange DP map on TOP, original on BOTTOM
        dp_img   = ImageMobject(dp_frames[0]).set_height(DISP_H)
        orig_img = ImageMobject(orig_frames[0]).set_height(DISP_H)

        pair = Group(dp_img, orig_img).arrange(DOWN, buff=0.5)
        pair.move_to(ORIGIN)

        # Compute anchors so images always shrink from the RIGHT within fixed frames
        dp_left   = dp_img.get_left()[0]
        dp_center = dp_img.get_center()
        orig_left   = orig_img.get_left()[0]
        orig_center = orig_img.get_center()

        initial_width = dp_img.width  # same for both

        # Frame rectangles (fixed width) around each image
        dp_frame = Rectangle(
            width=initial_width,
            height=dp_img.height,
            stroke_color=BLUE,
            stroke_width=4,
            fill_opacity=0,
        ).move_to(dp_center)
        dp_glow = dp_frame.copy().set_stroke(color=BLUE, width=12, opacity=0.3)

        orig_frame = Rectangle(
            width=initial_width,
            height=orig_img.height,
            stroke_color=BLUE,
            stroke_width=4,
            fill_opacity=0,
        ).move_to(orig_center)
        orig_glow = orig_frame.copy().set_stroke(color=BLUE, width=12, opacity=0.3)

        for r in [dp_frame, dp_glow, orig_frame, orig_glow]:
            r.set_z_index(100)

        # Labels (match new order: top = DP, bottom = original)
        label_dp   = Text("Min-energy map", font_size=24, color=GRAY_B)
        label_orig = Text("Original painting",    font_size=24, color=GRAY_B)
        label_dp.next_to(dp_img, LEFT, buff=0.3)
        label_orig.next_to(orig_img, LEFT, buff=0.3)

        labels = Group(label_dp, label_orig)

        # Fade out title as images & frames come in
        self.play(
            FadeOut(title, shift=UP * 0.2),
            FadeIn(pair, shift=0.2 * UP),
            FadeIn(dp_glow), FadeIn(dp_frame),
            FadeIn(orig_glow), FadeIn(orig_frame),
            FadeIn(labels, shift=0.2 * LEFT),
            run_time=1.0,
        )

        self.wait(HOLD_BEFORE)

        # ---------------- Animate seam carving ----------------
        set_caption("Each frame removes one low-energy vertical seam chosen on the original.")

        dt = CARVE_TIME / num_frames  # time per step (now slower)

        # We'll keep frames + labels, just swap the images inside and
        # always anchor them to the same left edge so they shrink from the right.
        for k in range(1, num_frames):
            new_dp   = ImageMobject(dp_frames[k]).set_height(DISP_H)
            new_orig = ImageMobject(orig_frames[k]).set_height(DISP_H)

            # Anchor DP image to fixed left edge and center-y
            new_dp.move_to([
                dp_left + new_dp.width / 2.0,
                dp_center[1],
                0,
            ])

            # Anchor original image likewise
            new_orig.move_to([
                orig_left + new_orig.width / 2.0,
                orig_center[1],
                0,
            ])

            # Replace old images with new ones (frames & labels stay put)
            self.remove(dp_img, orig_img)
            self.add(new_dp, new_orig)

            dp_img = new_dp
            orig_img = new_orig

            self.wait(dt)

        self.wait(HOLD_AFTER)

        # ---------------- Clean exit ----------------
        self.play(
            FadeOut(dp_img),
            FadeOut(orig_img),
            FadeOut(dp_frame), FadeOut(dp_glow),
            FadeOut(orig_frame), FadeOut(orig_glow),
            FadeOut(labels),
            FadeOut(bottom_caption),
            run_time=0.8,
        )
        self.wait(0.3)