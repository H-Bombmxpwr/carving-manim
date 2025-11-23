from manim import *
import numpy as np
from PIL import Image
from importlib.resources import files
from pathlib import Path

from seamcarving_manim.style import H1, caption


class FirstDemoScene(Scene):
    def construct(self):
        # ---- look & pacing ----
        self.camera.background_color = "#0a0a0a"
        TITLE_RT = 0.8
        CAP_RT = 0.6
        CARVE_TIME = 12.0
        HOLD = 4

        # ---- title ----
        title = H1("Seam Carving: Content-Aware Resizing").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)

        # ---- load pre-generated frames ----
        frames_dir = files("seamcarving_manim.assets.images").joinpath("memory_carved")
        
        # Load all frames
        print("Loading pre-generated seam carving frames...")
        frames = []
        frame_files = sorted(Path(str(frames_dir)).glob("frame_*.jpg"))
        
        for frame_file in frame_files:
            img = np.array(Image.open(frame_file).convert("RGB"), dtype=np.uint8)
            frames.append(img)
        
        print(f"Loaded {len(frames)} frames")
        
        if len(frames) == 0:
            raise FileNotFoundError(
                "No frames found! Please run the pregenerate_frames.py script first to generate frames."
            )

        # ---- centered display ----
        DISP_H = 4.5
        CENTER = ORIGIN

        # Create initial image mobject
        img_mobj = ImageMobject(frames[0]).set_height(DISP_H).move_to(CENTER)
        start_left_x = img_mobj.get_left()[0]
        
        self.add(img_mobj)

        # Enhanced frame with fixed width
        initial_width = img_mobj.width
        frame_rect = Rectangle(
            width=initial_width, height=img_mobj.height,
            stroke_color=BLUE, stroke_width=4, fill_opacity=0
        ).move_to(img_mobj.get_center())
        
        frame_glow = frame_rect.copy().set_stroke(color=BLUE, width=12, opacity=0.3)
        frame_rect.set_z_index(100)
        frame_glow.set_z_index(99)
        self.add(frame_glow, frame_rect)

        # Goal statement
        goal_cap = caption("Goal: reduce width by 15% from the RIGHT edge").to_edge(DOWN, buff=1.2)
        goal_cap.set_color(YELLOW)
        self.play(
            FadeIn(goal_cap, shift=UP*0.1),
            Flash(goal_cap, color=YELLOW, flash_radius=0.5, line_length=0.2),
            run_time=CAP_RT
        )
        self.wait(HOLD)

        # Seam carving caption
        seam_cap = caption("Seam Carving: \"intelligently\" removes low-energy vertical seams").next_to(goal_cap, DOWN, buff=0.1)
        seam_cap.set_color(GREEN)
        self.play(FadeIn(seam_cap, shift=UP*0.1), run_time=CAP_RT)
        self.wait(0.4)

        # Create seam indicator line
        seam_line = Line(
            start=img_mobj.get_top() + RIGHT * (img_mobj.width/2),
            end=img_mobj.get_bottom() + RIGHT * (img_mobj.width/2),
            stroke_color=RED,
            stroke_width=3,
            stroke_opacity=0.9
        )
        seam_line.set_z_index(105)
        
        seam_glow = seam_line.copy().set_stroke(width=10, opacity=0.3)
        seam_glow.set_z_index(104)

        self.add(seam_glow, seam_line)

        # Animate through frames by removing and adding new ImageMobjects
        num_frames = len(frames)
        dt = CARVE_TIME / num_frames  # Time per frame
        
        for i in range(1, num_frames):
            # Create new image for this frame
            new_img = ImageMobject(frames[i]).set_height(DISP_H)
            new_img.align_to(img_mobj, LEFT)
            new_img.shift(RIGHT * (start_left_x - new_img.get_left()[0]))
            
            # Keep frame rectangles fixed (don't update them)
            
            # Update seam line position
            right_x = new_img.get_right()[0]
            new_seam_line = Line(
                start=np.array([right_x, new_img.get_top()[1], 0]),
                end=np.array([right_x, new_img.get_bottom()[1], 0]),
                stroke_color=RED,
                stroke_width=3,
                stroke_opacity=0.9
            )
            new_seam_line.set_z_index(105)
            
            new_seam_glow = new_seam_line.copy().set_stroke(width=10, opacity=0.3)
            new_seam_glow.set_z_index(104)
            
            # Remove old image and seam line, add new ones (keep frame fixed)
            self.remove(img_mobj, seam_line, seam_glow)
            self.add(new_img, new_seam_glow, new_seam_line)
            
            # Update references
            img_mobj = new_img
            seam_line = new_seam_line
            seam_glow = new_seam_glow
            
            # Wait for next frame
            self.wait(dt)
        
        # Remove seam line
        self.play(FadeOut(seam_line), FadeOut(seam_glow), run_time=0.4)
        self.wait(HOLD)

        # Success captions
        self.play(FadeOut(seam_cap, shift=DOWN*0.1), run_time=0.3)
        
        success_cap1 = caption("✓ Important content preserved").next_to(goal_cap, DOWN, buff=0.1)
        success_cap1.set_color(GREEN)
        self.play(FadeIn(success_cap1, shift=UP*0.1), run_time=CAP_RT)
        self.wait(0.4)
        
        success_cap2 = caption("✓ No distortion or squishing").next_to(success_cap1, DOWN, buff=0.1)
        success_cap2.set_color(GREEN)
        self.play(FadeIn(success_cap2, shift=UP*0.1), run_time=CAP_RT)
        self.wait(HOLD * 2)

        # Highlight the main subject (clocks)
        clock_highlight1 = Rectangle(
            width=1.2, height=1.0,
            stroke_color=GREEN, stroke_width=3, fill_opacity=0
        ).move_to(img_mobj.get_center() + LEFT*0.6 + UP*0.8)
        clock_highlight1.set_z_index(105)
        
        clock_highlight2 = Rectangle(
            width=1.9, height=1.5,
            stroke_color=GREEN, stroke_width=3, fill_opacity=0
        ).move_to(img_mobj.get_center() + RIGHT*0.5 + DOWN*0.5)
        clock_highlight2.set_z_index(105)

        self.play(
            Create(clock_highlight1),
            Create(clock_highlight2),
            run_time=0.8
        )
        
        preserved_label = Text("Key objects intact", font_size=20, color=GREEN).next_to(clock_highlight1, UP, buff=0.2)
        preserved_label.set_z_index(105)
        self.play(FadeIn(preserved_label, shift=UP*0.1), run_time=0.4)
        
        self.wait(HOLD * 2)
        
        # Fade out highlights
        self.play(
            FadeOut(clock_highlight1),
            FadeOut(clock_highlight2),
            FadeOut(preserved_label),
            run_time=0.5
        )
        
        self.wait(1.0)