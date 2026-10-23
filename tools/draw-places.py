"""Draws the Travel page's illustrations (Places I'm going, Places I'd like to go) as 1200x800 SVGs in images/places/.

Each is an original drawing of one iconic spot, not a photograph. Run from the
repo root after changing a drawing:
  python3 tools/draw-places.py
"""
import math, os, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "images/places"
W, H = 1200, 800
INK = "#1c1b19"


def grad(gid, top, bottom, x2=0, y2=1):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')


def svg(name, body, sky, defs=""):
    top, bottom = sky
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{grad(name + "-sky", top, bottom)}{defs}</defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{name}-sky)"/>{body}</svg>')


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def poly(points, fill, **kw):
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<polygon points="{pts(points)}" fill="{fill}"{extra}/>'


def ridge(x0, x1, base, rng, peaks, height, jag=0.0, step=20):
    """A mountain silhouette: smooth bumps plus optional jagged noise, closed at `base`."""
    out = [(x0, base)]
    phases = [rng.uniform(0, 6.28) for _ in peaks]
    x = x0
    while x <= x1:
        t = (x - x0) / (x1 - x0)
        y = 0.0
        for (c, w, a), ph in zip(peaks, phases):
            y = max(y, a * math.exp(-((t - c) / w) ** 2))
        y = height * y + jag * rng.uniform(-1, 1)
        out.append((x, base - y))
        x += step
    out.append((x1, base))
    return out


def clouds(rng, n, y0, y1, colour="#ffffff", opacity=0.55, x0=0, x1=W):
    out = []
    for _ in range(n):
        cx, cy, w = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(120, 260)
        for k in range(5):
            out.append(f'<ellipse cx="{cx + (k - 2) * w * 0.22 + rng.uniform(-10, 10):.0f}" cy="{cy - rng.uniform(0, 18):.0f}" '
                       f'rx="{w * rng.uniform(0.2, 0.32):.0f}" ry="{w * rng.uniform(0.07, 0.12):.0f}" fill="{colour}" opacity="{opacity}"/>')
    return "".join(out)


_glows = [0]


def glow(cx, cy, rx, ry, colour, opacity):
    """A soft light that fades to nothing at its edge (no visible rim)."""
    _glows[0] += 1
    gid = f"glow{_glows[0]}"
    return (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{colour}" stop-opacity="{opacity}"/>'
            f'<stop offset="1" stop-color="{colour}" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{gid})"/>')


# ---------------------------------------------------------------- Hokkaido: Mount Yotei over snowfields
def hokkaido():
    rng = random.Random(1)
    b = []
    # Mount Yotei: a near-perfect cone with a flat crater top.
    b.append(glow(600, 560, 760, 190, "#f6dccd", 0.7))
    b.append(clouds(rng, 4, 90, 200, opacity=0.6))
    cone = [(170, 560), (520, 250), (600, 238), (680, 250), (1030, 560)]
    b.append(poly(cone, "#7f97b2"))
    snow = [(330, 420), (520, 250), (600, 238), (680, 250), (870, 420)]
    edge = [(870, 420)]
    for i in range(1, 16):
        x = 870 - i * 36
        edge.append((x, 420 - 40 * math.sin(i * 1.7) ** 2 - rng.uniform(0, 30)))
    b.append(poly(snow + edge[1:], "#f7f9fb"))
    b.append(poly([(600, 238), (680, 250), (1030, 560), (640, 560)], "#24364d", opacity="0.16"))
    # Rolling snowfields.
    b.append(f'<path d="M0,600 C200,560 380,600 600,580 S1000,550 1200,590 L1200,800 L0,800 Z" fill="#eef2f6"/>')
    b.append(f'<path d="M0,680 C250,640 520,700 760,660 S1080,640 1200,670 L1200,800 L0,800 Z" fill="#fbfcfd"/>')
    b.append(f'<path d="M0,690 C250,650 520,710 760,670" fill="none" stroke="#dbe4ee" stroke-width="4"/>')
    # A line of conifers on the middle ridge, and a lone tree in front.
    for i in range(26):
        x = 40 + i * 44 + rng.uniform(-8, 8)
        y = 585 - 12 * math.sin(x / 180)
        h = rng.uniform(26, 44)
        b.append(poly([(x - h * 0.28, y), (x, y - h), (x + h * 0.28, y)], "#2f4a3c"))
    tx, ty = 840, 668
    b.append(f'<path d="M{tx},{ty} L{tx},{ty - 90}" stroke="#3b3a37" stroke-width="7" stroke-linecap="round"/>')
    for a, l in ((-0.9, 50), (-0.4, 60), (0.3, 55), (0.8, 45), (-0.1, 40)):
        bx, by = tx, ty - 55 - l * 0.2
        b.append(f'<path d="M{bx},{by} L{bx + l * math.sin(a):.0f},{by - l * math.cos(a):.0f}" stroke="#3b3a37" stroke-width="3" stroke-linecap="round"/>')
    b.append(f'<ellipse cx="{tx}" cy="{ty + 4}" rx="60" ry="7" fill="#c8d4e2" opacity="0.7"/>')
    # Falling snow.
    for _ in range(140):
        b.append(f'<circle cx="{rng.uniform(0, W):.0f}" cy="{rng.uniform(0, H):.0f}" r="{rng.uniform(1.5, 3.5):.1f}" fill="#fff" opacity="0.85"/>')
    return svg("hokkaido", "".join(b), ("#c9d8e8", "#eef2f6"))


