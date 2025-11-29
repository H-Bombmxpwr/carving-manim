from manim import *
from seamcarving_manim.style import H1, caption


class ManimIntroShowcase(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#050509"
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)

        # ===== TIMING CONSTANTS =====
        TITLE_IN_RT        = 0.8
        TITLE_HOLD         = 1.8
        GRID_FADEIN_RT     = 1.5
        PANEL_INTRO_RT     = 1.0
        GRID_WARP_RT       = 3.0
        FINAL_HOLD         = 2.5
        # ============================

        # ---------- Title + one-line subtitle (top) ----------
        title = H1("What is Manim?").to_edge(UP, buff=0.5)
        subtitle = Text(
            "Open-source Python library for math and science animations.",
            font_size=30,
            color=GREY_B,
        ).next_to(title, DOWN, buff=0.25)

        extra_caption = Text(
            "Manim = Mathematical Animation Engine",
            font_size=24,
            color=GREY_A,
        ).next_to(subtitle, DOWN, buff=0.25)

        # Optional 3Blue1Brown logo (if available)
        has_logo = False
        try:
            logo = SVGMobject("3b1b_logo.svg")
            logo.set_height(0.8)
            logo.next_to(extra_caption, RIGHT, buff=0.4)
            has_logo = True
        except Exception:
            logo = VGroup()

        self.play(Write(title), run_time=TITLE_IN_RT)
        self.play(FadeIn(subtitle, shift=0.1 * UP), run_time=TITLE_IN_RT)
        self.play(FadeIn(extra_caption, shift=0.1 * UP), run_time=0.7)
        if has_logo:
            self.play(FadeIn(logo, shift=0.1 * UP), run_time=0.6)
        self.wait(TITLE_HOLD)

        # Fade out all title-related elements before 2×2 grid
        to_fade = VGroup(title, subtitle, extra_caption, logo)
        self.play(FadeOut(to_fade), run_time=0.6)

        # ---------- Layout for 2×2 grid ----------
        top_left     = UP * 1.8 + LEFT * 4.0
        top_right    = UP * 1.8 + RIGHT * 4.0
        bottom_left  = DOWN * 1.8 + LEFT * 4.0
        bottom_right = DOWN * 1.8 + RIGHT * 4.0

        panel_frames = VGroup(
            RoundedRectangle(width=5.0, height=3.0, corner_radius=0.2).move_to(top_left),
            RoundedRectangle(width=5.0, height=3.0, corner_radius=0.2).move_to(top_right),
            RoundedRectangle(width=5.0, height=3.0, corner_radius=0.2).move_to(bottom_left),
            RoundedRectangle(width=5.0, height=3.0, corner_radius=0.2).move_to(bottom_right),
        )
        panel_frames.set_stroke(color=GRAY_D, width=1.5)
        panel_frames.set_fill(color=BLACK, opacity=0.15)

        self.play(
            LaggedStart(*[FadeIn(f, shift=0.1 * UP) for f in panel_frames], lag_ratio=0.1),
            run_time=GRID_FADEIN_RT,
        )

        # ============================================================
        # Top-Left: simple shape morph loop (triangle → circle → square)
        # ============================================================
        panel0_center = panel_frames[0].get_center()

        # Base size such that everything stays nicely inside 5×3 panel
        base_size = 1.2

        triangle = RegularPolygon(
            n=3,
            radius=base_size,
        ).set_fill(BLUE_C, opacity=0.6).set_stroke(BLUE_E, width=2)

        circle = Circle(
            radius=base_size,
        ).set_fill(GREEN_C, opacity=0.6).set_stroke(GREEN_E, width=2)

        square = Square(
            side_length=2 * base_size * 0.9,  # slightly smaller so corners stay clear of frame
        ).set_fill(RED_C, opacity=0.6).set_stroke(RED_E, width=2)

        for shape in (triangle, circle, square):
            shape.move_to(ORIGIN)

        # Single animated mobject we keep transforming
        shape_mob = triangle.copy()
        shape_mob.move_to(panel0_center)

        # Extra scale so we’re guaranteed not to touch the frame
        shape_mob.scale(0.8, about_point=panel0_center)
        triangle.move_to(panel0_center).scale(0.8, about_point=panel0_center)
        circle.move_to(panel0_center).scale(0.8, about_point=panel0_center)
        square.move_to(panel0_center).scale(0.8, about_point=panel0_center)

        self.play(FadeIn(shape_mob, shift=0.1 * UP), run_time=PANEL_INTRO_RT)

        # Loop through triangle → circle → square a couple of times
        morph_sequence = [circle, square, triangle]
        for _ in range(2):
            for target in morph_sequence:
                self.play(
                    Transform(shape_mob, target),
                    run_time=0.8,
                )

        # ============================================================
        # Top-Right: Grid + line segment with NON-LINEAR TRANSFORM
        # ============================================================
        grid_panel_center = panel_frames[1].get_center()

        grid = NumberPlane(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            background_line_style={"stroke_width": 1, "stroke_opacity": 0.6},
        )
        grid.scale(0.5)
        grid.move_to(grid_panel_center)

        line = Line(
            grid_panel_center + LEFT * 0.9 + DOWN * 0.4,
            grid_panel_center + RIGHT * 0.9 + UP * 0.4,
            stroke_width=3,
            color=YELLOW,
        )

        grid_group = VGroup(grid, line)

        self.play(FadeIn(grid_group, shift=0.1 * UP), run_time=PANEL_INTRO_RT)

        grid.prepare_for_nonlinear_transform()

        self.play(
            grid.animate.apply_function(
                lambda p: p + np.array(
                    [
                        0.25 * np.sin(p[1]),
                        0.25 * np.sin(p[0]),
                        0,
                    ]
                )
            ),
            line.animate.apply_function(
                lambda p: p + np.array(
                    [
                        0.25 * np.sin(p[1]),
                        0.25 * np.sin(p[0]),
                        0,
                    ]
                )
            ),
            run_time=GRID_WARP_RT,
        )

        # ============================================================
        # Bottom-Left: “Product rule” style highlight
        # ============================================================
        formula = VGroup(
            Text("d/dx [ f(x) g(x) ]  =", font_size=24),
            Text("f(x) · g'(x)", font_size=24),
            Text("+", font_size=22),
            Text("g(x) · f'(x)", font_size=24),
        )
        formula.arrange(RIGHT, buff=0.18)
        formula.scale(0.7)
        formula.move_to(panel_frames[2].get_center())

        framebox1 = SurroundingRectangle(formula[1], buff=0.08)
        framebox2 = SurroundingRectangle(formula[3], buff=0.08)

        self.play(FadeIn(formula, shift=0.1 * UP), run_time=PANEL_INTRO_RT)
        self.play(Create(framebox1), run_time=0.5)
        self.play(ReplacementTransform(framebox1, framebox2), run_time=0.8)

        # ============================================================
        # Bottom-Right: 3D pulsating + rotating sphere
        # ============================================================
        self.renderer.camera.light_source.move_to(3 * IN)

        sphere_axes = ThreeDAxes(
            x_range=[-2, 2, 1],
            y_range=[-2, 2, 1],
            z_range=[-2, 2, 1],
        )
        sphere_axes.scale(0.4)

        base_radius = 1.0

        def make_sphere(r=base_radius):
            return Surface(
                lambda u, v: np.array([
                    r * np.cos(u) * np.cos(v),
                    r * np.cos(u) * np.sin(v),
                    r * np.sin(u),
                ]),
                v_range=[0, TAU],
                u_range=[-PI / 2, PI / 2],
                checkerboard_colors=[RED_D, RED_E],
                resolution=(15, 32),
            )

        sphere = make_sphere(base_radius)

        sphere_group = VGroup(sphere_axes, sphere)
        sphere_group.scale(0.7)
        sphere_group.move_to(panel_frames[3].get_center())

        self.play(FadeIn(sphere_group, shift=0.1 * UP), run_time=PANEL_INTRO_RT)

        t_sphere = ValueTracker(0.0)
        base_sphere_group = sphere_group.copy()

        def update_sphere_group(m, dt):
            t_sphere.increment_value(dt)
            t = t_sphere.get_value()

            scale_factor = 0.8 + 0.2 * np.sin(t)
            new_group = base_sphere_group.copy()
            new_group.scale(scale_factor, about_point=base_sphere_group.get_center())
            new_group.rotate(0.6 * t, axis=RIGHT)
            new_group.rotate(0.4 * t, axis=OUT)

            m.become(new_group)

        sphere_group.add_updater(update_sphere_group)

        # Let everything run together for a while
        self.wait(FINAL_HOLD * 2)

        outro_cap = Text(
            "All of this is scripted — every pixel comes from code.",
            font_size=28,
            color=GREY_B,
        ).to_edge(UP, buff=0.6)

        self.play(FadeIn(outro_cap, shift=0.1 * UP), run_time=0.7)
        self.wait(FINAL_HOLD)

        self.play(
            FadeOut(
                VGroup(
                    shape_mob,
                    grid_group,
                    formula,
                    framebox2,
                    sphere_group,
                    panel_frames,
                    outro_cap,
                )
            ),
            run_time=1.2,
        )
        self.wait(0.3)
