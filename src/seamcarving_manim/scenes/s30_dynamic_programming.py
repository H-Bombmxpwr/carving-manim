from manim import *
from seamcarving_manim.style import H1, caption
import random


class EnergyGridSeamsScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # ===== TIMING PARAMETERS (in seconds) =====
        TITLE_RT = 0.8
        HOLD = 3.2
        GRID_FADEIN_TIME = 2.0
        CAPTION_TIME = 0.8
        GREEDY_STEP_TIME = .75
        GREEDY_WAIT_TIME = 0.15
        BRUTE_FORCE_IN_TIME = 0.02
        BRUTE_FORCE_OUT_TIME = 0.01
        DP_GRID_FADEIN_TIME = 1.5
        DP_BOTTOM_ROW_TIME = 0.2
        DP_SECOND_ROW_WAIT = 1
        DP_SECOND_ROW_FILL_TIME = 1
        DP_SHOW_FORMULA_TIME = 4
        DP_REST_FILL_TIME = 0.1
        DP_PATH_TRACE_TIME = 0.2
        FINAL_HOLD = 6.0
        # ==========================================

        # Helper to manage bottom-of-screen captions so they never overlap
        bottom_caption = None

        def set_bottom_caption(new_cap, rt=CAPTION_TIME):
            nonlocal bottom_caption
            if bottom_caption is None:
                self.play(FadeIn(new_cap, shift=0.1 * UP), run_time=rt)
            else:
                self.play(
                    FadeOut(bottom_caption, shift=0.1 * DOWN),
                    FadeIn(new_cap, shift=0.1 * UP),
                    run_time=rt,
                )
            bottom_caption = new_cap
            return bottom_caption

        # --- Title ---
        title = H1("Energy Grid and Seams").to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=TITLE_RT)

        # --- Energy values (random 0.0–0.9) ---
        n_rows, n_cols = 6, 6
        cell_size = 0.9

        random.seed(42)  # fixed seed for reproducibility
        values = [
            [round(random.uniform(0.0, 0.9), 1) for _ in range(n_cols)]
            for _ in range(n_rows)
        ]

        # Build ORIGINAL energy grid (grayscale)
        grid_group = VGroup()
        cell_squares = {}
        cell_centers = {}

        for i in range(n_rows):
            for j in range(n_cols):
                v = values[i][j]
                fill_color = interpolate_color(BLACK, WHITE, v)

                sq = Square(
                    side_length=cell_size,
                    stroke_color=BLUE_E,
                    stroke_width=2,
                    fill_color=fill_color,
                    fill_opacity=1.0,
                )

                x = (j - (n_cols - 1) / 2) * cell_size
                y = ((n_rows - 1) / 2 - i) * cell_size
                sq.move_to([x, y, 0])

                txt = Text(
                    f"{v:.1f}",
                    font_size=32,
                    color=WHITE if v > 0.35 else GRAY_A,
                )
                txt.move_to(sq.get_center())

                cell_squares[(i, j)] = sq
                cell_centers[(i, j)] = sq.get_center()

                grid_group.add(sq, txt)

        grid_group.shift(LEFT * 3)

        cap_grid = caption(
            "Per-pixel energies e(i, j) (brighter = higher energy)"
        ).next_to(grid_group, DOWN, buff=0.5)

        self.play(
            LaggedStart(
                *[FadeIn(m, shift=0.15 * UP) for m in grid_group],
                lag_ratio=0.03,
            ),
            run_time=GRID_FADEIN_TIME,
        )
        self.play(FadeIn(cap_grid, shift=UP * 0.1), run_time=CAPTION_TIME)
        self.wait(HOLD)

        # Remove title after the gray grid comes in so it won't collide with DP title
        self.play(FadeOut(title), run_time=0.5)
        self.wait(0.3)

        # =====================================================
        # Phase 1: Greedy seam (always choose lowest neighbor)
        # =====================================================
        greedy_cap = caption(
            "Greedy seam: at each row, pick the lowest of the 3 neighbors below"
        ).next_to(cap_grid, DOWN, buff=0.2)
        self.play(FadeIn(greedy_cap, shift=UP * 0.1), run_time=CAPTION_TIME)

        # Greedy path (start at MIDDLE of top row)
        start_j = n_cols // 2  # middle column

        def greedy_path():
            j = start_j
            path = [(0, j)]
            for i in range(1, n_rows):
                candidates = []
                for dj in (-1, 0, 1):
                    jj = j + dj
                    if 0 <= jj < n_cols:
                        candidates.append(jj)
                j = min(candidates, key=lambda c: values[i][c])
                path.append((i, j))
            return path

        g_path = greedy_path()

        # Running sum text to the side of the grid
        running_sum = 0.0
        sum_text = caption(f"Greedy energy = {running_sum:.1f}")
        sum_text.next_to(grid_group, RIGHT, buff=1.0)
        sum_text.align_to(grid_group, UP)
        self.play(FadeIn(sum_text, shift=LEFT * 0.1), run_time=0.5)

        # Animate greedy path step-by-step (semi-transparent purple)
        greedy_highlights = VGroup()
        for (i, j) in g_path:
            sq = cell_squares[(i, j)]
            v = values[i][j]
            running_sum += v

            hl = (
                sq.copy()
                .set_fill(color=PURPLE, opacity=0.35)
                .set_stroke(PURPLE, width=4)
            )
            hl.move_to(sq.get_center())
            greedy_highlights.add(hl)

            new_sum = caption(f"Greedy energy = {running_sum:.1f}")
            new_sum.move_to(sum_text.get_center())

            self.play(
                FadeIn(hl, run_time=GREEDY_STEP_TIME),
                Transform(sum_text, new_sum),
            )
            self.wait(GREEDY_WAIT_TIME)

        self.wait(HOLD * 1.2)

        # --- Greedy Big-O caption ---
        greedy_big_o_cap = caption(
            " O(n_rows × n_cols)"
        ).next_to(sum_text, DOWN, buff=0.2)
        self.play(FadeIn(greedy_big_o_cap, shift=UP * 0.1), run_time=CAPTION_TIME)
        self.wait(HOLD*2.2)

        # =====================================================
        # Phase 2: Tree-style enumeration of all seams
        # =====================================================
        self.play(
            FadeOut(greedy_cap, shift=DOWN * 0.1),
            FadeOut(greedy_highlights),
            FadeOut(greedy_big_o_cap),
            run_time=0.4,
        )

        all_cap = caption(
            "Now explore all seams from same starting pixel"
        ).next_to(cap_grid, DOWN, buff=0.2)
        self.play(FadeIn(all_cap, shift=UP * 0.1), run_time=CAPTION_TIME)

        # Generate all paths with a DFS tree search starting from *same* start as greedy
        def path_cost(path):
            return sum(values[i][j] for (i, j) in path)

        paths = []

        def dfs(i, j, current_path):
            if i == n_rows - 1:
                paths.append(list(current_path))
                return
            for dj in (-1, 0, 1):
                nj = j + dj
                if 0 <= nj < n_cols:
                    current_path.append((i + 1, nj))
                    dfs(i + 1, nj, current_path)
                    current_path.pop()

        dfs(0, start_j, [(0, start_j)])  # fills `paths` with all seams from that start
        total_paths = len(paths)

        # Initialize best seam tracking
        best_cost = float("inf")
        best_path = None

        # Live text showing number of seams and best energy so far
        count_text = caption(
            f"Enumerating seams: 0 / {total_paths}"
        ).next_to(sum_text, DOWN, buff=0.2)
        best_text = caption(
            "Best energy so far = –"
        ).next_to(count_text, DOWN, buff=0.15)
        self.play(
            FadeIn(count_text, shift=UP * 0.1),
            FadeIn(best_text, shift=UP * 0.1),
            run_time=CAPTION_TIME,
        )

        # Helper: seam as stack of semi-transparent boxes
        def make_seam_boxes(path, color):
            g = VGroup()
            for (i, j) in path:
                base_sq = cell_squares[(i, j)]
                box = (
                    base_sq.copy()
                    .set_fill(color=color, opacity=0.35)
                    .set_stroke(color, width=4)
                )
                box.move_to(base_sq.get_center())
                g.add(box)
            return g

        # Fast sweep through all seams in tree (DFS) order
        for idx, path in enumerate(paths):
            seam_cost = path_cost(path)

            # Default seam color: purple; highlight if it's the best so far
            seam_color = PURPLE
            if seam_cost < best_cost:
                best_cost = seam_cost
                best_path = list(path)
                seam_color = YELLOW

            seam = make_seam_boxes(path, color=seam_color)

            new_count = caption(
                f"Enumerating seams: {idx+1} / {total_paths}"
            )
            new_count.move_to(count_text.get_center())

            new_best = caption(f"Best energy so far = {best_cost:.1f}")
            new_best.move_to(best_text.get_center())

            self.play(
                FadeIn(seam),
                Transform(count_text, new_count),
                Transform(best_text, new_best),
                run_time=BRUTE_FORCE_IN_TIME,
            )
            self.play(FadeOut(seam), run_time=BRUTE_FORCE_OUT_TIME)

        self.wait(HOLD)

        # --- Brute-force Big-O caption ---
        brute_big_o_cap = caption(
            "O(3^n)"
        ).next_to(best_text, DOWN, buff=0.2)
        self.play(FadeIn(brute_big_o_cap, shift=UP * 0.1), run_time=CAPTION_TIME)
        self.wait(HOLD)

        # Final: show the true minimum-energy seam as green boxes
        min_cap = caption(
            "Minimum-energy seam (among all explored combinations)"
        ).next_to(all_cap, DOWN, buff=0.2)
        self.play(FadeIn(min_cap, shift=UP * 0.1), run_time=CAPTION_TIME)

        best_seam_mobj = make_seam_boxes(best_path, color=GREEN)
        self.play(FadeIn(best_seam_mobj), run_time=1.0)
        self.wait(HOLD * 2)

        # =====================================================
        # Phase 3: Dynamic Programming - Min Energy to Bottom
        # =====================================================
        self.play(
            FadeOut(min_cap),
            FadeOut(best_seam_mobj),
            FadeOut(all_cap),
            FadeOut(sum_text),
            FadeOut(count_text),
            FadeOut(best_text),
            FadeOut(brute_big_o_cap),
            FadeOut(cap_grid),  # make sure the per-pixel caption is gone now
            run_time=0.6,
        )

        dp_cap = caption(
            "Dynamic Programming: compute 'minimum energy to bottom'"
        ).next_to(grid_group, DOWN, buff=0.4)
        self.play(FadeIn(dp_cap, shift=UP * 0.1), run_time=CAPTION_TIME)

        # Build DP grid on the RIGHT with orange theming
        dp_grid_group = VGroup()
        dp_squares = {}
        dp_texts = {}

        for i in range(n_rows):
            for j in range(n_cols):
                sq = Square(
                    side_length=cell_size,
                    stroke_color=ORANGE,
                    stroke_width=2,
                    fill_color=BLACK,
                    fill_opacity=1.0,
                )

                x = (j - (n_cols - 1) / 2) * cell_size
                y = ((n_rows - 1) / 2 - i) * cell_size
                sq.move_to([x, y, 0])

                dp_squares[(i, j)] = sq
                dp_grid_group.add(sq)

        dp_grid_group.shift(RIGHT * 3)

        dp_label = Text("Min Energy to Bottom", font_size=24, color=ORANGE).next_to(
            dp_grid_group, UP, buff=0.3
        )

        self.play(
            LaggedStart(
                *[FadeIn(sq, shift=0.15 * UP) for sq in dp_grid_group],
                lag_ratio=0.03,
            ),
            FadeIn(dp_label),
            run_time=DP_GRID_FADEIN_TIME,
        )
        self.wait(HOLD)

        # Compute DP values: dp[i][j] = min energy from (i,j) to bottom
        dp = [[0.0 for _ in range(n_cols)] for _ in range(n_rows)]

        # Bottom row: just the energy itself
        for j in range(n_cols):
            dp[n_rows - 1][j] = values[n_rows - 1][j]

        # Fill from bottom to top
        for i in range(n_rows - 2, -1, -1):
            for j in range(n_cols):
                # Min of three neighbors below
                min_below = float("inf")
                for dj in (-1, 0, 1):
                    jj = j + dj
                    if 0 <= jj < n_cols:
                        min_below = min(min_below, dp[i + 1][jj])
                dp[i][j] = values[i][j] + min_below

        # Animate filling DP grid - BOTTOM ROW FIRST
        fill_cap = caption("Bottom row: min energy = current energy").to_edge(
            DOWN, buff=0.5
        )
        self.play(FadeOut(dp_cap))
        set_bottom_caption(fill_cap)

        # Find max DP value for gradient normalization (for orange gradient)
        max_dp = max(max(row) for row in dp)

        # --- Bottom row with orange gradient ---
        for j in range(n_cols):
            val = dp[n_rows - 1][j]
            txt = Text(f"{val:.1f}", font_size=28, color=YELLOW)
            txt.move_to(dp_squares[(n_rows - 1, j)].get_center())
            dp_texts[(n_rows - 1, j)] = txt

            gradient_val = val / max_dp
            fill_color = interpolate_color(BLACK, ORANGE, gradient_val)

            self.play(
                dp_squares[(n_rows - 1, j)].animate.set_fill(fill_color, opacity=1.0),
                FadeIn(txt),
                run_time=DP_BOTTOM_ROW_TIME,
            )

        # Pause after filling bottom row
        self.wait(DP_SECOND_ROW_WAIT)

        # --- Second-to-last row: detailed equations for two cells + gradient ---
        formula_cap = caption(
            "Each cell: dp[i][j] = e[i][j] + min(neighbors below)"
        ).to_edge(DOWN, buff=0.5)
        set_bottom_caption(formula_cap)

        row_i = n_rows - 2

        def animate_dp_cell(i, j, wait_after=True, bg_color=GRAY_E):
            """Show detailed equation for dp[i][j] using both grids, with background."""

            val = dp[i][j]

            # Highlight corresponding ORIGINAL cell on the left
            current_highlight = (
                cell_squares[(i, j)].copy().set_stroke(YELLOW, width=5)
            )
            self.play(Create(current_highlight), run_time=0.3)

            # Connections to neighbors below in DP grid
            connections = VGroup()
            neighbor_vals = []
            for dj in (-1, 0, 1):
                jj = j + dj
                if 0 <= jj < n_cols:
                    line = Line(
                        dp_squares[(i, j)].get_center(),
                        dp_squares[(i + 1, jj)].get_center(),
                        color=YELLOW,
                        stroke_width=3,
                    )
                    connections.add(line)
                    neighbor_vals.append(dp[i + 1][jj])

            self.play(Create(connections), run_time=0.4)

            # Equation: e[i,j] (from left grid) + min(dp neighbors below) (from right grid)
            current_energy = values[i][j]
            min_neighbor = min(neighbor_vals)

            eq_start_pos = cell_squares[(i, j)].get_center()
            energy_text = Text(
                f"{current_energy:.1f}", font_size=24, color=WHITE
            ).move_to(eq_start_pos)

            # Lay out locally around the energy_text
            plus_sign = Text("+", font_size=24, color=YELLOW).next_to(
                energy_text, RIGHT, buff=0.1
            )
            min_text = Text(
                f"{min_neighbor:.1f}", font_size=24, color=YELLOW
            ).next_to(plus_sign, RIGHT, buff=0.1)
            equals_sign = Text("=", font_size=24, color=GREEN).next_to(
                min_text, RIGHT, buff=0.1
            )
            result_text = Text(f"{val:.1f}", font_size=24, color=GREEN).next_to(
                equals_sign, RIGHT, buff=0.1
            )

            equation_group = VGroup(
                energy_text, plus_sign, min_text, equals_sign, result_text
            )
            # Center the equation group at the original cell
            equation_group.move_to(eq_start_pos)

            # Background rectangle behind the equation (for readability)
            bg_rect = RoundedRectangle(
                corner_radius=0.15,
                width=equation_group.width + 0.3,
                height=equation_group.height + 0.25,
                stroke_width=1,
                stroke_color=GRAY_D,
                fill_color=bg_color,
                fill_opacity=0.9,
            )
            bg_rect.move_to(eq_start_pos)

            full_group = VGroup(bg_rect, equation_group)

            self.play(FadeIn(full_group, scale=1.1), run_time=0.4)
            if wait_after:
                self.wait(0.6)

            # Animate equation group flying over to the DP grid cell (visual link between grids)
            target_pos = dp_squares[(i, j)].get_center()
            self.play(
                full_group.animate.move_to(target_pos).scale(0.5),
                run_time=2,
            )

            # Replace with final DP text and orange gradient fill
            txt = Text(f"{val:.1f}", font_size=28, color=YELLOW)
            txt.move_to(dp_squares[(i, j)].get_center())
            dp_texts[(i, j)] = txt

            gradient_val = val / max_dp
            fill_color = interpolate_color(BLACK, ORANGE, gradient_val)

            self.play(
                FadeOut(full_group),
                FadeIn(txt),
                dp_squares[(i, j)].animate.set_fill(fill_color, opacity=1.0),
                FadeOut(connections),
                FadeOut(current_highlight),
                run_time=0.6,
            )

            if wait_after:
                self.wait(0.2)

        # Detailed example for j = 0 and j = 1
        animate_dp_cell(row_i, 0, wait_after=True)
        animate_dp_cell(row_i, 1, wait_after=True)

        # Pause after doing the detailed cells
        self.wait(DP_SHOW_FORMULA_TIME)

        # Fill the rest of the second-to-last row quickly, with the same orange gradient logic
        for j in range(2, n_cols):
            val = dp[row_i][j]
            txt = Text(f"{val:.1f}", font_size=28, color=YELLOW)
            txt.move_to(dp_squares[(row_i, j)].get_center())
            dp_texts[(row_i, j)] = txt

            gradient_val = val / max_dp
            fill_color = interpolate_color(BLACK, ORANGE, gradient_val)

            self.play(
                dp_squares[(row_i, j)].animate.set_fill(fill_color, opacity=1.0),
                FadeIn(txt),
                run_time=DP_SECOND_ROW_FILL_TIME,
            )

        # Fill the remaining rows faster (still with orange gradient)
        fast_fill_cap = caption("Filling remaining rows...").to_edge(DOWN, buff=0.5)
        set_bottom_caption(fast_fill_cap)

        for i in range(n_rows - 3, -1, -1):
            for j in range(n_cols):
                val = dp[i][j]
                txt = Text(f"{val:.1f}", font_size=28, color=YELLOW)
                txt.move_to(dp_squares[(i, j)].get_center())
                dp_texts[(i, j)] = txt

                gradient_val = val / max_dp
                fill_color = interpolate_color(BLACK, ORANGE, gradient_val)

                self.play(
                    dp_squares[(i, j)].animate.set_fill(fill_color, opacity=1.0),
                    FadeIn(txt),
                    run_time=DP_REST_FILL_TIME,
                )

        self.wait(HOLD)

        # --- DP Big-O caption ---
        dp_big_o_cap = caption(
            "DP time: O(n_rows × n_cols)"
        ).to_edge(DOWN, buff=0.5)
        set_bottom_caption(dp_big_o_cap)
        self.wait(HOLD)

        # =====================================================
        # Phase 4: Trace optimal path using DP (same start as greedy)
        # =====================================================

        trace_cap = caption(
            "Trace optimal path: start at same position as greedy, follow minimum neighbors downward"
        ).to_edge(DOWN, buff=0.5)
        set_bottom_caption(trace_cap)

        # Start from SAME position as greedy (middle column)
        dp_path = [(0, start_j)]
        j = start_j
        for i in range(1, n_rows):
            candidates = []
            for dj in (-1, 0, 1):
                jj = j + dj
                if 0 <= jj < n_cols:
                    candidates.append(jj)
            j = min(candidates, key=lambda c: dp[i][c])
            dp_path.append((i, j))

        # Highlight path on DP grid (green)
        dp_path_highlights = VGroup()
        for (i, j) in dp_path:
            sq = dp_squares[(i, j)]
            hl = (
                sq.copy()
                .set_fill(color=GREEN, opacity=0.4)
                .set_stroke(GREEN, width=4)
            )
            hl.move_to(sq.get_center())
            dp_path_highlights.add(hl)

            self.play(FadeIn(hl), run_time=DP_PATH_TRACE_TIME)

        self.wait(HOLD)

        # Final comparison caption
        final_cap = caption(
            f"DP optimal path energy = {dp[0][start_j]:.1f} (matches brute force!)"
        ).to_edge(DOWN, buff=0.5)
        set_bottom_caption(final_cap)

        # Highlight same path on original grid (green)
        original_path_highlights = VGroup()
        for (i, j) in dp_path:
            sq = cell_squares[(i, j)]
            hl = (
                sq.copy()
                .set_fill(color=GREEN, opacity=0.4)
                .set_stroke(GREEN, width=4)
            )
            hl.move_to(sq.get_center())
            original_path_highlights.add(hl)

        self.play(FadeIn(original_path_highlights), run_time=1.0)
        self.wait(FINAL_HOLD)