# ---------------------------------------------------------------- Lofoten: red cabins under Reine's peaks
def lofoten():
    rng = random.Random(2)
    b = []
    b.append(glow(700, 470, 620, 220, "#f7c9a8", 0.55))
    b.append(clouds(rng, 3, 70, 170, colour="#fbe7da", opacity=0.7))
    far = ridge(0, W, 520, rng, [(0.15, 0.08, 0.7), (0.32, 0.06, 1.0), (0.52, 0.1, 0.85), (0.8, 0.07, 0.95), (0.95, 0.06, 0.6)], 330, jag=14, step=16)
    b.append(poly(far, "#6b7d92"))
    b.append(f'<rect x="0" y="400" width="{W}" height="120" fill="url(#lofoten-haze)"/>')
    for x, y in far[1:-1:3]:  # snow streaks in the gullies
        if y < 360 and rng.random() < 0.6:
            b.append(f'<path d="M{x:.0f},{y + 8:.0f} L{x + rng.uniform(-14, 14):.0f},{y + rng.uniform(50, 110):.0f}" stroke="#eef2f6" stroke-width="4" stroke-linecap="round" opacity="0.9"/>')
    near = ridge(0, 520, 540, rng, [(0.2, 0.25, 0.9), (0.7, 0.2, 0.6)], 150, jag=6)
    b.append(poly(near, "#4c5b6c"))
    # Water and the peaks' reflection.
    b.append(f'<rect x="0" y="520" width="{W}" height="{H - 520}" fill="#4f7e9c"/>')
    refl = [(x, 520 + (520 - y) * 0.55) for x, y in far]
    b.append(poly(refl, "#3f6a86", opacity="0.75"))
    for _ in range(40):
        y = rng.uniform(560, 790)
        x = rng.uniform(0, W)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(30, 90):.0f},0" stroke="#9cc0d6" stroke-width="2.5" opacity="0.6" stroke-linecap="round"/>')
    # Rocky shore and the rorbuer on stilts.
    b.append(f'<path d="M560,540 C700,520 900,528 1200,520 L1200,560 L560,560 Z" fill="#5d5a55"/>')
    for i, x in enumerate((600, 700, 790, 890, 980, 1080)):
        w, h = rng.uniform(70, 86), rng.uniform(46, 58)
        base = 540 - i * 1.5
        for sx in (x + 8, x + w - 8):
            b.append(f'<line x1="{sx:.0f}" y1="{base:.0f}" x2="{sx:.0f}" y2="{base + 34:.0f}" stroke="#2f2d2a" stroke-width="4"/>')
        b.append(f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#b23a2c"/>')
        b.append(poly([(x - 6, base - h), (x + w / 2, base - h - 30), (x + w + 6, base - h)], "#2f2d2a"))
        b.append(f'<rect x="{x + w / 2 - 9:.0f}" y="{base - h + 14:.0f}" width="18" height="16" fill="#f7f3ea"/>')
        b.append(f'<rect x="{x:.0f}" y="{base + 34:.0f}" width="{w:.0f}" height="{h * 0.5:.0f}" fill="#b23a2c" opacity="0.35"/>')
    return svg("lofoten", "".join(b), ("#f2d6c4", "#dfe8f0"),
               defs=grad("lofoten-haze", "#dfe8f0", "#dfe8f0").replace('stop-color="#dfe8f0"/>', 'stop-color="#dfe8f0" stop-opacity="0"/>', 1)
               .replace('<stop offset="1" stop-color="#dfe8f0"/>', '<stop offset="1" stop-color="#dfe8f0" stop-opacity="0.55"/>'))


# ---------------------------------------------------------------- Patagonia: the towers of Torres del Paine
def patagonia():
    rng = random.Random(3)
    b = []
    for cx, cy, rx in ((330, 120, 170), (880, 90, 210), (620, 60, 130)):
        for k in range(3):
            b.append(f'<ellipse cx="{cx}" cy="{cy + k * 9}" rx="{rx - k * 30}" ry="{12 - k * 2}" fill="#ffffff" opacity="{0.75 - k * 0.15:.2f}"/>')
    back = ridge(0, W, 480, rng, [(0.1, 0.12, 0.5), (0.85, 0.15, 0.55)], 200, jag=5)
    b.append(poly(back, "#8d98a6"))
    # Three granite towers, lit on one side.
    for cx, top, w in ((470, 150, 92), (600, 110, 104), (735, 165, 88)):
        left = [(cx - w * 0.75, 470), (cx - w * 0.5, top + 60), (cx - w * 0.3, top + 8), (cx, top), (cx + w * 0.18, top + 14)]
        right = [(cx + w * 0.18, top + 14), (cx + w * 0.42, top + 70), (cx + w * 0.7, 470)]
        b.append(poly(left + right, "#c9bfae"))
        b.append(poly([(cx, top), (cx + w * 0.18, top + 14), (cx + w * 0.42, top + 70), (cx + w * 0.7, 470), (cx + w * 0.05, 470)], "#9c9282"))
        b.append(f'<path d="M{cx - w * 0.6:.0f},{top + 150:.0f} L{cx + w * 0.55:.0f},{top + 150:.0f}" stroke="#7f776a" stroke-width="3" opacity="0.6"/>')
    # Dark moraine with snow patches below the towers.
    mor = ridge(60, 1140, 534, rng, [(0.5, 0.32, 1.0), (0.15, 0.2, 0.45), (0.85, 0.2, 0.5)], 130, jag=4)
    b.append(poly(mor, "#4f5258"))
    for _ in range(9):
        x, y = rng.uniform(340, 860), rng.uniform(430, 480)
        b.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rng.uniform(16, 40):.0f}" ry="5" fill="#eef2f6"/>')
    # Turquoise lake and golden steppe in front.
    b.append(f'<rect x="0" y="530" width="{W}" height="120" fill="#3fa9b5"/>')
    for _ in range(26):
        x, y = rng.uniform(0, W), rng.uniform(545, 640)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(30, 80):.0f},0" stroke="#a9dde2" stroke-width="2.5" opacity="0.7" stroke-linecap="round"/>')
    b.append(f'<path d="M0,640 C220,610 480,660 760,630 S1080,610 1200,630 L1200,800 L0,800 Z" fill="#c6a457"/>')
    b.append(f'<path d="M0,700 C300,670 600,720 900,690 S1150,680 1200,690 L1200,800 L0,800 Z" fill="#a8873f"/>')
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(650, 800)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(-4, 4):.0f},-{rng.uniform(10, 22):.0f}" stroke="#7d6328" stroke-width="2" stroke-linecap="round"/>')
    return svg("patagonia", "".join(b), ("#a9c8e3", "#e8eff5"))


