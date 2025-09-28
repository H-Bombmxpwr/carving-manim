from manim import *

# palette & common text style
ACCENT = YELLOW
HEATMAP_LOW, HEATMAP_HIGH = BLUE_E, RED_E

def H1(txt): return Text(txt, weight=BOLD).scale(0.9)
def H2(txt): return Text(txt).scale(0.6)
def caption(txt): return Text(txt).scale(0.45).set_opacity(0.8)
