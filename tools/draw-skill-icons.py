"""Draws the profile's Skills icons as hand-drawn line sketches and writes them into index.html.

Each icon is a few simple strokes in a 24x24 box, traced twice with a small wobble, the way a pen
goes over a line it didn't quite land the first time. Run from the repo root after changing one:
  python3 tools/draw-skill-icons.py
"""
import math, pathlib, random, re

PAGE = pathlib.Path(__file__).resolve().parent.parent / "index.html"


def arc(cx, cy, r, a0, a1, n=14):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def circle(cx, cy, r):
    return arc(cx, cy, r, -80, 290, 18)  # overshoots a little, as a hand-drawn circle does


def rect(x, y, w, h):
    return [(x + 0.4, y), (x + w, y + 0.2), (x + w - 0.2, y + h), (x, y + h - 0.2), (x + 0.2, y - 0.4)]


# Each icon: a list of strokes, each stroke a list of points
ICONS = {
    "code": [[(8.5, 7), (3.5, 12), (8.5, 17)], [(15.5, 7), (20.5, 12), (15.5, 17)], [(13.6, 4.8), (10.4, 19.2)]],
    "network": [circle(12, 12, 2.6), circle(5, 6, 1.8), circle(19, 6, 1.8), circle(5, 18.5, 1.8), circle(19, 18.5, 1.8),
                [(6.5, 7.2), (10, 10.4)], [(17.5, 7.2), (14, 10.4)], [(6.5, 17.2), (10, 13.8)], [(17.5, 17.2), (14, 13.8)]],
    "methods": [[(4, 6.5), (12.5, 6.5), (16, 9.5), (20, 9.5)], [(4, 17.5), (12.5, 17.5), (16, 14.5), (20, 14.5)],
                [(17.8, 7.6), (20, 9.5), (17.8, 11.4)], [(17.8, 12.6), (20, 14.5), (17.8, 16.4)]],
    "apps": [rect(4, 4.5, 16, 15), [(4.2, 9), (19.8, 9)], circle(6.8, 6.8, 0.5), circle(9, 6.8, 0.5), [(8, 13.5), (16, 13.5)], [(8, 16), (13, 16)]],
    "robot": [rect(5.5, 8, 13, 10), [(12, 8), (12, 4.6)], circle(12, 4, 0.9), circle(9.4, 12.2, 1.1), circle(14.6, 12.2, 1.1),
              [(9.5, 15.4), (12, 16), (14.5, 15.4)], [(3.6, 11.5), (3.6, 14.5)], [(20.4, 11.5), (20.4, 14.5)]],
    "skills": [[(15.2, 3.6), (12.4, 4.6), (11, 7.4), (11.6, 10)], [(11.6, 10), (4.4, 17.2), (4.4, 19.6), (6.8, 19.6), (14, 12.4)],
               [(14, 12.4), (16.6, 13), (19.4, 11.6), (20.4, 8.8)], [(20.4, 8.8), (17.8, 11), (15.4, 10.6), (13.4, 8.6), (13, 6.2), (15.2, 3.6)]],
}


def smooth(points):
    """A path through the points, Catmull-Rom style, so corners stay soft like a pen's."""
    if len(points) < 3:
        (x0, y0), (x1, y1) = points
        return f"M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}"
    d = f"M{points[0][0]:.2f} {points[0][1]:.2f}"
    for i in range(len(points) - 1):
        p0, p1, p2 = points[max(i - 1, 0)], points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}"
    return d


def wobble(points, rng, amount):
    out = []
    for x, y in points:
        out.append((x + rng.uniform(-amount, amount), y + rng.uniform(-amount, amount)))
    # a straight stroke gets a midpoint too, so it can bow a little
    if len(out) == 2:
        (x0, y0), (x1, y1) = out
        out.insert(1, ((x0 + x1) / 2 + rng.uniform(-0.35, 0.35), (y0 + y1) / 2 + rng.uniform(-0.35, 0.35)))
    return out


def svg(name):
    rng = random.Random(name)
    first = "".join(smooth(wobble(s, rng, 0.25)) for s in ICONS[name])
    second = "".join(smooth(wobble(s, rng, 0.4)) for s in ICONS[name])
    return (f'<svg class="skill-icon" viewBox="0 0 24 24" aria-hidden="true">'
            f'<path d="{first}"/><path class="again" d="{second}"/></svg>')


if __name__ == "__main__":
    page = PAGE.read_text(encoding="utf-8")
    for name in ICONS:
        page, n = re.subn(rf'(<div class="skill-row skill-{name}">\s*<h3>)(?:<svg class="skill-icon".*?</svg>)?',
                          lambda m: m.group(1) + svg(name), page, flags=re.S)
        if n != 1:
            raise SystemExit(f"draw-skill-icons.py: no Skills card for {name}")
    PAGE.write_text(page, encoding="utf-8")
    print("updated the Skills icons in index.html")