# ---------------------------------------------------------------- Bhutan: Tiger's Nest on its cliff
def bhutan():
    rng = random.Random(4)
    b = []
    for base, col, amp in ((520, "#9db3a2", 210), (620, "#6f8f78", 170)):
        b.append(poly(ridge(0, W, base, rng, [(0.15, 0.2, 0.8), (0.5, 0.25, 0.6), (0.85, 0.2, 0.9)], amp, jag=3), col))
    # The cliff face.
    cliff = [(600, 800), (640, 420), (700, 230), (760, 120), (900, 90), (1200, 80), (1200, 800)]
    b.append(poly(cliff, "#8b7f72"))
    for i in range(14):
        x = 700 + i * 34
        b.append(f'<path d="M{x},{140 + rng.uniform(0, 40):.0f} L{x - 30 + rng.uniform(-10, 10):.0f},{700:.0f}" stroke="#6f655b" stroke-width="3" opacity="0.6"/>')
    # The monastery: white halls with red bands and gold roofs, stepped on a ledge.
    halls = ((700, 330, 120, 70), (790, 290, 110, 80), (860, 340, 140, 64), (750, 390, 110, 52))
    for x, y, w, h in halls:
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#f6f2e8" stroke="#6f655b" stroke-width="1.5"/>')
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="10" fill="#9b2f23"/>')
        b.append(poly([(x - 12, y), (x + w / 2, y - 26), (x + w + 12, y)], "#c89a2e"))
        for k in range(3):
            b.append(f'<rect x="{x + 16 + k * (w - 40) / 2:.0f}" y="{y + 24}" width="12" height="18" fill="#3b3a37"/>')
    b.append(f'<path d="M690,430 C760,422 860,420 1010,410" stroke="#6f655b" stroke-width="5" fill="none"/>')
    b.append(f'<path d="M0,640 C200,620 420,660 640,640 L640,800 L0,800 Z" fill="#4f6f58"/>')
    # Pines in the foreground.
    for i in range(16):
        x = rng.uniform(0, 620)
        y = rng.uniform(690, 780)
        h = rng.uniform(70, 120)
        b.append(poly([(x - h * 0.22, y), (x, y - h), (x + h * 0.22, y)], "#2f4a3c"))
    # A string of prayer flags across the front.
    b.append(f'<path d="M0,560 Q420,650 820,600" stroke="#5f5c55" stroke-width="2" fill="none"/>')
    colours = ("#2f6db5", "#f7f3ea", "#c0392b", "#2f855a", "#e0b62e")
    for i in range(18):
        t = (i + 0.5) / 18
        x = 820 * t
        y = (1 - t) ** 2 * 560 + 2 * (1 - t) * t * 650 + t * t * 600
        b.append(f'<rect x="{x - 15:.0f}" y="{y:.0f}" width="30" height="38" fill="{colours[i % 5]}" stroke="#5f5c55" stroke-width="1" transform="rotate({rng.uniform(-6, 6):.0f} {x:.0f} {y:.0f})"/>')
    return svg("bhutan", "".join(b), ("#c7dcea", "#f1efe6"))


