from manim import *
from seamcarving_manim.style import H1, caption
import random


class EnergyGridSeamsScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        TITLE_RT = 0.8
        HOLD     = 1.2

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

        # Build grid
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
            run_time=2.0,
        )
        self.play(FadeIn(cap_grid, shift=UP * 0.1), run_time=0.6)
        self.wait(HOLD)

        # =====================================================
        # Phase 1: Greedy seam (always choose lowest neighbor)
        # =====================================================
        greedy_cap = caption(
            "Greedy seam: at each row, pick the lowest of the 3 neighbors below"
        ).next_to(cap_grid, DOWN, buff=0.2)
        self.play(FadeIn(greedy_cap, shift=UP * 0.1), run_time=0.6)

        # Greedy path (start at MIDDLE of top row)
        def greedy_path():
            j = n_cols // 2  # middle column
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
                FadeIn(hl, run_time=0.25),
                Transform(sum_text, new_sum),
            )
            self.wait(0.15)

        self.wait(HOLD * 1.2)

        # =====================================================
        # Phase 2: Tree-style enumeration of all seams
        # =====================================================
        self.play(
            FadeOut(greedy_cap, shift=DOWN * 0.1),
            FadeOut(greedy_highlights),
            run_time=0.4,
        )

        all_cap = caption(
            "Now explore all seams from that same starting pixel (tree of choices)"
        ).next_to(cap_grid, DOWN, buff=0.2)
        self.play(FadeIn(all_cap, shift=UP * 0.1), run_time=0.6)

        # --- Generate all paths with a DFS tree search starting from *same* start as greedy ---
        start_j = g_path[0][1]  # middle column (same as greedy)

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
            run_time=0.6,
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
        IN_TIME  = 0.02
        OUT_TIME = 0.01

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
                run_time=IN_TIME,
            )
            self.play(FadeOut(seam), run_time=OUT_TIME)

        self.wait(HOLD)

        # Final: show the true minimum-energy seam as green boxes
        min_cap = caption(
            "Minimum-energy seam (among all explored combinations)"
        ).next_to(all_cap, DOWN, buff=0.2)
        self.play(FadeIn(min_cap, shift=UP * 0.1), run_time=0.6)

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
            run_time=0.6
        )

        dp_cap = caption(
            "Dynamic Programming: compute 'minimum energy to bottom' for each cell"
        ).next_to(cap_grid, DOWN, buff=0.2)
        self.play(FadeIn(dp_cap, shift=UP * 0.1), run_time=0.6)

        # Build DP grid on the RIGHT
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
                    fill_opacity=0.8,
                )

                x = (j - (n_cols - 1) / 2) * cell_size
                y = ((n_rows - 1) / 2 - i) * cell_size
                sq.move_to([x, y, 0])

                dp_squares[(i, j)] = sq
                dp_grid_group.add(sq)

        dp_grid_group.shift(RIGHT * 3)

        dp_label = Text("Min Energy to Bottom", font_size=24, color=ORANGE).next_to(dp_grid_group, UP, buff=0.3)

        self.play(
            LaggedStart(
                *[FadeIn(sq, shift=0.15 * UP) for sq in dp_grid_group],
                lag_ratio=0.03,
            ),
            FadeIn(dp_label),
            run_time=1.5,
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
                min_below = float('inf')
                for dj in (-1, 0, 1):
                    jj = j + dj
                    if 0 <= jj < n_cols:
                        min_below = min(min_below, dp[i + 1][jj])
                dp[i][j] = values[i][j] + min_below

        # Animate filling DP grid from bottom to top
        fill_cap = caption("Filling bottom-up: dp[i][j] = e[i][j] + min(dp[i+1][j-1:j+1])").to_edge(DOWN, buff=0.5)
        self.play(FadeIn(fill_cap, shift=UP * 0.1), run_time=0.6)

        for i in range(n_rows - 1, -1, -1):
            for j in range(n_cols):
                val = dp[i][j]
                txt = Text(f"{val:.1f}", font_size=28, color=YELLOW)
                txt.move_to(dp_squares[(i, j)].get_center())
                dp_texts[(i, j)] = txt

                self.play(FadeIn(txt), run_time=0.15)

        self.wait(HOLD)

        # =====================================================
        # Phase 4: Trace optimal path using DP
        # =====================================================
        self.play(FadeOut(fill_cap), FadeOut(dp_cap), run_time=0.4)

        trace_cap = caption(
            "Trace optimal path: start at minimum in top row, follow minimum neighbors downward"
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(trace_cap, shift=UP * 0.1), run_time=0.6)

        # Find starting column (minimum dp value in top row)
        start_col = min(range(n_cols), key=lambda j: dp[0][j])

        # Trace path
        dp_path = [(0, start_col)]
        j = start_col
        for i in range(1, n_rows):
            candidates = []
            for dj in (-1, 0, 1):
                jj = j + dj
                if 0 <= jj < n_cols:
                    candidates.append(jj)
            j = min(candidates, key=lambda c: dp[i][c])
            dp_path.append((i, j))

        # Highlight path on DP grid
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

            self.play(FadeIn(hl), run_time=0.2)

        self.wait(HOLD)

        # Show that this matches the brute force optimal path
        final_cap = caption(
            f"DP optimal path energy = {dp[0][start_col]:.1f} (matches brute force!)"
        ).to_edge(DOWN, buff=0.5)
        self.play(
            FadeOut(trace_cap),
            FadeIn(final_cap, shift=UP * 0.1),
            run_time=0.6
        )

        # Highlight same path on original grid
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
        self.wait(HOLD * 3)