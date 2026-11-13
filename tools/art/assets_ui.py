"""UI icons, panels and particles."""
import palette as P
from svgkit import Canvas, mix, star


def coin() -> Canvas:
    c = Canvas(56, 56, 28, 28)
    c.circle(0, 2, 22, P.gold_dark)
    c.circle(0, 0, 22, c.radial([(0, "#FFF1B0"), (0.6, P.gold), (1, P.gold_dark)], -8, -10, 30))
    c.circle(0, 0, 15.5, "none", stroke=P.gold_dark, sw=2.2)
    # embossed sprout
    c.path("M0,9 L0,-2", "none", stroke=P.gold_dark, sw=3)
    c.path("M0,-1 Q-10,-3 -9,-11 Q-1,-10 0,-1 Z", P.gold_dark, stroke=None)
    c.path("M0,-3 Q8,-6 9,-13 Q1,-13 0,-3 Z", P.gold_dark, stroke=None)
    c.ellipse(-9, -12, 5, 3, "#FFFFFF", stroke=None, opacity=0.6, rot=-35)
    return c


def emerald() -> Canvas:
    c = Canvas(56, 56, 28, 28)
    outer = [(-12, -18), (12, -18), (22, -6), (0, 22), (-22, -6)]
    c.poly(outer, P.emerald_dark)
    c.poly([(-12, -18), (12, -18), (7, -6), (-7, -6)], P.emerald_light, stroke=None)
    c.poly([(-22, -6), (-12, -18), (-7, -6)], P.emerald, stroke=None)
    c.poly([(22, -6), (12, -18), (7, -6)], mix(P.emerald, P.emerald_dark, 0.4), stroke=None)
    c.poly([(-22, -6), (-7, -6), (0, 22)], P.emerald, stroke=None)
    c.poly([(-7, -6), (7, -6), (0, 22)], mix(P.emerald, P.emerald_light, 0.4), stroke=None)
    c.poly([(7, -6), (22, -6), (0, 22)], P.emerald_dark, stroke=None)
    c.poly(outer, "none")
    c.polyline([(-22, -6), (22, -6)], stroke=P.outline, sw=1.2, opacity=0.5)
    c.poly(star(-9, -12, 4.5, 1.6, 4, 0), "#FFFFFF", stroke=None, opacity=0.9)
    return c


def panel() -> Canvas:
    """9-slice panel: cream inside, wooden frame. Margins = 20 px."""
    c = Canvas(72, 72, 0, 0)
    c.rect(2, 4, 68, 66, 18, P.wood_dark)
    c.rect(2, 2, 68, 64, 18, P.wood)
    c.rect(8, 8, 56, 52, 13, c.linear([(0, P.cream), (1, P.cream_dark)], 0, 8, 0, 60), stroke=P.wood_dark, sw=2)
    return c


def button(col: str, dark: str, name_light: str) -> Canvas:
    c = Canvas(72, 72, 0, 0)
    c.rect(3, 8, 66, 60, 18, dark)
    c.rect(3, 3, 66, 58, 18, c.linear([(0, name_light), (1, col)], 0, 3, 0, 61))
    c.rect(12, 9, 30, 8, 4, "#FFFFFF", stroke=None, opacity=0.35)
    return c


def sparkle() -> Canvas:
    c = Canvas(28, 28, 14, 14)
    c.poly(star(0, 0, 11, 3.4, 4, -90), "#FFFFFF", stroke=None)
    return c


def leaf_particle() -> Canvas:
    c = Canvas(20, 20, 10, 10)
    c.path("M-6,4 Q-6,-6 6,-6 Q6,6 -6,4 Z", P.leaf_light, sw=1.6)
    return c


def grain_particle() -> Canvas:
    c = Canvas(16, 20, 8, 10)
    c.ellipse(0, 0, 3, 6, P.wheat, sw=1.6)
    return c