# ---------------------------------------------------------------- Samarkand: the Registan
def samarkand():
    rng = random.Random(5)
    b = []
    TILE, TURQ, BRICK, DARK = "#2a5f9e", "#2f9bb5", "#d4b483", "#b8955f"

    def minaret(x, top, w=30):
        out = [f'<rect x="{x - w / 2}" y="{top}" width="{w}" height="{620 - top}" fill="{BRICK}"/>']
        for y in range(top + 30, 600, 46):
            out.append(f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="12" fill="{TILE}"/>')
        out.append(f'<rect x="{x - w / 2 - 6}" y="{top - 12}" width="{w + 12}" height="14" fill="{TURQ}"/>')
        return "".join(out)

    def madrasa(cx, w, top, dome=None):
        out = []
        if dome:  # ribbed dome behind the portal
            dx, dy, r = dome
            out.append(f'<rect x="{dx - r * 0.55}" y="{dy}" width="{r * 1.1}" height="40" fill="{BRICK}"/>')
            out.append(f'<path d="M{dx - r},{dy} A{r},{r * 1.05} 0 0 1 {dx + r},{dy} Z" fill="{TURQ}"/>')
            for k in range(-3, 4):
                out.append(f'<path d="M{dx + k * r / 4:.0f},{dy} Q{dx + k * r / 7:.0f},{dy - r * 0.7:.0f} {dx},{dy - r * 1.04:.0f}" stroke="#1f7088" stroke-width="2" fill="none"/>')
        out.append(f'<rect x="{cx - w / 2}" y="{top}" width="{w}" height="{620 - top}" fill="{BRICK}"/>')
        out.append(f'<rect x="{cx - w / 2}" y="{top}" width="{w}" height="18" fill="{TILE}"/>')
        out.append(f'<rect x="{cx - w / 2 + 10}" y="{top + 18}" width="{w - 20}" height="{620 - top - 18}" fill="none" stroke="{TILE}" stroke-width="8"/>')
        # Pointed arch in the portal.
        aw, at = w * 0.5, top + 70
        out.append(f'<path d="M{cx - aw / 2},620 L{cx - aw / 2},{at + 60} Q{cx - aw / 2},{at} {cx},{at - 20} Q{cx + aw / 2},{at} {cx + aw / 2},{at + 60} L{cx + aw / 2},620 Z" fill="{TILE}"/>')
        out.append(f'<path d="M{cx - aw / 2 + 16},620 L{cx - aw / 2 + 16},{at + 70} Q{cx - aw / 2 + 16},{at + 18} {cx},{at + 2} Q{cx + aw / 2 - 16},{at + 18} {cx + aw / 2 - 16},{at + 70} L{cx + aw / 2 - 16},620 Z" fill="{DARK}"/>')
        for k in range(4):  # tile pattern dots on the portal frame
            out.append(f'<circle cx="{cx - w / 2 + 22 + k * (w - 44) / 3:.0f}" cy="{top + 40}" r="6" fill="{TURQ}"/>')
        return "".join(out)

    # Side wings, then the three madrasas (Ulugh Beg, Tilya-Kori with its dome, Sher-Dor).
    b.append(f'<rect x="60" y="430" width="1080" height="190" fill="{DARK}"/>')
    for x in range(80, 1140, 40):
        b.append(f'<path d="M{x},620 L{x},480 Q{x + 15},460 {x + 30},480 L{x + 30},620" fill="#9c7c4c"/>')
    b.append(minaret(70, 250))
    b.append(madrasa(230, 260, 260))
    b.append(minaret(390, 250))
    b.append(madrasa(600, 240, 300, dome=(600, 300, 120)))
    b.append(minaret(810, 250))
    b.append(madrasa(970, 260, 260))
    b.append(minaret(1130, 250))
    # The paved square.
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#d9cdb6"/>')
    for k in range(-12, 13):
        b.append(f'<path d="M{600 + k * 30},620 L{600 + k * 140},{H}" stroke="#c7b99e" stroke-width="2"/>')
    for y in (650, 690, 745):
        b.append(f'<path d="M0,{y} L{W},{y}" stroke="#c7b99e" stroke-width="2"/>')
    return svg("samarkand", "".join(b), ("#5b8fc7", "#e7eef6"))


# ---------------------------------------------------------------- Faroe Islands: Mulafossur falling into the sea
def faroe():
    rng = random.Random(6)
    b = []
    b.append(glow(930, 300, 420, 170, "#f7f4ec", 0.55))
    b.append(clouds(rng, 5, 40, 230, colour="#f2f4f5", opacity=0.55))
    # Mykines on the horizon.
    b.append(poly(ridge(760, 1200, 445, rng, [(0.35, 0.22, 1.0), (0.75, 0.12, 0.6)], 95, jag=2), "#a3afb6"))
    # Sea.
    b.append(f'<rect x="0" y="444" width="{W}" height="{H - 444}" fill="url(#faroe-sea)"/>')
    for _ in range(70):
        x, y = rng.uniform(0, W), rng.uniform(460, 790)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(25, 70) * (0.5 + (y - 440) / 360):.0f},0" stroke="#a9c3cf" '
                 f'stroke-width="{1.5 + (y - 440) / 200:.1f}" opacity="0.5" stroke-linecap="round"/>')
    # Steep green mountains behind the village, with gullies.
    mtn = "M0,410 L0,60 C60,40 120,30 190,52 C260,74 300,110 360,160 C420,212 470,262 540,318 C580,350 610,372 640,392 L640,410 Z"
    b.append(f'<path d="{mtn}" fill="url(#faroe-grass)"/>')
    for x0 in (60, 130, 200, 270, 340, 410):
        y0 = 60 + (x0 / 640) ** 1.4 * 320
        b.append(f'<path d="M{x0},{y0:.0f} C{x0 + 12},{y0 + 80:.0f} {x0 - 8},{y0 + 160:.0f} {x0 + 18},{min(y0 + 250, 390):.0f}" '
                 f'stroke="#3f6634" stroke-width="3" fill="none" opacity="0.55"/>')
    # The cliff: layered basalt with grass ledges, under the village.
    edge = [(612, 392), (640, 420), (662, 500), (676, 560), (690, 612)]
    cliff = [(0, 398), (300, 392)] + edge + [(0, 612)]
    b.append(f'<polygon points="{pts(cliff)}" fill="url(#faroe-rock)"/>')
    for y in range(414, 606, 22):
        ex = next(x for x, yy in reversed(edge) if yy <= y + 30) if y > 392 else 612
        wob = rng.uniform(-3, 3)
        b.append(f'<path d="M0,{y + wob:.0f} C200,{y - 4:.0f} 420,{y + 4:.0f} {ex - 6},{y:.0f}" stroke="#34332f" stroke-width="3" fill="none" opacity="0.7"/>')
        if rng.random() < 0.7:
            gx = rng.uniform(20, ex - 160)
            b.append(f'<path d="M{gx:.0f},{y - 3} l{rng.uniform(60, 160):.0f},{rng.uniform(-2, 2):.0f}" stroke="#5f8a4c" stroke-width="4" stroke-linecap="round"/>')
    b.append(poly([(612, 392), (640, 420), (662, 500), (676, 560), (690, 612), (650, 612), (640, 520), (620, 430)], "#2c2b28", opacity="0.45"))
    # Grass lip along the cliff top.
    b.append(f'<path d="M0,398 L300,392 L612,392 L604,384 L0,386 Z" fill="#5d8b4b"/>')
    # The stream and the waterfall.
    b.append(f'<path d="M330,300 C380,330 420,340 470,352 S560,372 604,390" stroke="#a8cfdd" stroke-width="6" fill="none" stroke-linecap="round"/>')
    b.append(f'<path d="M600,390 C606,430 612,520 620,612 L652,612 C640,520 628,440 616,392 Z" fill="#f6f9fa"/>')
    for k in range(4):
        b.append(f'<path d="M{604 + k * 3},{400 + k * 12} C{610 + k * 3},{470} {616 + k * 4},{540} {624 + k * 6},{606}" stroke="#cddde3" stroke-width="2" fill="none"/>')
    b.append(glow(636, 614, 60, 16, "#ffffff", 0.8))
    for _ in range(24):
        b.append(f'<circle cx="{rng.uniform(604, 676):.0f}" cy="{rng.uniform(596, 630):.0f}" r="{rng.uniform(5, 13):.0f}" fill="#fff" opacity="0.5"/>')
    b.append(f'<path d="M0,614 C120,606 300,620 460,612 S640,606 700,616" stroke="#dbe7ec" stroke-width="4" fill="none" opacity="0.8"/>')
    # Gasadalur: tarred houses with turf roofs, one red, and a small white church.
    for x, y, col in ((380, 350, "#2a2927"), (432, 356, "#9f3426"), (486, 362, "#2a2927"), (330, 344, "#2a2927")):
        b.append(f'<rect x="{x}" y="{y}" width="40" height="22" fill="{col}"/>')
        b.append(f'<rect x="{x + 15}" y="{y + 8}" width="8" height="8" fill="#f0e9d8"/>')
        b.append(poly([(x - 5, y), (x + 20, y - 15), (x + 45, y)], "#557f43"))
    cx, cy = 530, 368
    b.append(f'<rect x="{cx}" y="{cy}" width="36" height="20" fill="#f4f1ea"/>')
    b.append(poly([(cx - 4, cy), (cx + 18, cy - 14), (cx + 40, cy)], "#2a2927"))
    b.append(f'<rect x="{cx + 26}" y="{cy - 20}" width="8" height="12" fill="#f4f1ea"/>')
    b.append(poly([(cx + 24, cy - 20), (cx + 30, cy - 30), (cx + 36, cy - 20)], "#2a2927"))
    # Seabirds.
    for _ in range(7):
        x, y, w = rng.uniform(680, 1000), rng.uniform(200, 380), rng.uniform(8, 14)
        b.append(f'<path d="M{x - w:.0f},{y:.0f} q{w / 2:.0f},-{w / 2:.0f} {w:.0f},0 q{w / 2:.0f},-{w / 2:.0f} {w:.0f},0" stroke="#3b3a37" stroke-width="2" fill="none"/>')
    # Foreground: the grassy slope we're standing on, with a path and fence posts.
    b.append(f'<path d="M700,800 C780,720 940,650 1200,610 L1200,800 Z" fill="#5d8b4b"/>')
    b.append(f'<path d="M820,800 C900,740 1040,690 1200,668 L1200,800 Z" fill="#4c7a3d"/>')
    b.append(f'<path d="M1000,800 C1040,760 1110,720 1200,700" stroke="#a89a7c" stroke-width="10" fill="none" stroke-linecap="round"/>')
    for i in range(6):
        x = 780 + i * 80
        y = 800 - (x - 700) * 0.36 - 8
        b.append(f'<line x1="{x}" y1="{y:.0f}" x2="{x}" y2="{y - 34:.0f}" stroke="#4a3b2a" stroke-width="5" stroke-linecap="round"/>')
    for i in range(5):
        x1, x2 = 780 + i * 80, 860 + i * 80
        b.append(f'<line x1="{x1}" y1="{800 - (x1 - 700) * 0.36 - 30:.0f}" x2="{x2}" y2="{800 - (x2 - 700) * 0.36 - 30:.0f}" stroke="#6b5a45" stroke-width="2"/>')
    for _ in range(110):
        x = rng.uniform(720, 1200)
        ytop = 800 - (x - 700) * 0.38
        y = rng.uniform(max(ytop, 600), 800)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(-3, 3):.0f},-{rng.uniform(8, 16):.0f}" stroke="#3f6a32" stroke-width="2" stroke-linecap="round"/>')
    defs = (grad("faroe-sea", "#6f94a3", "#36596a") + grad("faroe-grass", "#7aa465", "#4d7a40")
            + grad("faroe-rock", "#55544f", "#3a3935"))
    return svg("faroe", "".join(b), ("#b4c0c8", "#e4e8ea"), defs=defs)


