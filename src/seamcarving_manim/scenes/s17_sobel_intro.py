from manim import *
import numpy as np

# Import style if available, otherwise define locally
try:
    from seamcarving_manim.style import H1, caption
except ImportError:
    def H1(text):
        return Text(text, font_size=42, color=WHITE, weight=BOLD)
    
    def caption(text):
        return Text(text, font_size=24, color=GRAY_B)


class SobelIntroScene(Scene):
    """
    Introductory scene explaining Sobel filters in detail.
    Target duration: ~1.5 minutes with pauses for voiceover.
    """
    
    def construct(self):
        # ---- Style & Timing ----
        self.camera.background_color = "#0a0a0a"
        TITLE_RT = 0.8
        CAP_RT = 0.6
        HOLD = 2.5  # Base hold time for voiceover pauses
        CAP_BUFF = 1.2  # Buffer for captions from bottom edge
        
        # Helper to create colored formula text without LaTeX
        def create_formula(parts, colors, position, font_size=48):
            """Create a formula from parts with individual colors."""
            group = VGroup()
            for text, color in zip(parts, colors):
                t = Text(text, font_size=font_size, color=color, font="serif")
                group.add(t)
            group.arrange(RIGHT, buff=0.08)
            group.move_to(position)
            return group
        
        # ---- Title ----
        title = H1("Understanding Sobel Filters").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)
        self.wait(HOLD)
        
        # ---- Introduction Caption - motivate "change" first ----
        intro_cap = caption(
            "How do we measure change in an image?"
        ).next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(intro_cap, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD * 1.5)
        
        self.play(FadeOut(intro_cap), run_time=0.4)
        
        # ---- Motivate gradient terminology ----
        change_cap = caption(
            "We look at how pixel intensity changes from one side to the other"
        ).to_edge(DOWN, buff=CAP_BUFF)
        self.play(FadeIn(change_cap, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD)
        
        self.play(FadeOut(change_cap), run_time=0.3)
        
        gradient_cap = caption(
            "This rate of change is called the gradient"
        ).to_edge(DOWN, buff=CAP_BUFF)
        gradient_cap.set_color(GREEN)
        self.play(FadeIn(gradient_cap, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD * 1.5)
        
        self.play(FadeOut(gradient_cap), run_time=0.4)
        
        # ---- Create the 3x3 pixel grid with labels A-I ----
        pixel_size = 1.2
        grid_group = VGroup()
        pixel_squares = {}
        pixel_labels = {}
        labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        
        for idx, label in enumerate(labels):
            i, j = idx // 3, idx % 3
            
            # Create square - E (center) is highlighted
            fill_color = "#8BA4D9" if label == "E" else "#B8B8B8"
            square = Square(
                side_length=pixel_size,
                fill_color=fill_color,
                fill_opacity=1.0,
                stroke_color=WHITE,
                stroke_width=2,
            )
            square.move_to(
                np.array([
                    (j - 1) * (pixel_size + 0.1),
                    (1 - i) * (pixel_size + 0.1),
                    0
                ])
            )
            
            # Create label
            label_text = Text(label, font_size=48, color=BLACK, weight=BOLD)
            label_text.move_to(square.get_center())
            
            pixel_squares[label] = square
            pixel_labels[label] = label_text
            grid_group.add(square, label_text)
        
        grid_group.shift(LEFT * 3)
        
        # ---- Show the grid ----
        grid_cap = caption(
            "Consider a 3×3 neighborhood of pixels around center E"
        ).to_edge(DOWN, buff=CAP_BUFF)
        
        self.play(
            FadeIn(grid_group, lag_ratio=0.05),
            FadeIn(grid_cap, shift=UP * 0.1),
            run_time=1.2,
        )
        self.wait(HOLD * 1.5)
        
        # ---- Highlight center pixel ----
        self.play(FadeOut(grid_cap), run_time=0.3)
        center_cap = caption(
            "We want to measure the change at pixel E"
        ).to_edge(DOWN, buff=CAP_BUFF)
        
        center_highlight = SurroundingRectangle(
            pixel_squares["E"], 
            color=YELLOW, 
            stroke_width=4,
            buff=0.05
        )
        
        self.play(
            FadeIn(center_cap, shift=UP * 0.1),
            Create(center_highlight),
            run_time=0.8,
        )
        self.wait(HOLD * 1.5)
        
        self.play(FadeOut(center_highlight), FadeOut(center_cap), run_time=0.4)
        
        # ---- Introduce Sobel X Kernel ----
        sobel_x_cap = caption(
            "The Sobel X filter measures horizontal change"
        ).to_edge(DOWN, buff=CAP_BUFF)
        self.play(FadeIn(sobel_x_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Create Sobel X kernel display
        kernel_title = Text("Sobel X Kernel", font_size=28, color=RED).shift(RIGHT * 3 + UP * 2.5)
        
        sobel_x_values = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        kernel_group = VGroup()
        kernel_squares = {}
        
        for i in range(3):
            for j in range(3):
                val = sobel_x_values[i][j]
                
                # Color based on value
                if val < 0:
                    fill_color = interpolate_color(WHITE, BLUE, abs(val) / 2)
                elif val > 0:
                    fill_color = interpolate_color(WHITE, YELLOW, abs(val) / 2)
                else:
                    fill_color = GRAY
                
                square = Square(
                    side_length=0.8,
                    fill_color=fill_color,
                    fill_opacity=0.8,
                    stroke_color=RED,
                    stroke_width=2,
                )
                square.move_to(
                    np.array([
                        (j - 1) * 0.85,
                        (1 - i) * 0.85,
                        0
                    ])
                )
                
                val_text = Text(
                    f"{val:+d}" if val != 0 else "0",
                    font_size=28,
                    color=BLACK,
                    weight=BOLD
                )
                val_text.move_to(square.get_center())
                
                kernel_squares[(i, j)] = (square, val_text)
                kernel_group.add(square, val_text)
        
        kernel_group.shift(RIGHT * 3 + UP * 0.5)
        
        # Brackets
        left_bracket = Text("[", font_size=120, color=RED, weight=LIGHT)
        left_bracket.next_to(kernel_group, LEFT, buff=0.15)
        right_bracket = Text("]", font_size=120, color=RED, weight=LIGHT)
        right_bracket.next_to(kernel_group, RIGHT, buff=0.15)
        
        kernel_with_brackets = VGroup(left_bracket, kernel_group, right_bracket)
        
        self.play(
            Write(kernel_title),
            FadeIn(kernel_with_brackets),
            run_time=1.0,
        )
        self.wait(HOLD * 1.5)
        
        # ---- Explain left column (negative weights) ----
        self.play(FadeOut(sobel_x_cap), run_time=0.3)
        left_cap = caption(
            "Left column subtracts: weights are -1, -2, -1"
        ).to_edge(DOWN, buff=CAP_BUFF)
        left_cap.set_color(BLUE)
        
        # Highlight left column in both grid and kernel
        left_grid_highlight = VGroup(
            SurroundingRectangle(pixel_squares["A"], color=BLUE, stroke_width=4, buff=0.02),
            SurroundingRectangle(pixel_squares["D"], color=BLUE, stroke_width=4, buff=0.02),
            SurroundingRectangle(pixel_squares["G"], color=BLUE, stroke_width=4, buff=0.02),
        )
        
        self.play(
            FadeIn(left_cap, shift=UP * 0.1),
            Create(left_grid_highlight),
            run_time=0.8,
        )
        self.wait(HOLD * 1.5)
        
        # ---- Explain right column (positive weights) ----
        self.play(
            FadeOut(left_cap),
            FadeOut(left_grid_highlight),
            run_time=0.4,
        )
        
        right_cap = caption(
            "Right column adds: weights are +1, +2, +1"
        ).to_edge(DOWN, buff=CAP_BUFF)
        right_cap.set_color(YELLOW)
        
        right_grid_highlight = VGroup(
            SurroundingRectangle(pixel_squares["C"], color=YELLOW, stroke_width=4, buff=0.02),
            SurroundingRectangle(pixel_squares["F"], color=YELLOW, stroke_width=4, buff=0.02),
            SurroundingRectangle(pixel_squares["I"], color=YELLOW, stroke_width=4, buff=0.02),
        )
        
        self.play(
            FadeIn(right_cap, shift=UP * 0.1),
            Create(right_grid_highlight),
            run_time=0.8,
        )
        self.wait(HOLD * 1.5)
        
        # ---- Explain center column (zero) ----
        self.play(
            FadeOut(right_cap),
            FadeOut(right_grid_highlight),
            run_time=0.4,
        )
        
        center_col_cap = caption(
            "Center column is zero: doesn't contribute to the change"
        ).to_edge(DOWN, buff=CAP_BUFF)
        center_col_cap.set_color(GRAY_B)
        
        center_col_highlight = VGroup(
            SurroundingRectangle(pixel_squares["B"], color=GRAY, stroke_width=4, buff=0.02),
            SurroundingRectangle(pixel_squares["E"], color=GRAY, stroke_width=4, buff=0.02),
            SurroundingRectangle(pixel_squares["H"], color=GRAY, stroke_width=4, buff=0.02),
        )
        
        self.play(
            FadeIn(center_col_cap, shift=UP * 0.1),
            Create(center_col_highlight),
            run_time=0.8,
        )
        self.wait(HOLD * 1.5)
        
        self.play(
            FadeOut(center_col_cap),
            FadeOut(center_col_highlight),
            FadeOut(kernel_title),
            FadeOut(kernel_with_brackets),
            run_time=0.6,
        )
        
        # ---- Show the formula breakdown (like the reference image) ----
        formula_cap = caption(
            "The filter computes: right side minus left side"
        ).to_edge(DOWN, buff=CAP_BUFF)
        formula_cap.set_color(RED)
        self.play(FadeIn(formula_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Create formula components matching the reference image style
        row1_formula = create_formula(
            ["(", "C", " − ", "A", ")"],
            [WHITE, YELLOW, WHITE, BLUE, WHITE],
            RIGHT * 3.5 + UP * 1.8
        )
        
        row2_formula = create_formula(
            ["2", "(", "F", " − ", "D", ")"],
            [WHITE, WHITE, YELLOW, WHITE, BLUE, WHITE],
            RIGHT * 3.5 + UP * 0.3
        )
        
        # Add box around row 2 to show emphasis (like reference)
        row2_box = SurroundingRectangle(row2_formula, color=BLUE_C, stroke_width=2, buff=0.15)
        
        row3_formula = create_formula(
            ["(", "I", " − ", "G", ")"],
            [WHITE, YELLOW, WHITE, BLUE, WHITE],
            RIGHT * 3.5 + DOWN * 1.2
        )
        
        # Show row 1
        highlight_AC = VGroup(
            SurroundingRectangle(pixel_squares["A"], color=BLUE, stroke_width=3, buff=0.02),
            SurroundingRectangle(pixel_squares["C"], color=YELLOW, stroke_width=3, buff=0.02),
        )
        
        self.play(
            Create(highlight_AC),
            Write(row1_formula),
            run_time=1.0,
        )
        self.wait(HOLD)
        
        # Show row 2 (with 2x weight - the important row)
        self.play(FadeOut(highlight_AC), run_time=0.3)
        
        highlight_DF = VGroup(
            SurroundingRectangle(pixel_squares["D"], color=BLUE, stroke_width=3, buff=0.02),
            SurroundingRectangle(pixel_squares["F"], color=YELLOW, stroke_width=3, buff=0.02),
        )
        
        self.play(
            Create(highlight_DF),
            Write(row2_formula),
            Create(row2_box),
            run_time=1.0,
        )
        self.wait(HOLD)
        
        # Show row 3
        self.play(FadeOut(highlight_DF), run_time=0.3)
        
        highlight_GI = VGroup(
            SurroundingRectangle(pixel_squares["G"], color=BLUE, stroke_width=3, buff=0.02),
            SurroundingRectangle(pixel_squares["I"], color=YELLOW, stroke_width=3, buff=0.02),
        )
        
        self.play(
            Create(highlight_GI),
            Write(row3_formula),
            run_time=1.0,
        )
        self.wait(HOLD)
        
        self.play(FadeOut(highlight_GI), run_time=0.3)
        
        # ---- Show complete formula ----
        self.play(FadeOut(formula_cap), run_time=0.3)
        
        complete_cap = caption(
            "Sum all terms to get the horizontal change at E"
        ).to_edge(DOWN, buff=CAP_BUFF)
        complete_cap.set_color(GREEN)
        self.play(FadeIn(complete_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Plus signs between rows
        plus1 = Text("+", font_size=36, color=WHITE, font="serif").move_to(
            (row1_formula.get_center() + row2_formula.get_center()) / 2 + LEFT * 1.2
        )
        plus2 = Text("+", font_size=36, color=WHITE, font="serif").move_to(
            (row2_formula.get_center() + row3_formula.get_center()) / 2 + LEFT * 1.2
        )
        
        # Final formula
        gx_parts = ["Gₓ", " = ", "(C−A)", " + ", "2(F−D)", " + ", "(I−G)"]
        gx_colors = [GREEN, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE]
        gx_formula = create_formula(gx_parts, gx_colors, RIGHT * 3.5 + DOWN * 2.4, font_size=28)
        
        self.play(
            Write(plus1),
            Write(plus2),
            run_time=0.6,
        )
        self.wait(HOLD * 0.5)
        
        self.play(
            Write(gx_formula),
            run_time=1.0,
        )
        self.wait(HOLD * 1.5)
        
        # ---- Transition to why 2x weight ----
        self.play(FadeOut(complete_cap), run_time=0.3)
        
        weight_cap = caption(
            "The ×2 weight on middle row: closer pixels matter more"
        ).to_edge(DOWN, buff=CAP_BUFF)
        weight_cap.set_color(PURPLE)
        
        self.play(
            FadeIn(weight_cap, shift=UP * 0.1),
            row2_box.animate.set_stroke(color=PURPLE, width=4),
            Indicate(row2_formula[0], color=PURPLE, scale_factor=1.3),  # The "2"
            run_time=1.0,
        )
        self.wait(HOLD * 2)
        
        # ---- Clean up letter formulas ----
        self.play(
            FadeOut(row1_formula),
            FadeOut(row2_formula),
            FadeOut(row2_box),
            FadeOut(row3_formula),
            FadeOut(plus1),
            FadeOut(plus2),
            FadeOut(gx_formula),
            FadeOut(weight_cap),
            FadeOut(grid_group),
            run_time=0.8,
        )
        
        # ============================================================
        # NUMERICAL EXAMPLE - Show how the filter matrix is applied
        # ============================================================
        
        num_example_cap = caption(
            "Let's see this with actual numbers"
        ).to_edge(DOWN, buff=CAP_BUFF)
        num_example_cap.set_color(ORANGE)
        self.play(FadeIn(num_example_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Create numerical pixel grid (showing an edge: dark on left, bright on right)
        num_pixel_values = [
            [50, 50, 200],
            [50, 100, 200],
            [50, 50, 200]
        ]
        
        num_grid_group = VGroup()
        num_pixel_squares = {}
        num_pixel_texts = {}
        num_pixel_size = 1.0
        
        for i in range(3):
            for j in range(3):
                val = num_pixel_values[i][j]
                color = interpolate_color(BLACK, WHITE, val / 255.0)
                
                square = Square(
                    side_length=num_pixel_size,
                    fill_color=color,
                    fill_opacity=1.0,
                    stroke_color=WHITE,
                    stroke_width=2,
                )
                square.move_to(
                    np.array([
                        (j - 1) * (num_pixel_size + 0.1),
                        (1 - i) * (num_pixel_size + 0.1),
                        0
                    ])
                )
                
                # Value text
                text_color = WHITE if val < 128 else BLACK
                val_text = Text(str(val), font_size=28, color=text_color, weight=BOLD)
                val_text.move_to(square.get_center())
                
                num_pixel_squares[(i, j)] = square
                num_pixel_texts[(i, j)] = val_text
                num_grid_group.add(square, val_text)
        
        num_grid_group.shift(LEFT * 4)
        
        # Pixel grid label
        pixel_label = Text("Pixel Values", font_size=24, color=WHITE)
        pixel_label.next_to(num_grid_group, UP, buff=0.3)
        
        self.play(
            FadeIn(num_grid_group, lag_ratio=0.05),
            FadeIn(pixel_label),
            run_time=1.0,
        )
        self.wait(HOLD)
        
        # Show the Sobel X kernel again
        self.play(FadeOut(num_example_cap), run_time=0.3)
        
        kernel_cap = caption(
            "Multiply each pixel by its kernel weight, then sum"
        ).to_edge(DOWN, buff=CAP_BUFF)
        kernel_cap.set_color(RED)
        self.play(FadeIn(kernel_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Create kernel display for numerical example
        num_kernel_group = VGroup()
        kernel_size = 1.0
        
        for i in range(3):
            for j in range(3):
                val = sobel_x_values[i][j]
                
                if val < 0:
                    fill_color = interpolate_color(GRAY_D, BLUE, abs(val) / 2)
                elif val > 0:
                    fill_color = interpolate_color(GRAY_D, YELLOW, abs(val) / 2)
                else:
                    fill_color = GRAY_D
                
                square = Square(
                    side_length=kernel_size,
                    fill_color=fill_color,
                    fill_opacity=0.8,
                    stroke_color=RED,
                    stroke_width=2,
                )
                square.move_to(
                    np.array([
                        (j - 1) * (kernel_size + 0.1),
                        (1 - i) * (kernel_size + 0.1),
                        0
                    ])
                )
                
                val_text = Text(
                    f"{val:+d}" if val != 0 else "0",
                    font_size=28,
                    color=WHITE,
                    weight=BOLD
                )
                val_text.move_to(square.get_center())
                
                num_kernel_group.add(square, val_text)
        
        num_kernel_group.shift(LEFT * 0.5)
        
        # Kernel label
        kernel_label = Text("Sobel X", font_size=24, color=RED)
        kernel_label.next_to(num_kernel_group, UP, buff=0.3)
        
        # Multiply symbol
        multiply_symbol = Text("×", font_size=48, color=WHITE)
        multiply_symbol.move_to((num_grid_group.get_center() + num_kernel_group.get_center()) / 2)
        
        self.play(
            FadeIn(num_kernel_group),
            FadeIn(kernel_label),
            FadeIn(multiply_symbol),
            run_time=1.0,
        )
        self.wait(HOLD)
        
        # Show the calculation step by step
        self.play(FadeOut(kernel_cap), run_time=0.3)
        
        calc_cap = caption(
            "Element-wise multiply, then add all products"
        ).to_edge(DOWN, buff=CAP_BUFF)
        calc_cap.set_color(ORANGE)
        self.play(FadeIn(calc_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Create calculation display
        calc_group = VGroup()
        calc_x = RIGHT * 3.8
        calc_y_start = UP * 2.5
        
        products = []
        calc_texts = []
        
        for i in range(3):
            for j in range(3):
                pixel_val = num_pixel_values[i][j]
                kernel_val = sobel_x_values[i][j]
                product = pixel_val * kernel_val
                products.append(product)
                
                # Create text showing: pixel × kernel = product
                if kernel_val != 0:
                    calc_text = Text(
                        f"{pixel_val} × {kernel_val:+d} = {product:+d}",
                        font_size=20,
                        color=WHITE
                    )
                else:
                    calc_text = Text(
                        f"{pixel_val} × 0 = 0",
                        font_size=20,
                        color=GRAY
                    )
                
                idx = i * 3 + j
                calc_text.move_to(calc_x + calc_y_start + DOWN * (idx * 0.35))
                calc_texts.append(calc_text)
                calc_group.add(calc_text)
        
        # Animate calculations appearing
        self.play(
            LaggedStart(
                *[FadeIn(ct, shift=LEFT * 0.2) for ct in calc_texts],
                lag_ratio=0.1,
            ),
            run_time=2.0,
        )
        self.wait(HOLD)
        
        # Show the sum
        self.play(FadeOut(calc_cap), run_time=0.3)
        
        sum_cap = caption(
            "The result tells us the strength of horizontal change"
        ).to_edge(DOWN, buff=CAP_BUFF)
        sum_cap.set_color(GREEN)
        self.play(FadeIn(sum_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        total = sum(products)
        
        # Sum line - position just below the last calculation
        last_calc_y = calc_y_start + DOWN * (8 * 0.35)  # 9 items, index 8 is last
        sum_line = Line(
            calc_x + LEFT * 1.2 + last_calc_y + DOWN * 0.3,
            calc_x + RIGHT * 1.2 + last_calc_y + DOWN * 0.3,
            color=WHITE,
            stroke_width=2
        )
        
        sum_text = Text(
            f"Sum = {total:+d}",
            font_size=28,
            color=GREEN,
            weight=BOLD
        )
        sum_text.next_to(sum_line, DOWN, buff=0.2)
        
        self.play(
            Create(sum_line),
            Write(sum_text),
            run_time=1.0,
        )
        self.wait(HOLD)
        
        # Explain the result
        self.play(FadeOut(sum_cap), run_time=0.3)
        
        result_cap = caption(
            f"Positive value (+{total}) means brightness increases left to right → vertical edge!"
        ).to_edge(DOWN, buff=CAP_BUFF)
        result_cap.set_color(GREEN)
        self.play(FadeIn(result_cap, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD * 2)
        
        # Clean up numerical example
        self.play(
            FadeOut(num_grid_group),
            FadeOut(pixel_label),
            FadeOut(num_kernel_group),
            FadeOut(kernel_label),
            FadeOut(multiply_symbol),
            FadeOut(calc_group),
            FadeOut(sum_line),
            FadeOut(sum_text),
            FadeOut(result_cap),
            run_time=0.8,
        )
        
        # ============================================================
        # SOBEL Y SECTION
        # ============================================================
        
        # Bring back the letter grid - reset to original left position
        # grid_group was shifted LEFT * 3, then faded out. Now move it back to that position.
        grid_group.move_to(ORIGIN).shift(LEFT * 3)
        self.play(FadeIn(grid_group), run_time=0.6)
        
        # ---- Sobel Y Introduction ----
        sobel_y_cap = caption(
            "Sobel Y measures vertical change the same way"
        ).to_edge(DOWN, buff=CAP_BUFF)
        sobel_y_cap.set_color(BLUE)
        self.play(FadeIn(sobel_y_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Create Sobel Y kernel
        kernel_y_title = Text("Sobel Y Kernel", font_size=28, color=BLUE).shift(RIGHT * 3 + UP * 2.5)
        
        sobel_y_values = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        kernel_y_group = VGroup()
        
        for i in range(3):
            for j in range(3):
                val = sobel_y_values[i][j]
                
                if val < 0:
                    fill_color = interpolate_color(WHITE, BLUE, abs(val) / 2)
                elif val > 0:
                    fill_color = interpolate_color(WHITE, YELLOW, abs(val) / 2)
                else:
                    fill_color = GRAY
                
                square = Square(
                    side_length=0.8,
                    fill_color=fill_color,
                    fill_opacity=0.8,
                    stroke_color=BLUE,
                    stroke_width=2,
                )
                square.move_to(
                    np.array([
                        (j - 1) * 0.85,
                        (1 - i) * 0.85,
                        0
                    ])
                )
                
                val_text = Text(
                    f"{val:+d}" if val != 0 else "0",
                    font_size=28,
                    color=BLACK,
                    weight=BOLD
                )
                val_text.move_to(square.get_center())
                
                kernel_y_group.add(square, val_text)
        
        kernel_y_group.shift(RIGHT * 3 + UP * 0.5)
        
        left_bracket_y = Text("[", font_size=120, color=BLUE, weight=LIGHT)
        left_bracket_y.next_to(kernel_y_group, LEFT, buff=0.15)
        right_bracket_y = Text("]", font_size=120, color=BLUE, weight=LIGHT)
        right_bracket_y.next_to(kernel_y_group, RIGHT, buff=0.15)
        
        kernel_y_with_brackets = VGroup(left_bracket_y, kernel_y_group, right_bracket_y)
        
        self.play(
            Write(kernel_y_title),
            FadeIn(kernel_y_with_brackets),
            run_time=1.0,
        )
        self.wait(HOLD * 1.5)
        
        # ---- Show Y formula ----
        self.play(FadeOut(sobel_y_cap), run_time=0.3)
        
        y_formula_cap = caption(
            "Sobel Y: bottom row minus top row"
        ).to_edge(DOWN, buff=CAP_BUFF)
        y_formula_cap.set_color(BLUE)
        self.play(FadeIn(y_formula_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Highlight top row
        top_highlight = VGroup(
            SurroundingRectangle(pixel_squares["A"], color=BLUE, stroke_width=3, buff=0.02),
            SurroundingRectangle(pixel_squares["B"], color=BLUE, stroke_width=3, buff=0.02),
            SurroundingRectangle(pixel_squares["C"], color=BLUE, stroke_width=3, buff=0.02),
        )
        
        # Highlight bottom row
        bottom_highlight = VGroup(
            SurroundingRectangle(pixel_squares["G"], color=YELLOW, stroke_width=3, buff=0.02),
            SurroundingRectangle(pixel_squares["H"], color=YELLOW, stroke_width=3, buff=0.02),
            SurroundingRectangle(pixel_squares["I"], color=YELLOW, stroke_width=3, buff=0.02),
        )
        
        self.play(
            Create(top_highlight),
            Create(bottom_highlight),
            run_time=1.0,
        )
        self.wait(HOLD * 1.5)
        
        # Y formula
        gy_parts = ["Gᵧ", " = ", "(G−A)", " + ", "2(H−B)", " + ", "(I−C)"]
        gy_colors = [BLUE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE]
        gy_formula = create_formula(gy_parts, gy_colors, RIGHT * 3 + DOWN * 1.8, font_size=28)
        
        self.play(
            Write(gy_formula),
            run_time=1.0,
        )
        self.wait(HOLD * 1.5)
        
        # ---- Final summary ----
        self.play(
            FadeOut(top_highlight),
            FadeOut(bottom_highlight),
            FadeOut(y_formula_cap),
            FadeOut(kernel_y_title),
            FadeOut(kernel_y_with_brackets),
            FadeOut(gy_formula),
            run_time=0.8,
        )
        
        # Show both kernels side by side
        summary_cap = caption(
            "Together, Sobel X and Y give us the complete gradient"
        ).to_edge(DOWN, buff=CAP_BUFF)
        summary_cap.set_color(GREEN)
        self.play(FadeIn(summary_cap, shift=UP * 0.1), run_time=CAP_RT)
        
        # Recreate both kernels smaller and side by side
        def create_mini_kernel(values, color, position, label):
            group = VGroup()
            for i in range(3):
                for j in range(3):
                    val = values[i][j]
                    sq = Square(
                        side_length=0.5,
                        fill_color=GRAY_D,
                        fill_opacity=0.8,
                        stroke_color=color,
                        stroke_width=1.5,
                    )
                    sq.move_to(position + RIGHT * (j - 1) * 0.55 + DOWN * (i - 1) * 0.55)
                    
                    txt = Text(
                        str(val) if val >= 0 else str(val),
                        font_size=18,
                        color=WHITE,
                    )
                    txt.move_to(sq.get_center())
                    group.add(sq, txt)
            
            lbl = Text(label, font_size=24, color=color)
            lbl.next_to(group, UP, buff=0.2)
            group.add(lbl)
            return group
        
        mini_x = create_mini_kernel(sobel_x_values, RED, RIGHT * 2 + UP * 1, "Sobel X")
        mini_y = create_mini_kernel(sobel_y_values, BLUE, RIGHT * 4.5 + UP * 1, "Sobel Y")
        
        self.play(
            FadeIn(mini_x),
            FadeIn(mini_y),
            run_time=1.0,
        )
        self.wait(HOLD)
        
        # Final gradient formula
        gradient_parts = ["|∇I|", " = ", "√(Gₓ² + Gᵧ²)"]
        gradient_colors = [GREEN, WHITE, GREEN]
        gradient_formula = create_formula(gradient_parts, gradient_colors, RIGHT * 3.25 + DOWN * 0.8, font_size=28)
        
        self.play(Write(gradient_formula), run_time=1.0)
        self.wait(HOLD * 2)
        
        # ---- Fade out everything for transition ----
        self.play(
            FadeOut(title),
            FadeOut(grid_group),
            FadeOut(mini_x),
            FadeOut(mini_y),
            FadeOut(gradient_formula),
            FadeOut(summary_cap),
            run_time=1.0,
        )
        self.wait(0.5)