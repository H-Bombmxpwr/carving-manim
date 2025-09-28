from manim import *

ACCENT = YELLOW  # shared accent color

def H1(txt: str):
    return Text(txt, weight=BOLD).scale(0.9)

def H2(txt: str):
    return Text(txt).scale(0.6)

def caption(txt: str):
    t = Text(txt).scale(0.45)
    t.set_opacity(0.8)
    return t