# ---------------------------------------------------------------- Chamonix: Mont Blanc and the Aiguille du Midi
def chamonix():
    rng = random.Random(7)
    b = []
    b.append(glow(820, 300, 620, 260, "#fbe7d6", 0.55))
    b.append(clouds(rng, 3, 70, 170, opacity=0.5))
    # Far ridge, then the Mont Blanc massif: a broad snow dome on the right.
    b.append(poly(ridge(0, W, 580, rng, [(0.15, 0.12, 0.6), (0.45, 0.1, 0.5), (0.8, 0.2, 0.7)], 150, jag=6), "#a9b8c9"))
    dome = [(380, 580), (560, 330), (700, 250), (790, 205), (860, 190), (930, 200), (1030, 250), (1130, 320), (1200, 360), (1200, 580)]
    b.append(poly(dome, "#f4f7fa"))
    b.append(poly([(860, 190), (930, 200), (1030, 250), (1130, 320), (1200, 360), (1200, 580), (900, 580)], "#24364d", opacity="0.10"))
    for x0, y0 in ((640, 300), (760, 250), (980, 260), (1090, 320)):  # rock bands showing through the snow
        b.append(f'<path d="M{x0},{y0} q{rng.uniform(10, 30):.0f},{rng.uniform(40, 70):.0f} {rng.uniform(-10, 20):.0f},{rng.uniform(110, 150):.0f}" '
                 f'fill="none" stroke="#7b8796" stroke-width="{rng.uniform(5, 9):.0f}" stroke-linecap="round" opacity="0.35"/>')
    # The Bossons glacier, tumbling from the dome toward the valley.
    b.append(f'<path d="M840,215 C820,300 760,400 730,560 L810,560 C830,400 860,300 870,215 Z" fill="#e3edf6"/>')
    b.append(f'<path d="M760,420 l20,-6 M772,380 l22,-6 M790,330 l20,-5" stroke="#b9cde0" stroke-width="4" stroke-linecap="round"/>')
    # The Aiguille du Midi: granite needles on the left, the summit station on the tallest.
    needles = [(100, 580), (170, 360), (200, 300), (215, 210), (232, 150), (250, 214), (272, 260), (300, 230), (330, 320), (380, 300), (430, 400), (500, 580)]
    b.append(poly(needles, "#5f6670"))
    b.append(poly([(232, 150), (250, 214), (272, 260), (300, 230), (330, 320), (380, 300), (430, 400), (500, 580), (300, 580)], "#24364d", opacity="0.22"))
    b.append(poly([(200, 300), (215, 210), (232, 150), (240, 190), (222, 240)], "#f4f7fa", opacity="0.85"))
    b.append(f'<rect x="222" y="128" width="22" height="24" rx="2" fill="#3b3a37"/><path d="M233,128 L233,104" stroke="#3b3a37" stroke-width="3"/>')
    # The cable car line down to the valley, with one cabin on it.
    b.append(f'<path d="M244,146 Q520,420 780,520" fill="none" stroke="#3b3a37" stroke-width="1.6" opacity="0.7"/>')
    b.append(f'<rect x="520" y="372" width="18" height="14" rx="3" fill="#c8402f"/><path d="M529,366 L529,372" stroke="#3b3a37" stroke-width="2"/>')
    b.append(f'<rect x="768" y="512" width="26" height="18" rx="2" fill="#3b3a37"/>')  # the valley station
    # Snowfields and dark pine forest on the lower slopes.
    b.append(f'<path d="M0,560 C240,500 520,540 760,520 S1060,500 1200,530 L1200,800 L0,800 Z" fill="#e9eff5"/>')
    for i in range(46):
        x = rng.uniform(0, W)
        y = 545 - 18 * math.sin(x / 210) + rng.uniform(-6, 26)
        h = rng.uniform(30, 58)
        b.append(poly([(x - h * 0.26, y), (x, y - h), (x + h * 0.26, y)], rng.choice(("#2f4a3c", "#294235", "#365443"))))
    # The valley floor, ski tracks and a few snow-roofed chalets.
    b.append(f'<path d="M0,650 C260,610 560,670 820,630 S1100,610 1200,640 L1200,800 L0,800 Z" fill="#fbfcfd"/>')
    for d in ("M90,800 C200,720 240,690 330,660", "M140,800 C250,720 300,690 380,662"):
        b.append(f'<path d="{d}" fill="none" stroke="#d3deea" stroke-width="3" stroke-linecap="round"/>')
    for cx, cy, w in ((560, 690, 70), (650, 678, 56), (930, 668, 64), (1030, 690, 74)):
        h = w * 0.55
        b.append(f'<rect x="{cx - w / 2:.0f}" y="{cy - h:.0f}" width="{w}" height="{h:.0f}" fill="#8a5a3b"/>')
        b.append(f'<rect x="{cx - w * 0.18:.0f}" y="{cy - h * 0.62:.0f}" width="{w * 0.14:.0f}" height="{h * 0.3:.0f}" fill="#f1c76b"/>')
        b.append(poly([(cx - w * 0.66, cy - h + 2), (cx, cy - h - w * 0.42), (cx + w * 0.66, cy - h + 2)], "#f7f9fb"))
        b.append(f'<path d="M{cx - w * 0.66:.0f},{cy - h + 2:.0f} L{cx + w * 0.66:.0f},{cy - h + 2:.0f}" stroke="#c8d4e2" stroke-width="3"/>')
    b.append(f'<ellipse cx="800" cy="702" rx="380" ry="10" fill="#c8d4e2" opacity="0.45"/>')
    return svg("chamonix", "".join(b), ("#9fc0de", "#e8f0f7"))


