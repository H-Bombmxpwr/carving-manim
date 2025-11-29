from manim import *
import numpy as np
from scipy.ndimage import convolve

from seamcarving_manim.style import H1, caption


class EdgeDetectionScene(Scene):
    def construct(self):
        # ---- look & pacing ----
        self.camera.background_color = "#0a0a0a"
        TITLE_RT = 0.8
        CAP_RT = 0.8
        HOLD = 3
        CONV_STEP_TIME = 0.15

        # ---- title ----
        title = H1("Edge Detection: Finding Image Gradients").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)
        self.wait(HOLD)

        # ---- Create grayscale circle (11x11 for more detail) ----
        size = 11
        circle_pattern = np.zeros((size, size), dtype=np.uint8)
        center = size // 2
        for i in range(size):
            for j in range(size):
                dist = np.sqrt((i - center) ** 2 + (j - center) ** 2)
                if dist <= 3.0:
                    circle_pattern[i, j] = 255
                elif dist <= 3.5:
                    circle_pattern[i, j] = 200
                elif dist <= 4.0:
                    circle_pattern[i, j] = 150
                elif dist <= 4.5:
                    circle_pattern[i, j] = 100
                elif dist <= 5.0:
                    circle_pattern[i, j] = 50

        # ---- Display pixel grid LEFT ----
        pixel_size = 0.45
        grid = VGroup()
        pixel_squares = {}
        intensity_texts = VGroup()

        for i in range(size):
            for j in range(size):
                val = circle_pattern[i, j]
                color = interpolate_color(BLACK, WHITE, val / 255.0)
                square = Square(
                    side_length=pixel_size,
                    fill_color=color,
                    fill_opacity=1.0,
                    stroke_color=GRAY,
                    stroke_width=1,
                )
                square.move_to(
                    np.array(
                        [
                            (j - center) * pixel_size,
                            (center - i) * pixel_size,
                            0,
                        ]
                    )
                )

                intensity_text = Text(
                    str(val),
                    font_size=12,
                    color=RED if val < 128 else BLACK,
                )
                intensity_text.move_to(square.get_center())

                pixel_squares[(i, j)] = square
                grid.add(square, intensity_text)
                intensity_texts.add(intensity_text)

        grid.shift(LEFT * 4.5)

        intro_cap = caption("Simple grayscale circle").next_to(
            grid, DOWN, buff=0.5
        )
        self.play(
            FadeIn(grid, lag_ratio=0.05),
            FadeIn(intro_cap, shift=UP * 0.1),
            run_time=1.5,
        )
        self.wait(HOLD * 1.5)

        self.play(
            FadeOut(title),
            FadeOut(intro_cap),
            run_time=0.6,
        )
        self.wait(0.5)

        # ---- helper: Sobel kernel matrix drawing ----
        def create_kernel_matrix(values, color, position):
            matrix_group = VGroup()
            for i in range(3):
                for j in range(3):
                    num = Text(str(values[i][j]), font_size=24, color=WHITE)
                    num.move_to(
                        position
                        + RIGHT * (j - 1) * 0.5
                        + DOWN * (i - 1) * 0.5
                    )
                    matrix_group.add(num)
            left_bracket = Text("[", font_size=50, color=color).next_to(
                matrix_group, LEFT, buff=0.1
            )
            right_bracket = Text("]", font_size=50, color=color).next_to(
                matrix_group, RIGHT, buff=0.1
            )
            return VGroup(left_bracket, matrix_group, right_bracket)

        # ---- Explain Sobel X Filter Concept ----
        explain_cap1 = caption(
            "Sobel filters detect edges by finding intensity changes"
        ).to_edge(DOWN, buff=1.2)
        self.play(FadeIn(explain_cap1, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD * 1.5)

        sobel_x_values = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        sobel_x_matrix = create_kernel_matrix(
            sobel_x_values, RED, RIGHT * 3 + UP * 1.5
        )
        sobel_x_label = Text(
            "Sobel X Kernel", font_size=24, color=RED
        ).next_to(sobel_x_matrix, UP, buff=0.2)

        self.play(
            Write(sobel_x_matrix),
            Write(sobel_x_label),
            run_time=1.2,
        )
        self.wait(HOLD)

        self.play(FadeOut(explain_cap1, shift=DOWN * 0.1), run_time=0.3)
        explain_cap2 = caption(
            "Left column: -1, -2, -1  →  detects dark pixels on left"
        ).next_to(sobel_x_matrix, DOWN, buff=0.8)
        explain_cap2.set_color(BLUE)
        self.play(FadeIn(explain_cap2, shift=UP * 0.1), run_time=CAP_RT)

        left_indices = [0, 3, 6]
        for i in left_indices:
            sobel_x_matrix[1][i].set_color(BLUE)

        self.play(
            *[
                Indicate(sobel_x_matrix[1][i], color=BLUE, scale_factor=1.2)
                for i in left_indices
            ],
            run_time=0.8,
        )
        self.wait(HOLD)

        self.play(FadeOut(explain_cap2, shift=DOWN * 0.1), run_time=0.3)
        explain_cap3 = caption(
            "Right column: +1, +2, +1  →  detects bright pixels on right"
        ).next_to(sobel_x_matrix, DOWN, buff=0.8)
        explain_cap3.set_color(YELLOW)
        self.play(FadeIn(explain_cap3, shift=UP * 0.1), run_time=CAP_RT)

        right_indices = [2, 5, 8]
        for i in right_indices:
            sobel_x_matrix[1][i].set_color(YELLOW)

        self.play(
            *[
                Indicate(sobel_x_matrix[1][i], color=YELLOW, scale_factor=1.2)
                for i in right_indices
            ],
            run_time=0.8,
        )
        self.wait(HOLD)

        self.play(
            FadeOut(explain_cap3, shift=DOWN * 0.1),
            run_time=0.6,
        )
        self.wait(HOLD)

        explain_cap4 = caption(
            "Result: positive when bright→left, negative when dark→left"
        ).next_to(sobel_x_matrix, DOWN, buff=0.8)
        explain_cap4.set_color(GREEN)
        self.play(FadeIn(explain_cap4, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD * 2)

        self.play(
            FadeOut(explain_cap4, shift=DOWN * 0.1),
            run_time=0.6,
        )

        # ---- Example convolution explanation (kept as-is) ----
        self.play(
            FadeOut(sobel_x_matrix),
            FadeOut(sobel_x_label),
            run_time=0.6,
        )

        explain_cap5 = caption(
            "Example: multiply each pixel by kernel weight, then sum"
        ).to_edge(DOWN, buff=0.8)
        explain_cap5.set_color(PURPLE)
        self.play(FadeIn(explain_cap5, shift=UP * 0.1), run_time=CAP_RT)

        example_i, example_j = 4, 7
        kernel_display = VGroup()
        kernel_matrix_pos = LEFT * 2 + UP * 1

        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                kernel_val = sobel_x_values[di + 1][dj + 1]
                pixel_val = int(circle_pattern[example_i + di, example_j + dj])

                box = Square(
                    side_length=0.6,
                    fill_color=PURPLE,
                    fill_opacity=0.2,
                    stroke_color=PURPLE,
                    stroke_width=2,
                )
                box.move_to(
                    kernel_matrix_pos
                    + RIGHT * dj * 0.65
                    + DOWN * di * 0.65
                )

                kernel_text = Text(
                    f"{kernel_val}",
                    font_size=20,
                    color=WHITE,
                    weight=BOLD,
                )
                kernel_text.move_to(box.get_center() + UP * 0.12)

                pixel_text = Text(
                    f"×{pixel_val}",
                    font_size=16,
                    color=GRAY,
                )
                pixel_text.move_to(box.get_center() + DOWN * 0.12)

                kernel_display.add(box, kernel_text, pixel_text)

        example_region = VGroup()
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                h = pixel_squares[(example_i + di, example_j + dj)].copy()
                h.set_stroke(color=PURPLE, width=4)
                example_region.add(h)

        self.play(
            Create(example_region),
            FadeIn(kernel_display, shift=RIGHT * 0.3),
            run_time=1.0,
        )
        self.wait(HOLD)

        calculation_group = VGroup()
        calc_title = Text(
            "Multiplications:", font_size=18, color=PURPLE
        ).shift(RIGHT * 4.5 + UP * 2.8)
        calculation_group.add(calc_title)

        y_offset = 2.2
        idx = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                pixel_val = int(circle_pattern[example_i + di, example_j + dj])
                kernel_val = sobel_x_values[di + 1][dj + 1]
                product = pixel_val * kernel_val

                calc_text = Text(
                    f"{pixel_val} × {kernel_val:+d} = {product:+d}",
                    font_size=16,
                    color=PURPLE,
                ).shift(
                    RIGHT * 4.5
                    + UP * (y_offset - idx * 0.28)
                )
                idx += 1
                calculation_group.add(calc_text)

        self.play(
            LaggedStart(
                *[
                    FadeIn(calc, shift=LEFT * 0.2)
                    for calc in calculation_group[1:]
                ],
                lag_ratio=0.25,
            ),
            FadeIn(calc_title),
            run_time=4,
        )
        self.wait(HOLD * 1.5)

        self.play(
            FadeOut(example_region),
            FadeOut(kernel_display),
            FadeOut(calculation_group),
            FadeOut(explain_cap5, shift=DOWN * 0.1),
            run_time=0.8,
        )
        self.wait(0.5)

        # ---- Part 1: Apply Sobel X ----
        sobel_x_cap = caption(
            "Applying Sobel X: detects vertical edges"
        ).to_edge(DOWN, buff=0.8)
        sobel_x_cap.set_color(RED)
        self.play(FadeIn(sobel_x_cap, shift=UP * 0.1), run_time=CAP_RT)

        sobel_x_matrix = create_kernel_matrix(
            sobel_x_values, RED, ORIGIN + UP * 2.5
        )
        sobel_x_label = Text(
            "Sobel X", font_size=24, color=RED
        ).next_to(sobel_x_matrix, UP, buff=0.2)

        self.play(
            Write(sobel_x_matrix),
            Write(sobel_x_label),
            run_time=0.8,
        )
        self.wait(HOLD * 0.5)

        result_x_grid = VGroup()
        result_x_squares = {}
        result_x_texts = VGroup()

        sobel_x_kernel = np.array(sobel_x_values)
        grad_x = convolve(circle_pattern.astype(float), sobel_x_kernel, mode="constant")

        grad_x_max = np.abs(grad_x).max()
        grad_x_normalized = np.clip(
            np.abs(grad_x) / grad_x_max * 255, 0, 255
        ).astype(np.uint8)

        for i in range(size):
            for j in range(size):
                val = grad_x_normalized[i, j]
                color = interpolate_color(BLACK, RED, val / 255.0)
                square = Square(
                    side_length=pixel_size,
                    fill_color=color,
                    fill_opacity=0.0,  # start hidden
                    stroke_color=GRAY,
                    stroke_width=1,
                )
                square.move_to(
                    np.array(
                        [
                            (j - center) * pixel_size,
                            (center - i) * pixel_size,
                            0,
                        ]
                    )
                )
                result_x_squares[(i, j)] = square
                result_x_grid.add(square)

        result_x_grid.shift(RIGHT * 1.5)
        result_x_grid.set_opacity(0)  # group opacity
        self.add(result_x_grid)

        result_x_label = Text("∂I/∂x", font_size=24, color=RED).next_to(result_x_grid, UP, buff=0.25)


        self.play(
            FadeOut(sobel_x_matrix),
            FadeOut(sobel_x_label),
            run_time=0.5,
        )

        for i in range(1, size - 1):
            for j in range(1, size - 1):
                kernel_overlay = VGroup()
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        pos = pixel_squares[(i + di, j + dj)].get_center()
                        kernel_val = sobel_x_values[di + 1][dj + 1]

                        h = pixel_squares[(i + di, j + dj)].copy()
                        h.set_stroke(color=RED, width=3)

                        kernel_text = Text(
                            f"[{kernel_val}]",
                            font_size=10,
                            color=RED,
                            weight=BOLD,
                        ).move_to(pos + UP * 0.15)

                        kernel_overlay.add(h, kernel_text)

                self.add(kernel_overlay)

                result_val = int(grad_x[i, j])
                result_text = Text(
                    str(result_val),
                    font_size=12,
                    color=WHITE,
                ).move_to(result_x_squares[(i, j)].get_center())

                result_x_squares[(i, j)].set_opacity(1)
                self.add(result_text)
                result_x_texts.add(result_text)

                self.wait(CONV_STEP_TIME)
                self.remove(kernel_overlay)

        self.play(
            FadeIn(result_x_label, shift=UP * 0.1),
            run_time=0.5,
        )
        self.wait(HOLD)

        self.play(FadeOut(sobel_x_cap, shift=DOWN * 0.1), run_time=0.3)
        vector_x_cap = caption(
            "Gradient vectors show direction and magnitude of change"
        ).to_edge(DOWN, buff=0.8)
        vector_x_cap.set_color(RED)
        self.play(FadeIn(vector_x_cap, shift=UP * 0.1), run_time=CAP_RT)

        x_vectors = VGroup()
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                gx_val = grad_x[i, j]
                if abs(gx_val) > 20:
                    pos = result_x_squares[(i, j)].get_center()
                    mag = gx_val / grad_x_max * 0.8
                    vec = Arrow(
                        start=pos,
                        end=pos + RIGHT * mag,
                        color=RED,
                        stroke_width=2,
                        buff=0,
                        max_tip_length_to_length_ratio=0.35,
                        max_stroke_width_to_length_ratio=8,
                    )
                    x_vectors.add(vec)

        self.play(
            LaggedStart(
                *[GrowArrow(v) for v in x_vectors],
                lag_ratio=0.02,
            ),
            run_time=2.5,
        )
        self.wait(HOLD * 1.5)

        self.play(
            FadeOut(vector_x_cap, shift=DOWN*0.1),
            FadeOut(result_x_grid),
            FadeOut(result_x_label),
            FadeOut(x_vectors),
            FadeOut(result_x_texts),
            run_time=1.0
        )

        self.wait(0.5)

        # ---- Part 2: Apply Sobel Y (NOW MIRRORS SOBEL X FLOW) ----
        sobel_y_cap = caption(
            "Applying Sobel Y: detects horizontal edges"
        ).to_edge(DOWN, buff=0.8)
        sobel_y_cap.set_color(BLUE)
        self.play(FadeIn(sobel_y_cap, shift=UP * 0.1), run_time=CAP_RT)

        sobel_y_values = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        sobel_y_matrix = create_kernel_matrix(
            sobel_y_values, BLUE, ORIGIN + UP * 2.5
        )
        sobel_y_label = Text(
            "Sobel Y", font_size=24, color=BLUE
        ).next_to(sobel_y_matrix, UP, buff=0.2)

        self.play(
            Write(sobel_y_matrix),
            Write(sobel_y_label),
            run_time=0.8,
        )
        self.wait(HOLD * 0.5)

        result_y_grid = VGroup()
        result_y_squares = {}
        result_y_texts = VGroup()

        sobel_y_kernel = np.array(sobel_y_values)
        grad_y = convolve(circle_pattern.astype(float), sobel_y_kernel, mode="constant")

        grad_y_max = np.abs(grad_y).max()
        grad_y_normalized = np.clip(
            np.abs(grad_y) / grad_y_max * 255, 0, 255
        ).astype(np.uint8)

        for i in range(size):
            for j in range(size):
                val = grad_y_normalized[i, j]
                color = interpolate_color(BLACK, BLUE, val / 255.0)
                square = Square(
                    side_length=pixel_size,
                    fill_color=color,
                    fill_opacity=0.0,  # start hidden
                    stroke_color=GRAY,
                    stroke_width=1,
                )
                square.move_to(
                    np.array(
                        [
                            (j - center) * pixel_size,
                            (center - i) * pixel_size,
                            0,
                        ]
                    )
                )
                result_y_squares[(i, j)] = square
                result_y_grid.add(square)

        result_y_grid.shift(RIGHT * 1.5)
        result_y_grid.set_opacity(0)
        self.add(result_y_grid)

        result_y_label = Text("∂I/∂y", font_size=24, color=BLUE).next_to(result_y_grid, UP, buff=0.25)


        # fade out Y kernel before the step-by-step conv, just like X
        self.play(
            FadeOut(sobel_y_matrix),
            FadeOut(sobel_y_label),
            run_time=0.5,
        )

        for i in range(1, size - 1):
            for j in range(1, size - 1):
                kernel_overlay = VGroup()
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        pos = pixel_squares[(i + di, j + dj)].get_center()
                        kernel_val = sobel_y_values[di + 1][dj + 1]

                        h = pixel_squares[(i + di, j + dj)].copy()
                        h.set_stroke(color=BLUE, width=3)

                        kernel_text = Text(
                            f"[{kernel_val}]",
                            font_size=10,
                            color=BLUE,
                            weight=BOLD,
                        ).move_to(pos + UP * 0.15)

                        kernel_overlay.add(h, kernel_text)

                self.add(kernel_overlay)

                result_val = int(grad_y[i, j])
                result_text = Text(
                    str(result_val),
                    font_size=12,
                    color=WHITE,
                ).move_to(result_y_squares[(i, j)].get_center())

                result_y_squares[(i, j)].set_opacity(1)
                self.add(result_text)
                result_y_texts.add(result_text)

                self.wait(CONV_STEP_TIME)
                self.remove(kernel_overlay)

        self.play(
            FadeIn(result_y_label, shift=UP * 0.1),
            run_time=0.5,
        )
        self.wait(HOLD)

        self.play(FadeOut(sobel_y_cap, shift=DOWN * 0.1), run_time=0.3)
        vector_y_cap = caption(
            "Y-gradients point in vertical direction"
        ).to_edge(DOWN, buff=0.8)
        vector_y_cap.set_color(BLUE)
        self.play(FadeIn(vector_y_cap, shift=UP * 0.1), run_time=CAP_RT)

        y_vectors = VGroup()
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                gy_val = grad_y[i, j]
                if abs(gy_val) > 20:
                    pos = result_y_squares[(i, j)].get_center()
                    mag = gy_val / grad_y_max * 0.8
                    vec = Arrow(
                        start=pos,
                        end=pos + DOWN * mag,
                        color=BLUE,
                        stroke_width=2,
                        buff=0,
                        max_tip_length_to_length_ratio=0.35,
                        max_stroke_width_to_length_ratio=8,
                    )
                    y_vectors.add(vec)

        self.play(
            LaggedStart(
                *[GrowArrow(v) for v in y_vectors],
                lag_ratio=0.02,
            ),
            run_time=2.5,
        )
        self.wait(HOLD * 1.5)

        # ---- Clean up Y like X ----
        self.play(
            FadeOut(vector_y_cap, shift=DOWN * 0.1),
            FadeOut(result_y_grid),
            FadeOut(result_y_label),
            FadeOut(y_vectors),
            FadeOut(result_y_texts),
            run_time=1.0,
        )
        self.wait(0.5)

        # ---- Combine on original image ----
        combine_cap = caption(
            "Combining X and Y gradients into single edge detection"
        ).to_edge(DOWN, buff=0.8)
        combine_cap.set_color(GREEN)
        self.play(FadeIn(combine_cap, shift=UP * 0.1), run_time=CAP_RT)

        self.play(FadeOut(intensity_texts), run_time=0.4)
        self.play(grid.animate.shift(RIGHT * 4.5), run_time=0.8)


        x_vectors_centered = VGroup()
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                gx_val = grad_x[i, j]
                if abs(gx_val) > 20:
                    pos = pixel_squares[(i, j)].get_center()
                    mag = gx_val / grad_x_max * 0.8
                    vec = Arrow(
                        start=pos,
                        end=pos + RIGHT * mag,
                        color=RED,
                        stroke_width=2,
                        buff=0,
                        max_tip_length_to_length_ratio=0.35,
                        max_stroke_width_to_length_ratio=8,
                    )
                    x_vectors_centered.add(vec)

        self.play(
            LaggedStart(
                *[GrowArrow(v) for v in x_vectors_centered],
                lag_ratio=0.01,
            ),
            run_time=1.5,
        )
        self.wait(HOLD * 0.5)

        y_vectors_centered = VGroup()
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                gy_val = grad_y[i, j]
                if abs(gy_val) > 20:
                    pos = pixel_squares[(i, j)].get_center()
                    mag = gy_val / grad_y_max * 0.8
                    vec = Arrow(
                        start=pos,
                        end=pos + DOWN * mag,
                        color=BLUE,
                        stroke_width=2,
                        buff=0,
                        max_tip_length_to_length_ratio=0.35,
                        max_stroke_width_to_length_ratio=8,
                    )
                    y_vectors_centered.add(vec)

        self.play(
            LaggedStart(
                *[GrowArrow(v) for v in y_vectors_centered],
                lag_ratio=0.01,
            ),
            run_time=1.5,
        )
        self.wait(HOLD)

        self.play(FadeOut(combine_cap, shift=DOWN * 0.1), run_time=0.3)
        combined_cap = caption(
            "Combined gradient vectors ∇I = (∂I/∂x, ∂I/∂y)"
        ).to_edge(DOWN, buff=0.8)
        combined_cap.set_color(GREEN)
        self.play(FadeIn(combined_cap, shift=UP * 0.1), run_time=CAP_RT)

        gradient_vectors = VGroup()
        grad_mag_max = np.sqrt(grad_x_max**2 + grad_y_max**2)
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                gx_val = grad_x[i, j]
                gy_val = grad_y[i, j]
                magnitude_val = np.sqrt(gx_val**2 + gy_val**2)

                if magnitude_val > 30:
                    pos = pixel_squares[(i, j)].get_center()
                    scale = magnitude_val / grad_mag_max * 0.7
                    vec = Arrow(
                        start=pos,
                        end=pos
                        + RIGHT * (gx_val / magnitude_val * scale)
                        + DOWN * (gy_val / magnitude_val * scale),
                        color=GREEN,
                        stroke_width=2,
                        buff=0,
                        max_tip_length_to_length_ratio=0.35,
                        max_stroke_width_to_length_ratio=8,
                    )
                    gradient_vectors.add(vec)

        self.play(
            FadeOut(x_vectors_centered),
            FadeOut(y_vectors_centered),
            *[GrowArrow(v) for v in gradient_vectors],
            run_time=2.0,
        )
        self.wait(HOLD * 2)

        self.play(FadeOut(combined_cap, shift=DOWN * 0.1), run_time=0.3)
        magnitude_cap = caption(
            "Taking magnitude: |∇I| = √((∂I/∂x)² + (∂I/∂y)²)"
        ).to_edge(DOWN, buff=0.8)
        magnitude_cap.set_color(YELLOW)
        self.play(FadeIn(magnitude_cap, shift=UP * 0.1), run_time=CAP_RT)

        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        magnitude_normalized = np.clip(
            magnitude / magnitude.max() * 255, 0, 255
        ).astype(np.uint8)

        self.play(FadeOut(gradient_vectors), run_time=0.8)

        self.play(
            *[
                pixel_squares[(i, j)].animate.set_fill(
                    interpolate_color(
                        BLACK,
                        YELLOW,
                        magnitude_normalized[i, j] / 255.0,
                    ),
                    opacity=1.0,
                )
                for i in range(size)
                for j in range(size)
            ],
            run_time=2.0,
        )
        self.wait(HOLD * 2)

        self.play(FadeOut(magnitude_cap, shift=DOWN * 0.1), run_time=0.3)
        summary = caption(
            "This edge map identifies important features to preserve during seam carving"
        ).to_edge(DOWN, buff=0.5)
        summary.set_color(GREEN)
        self.play(FadeIn(summary, shift=UP * 0.1), run_time=CAP_RT)
        self.wait(HOLD * 3)
