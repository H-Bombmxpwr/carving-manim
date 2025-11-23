from manim import *
import numpy as np
from PIL import Image
from importlib.resources import files

from seamcarving_manim.style import H1, caption


class BaselinesScene(Scene):
    def construct(self):
        # ---- look & pacing ----
        self.camera.background_color = "#0a0a0a"
        TITLE_RT   = 1.5
        CAP_RT     = 1.2

        # same pacing for both approaches
        SHRINK_TIME = 6.0
        RETURN_TIME = 4.0
        HOLD        = 3

        # 15% width reduction from the RIGHT edge
        fx = 0.85

        # ---- title ----
        title = H1("Traditional Approaches: Crop & Scale").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)

        # ---- load image ----
        img_path = files("seamcarving_manim.assets.images").joinpath("memory.jpg")
        img_u8   = np.array(Image.open(img_path).convert("RGB"), dtype=np.uint8)

        # ---- centered display with enhanced frame ----
        DISP_H   = 4.5
        CENTER   = ORIGIN

        img_mobj = ImageMobject(img_u8).set_height(DISP_H).move_to(CENTER)
        self.add(img_mobj)

        # Enhanced frame with glow effect
        frame_rect = Rectangle(
            width=img_mobj.width, height=img_mobj.height,
            stroke_color=BLUE, stroke_width=4, fill_opacity=0
        ).move_to(CENTER)
        frame_glow = frame_rect.copy().set_stroke(color=BLUE, width=12, opacity=0.3)
        frame_rect.set_z_index(100)
        frame_glow.set_z_index(99)
        self.add(frame_glow, frame_rect)


        # problem statement with highlight
        problem_cap = caption("Goal: reduce width by 15% from the RIGHT edge").next_to(frame_rect, DOWN, buff=0.25)
        problem_cap.set_color(YELLOW)
        self.play(
            FadeIn(problem_cap, shift=UP*0.1),
            Flash(problem_cap, color=YELLOW, flash_radius=0.5, line_length=0.2),
            run_time=CAP_RT
        )
        self.wait(0.6)

        # =========================
        # Part 1 — Crop from the right (cut + disappear)
        # =========================
        self.play(problem_cap.animate.shift(0.4 * DOWN), run_time=0.4)
        cap_crop = caption("Approach 1: Hard Crop from Right Edge").next_to(problem_cap, DOWN, buff=0.1)
        cap_crop.set_color(ORANGE)
        self.play(FadeIn(cap_crop, shift=UP*0.1), run_time=CAP_RT)

        # vertical cutting line with glow
        top_pt    = frame_rect.get_top()
        bot_pt    = frame_rect.get_bottom()
        right_pt  = frame_rect.get_right()
        full_w    = frame_rect.width
        cut_w     = full_w * (1.0 - fx)
        target_x  = right_pt[0] - cut_w

        cut_line = Line(
            start=top_pt,
            end=bot_pt,
            stroke_width=5,
            color=RED
        )
        cut_glow = cut_line.copy().set_stroke(width=15, opacity=0.4)
        cut_line.move_to(right_pt)
        cut_glow.move_to(right_pt)
        cut_line.set_z_index(111)
        cut_glow.set_z_index(110)

        # cover rectangle with gradient-like effect
        cover_rect = Rectangle(
            width=cut_w, height=frame_rect.height,
            stroke_opacity=0,
            fill_color="#0a0a0a",
            fill_opacity=1.0
        ).align_to(frame_rect, RIGHT).align_to(frame_rect, UP)
        cover_rect.set_z_index(90)

        base_cover = cover_rect.copy()

        def crop_update(alpha):
            x_now = right_pt[0] - cut_w * alpha
            cut_line.move_to(np.array([x_now, cut_line.get_center()[1], 0]))
            cut_glow.move_to(np.array([x_now, cut_glow.get_center()[1], 0]))
            
            cover_rect.become(base_cover.copy())
            cover_rect.stretch(alpha, dim=0, about_point=right_pt)
            cover_rect.align_to(frame_rect, RIGHT).align_to(frame_rect, UP)

        self.add(cover_rect)
        self.add(cut_glow, cut_line)

        self.play(
            UpdateFromAlphaFunc(cut_line, lambda m, a: crop_update(a)),
            run_time=SHRINK_TIME,
            rate_func=smooth,
        )
        self.wait(HOLD)

        # clean up with smooth fadeout
        self.play(
            FadeOut(cut_line), 
            FadeOut(cut_glow), 
            FadeOut(cover_rect), 
            run_time=0.6
        )
        self.play(FadeOut(cap_crop, shift=DOWN*0.1), run_time=0.3)
        self.wait(0.4)

        # =========================
        # Part 2 — Uniform scaling
        # =========================
        cap_scale = caption("Approach 2: Uniform Horizontal Scaling").next_to(problem_cap, DOWN, buff=0.1)
        cap_scale.set_color(TEAL)
        self.play(FadeIn(cap_scale, shift=UP*0.1), run_time=CAP_RT)

        orig      = img_mobj.copy()
        left_edge = orig.get_left()

        # Add visual indicator for scaling
        right_arrow = Arrow(
            start=frame_rect.get_right() + RIGHT*0.3,
            end=frame_rect.get_right() + LEFT*0.5,
            color=TEAL,
            stroke_width=6,
            buff=0
        ).set_z_index(105)
        self.play(GrowArrow(right_arrow), run_time=0.5)

        def squish(m, alpha):
            m.become(orig.copy())
            s = 1.0 + (fx - 1.0) * alpha
            m.stretch(s, dim=0, about_point=left_edge)

        def unsquish(m, alpha):
            m.become(orig.copy())
            s = fx + (1.0 - fx) * alpha
            m.stretch(s, dim=0, about_point=left_edge)

        # animate squish with arrow following
        def update_arrow(alpha):
            new_right = orig.get_right()[0] * (1.0 + (fx - 1.0) * alpha)
            right_arrow.put_start_and_end_on(
                np.array([new_right + 0.3, frame_rect.get_center()[1], 0]),
                np.array([new_right - 0.5, frame_rect.get_center()[1], 0])
            )

        self.play(
            UpdateFromAlphaFunc(img_mobj, squish),
            UpdateFromAlphaFunc(right_arrow, lambda m, a: update_arrow(a)),
            run_time=SHRINK_TIME,
            rate_func=smooth,
        )
        self.wait(HOLD * 2)