# ---------------------------------------------------------------- Garibaldi: the lake below the Black Tusk
def garibaldi():
    rng = random.Random(8)
    b = []
    b.append(clouds(rng, 4, 70, 190, opacity=0.7))
    # Snow peaks and glaciers across the lake (the Guard, Sphinx and Garibaldi massif)
    back = ridge(0, W, 470, rng, [(0.18, 0.1, 0.75), (0.42, 0.09, 1.0), (0.62, 0.1, 0.85), (0.86, 0.12, 0.7)], 260, jag=10, step=16)
    b.append(poly(back, "#7f8ea1"))
    # Snowcaps: white above a ragged snowline, cut to the peaks' own shape
    line = [(x, 330 + 26 * math.sin(x / 37) + rng.uniform(-14, 14)) for x in range(0, W + 1, 24)]
    b.append(f'<defs><clipPath id="garibaldi-peaks">{poly(back, "#000")}</clipPath></defs>'
             f'<g clip-path="url(#garibaldi-peaks)">{poly([(0, 0), (W, 0)] + line[::-1], "#f3f6f9")}'
             f'{poly([(600, 0), (W, 0)] + [p for p in line[::-1] if p[0] >= 600], "#d5dde6")}</g>')
    b.append(poly([(260, 470), (420, 400), (560, 430), (700, 380), (860, 420), (960, 470)], "#e8eef4", opacity="0.85"))  # the Sphinx Glacier tongue
    # The Black Tusk: a dark volcanic spire on its ridge, at the left
    tusk_ridge = ridge(0, 420, 500, rng, [(0.35, 0.3, 0.8)], 120, jag=4)
    b.append(poly(tusk_ridge, "#5b5048"))
    b.append(poly([(150, 400), (166, 300), (172, 252), (186, 236), (198, 248), (206, 236), (214, 254), (222, 306), (240, 400)], "#2f2a28"))
    b.append(poly([(198, 248), (206, 236), (214, 254), (222, 306), (240, 400), (210, 400)], "#4a423d"))
    # Garibaldi Lake: milky turquoise glacial water
    b.append(f'<rect x="0" y="470" width="{W}" height="200" fill="#36b2b5"/>')
    b.append(f'<rect x="0" y="470" width="{W}" height="30" fill="#5cc6c4" opacity="0.7"/>')
    refl = [(x, 470 + (470 - y) * 0.35) for x, y in back]
    b.append(poly(refl, "#2f9ea3", opacity="0.5"))
    for _ in range(34):
        x, y = rng.uniform(0, W), rng.uniform(500, 660)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(30, 80):.0f},0" stroke="#a8e3e0" stroke-width="2.5" opacity="0.6" stroke-linecap="round"/>')
    # The near shore: a meadow and subalpine firs
    b.append(f'<path d="M0,660 C220,630 520,680 780,650 S1080,630 1200,650 L1200,800 L0,800 Z" fill="#6f9a58"/>')
    b.append(f'<path d="M0,720 C300,690 640,740 940,705 S1150,700 1200,710 L1200,800 L0,800 Z" fill="#55804a"/>')
    for x, base, h in ((70, 700, 170), (150, 690, 120), (1040, 690, 190), (1130, 700, 150), (980, 700, 110)):
        for k in range(5):
            w = h * (0.36 - k * 0.06)
            y = base - k * h * 0.2
            b.append(poly([(x - w, y), (x, y - h * 0.32), (x + w, y)], "#2b4a37"))
    for _ in range(40):  # wildflowers in the meadow
        x, y = rng.uniform(0, W), rng.uniform(690, 790)
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(2.5, 4.5):.1f}" fill="{rng.choice(("#e8d35a", "#d65f7a", "#f4f1ea", "#8e6fc4"))}"/>')
    return svg("garibaldi", "".join(b), ("#9fc4e0", "#e9f1f7"))


