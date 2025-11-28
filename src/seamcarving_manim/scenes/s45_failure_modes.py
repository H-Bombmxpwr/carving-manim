from manim import *
import numpy as np
from PIL import Image
from pathlib import Path

# Import style if available, otherwise define locally
try:
    from seamcarving_manim.style import H1, caption
except ImportError:
    def H1(text):
        return Text(text, font_size=42, color=WHITE, weight=BOLD)
    
    def caption(text):
        return Text(text, font_size=24, color=GRAY_B)


class FailureModesScene(Scene):
    """
    Scene showing why naive approaches fail and seam carving succeeds.
    Animates through frames like DualSeamCarvingScene for each strategy.
    
    Strategies shown:
    1. Column removal - vertical artifacts
    2. Pixel per row - zigzag effect  
    3. Optimal global - destroys rectangle
    4. Seam carving - the solution
    """
    
    def construct(self):
        self.camera.background_color = "#0a0a0a"
        
        # ================= TIMING / DISPLAY PARAMS =================
        TITLE_RT = 0.8
        CAP_RT = 0.6
        CAP_BUFF = 0.5
        DISP_H = 4.5  # Larger display height so audience can see
        ANIM_TIME = 8.0  # Time per strategy animation
        HOLD = 2.0
        # ==========================================================
        
        # ---- Load precomputed frames ----
        repo_root = Path(__file__).resolve().parents[3]
        frames_root = (
            repo_root / "src" / "seamcarving_manim" / "assets" / "images" / "failure_modes"
        )
        
        def load_frames(subdir):
            """Load all frames from a subdirectory."""
            frame_dir = frames_root / subdir
            frame_files = sorted(frame_dir.glob("frame_*.png"))
            if not frame_files:
                raise FileNotFoundError(f"No frames in {frame_dir}")
            return [
                np.array(Image.open(f).convert("RGB"), dtype=np.uint8)
                for f in frame_files
            ]
        
        # Load all strategy frames
        column_frames = load_frames("column")
        pixel_frames = load_frames("pixel")
        optimal_frames = load_frames("optimal")
        seam_frames = load_frames("seam")
        
        # Load original for reference
        original_path = frames_root / "original.png"
        original_array = np.array(Image.open(original_path).convert("RGB"), dtype=np.uint8)
        
        # ---- Caption helper ----
        bottom_caption = None
        
        def set_caption(text, color=GRAY_B, rt=CAP_RT):
            nonlocal bottom_caption
            new_cap = caption(text).to_edge(DOWN, buff=CAP_BUFF)
            if color != GRAY_B:
                new_cap.set_color(color)
            if bottom_caption is None:
                self.play(FadeIn(new_cap, shift=UP * 0.1), run_time=rt)
            else:
                self.play(
                    FadeOut(bottom_caption, shift=DOWN * 0.1),
                    FadeIn(new_cap, shift=UP * 0.1),
                    run_time=rt,
                )
            bottom_caption = new_cap
            return new_cap
        
        def clear_caption(rt=0.3):
            nonlocal bottom_caption
            if bottom_caption:
                self.play(FadeOut(bottom_caption), run_time=rt)
                bottom_caption = None
        
        # ---- Animation helper (like DualSeamCarvingScene) ----
        def animate_strategy(frames, label_text, frame_color, anim_time=ANIM_TIME):
            """Animate through frames showing the strategy in action."""
            num_frames = len(frames)
            dt = anim_time / num_frames
            
            # Create initial image
            img = ImageMobject(frames[0]).set_height(DISP_H)
            img.move_to(ORIGIN)
            
            # Compute anchor for left-aligned shrinking
            img_left = img.get_left()[0]
            img_center_y = img.get_center()[1]
            initial_width = img.width
            
            # Frame rectangle
            frame_rect = Rectangle(
                width=initial_width,
                height=img.height,
                stroke_color=frame_color,
                stroke_width=4,
                fill_opacity=0,
            ).move_to(img.get_center())
            frame_glow = frame_rect.copy().set_stroke(color=frame_color, width=12, opacity=0.3)
            
            for r in [frame_rect, frame_glow]:
                r.set_z_index(100)
            
            # Label
            label = Text(label_text, font_size=28, color=frame_color)
            label.next_to(img, UP, buff=0.3)
            
            # Show initial state
            self.play(
                FadeIn(img, shift=UP * 0.2),
                FadeIn(frame_rect),
                FadeIn(frame_glow),
                FadeIn(label),
                run_time=0.8,
            )
            
            # Animate through frames
            for k in range(1, num_frames):
                new_img = ImageMobject(frames[k]).set_height(DISP_H)
                
                # Anchor to fixed left edge
                new_img.move_to([
                    img_left + new_img.width / 2.0,
                    img_center_y,
                    0,
                ])
                
                self.remove(img)
                self.add(new_img)
                img = new_img
                
                self.wait(dt)
            
            return img, frame_rect, frame_glow, label
        
        # ============================================================
        # TITLE
        # ============================================================
        title = H1("Why Seam Carving?").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)
        self.wait(HOLD * 0.5)
        
        set_caption("Different ways to shrink width using the same energy map")
        self.wait(HOLD)
        
        self.play(FadeOut(title), run_time=0.5)
        
        # ============================================================
        # STRATEGY 1: COLUMN REMOVAL
        # ============================================================
        set_caption(
            "Column removal: add up energy per column and throw away the lowest-energy columns.",
            color=YELLOW
        )
        
        img, frame, glow, label = animate_strategy(
            column_frames, 
            "Column Removal", 
            YELLOW,
            anim_time=ANIM_TIME
        )
        
        set_caption(
            "Whole strips of the image vanish at once, so edges jump suddenly.",
            color=RED
        )
        self.wait(HOLD * 1.5)
        
        # Clean up
        self.play(
            FadeOut(img),
            FadeOut(frame),
            FadeOut(glow),
            FadeOut(label),
            run_time=0.6
        )
        
        # ============================================================
        # STRATEGY 2: PIXEL PER ROW
        # ============================================================
        set_caption(
            "Pixel-per-row: in each row, remove the single pixel with the lowest energy.",
            color=PURPLE
        )
        
        img, frame, glow, label = animate_strategy(
            pixel_frames,
            "Pixel Per Row",
            PURPLE,
            anim_time=ANIM_TIME
        )
        
        set_caption(
            "Rows slide by different amounts, so straight lines turn into zigzags.",
            color=RED
        )
        self.wait(HOLD * 1.5)
        
        # Clean up
        self.play(
            FadeOut(img),
            FadeOut(frame),
            FadeOut(glow),
            FadeOut(label),
            run_time=0.6
        )
        
        # ============================================================
        # STRATEGY 3: OPTIMAL GLOBAL
        # ============================================================
        set_caption(
            "Global pixels: always remove the single lowest-energy pixel anywhere in the image.",
            color=ORANGE
        )
        
        img, frame, glow, label = animate_strategy(
            optimal_frames,
            "Global Optimal",
            ORANGE,
            anim_time=ANIM_TIME
        )
        
        set_caption(
            "Different rows lose different counts of pixels, so the picture stops being a neat rectangle.",
            color=RED
        )
        self.wait(HOLD * 1.5)
        
        # Clean up
        self.play(
            FadeOut(img),
            FadeOut(frame),
            FadeOut(glow),
            FadeOut(label),
            run_time=0.6
        )
        
        # ============================================================
        # THE SOLUTION: SEAM CARVING
        # ============================================================
        set_caption(
            "Seam carving: follow a connected low-energy path from top to bottom.",
            color=GREEN
        )
        
        img, frame, glow, label = animate_strategy(
            seam_frames,
            "Seam Carving",
            GREEN,
            anim_time=ANIM_TIME
        )
        
        set_caption(
            "Each seam removes one low-energy pixel per row, keeping shapes and the rectangle intact.",
            color=GREEN
        )
        self.wait(HOLD * 2)
        
        # ============================================================
        # CLEAN EXIT
        # ============================================================
        self.play(
            FadeOut(img),
            FadeOut(frame),
            FadeOut(glow),
            FadeOut(label),
            FadeOut(bottom_caption),
            run_time=0.8
        )
        self.wait(0.3)