# ---------------------------------------------------------------- Glacier: Wild Goose Island in St. Mary Lake
def glacier():
    rng = random.Random(9)
    b = []
    b.append(glow(820, 300, 520, 200, "#ffe2b8", 0.55))
    b.append(clouds(rng, 3, 80, 180, colour="#fff4e6", opacity=0.7))
    # Layered peaks around the lake: far, middle, near
    far = ridge(0, W, 470, rng, [(0.2, 0.08, 0.8), (0.4, 0.07, 1.0), (0.62, 0.09, 0.9), (0.85, 0.08, 0.75)], 290, jag=9, step=14)
    b.append(poly(far, "#8a92a8"))
    for x, y in far[1:-1:3]:
        if y < 300 and rng.random() < 0.7:  # lingering snow in the couloirs
            b.append(f'<path d="M{x:.0f},{y + 6:.0f} L{x + rng.uniform(-12, 12):.0f},{y + rng.uniform(40, 90):.0f}" stroke="#f3f5f8" stroke-width="5" stroke-linecap="round" opacity="0.9"/>')
    mid = ridge(0, W, 490, rng, [(0.1, 0.12, 0.8), (0.75, 0.14, 0.7), (0.95, 0.08, 0.9)], 170, jag=5)
    b.append(poly(mid, "#5f6a7c"))
    b.append(poly([(0, 490), (0, 330), (110, 300), (230, 360), (330, 430), (420, 490)], "#3f4a3c"))  # forested slope at the left
    for _ in range(70):
        x = rng.uniform(0, 400); y = rng.uniform(340 + x * 0.3, 490)
        h = rng.uniform(16, 30)
        b.append(poly([(x - h * 0.28, y), (x, y - h), (x + h * 0.28, y)], "#2a3a2c"))
    # St. Mary Lake, deep blue, mirroring the peaks
    b.append(f'<rect x="0" y="488" width="{W}" height="{H - 488}" fill="#3f6f95"/>')
    refl = [(x, 488 + (488 - y) * 0.5) for x, y in far]
    b.append(poly(refl, "#5a7f9e", opacity="0.55"))
    for _ in range(46):
        x, y = rng.uniform(0, W), rng.uniform(520, 790)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(30, 90):.0f},0" stroke="#a9c8de" stroke-width="2.5" opacity="0.55" stroke-linecap="round"/>')
    # Wild Goose Island: a small rocky island with a handful of conifers
    ix, iy = 640, 600
    b.append(f'<ellipse cx="{ix}" cy="{iy}" rx="70" ry="16" fill="#5b4a3a"/>')
    b.append(f'<ellipse cx="{ix}" cy="{iy + 8}" rx="84" ry="10" fill="#2f5470" opacity="0.6"/>')
    for dx, h in ((-44, 54), (-26, 78), (-8, 96), (10, 84), (28, 66), (44, 48)):
        x = ix + dx
        for k in range(4):
            w = h * (0.3 - k * 0.06)
            y = iy - 6 - k * h * 0.22
            b.append(poly([(x - w, y), (x, y - h * 0.34), (x + w, y)], "#23402e"))
        b.append(poly([(x - h * 0.2, iy + 10), (x, iy + 10 + h * 0.5), (x + h * 0.2, iy + 10)], "#23402e", opacity="0.35"))
    return svg("glacier", "".join(b), ("#f6d7b4", "#dfe9f2"))


# ---------------------------------------------------------------- Moorea: Opunohu Bay's peaks over the lagoon
def moorea():
    rng = random.Random(10)
    b = []
    b.append(clouds(rng, 4, 60, 170, opacity=0.75))
    # The jagged volcanic peaks, with Mouaroa's shark-tooth spire in the middle
    back = ridge(0, W, 470, rng, [(0.12, 0.1, 0.6), (0.3, 0.07, 0.8), (0.72, 0.08, 0.85), (0.9, 0.09, 0.65)], 240, jag=10, step=14)
    b.append(poly(back, "#3f7a52"))
    b.append(poly([(458, 506), (540, 300), (566, 180), (580, 150), (592, 172), (612, 240), (650, 340), (734, 506)], "#2f6544"))
    b.append(poly([(580, 150), (592, 172), (612, 240), (650, 340), (734, 506), (624, 506)], "#285a3c"))
    front = ridge(0, W, 500, rng, [(0.22, 0.16, 0.7), (0.78, 0.18, 0.75)], 120, jag=4)
    b.append(poly(front, "#4f9461"))
    for x, y in front[1:-1:2]:  # trees on the lower slopes
        if rng.random() < 0.7:
            b.append(f'<circle cx="{x:.0f}" cy="{y + rng.uniform(6, 30):.0f}" r="{rng.uniform(8, 16):.0f}" fill="#3d8152" opacity="0.8"/>')
    # The lagoon: turquoise in the shallows, deep blue past the reef
    b.append(f'<rect x="0" y="500" width="{W}" height="{H - 500}" fill="#3ec8c4"/>')
    b.append(f'<path d="M0,500 C300,530 700,515 1200,505 L1200,560 C800,575 400,560 0,575 Z" fill="#6fdad2" opacity="0.8"/>')
    b.append(f'<path d="M0,700 C320,680 760,700 1200,684 L1200,800 L0,800 Z" fill="#2a8fb0"/>')
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(560, 690)
        b.append(f'<path d="M{x:.0f},{y:.0f} l{rng.uniform(30, 80):.0f},0" stroke="#b6eee8" stroke-width="2.5" opacity="0.6" stroke-linecap="round"/>')
    # Overwater bungalows on a curving jetty
    jetty = [(140 + i * 74, 612 - 6 * math.sin(i / 2.2)) for i in range(9)]
    b.append(f'<polyline points="{pts(jetty)}" fill="none" stroke="#8a6a45" stroke-width="7"/>')
    for x, y in jetty[1:]:
        for sx in (x - 22, x + 22):
            b.append(f'<line x1="{sx:.0f}" y1="{y - 4:.0f}" x2="{sx:.0f}" y2="{y + 30:.0f}" stroke="#6b4f33" stroke-width="4"/>')
        b.append(f'<rect x="{x - 28:.0f}" y="{y - 30:.0f}" width="56" height="28" fill="#c9a26b"/>')
        b.append(poly([(x - 36, y - 30), (x, y - 58), (x + 36, y - 30)], "#a5793f"))
        b.append(f'<rect x="{x - 8:.0f}" y="{y - 22:.0f}" width="16" height="14" fill="#5a4630"/>')
    # A leaning palm on the beach in front
    b.append(f'<path d="M1080,800 C1070,720 1040,660 990,610" fill="none" stroke="#7a5a3a" stroke-width="14" stroke-linecap="round"/>')
    for a, l in ((-2.6, 120), (-2.1, 140), (-1.5, 130), (-0.9, 120), (-0.3, 100), (2.9, 110)):
        x2, y2 = 990 + l * math.cos(a), 610 + l * math.sin(a) * 0.6
        b.append(f'<path d="M990,610 Q{(990 + x2) / 2:.0f},{min(610, y2) - 30:.0f} {x2:.0f},{y2 + 20:.0f}" fill="none" stroke="#2f7a44" stroke-width="12" stroke-linecap="round"/>')
    b.append(f'<path d="M900,800 C980,780 1100,770 1200,775 L1200,800 Z" fill="#efe0b9"/>')
    return svg("moorea", "".join(b), ("#7fc0e6", "#e6f4fa"))


PLACES = (("hokkaido", hokkaido), ("lofoten", lofoten), ("patagonia", patagonia),
          ("bhutan", bhutan), ("samarkand", samarkand), ("faroe-islands", faroe),
          ("chamonix", chamonix), ("garibaldi", garibaldi), ("glacier-national-park", glacier), ("moorea", moorea))
os.makedirs(OUT, exist_ok=True)
for name, fn in PLACES:
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(fn())
print("wrote", ", ".join(n + ".svg" for n, _ in PLACES), "to", OUT)
