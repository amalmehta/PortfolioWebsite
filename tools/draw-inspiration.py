"""Draws the What I live by page's Inspiration cards as 1200x800 SVGs in images/inspiration/.

Each is an original flat drawing in the style of the Travel page's places, not a
photograph. Run from the repo root after changing a drawing:
  python3 tools/draw-inspiration.py
"""
import os, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "images/inspiration"
W, H = 1200, 800
SKIN, SKIN_SHADE = "#d6a07a", "#c08a66"
HAIR = "#3a2a20"
SKY_BLUE, WHITE = "#78acdc", "#f4f6f8"
GOLD, GOLD_DARK, GOLD_LIGHT = "#d9a93a", "#a9781e", "#f2cf6b"
MALACHITE = "#2e7d5b"


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def messi():
    """Lionel Messi lifting the World Cup over his head in the bisht he wore for it, Lusail, 18 December 2022."""
    rng = random.Random(10)
    defs = (
        '<linearGradient id="night" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#0d1a36"/><stop offset="1" stop-color="#243f6b"/></linearGradient>'
        '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#fff6d8" stop-opacity="0.55"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#f2cf6b" stop-opacity="0.35"/><stop offset="1" stop-color="#f2cf6b" stop-opacity="0"/></radialGradient>'
    )
    body = [f'<rect width="{W}" height="{H}" fill="url(#night)"/>']
    # Floodlights in the top corners, and their glow
    for cx in (120, 1080):
        body.append(f'<circle cx="{cx}" cy="70" r="230" fill="url(#glow)"/>')
        for i in range(4):
            body.append(f'<rect x="{cx - 46 + i * 24}" y="58" width="18" height="12" rx="2" fill="#fff8e6"/>')
    # The crowd: rows of dim heads, with phone lights here and there
    for row, (y, shade) in enumerate(((560, "#1b2c4d"), (610, "#172745"), (660, "#13213c"), (712, "#101c33"))):
        x = -10 + row * 9
        while x < W + 20:
            r = rng.uniform(13, 17)
            body.append(f'<circle cx="{x:.1f}" cy="{y + rng.uniform(-4, 4):.1f}" r="{r:.1f}" fill="{shade}"/>')
            if rng.random() < 0.08:
                body.append(f'<circle cx="{x:.1f}" cy="{y - 22:.1f}" r="2.6" fill="#fff4c2"/>')
            x += rng.uniform(26, 34)
    body.append(f'<rect y="735" width="{W}" height="65" fill="#0e1830"/>')
    # Confetti, mostly gold, as it fell in Lusail
    for _ in range(170):
        x, y = rng.uniform(0, W), rng.uniform(0, 560)
        if 380 < x < 820 and y > 120:  # keep the figure clear
            continue
        col = rng.choice((GOLD_LIGHT, GOLD, GOLD, GOLD_LIGHT, WHITE, SKY_BLUE))
        w, h, a = rng.uniform(6, 12), rng.uniform(3, 6), rng.uniform(0, 180)
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}" '
                    f'transform="rotate({a:.0f} {x:.1f} {y:.1f})" opacity="0.9"/>')
    body.append('<circle cx="600" cy="140" r="190" fill="url(#halo)"/>')

    # Shirt: Argentina's sky-blue and white stripes, clipped to the torso
    torso = [(430, 800), (434, 570), (446, 526), (478, 500), (540, 480), (660, 480), (722, 500), (754, 526), (766, 570), (770, 800)]
    defs += f'<clipPath id="shirt"><polygon points="{pts(torso)}"/></clipPath>'
    stripes = "".join(f'<rect x="{x}" y="460" width="46" height="340" fill="{SKY_BLUE}"/>' for x in range(416, 790, 92))
    body.append(f'<g clip-path="url(#shirt)"><rect x="420" y="460" width="360" height="340" fill="{WHITE}"/>{stripes}'
                f'<rect x="420" y="460" width="360" height="340" fill="#0d1a36" opacity="0.06"/></g>')
    # Collar and neck
    body.append(f'<rect x="572" y="412" width="56" height="74" rx="18" fill="{SKIN_SHADE}"/>')
    body.append(f'<polygon points="{pts([(548, 480), (600, 518), (652, 480), (636, 474), (600, 500), (564, 474)])}" fill="#1f2a3d"/>')

    # Arms raised to the trophy
    for side in (-1, 1):
        sx, ex, hx = 600 + side * 122, 600 + side * 172, 600 + side * 52
        body.append(f'<polyline points="{pts([(sx, 520), (ex, 360), (hx, 236)])}" fill="none" stroke="{SKIN}" '
                    'stroke-width="44" stroke-linecap="round" stroke-linejoin="round"/>')
        body.append(f'<circle cx="{hx}" cy="232" r="26" fill="{SKIN}"/>')
    # The bisht he was given before the lift: a sheer black cloak with gold trim, open down the
    # front over the shirt, its wide sleeves falling from his raised arms to just below the elbow
    for side in (-1, 1):
        x = lambda d: 600 + side * d
        cloak = [(x(56), 484), (x(146), 378), (x(202), 390), (x(238), 610), (x(224), 800), (x(58), 800)]
        body.append(f'<polygon points="{pts(cloak)}" fill="#111214" opacity="0.94"/>')
        body.append(f'<polyline points="{pts([(x(204), 396), (x(232), 600)])}" fill="none" stroke="#2a2b30" stroke-width="3"/>')
        body.append(f'<polyline points="{pts([(x(56), 484), (x(58), 800)])}" fill="none" stroke="{GOLD}" stroke-width="8"/>')
        body.append(f'<polyline points="{pts([(x(146), 378), (x(202), 390)])}" fill="none" stroke="{GOLD}" stroke-width="7" stroke-linecap="round"/>')
        body.append(f'<polyline points="{pts([(x(56), 484), (x(70), 470), (x(96), 462)])}" fill="none" stroke="{GOLD}" stroke-width="7" stroke-linecap="round"/>')

    # Head: hair, face and beard, without features, like the figures elsewhere on the site
    body.append(f'<ellipse cx="600" cy="352" rx="62" ry="74" fill="{SKIN}"/>')
    body.append(f'<path d="M538 336 Q536 268 600 266 Q666 266 664 336 Q652 300 600 300 Q552 300 538 336 Z" fill="{HAIR}"/>')
    body.append(f'<path d="M540 352 Q548 428 600 432 Q652 428 660 352 Q650 392 600 396 Q550 392 540 352 Z" fill="{HAIR}"/>')
    body.append(f'<ellipse cx="538" cy="356" rx="10" ry="16" fill="{SKIN_SHADE}"/><ellipse cx="662" cy="356" rx="10" ry="16" fill="{SKIN_SHADE}"/>')

    # The trophy: a base with two malachite bands, then two figures spiralling up from a narrow
    # waist and widening to their raised arms, which cradle the globe
    body.append(f'<polygon points="{pts([(562, 214), (638, 214), (644, 254), (556, 254)])}" fill="{GOLD}"/>')
    for y in (221, 237):
        body.append(f'<polygon points="{pts([(562 - (y - 214) * 0.15, y), (638 + (y - 214) * 0.15, y), (639 + (y - 206) * 0.15, y + 9), (561 - (y - 206) * 0.15, y + 9)])}" fill="{MALACHITE}"/>')
    body.append(f'<path d="M572 214 C576 198 588 192 586 182 C580 162 554 134 552 112 Q572 98 600 103 Q628 98 648 112 '
                f'C646 134 620 162 614 182 C612 192 624 198 628 214 Z" fill="{GOLD}"/>')
    body.append(f'<path d="M590 212 C600 192 620 172 604 152 S570 124 564 112" fill="none" stroke="{GOLD_DARK}" stroke-width="5" stroke-linecap="round"/>')
    body.append(f'<path d="M612 212 C602 196 584 178 598 158 S630 126 638 112" fill="none" stroke="{GOLD_LIGHT}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>')
    body.append(f'<circle cx="600" cy="68" r="40" fill="{GOLD}"/>')
    body.append(f'<path d="M574 52 Q588 46 592 60 Q586 72 574 66 Z M606 42 Q624 40 628 56 Q616 60 608 54 Z M600 78 Q618 74 624 92 Q608 100 600 90 Z" fill="{GOLD_DARK}"/>')
    body.append(f'<path d="M574 46 Q588 34 606 32" fill="none" stroke="{GOLD_LIGHT}" stroke-width="5" stroke-linecap="round"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{defs}</defs>{"".join(body)}</svg>\n')


def alphago():
    """AlphaGo against Lee Sedol, Seoul, March 2016: a 19x19 board mid-game, one black stone glowing
    for the move that surprised everyone, and a small policy-and-value network beside the board."""
    rng = random.Random(37)
    defs = (
        '<linearGradient id="room" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#1d2326"/><stop offset="1" stop-color="#2c3236"/></linearGradient>'
        '<linearGradient id="wood" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#e2bd72"/><stop offset="1" stop-color="#c99a4e"/></linearGradient>'
        '<radialGradient id="spot" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#ffe9a8" stop-opacity="0.9"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="lamp" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#fff3d6" stop-opacity="0.16"/><stop offset="1" stop-color="#fff3d6" stop-opacity="0"/></radialGradient>'
    )
    body = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', '<circle cx="600" cy="400" r="520" fill="url(#lamp)"/>']
    # The board, seen from above: wood with a faint grain, and a shadow under it
    x0, y0, size = 290, 90, 620
    body.append(f'<rect x="{x0 + 14}" y="{y0 + 18}" width="{size}" height="{size}" rx="8" fill="#0f1315" opacity="0.55"/>')
    body.append(f'<rect x="{x0}" y="{y0}" width="{size}" height="{size}" rx="8" fill="url(#wood)"/>')
    for i in range(14):
        y = y0 + 20 + i * 44 + rng.uniform(-8, 8)
        body.append(f'<path d="M{x0 + 6} {y:.1f} Q{x0 + size / 2} {y + rng.uniform(-10, 10):.1f} {x0 + size - 6} {y + rng.uniform(-6, 6):.1f}" '
                    'fill="none" stroke="#b78a43" stroke-width="2" opacity="0.35"/>')
    m = 34
    step = (size - 2 * m) / 18
    gx = lambda c: x0 + m + c * step
    gy = lambda r: y0 + m + r * step
    lines = "".join(f'<line x1="{gx(0):.1f}" y1="{gy(i):.1f}" x2="{gx(18):.1f}" y2="{gy(i):.1f}"/>'
                    f'<line x1="{gx(i):.1f}" y1="{gy(0):.1f}" x2="{gx(i):.1f}" y2="{gy(18):.1f}"/>' for i in range(19))
    body.append(f'<g stroke="#3b2c18" stroke-width="1.6">{lines}</g>')
    for c in (3, 9, 15):
        for r in (3, 9, 15):
            body.append(f'<circle cx="{gx(c):.1f}" cy="{gy(r):.1f}" r="4.5" fill="#3b2c18"/>')
    # A game in progress: corners and sides taken first, as in a real opening
    taken = set()
    def stone(c, r, black):
        taken.add((c, r))
        x, y, rad = gx(c), gy(r), step * 0.47
        body.append(f'<circle cx="{x + 2:.1f}" cy="{y + 3:.1f}" r="{rad:.1f}" fill="#000" opacity="0.25"/>')
        if black:
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="#1b1c1e"/>'
                        f'<circle cx="{x - rad * 0.32:.1f}" cy="{y - rad * 0.34:.1f}" r="{rad * 0.28:.1f}" fill="#4a4d52" opacity="0.7"/>')
        else:
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="#f3f1ea"/>'
                        f'<circle cx="{x + rad * 0.18:.1f}" cy="{y + rad * 0.22:.1f}" r="{rad * 0.8:.1f}" fill="#d9d5ca" opacity="0.45"/>')
    groups = [((3, 3), 7), ((15, 3), 6), ((3, 15), 6), ((15, 15), 7), ((9, 3), 3), ((3, 9), 3), ((15, 10), 4), ((10, 15), 3)]
    black = True
    for (cc, cr), n in groups:
        for _ in range(n):
            for _try in range(20):
                c, r = cc + rng.randint(-2, 2), cr + rng.randint(-2, 2)
                if 0 <= c <= 18 and 0 <= r <= 18 and (c, r) not in taken:
                    stone(c, r, black)
                    black = not black
                    break
    # The move that surprised everyone: a black stone on the fifth line, ringed in light
    mc, mr = 13, 8
    taken.discard((mc, mr))
    body.append(f'<circle cx="{gx(mc):.1f}" cy="{gy(mr):.1f}" r="{step * 1.6:.1f}" fill="url(#spot)"/>')
    stone(mc, mr, True)
    body.append(f'<circle cx="{gx(mc):.1f}" cy="{gy(mr):.1f}" r="{step * 0.62:.1f}" fill="none" stroke="#f5c84c" stroke-width="3"/>')

    # Beside the board: the policy and value network, layers of nodes feeding one output
    layers = [5, 7, 7, 4, 1]
    nx = [80, 135, 190, 230, 262]
    nodes = [[(nx[i], 400 + (j - (n - 1) / 2) * 46) for j in range(n)] for i, n in enumerate(layers)]
    edges = []
    for a, b in zip(nodes, nodes[1:]):
        for p in a:
            for q in b:
                edges.append(f'<line x1="{p[0]}" y1="{p[1]:.1f}" x2="{q[0]}" y2="{q[1]:.1f}"/>')
    body.append(f'<g stroke="#78acdc" stroke-width="1.2" opacity="0.35">{"".join(edges)}</g>')
    for i, layer in enumerate(nodes):
        for p in layer:
            fill = "#f5c84c" if i == len(nodes) - 1 else "#78acdc"
            body.append(f'<circle cx="{p[0]}" cy="{p[1]:.1f}" r="{9 if i < len(nodes) - 1 else 12}" fill="{fill}"/>')
    body.append(f'<line x1="274" y1="400" x2="{x0 - 4}" y2="400" stroke="#f5c84c" stroke-width="2.5" stroke-dasharray="5 5" opacity="0.7"/>')
    # The other side: the bowls of stones, lids off
    for cy, fill, rim in ((290, "#1b1c1e", "#6b4a26"), (520, "#f3f1ea", "#6b4a26")):
        body.append(f'<ellipse cx="1060" cy="{cy}" rx="86" ry="78" fill="{rim}"/><ellipse cx="1060" cy="{cy}" rx="70" ry="62" fill="#4c3319"/>')
        for _ in range(14):
            x, y = 1060 + rng.uniform(-48, 48), cy + rng.uniform(-40, 40)
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{fill}"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{defs}</defs>{"".join(body)}</svg>\n')


def wrap(defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{defs}</defs>{"".join(body)}</svg>\n')


def feynman():
    """Richard Feynman from behind at a chalkboard, chalk raised beside his diagram of two
    electrons exchanging a photon."""
    rng = random.Random(1965)
    CHALK = "#eef0e6"
    defs = ('<linearGradient id="board" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#2f4b3f"/><stop offset="1" stop-color="#253d33"/></linearGradient>')
    body = [f'<rect width="{W}" height="{H}" fill="#6b5a48"/>',
            f'<rect x="40" y="40" width="1120" height="640" rx="6" fill="#8a6a45"/>',
            f'<rect x="60" y="60" width="1080" height="600" fill="url(#board)"/>']
    # Old chalk smudges
    for _ in range(26):
        x, y = rng.uniform(90, 1110), rng.uniform(90, 630)
        body.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rng.uniform(40, 120):.0f}" ry="{rng.uniform(8, 22):.0f}" fill="{CHALK}" opacity="0.04"/>')
    ch = f'fill="none" stroke="{CHALK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
    # The diagram: two electrons come in, swap a photon (the wavy line), and fly apart
    v1, v2 = (300, 260), (300, 480)
    body.append(f'<polyline points="{pts([(140, 140), v1, (460, 140)])}" {ch}/>')
    body.append(f'<polyline points="{pts([(140, 600), v2, (460, 600)])}" {ch}/>')
    for (ax, ay), (bx, by) in (((140, 140), v1), (v1, (460, 140)), ((140, 600), v2), (v2, (460, 600))):
        mx, my = (ax + bx) / 2, (ay + by) / 2
        dx, dy = (bx - ax), (by - ay)
        n = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / n, dy / n
        body.append(f'<polyline points="{pts([(mx - ux * 16 - uy * 12, my - uy * 16 + ux * 12), (mx, my), (mx - ux * 16 + uy * 12, my - uy * 16 - ux * 12)])}" {ch}/>')
    wave = "M300 260 " + " ".join(f"Q{300 + (18 if i % 2 == 0 else -18)} {260 + i * 22 + 11} 300 {260 + (i + 1) * 22}" for i in range(10))
    body.append(f'<path d="{wave}" {ch}/>')
    for x, y in (v1, v2):
        body.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{CHALK}"/>')
    tx = f'fill="{CHALK}" font-family="Georgia, serif" font-style="italic" font-size="34"'
    body.append(f'<text x="112" y="132" {tx}>e⁻</text><text x="472" y="132" {tx}>e⁻</text>'
                f'<text x="112" y="636" {tx}>e⁻</text><text x="472" y="636" {tx}>e⁻</text><text x="334" y="384" {tx}>γ</text>')
    # A few lines of working, just chalk marks, not real equations
    for i, w in enumerate((300, 240, 330, 190)):
        y = 170 + i * 56
        body.append(f'<path d="M560 {y} q{w / 4} -10 {w / 2} 0 t{w / 2} 0" fill="none" stroke="{CHALK}" stroke-width="4" stroke-linecap="round" opacity="0.6"/>')
    body.append(f'<rect x="60" y="660" width="1080" height="16" fill="#7a5c3a"/>')
    body.append(f'<rect x="250" y="662" width="40" height="9" rx="3" fill="{CHALK}"/><rect x="310" y="664" width="26" height="7" rx="3" fill="#e9c46a"/>')

    # Feynman, from behind: white shirt, wavy grey hair, right arm raised with the chalk
    shirt, shade, skin, hair = "#f1efe8", "#d9d6cc", "#d8a682", "#8c8a86"
    body.append(f'<polyline points="{pts([(930, 520), (870, 380), (790, 300)])}" fill="none" stroke="{shirt}" stroke-width="54" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<circle cx="784" cy="292" r="24" fill="{skin}"/>')
    body.append(f'<line x1="770" y1="280" x2="752" y2="262" stroke="{CHALK}" stroke-width="9" stroke-linecap="round"/>')
    body.append(f'<path d="M780 304 q-6 6 -14 6" fill="none" stroke="{CHALK}" stroke-width="5" stroke-linecap="round"/>')
    body.append(f'<polygon points="{pts([(800, 800), (812, 560), (842, 500), (900, 476), (1010, 476), (1068, 500), (1094, 560), (1106, 800)])}" fill="{shirt}"/>')
    body.append(f'<polygon points="{pts([(955, 476), (1010, 476), (1068, 500), (1094, 560), (1106, 800), (1000, 800)])}" fill="{shade}" opacity="0.6"/>')
    body.append(f'<line x1="953" y1="500" x2="953" y2="800" stroke="{shade}" stroke-width="3"/>')
    body.append(f'<polyline points="{pts([(1062, 520), (1086, 650), (1074, 790)])}" fill="none" stroke="{shirt}" stroke-width="52" stroke-linecap="round"/>')
    body.append(f'<rect x="928" y="430" width="52" height="60" rx="16" fill="{skin}"/>')
    body.append(f'<ellipse cx="954" cy="384" rx="66" ry="76" fill="{skin}"/>')
    body.append(f'<path d="M886 392 Q878 300 954 300 Q1032 300 1022 392 Q1010 440 954 444 Q900 440 886 392 Z" fill="{hair}"/>')
    for i in range(7):
        x = 900 + i * 18
        body.append(f'<path d="M{x} {318 + (i % 2) * 6} q10 -16 20 0" fill="none" stroke="#a7a5a0" stroke-width="5" stroke-linecap="round"/>')
    body.append(f'<ellipse cx="886" cy="392" rx="10" ry="18" fill="{skin}"/><ellipse cx="1022" cy="392" rx="10" ry="18" fill="{skin}"/>')
    return wrap(defs, body)


def kipchoge():
    """Eliud Kipchoge breaking the tape in Vienna, October 2019, the first marathon under two hours:
    arms flung wide under the finish gantry, the clock at 1:59:40, Kenyan flags in the crowd and his
    pacers in black celebrating behind him."""
    rng = random.Random(15940)
    vx, vy = 600, 360  # where the Hauptallee meets the horizon
    defs = ('<linearGradient id="ksky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#bcd3e2"/><stop offset="1" stop-color="#e9eee8"/></linearGradient>'
            '<linearGradient id="kroad" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#9a9c98"/><stop offset="1" stop-color="#5c5f5c"/></linearGradient>')
    body = [f'<rect width="{W}" height="{H}" fill="url(#ksky)"/>',
            f'<rect y="{vy}" width="{W}" height="{H - vy}" fill="#86a266"/>',
            f'<polygon points="{pts([(vx - 30, vy), (vx + 30, vy), (1040, H), (160, H)])}" fill="url(#kroad)"/>']
    # Autumn chestnut trees down the avenue
    for side in (-1, 1):
        for i in range(9):
            t = (i / 8) ** 1.5
            x, y, r = vx + side * (70 + t * 520), vy + 10 + t * 160, 26 + t * 90
            col = rng.choice(("#c98a3a", "#b8742e", "#d9a347", "#a3a14c"))
            body.append(f'<rect x="{x - r * 0.07:.0f}" y="{y - r * 0.5:.0f}" width="{r * 0.14:.0f}" height="{r * 0.7:.0f}" fill="#5b4632"/>')
            body.append(f'<circle cx="{x:.0f}" cy="{y - r * 0.95:.0f}" r="{r:.0f}" fill="{col}"/>'
                        f'<circle cx="{x - side * r * 0.45:.0f}" cy="{y - r * 1.25:.0f}" r="{r * 0.7:.0f}" fill="{col}" opacity="0.85"/>')
    # The crowd behind the barriers on both sides, some waving Kenyan flags
    def flag(x, y, s):
        body.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x:.0f}" y2="{y + 46 * s:.0f}" stroke="#3a3a3a" stroke-width="{2.5 * s:.1f}"/>')
        for k, col in enumerate(("#111111", "#ffffff", "#bb1f2a", "#ffffff", "#1d7a3a")):
            hgt = (9, 2, 8, 2, 9)[k] * s
            off = sum((9, 2, 8, 2, 9)[:k]) * s
            body.append(f'<rect x="{x:.0f}" y="{y + off:.1f}" width="{44 * s:.1f}" height="{hgt:.1f}" fill="{col}"/>')
    for side in (-1, 1):
        for row, y in enumerate((468, 500, 532)):
            x = vx + side * 250
            while 0 < x < W:
                body.append(f'<rect x="{x - 13:.0f}" y="{y:.0f}" width="26" height="40" rx="8" fill="{rng.choice(("#c0392b", "#2c3e50", "#e1b12c", "#6c7a89", "#1d7a3a", "#f0f0f0"))}"/>'
                            f'<circle cx="{x:.0f}" cy="{y - 6:.0f}" r="11" fill="{rng.choice(("#5a3a28", "#8a5a3c", "#d6a07a"))}"/>')
                if row == 0 and rng.random() < 0.3:
                    flag(x + 6, y - 64, 1.0)
                x += side * rng.uniform(30, 40)
        body.append(f'<rect x="{0 if side < 0 else vx + 230}" y="560" width="{vx - 230}" height="26" fill="#f2f2f2"/>'
                    f'<rect x="{0 if side < 0 else vx + 230}" y="572" width="{vx - 230}" height="6" fill="#2f6db5"/>')

    def runner_front(x, y, s, vest, shorts, shoes, skin="#4a2e1f", arms="wide"):
        """A runner coming toward the viewer at scale s, feet at y."""
        lg = f'stroke="{skin}" stroke-width="{16 * s:.1f}" stroke-linecap="round" stroke-linejoin="round" fill="none"'
        body.append(f'<polyline points="{pts([(x - 12 * s, y - 120 * s), (x - 20 * s, y - 64 * s), (x - 16 * s, y - 8 * s)])}" {lg}/>')
        body.append(f'<polyline points="{pts([(x + 12 * s, y - 120 * s), (x + 26 * s, y - 84 * s), (x + 18 * s, y - 44 * s)])}" {lg}/>')
        body.append(f'<ellipse cx="{x - 16 * s:.1f}" cy="{y - 4 * s:.1f}" rx="{13 * s:.1f}" ry="{7 * s:.1f}" fill="{shoes}"/>'
                    f'<ellipse cx="{x + 19 * s:.1f}" cy="{y - 40 * s:.1f}" rx="{12 * s:.1f}" ry="{7 * s:.1f}" fill="{shoes}"/>')
        body.append(f'<rect x="{x - 30 * s:.1f}" y="{y - 150 * s:.1f}" width="{60 * s:.1f}" height="{38 * s:.1f}" rx="{8 * s:.1f}" fill="{shorts}"/>')
        body.append(f'<polygon points="{pts([(x - 32 * s, y - 148 * s), (x - 36 * s, y - 236 * s), (x - 18 * s, y - 246 * s), (x + 18 * s, y - 246 * s), (x + 36 * s, y - 236 * s), (x + 32 * s, y - 148 * s)])}" fill="{vest}"/>')
        am = f'stroke="{skin}" stroke-width="{13 * s:.1f}" stroke-linecap="round" stroke-linejoin="round" fill="none"'
        if arms == "wide":  # flung out wide and up, the way he crossed the line
            for d in (-1, 1):
                body.append(f'<polyline points="{pts([(x + d * 34 * s, y - 236 * s), (x + d * 92 * s, y - 266 * s), (x + d * 140 * s, y - 318 * s)])}" {am}/>')
                body.append(f'<circle cx="{x + d * 144 * s:.1f}" cy="{y - 324 * s:.1f}" r="{9 * s:.1f}" fill="{skin}"/>')
        else:  # fists raised
            for d in (-1, 1):
                body.append(f'<polyline points="{pts([(x + d * 34 * s, y - 236 * s), (x + d * 56 * s, y - 280 * s), (x + d * 52 * s, y - 330 * s)])}" {am}/>')
        body.append(f'<rect x="{x - 9 * s:.1f}" y="{y - 266 * s:.1f}" width="{18 * s:.1f}" height="{24 * s:.1f}" fill="{skin}"/>')
        body.append(f'<ellipse cx="{x:.1f}" cy="{y - 290 * s:.1f}" rx="{22 * s:.1f}" ry="{27 * s:.1f}" fill="{skin}"/>')
        body.append(f'<path d="M{x - 22 * s:.1f} {y - 294 * s:.1f} Q{x:.1f} {y - 330 * s:.1f} {x + 22 * s:.1f} {y - 294 * s:.1f} Q{x:.1f} {y - 308 * s:.1f} {x - 22 * s:.1f} {y - 294 * s:.1f} Z" fill="#1c1410"/>')

    # His pacers behind him, in black, celebrating
    for x, s in ((470, 0.62), (548, 0.56), (652, 0.56), (730, 0.62)):
        runner_front(x, 540, s, "#16181b", "#16181b", "#e8e8e8", arms="fists")
    # The finish gantry: two posts and a beam with the clock
    for x in (150, 1050):
        body.append(f'<rect x="{x - 22}" y="70" width="44" height="730" fill="#20365e"/>')
    body.append('<rect x="128" y="60" width="944" height="120" rx="6" fill="#20365e"/>')
    body.append('<rect x="420" y="78" width="360" height="84" rx="8" fill="#0b0d10"/>')
    body.append('<text x="600" y="146" text-anchor="middle" font-family="Menlo, Consolas, monospace" font-weight="700" '
                'font-size="66" letter-spacing="4" fill="#ffb02e">1:59:40</text>')
    body.append('<rect x="190" y="96" width="190" height="48" rx="6" fill="#ffffff" opacity="0.92"/>'
                '<rect x="820" y="96" width="190" height="48" rx="6" fill="#ffffff" opacity="0.92"/>')
    body.append('<text x="285" y="129" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="26" fill="#20365e">VIENNA</text>'
                '<text x="915" y="129" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="26" fill="#20365e">FINISH</text>')
    # Kipchoge, white vest and pink shoes, arms wide as he breaks the tape
    runner_front(600, 790, 1.55, "#f6f6f3", "#2a2f3a", "#ff4fa0")
    # The tape, broken at his waist, its two ends flying back
    body.append('<path d="M172 560 Q380 590 548 600 L552 612 Q370 606 172 576 Z" fill="#e8443a"/>'
                '<path d="M1028 560 Q820 590 652 598 L648 610 Q830 606 1028 576 Z" fill="#e8443a"/>')
    return wrap(defs, body)


def honnold():
    """Alex Honnold free soloing El Capitan, June 2017: a tiny figure in a red shirt high on the
    granite, with the Yosemite valley far below."""
    rng = random.Random(2017)
    defs = ('<linearGradient id="ysky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#7fb3de"/><stop offset="1" stop-color="#cfe3f1"/></linearGradient>'
            '<linearGradient id="granite" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0" stop-color="#d9d2c3"/><stop offset="0.6" stop-color="#c7bfae"/><stop offset="1" stop-color="#a99f8c"/></linearGradient>')
    body = [f'<rect width="{W}" height="{H}" fill="url(#ysky)"/>']
    # Far valley wall and the forest on the valley floor
    body.append(f'<polygon points="{pts([(0, 560), (120, 470), (260, 520), (360, 490), (420, 800), (0, 800)])}" fill="#a6b3bd"/>')
    for i in range(40):
        x = rng.uniform(0, 420)
        y = rng.uniform(660, 790)
        h = rng.uniform(30, 60)
        body.append(f'<polygon points="{pts([(x, y - h), (x - h * 0.3, y), (x + h * 0.3, y)])}" fill="{rng.choice(("#2f5a3a", "#3b6a45", "#284d33"))}"/>')
    # El Capitan: a huge granite face, its prow on the left, lit from the left
    face = [(330, 800), (360, 520), (420, 250), (520, 90), (640, 40), (900, 30), (1200, 60), (1200, 800)]
    body.append(f'<polygon points="{pts(face)}" fill="url(#granite)"/>')
    body.append(f'<polygon points="{pts([(520, 90), (640, 40), (900, 30), (1200, 60), (1200, 110), (880, 80), (650, 92)])}" fill="#2f5a3a" opacity="0.8"/>')
    # Cracks and streaks in the granite
    for _ in range(26):
        x, y = rng.uniform(430, 1180), rng.uniform(120, 780)
        pts_ = [(x, y)]
        for _k in range(5):
            x += rng.uniform(-14, 14); y += rng.uniform(18, 40)
            pts_.append((x, y))
        body.append(f'<polyline points="{pts(pts_)}" fill="none" stroke="#8f8676" stroke-width="{rng.uniform(1.5, 3.5):.1f}" opacity="0.6"/>')
    for _ in range(10):
        x = rng.uniform(600, 1180)
        body.append(f'<rect x="{x:.0f}" y="{rng.uniform(150, 400):.0f}" width="{rng.uniform(8, 20):.0f}" height="{rng.uniform(200, 420):.0f}" fill="#8f8676" opacity="0.12"/>')
    # Honnold: a small figure in a red shirt, one hand high, a foot on a hold
    x, y, s = 700, 330, 1.0
    skin = "#e0b08a"
    body.append(f'<polyline points="{pts([(x - 4, y + 8), (x - 16, y + 30), (x - 12, y + 48)])}" fill="none" stroke="#3a4a5e" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<polyline points="{pts([(x + 4, y + 8), (x + 18, y + 22), (x + 26, y + 18)])}" fill="none" stroke="#3a4a5e" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<rect x="{x - 9}" y="{y - 26}" width="18" height="36" rx="6" fill="#c8312b"/>')
    body.append(f'<polyline points="{pts([(x - 6, y - 22), (x - 14, y - 44), (x - 10, y - 64)])}" fill="none" stroke="{skin}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<polyline points="{pts([(x + 7, y - 20), (x + 20, y - 30), (x + 24, y - 42)])}" fill="none" stroke="{skin}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<circle cx="{x}" cy="{y - 34}" r="8" fill="{skin}"/><path d="M{x - 8} {y - 36} q8 -12 16 0" fill="#3a2a20"/>')
    body.append(f'<rect x="{x - 6}" y="{y + 6}" width="12" height="8" rx="3" fill="#e8e2d0"/>')
    return wrap(defs, body)


def alcaraz():
    """Carlos Alcaraz flat on his back on Centre Court's grass, arms flung out, just after winning
    Wimbledon in July 2023, seen from the side with the crowd on its feet behind him."""
    rng = random.Random(2023)
    defs = ('<linearGradient id="asky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#cfe2ee"/><stop offset="1" stop-color="#eef3f2"/></linearGradient>')
    body = [f'<rect width="{W}" height="{H}" fill="url(#asky)"/>']
    # The stands, rising away from the court, packed and standing
    body.append(f'<polygon points="{pts([(0, 70), (W, 40), (W, 440), (0, 440)])}" fill="#1f4a2c"/>')
    for row in range(9):
        y = 92 + row * 38
        x = rng.uniform(-10, 10)
        while x < W + 10:
            col = rng.choice(("#f2f2ee", "#c0392b", "#2c3e50", "#e1b12c", "#7f8c8d", "#e8c4a0", "#5b2a86", "#f2f2ee"))
            body.append(f'<rect x="{x:.0f}" y="{y + 8:.0f}" width="20" height="22" rx="5" fill="{col}"/>'
                        f'<circle cx="{x + 10:.0f}" cy="{y + 3:.0f}" r="8" fill="{rng.choice(("#e2b48c", "#c69070", "#8a5a3c", "#f0cfb0"))}"/>')
            if rng.random() < 0.12:  # an arm up in the air
                body.append(f'<line x1="{x + 16:.0f}" y1="{y + 10:.0f}" x2="{x + 24:.0f}" y2="{y - 12:.0f}" stroke="#e2b48c" stroke-width="5" stroke-linecap="round"/>')
            x += rng.uniform(24, 30)
    # The court's back wall, dark green with a purple band
    body.append(f'<rect y="440" width="{W}" height="62" fill="#17391f"/><rect y="440" width="{W}" height="9" fill="#5b2a86"/>')
    # Grass, its mowing stripes running away from us, and the baseline
    body.append(f'<rect y="502" width="{W}" height="{H - 502}" fill="#5f9a46"/>')
    for i, y in enumerate((502, 540, 590, 652, 728)):
        if i % 2 == 0:
            body.append(f'<rect y="{y}" width="{W}" height="{(540, 590, 652, 728, 800)[i] - y}" fill="#6aa54f"/>')
    body.append(f'<polygon points="{pts([(0, 556), (W, 548), (W, 558), (0, 566)])}" fill="#f7f7f2"/>')
    body.append('<ellipse cx="610" cy="650" rx="420" ry="60" fill="#b59a63" opacity="0.55"/>')

    skin, kit, kit_shade, hair = "#e2b48c", "#fbfbf8", "#e4e4de", "#2b1d16"
    # His shadow on the grass, then Alcaraz lying on his back, head to the left
    body.append('<ellipse cx="610" cy="690" rx="270" ry="22" fill="#000" opacity="0.12"/>')
    body.append(f'<polyline points="{pts([(500, 652), (420, 630), (346, 620)])}" fill="none" stroke="{skin}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>')  # far arm, over his head
    body.append(f'<circle cx="340" cy="619" r="13" fill="{skin}"/>')
    body.append(f'<polyline points="{pts([(760, 668), (820, 600), (900, 664)])}" fill="none" stroke="{skin}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>')  # far leg, knee up
    body.append(f'<ellipse cx="912" cy="668" rx="26" ry="14" fill="{kit}"/>')
    body.append(f'<rect x="490" y="636" width="200" height="58" rx="24" fill="{kit}"/>')  # shirt
    body.append(f'<rect x="680" y="640" width="96" height="52" rx="18" fill="{kit_shade}"/>')  # shorts
    body.append(f'<polyline points="{pts([(760, 680), (860, 684), (950, 690)])}" fill="none" stroke="{skin}" stroke-width="24" stroke-linecap="round"/>')  # near leg, straight
    body.append(f'<ellipse cx="966" cy="688" rx="28" ry="15" fill="{kit}"/>')
    body.append(f'<rect x="448" y="652" width="50" height="22" rx="10" fill="{skin}"/>')  # neck
    body.append(f'<ellipse cx="424" cy="662" rx="40" ry="34" fill="{skin}"/>')
    body.append(f'<path d="M386 664 Q384 700 424 700 Q462 700 462 676 Q440 690 420 686 Q396 682 386 664 Z" fill="{hair}"/>')
    body.append(f'<polyline points="{pts([(540, 660), (520, 720), (470, 748)])}" fill="none" stroke="{skin}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>')  # near arm, flung out toward us
    body.append(f'<circle cx="462" cy="752" r="15" fill="{skin}"/>')
    # His racket on the grass where he let it go, and a ball
    body.append('<line x1="1040" y1="736" x2="1100" y2="722" stroke="#2b2b2b" stroke-width="11" stroke-linecap="round"/>')
    body.append('<ellipse cx="1006" cy="742" rx="58" ry="20" fill="#d9d9d2" stroke="#2b2b2b" stroke-width="9"/>')
    body.append('<circle cx="250" cy="720" r="13" fill="#dfe86a"/><path d="M240 713 q10 8 20 0" fill="none" stroke="#f7f7f2" stroke-width="2"/>')
    return wrap(defs, body)

def neuralink():
    """Neuralink's first patient, 2024: a man in a wheelchair moving a cursor across a chess game on
    a laptop by thought, a faint signal running from his head to the screen. A generic, faceless
    figure, not a likeness."""
    defs = ('<linearGradient id="nwall" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#efe7da"/><stop offset="1" stop-color="#e2d6c3"/></linearGradient>'
            '<linearGradient id="nscreen" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#2b3a4e"/><stop offset="1" stop-color="#1c2735"/></linearGradient>')
    body = [f'<rect width="{W}" height="{H}" fill="url(#nwall)"/>',
            f'<rect y="600" width="{W}" height="200" fill="#b8a283"/>', f'<rect y="596" width="{W}" height="8" fill="#a48e70"/>']
    # A window with soft daylight, and a plant
    body.append('<rect x="70" y="90" width="300" height="330" rx="6" fill="#cfe2ee"/><rect x="70" y="90" width="300" height="330" rx="6" fill="none" stroke="#fbf8f2" stroke-width="16"/>'
                '<line x1="220" y1="90" x2="220" y2="420" stroke="#fbf8f2" stroke-width="10"/><line x1="70" y1="255" x2="370" y2="255" stroke="#fbf8f2" stroke-width="10"/>')
    body.append('<rect x="1040" y="500" width="70" height="100" rx="10" fill="#c46a43"/>')
    for dx, dy, r in ((-24, -40, 36), (26, -52, 40), (0, -86, 38), (-40, -88, 26), (40, -100, 28)):
        body.append(f'<ellipse cx="{1075 + dx}" cy="{500 + dy}" rx="{r * 0.6:.0f}" ry="{r}" fill="#4f8a4f"/>')
    # The table and laptop, its screen turned toward him and us
    body.append('<rect x="640" y="470" width="360" height="22" rx="6" fill="#8a6a45"/><rect x="664" y="492" width="16" height="108" fill="#7a5c3a"/><rect x="960" y="492" width="16" height="108" fill="#7a5c3a"/>')
    body.append(f'<polygon points="{pts([(700, 468), (940, 468), (960, 458), (712, 458)])}" fill="#b9c0c8"/>')
    body.append(f'<polygon points="{pts([(712, 458), (952, 458), (930, 250), (690, 270)])}" fill="#9aa3ad"/>')
    body.append(f'<polygon points="{pts([(722, 448), (940, 448), (920, 262), (702, 280)])}" fill="url(#nscreen)"/>')
    # The chess game on the screen, drawn flat and skewed onto it
    board = []
    for r in range(8):
        for c in range(8):
            board.append(f'<rect x="{c * 20}" y="{r * 20}" width="20" height="20" fill="{"#e8d8b0" if (r + c) % 2 == 0 else "#9c7a54"}"/>')
    # Chess pieces mid-game (solid glyphs, filled white or black)
    pieces = ((4, 7, "♚", "#f6f6f2"), (3, 7, "♛", "#f6f6f2"), (0, 7, "♜", "#f6f6f2"), (5, 6, "♟", "#f6f6f2"), (6, 6, "♟", "#f6f6f2"),
              (2, 5, "♞", "#f6f6f2"), (4, 4, "♟", "#f6f6f2"), (4, 0, "♚", "#1b1c1e"), (3, 0, "♛", "#1b1c1e"), (7, 0, "♜", "#1b1c1e"),
              (2, 1, "♟", "#1b1c1e"), (5, 2, "♞", "#1b1c1e"), (3, 3, "♟", "#1b1c1e"), (6, 1, "♟", "#1b1c1e"))
    for c, r, g, col in pieces:
        stroke = "#1b1c1e" if col != "#1b1c1e" else "#f6f6f2"
        board.append(f'<text x="{c * 20 + 10}" y="{r * 20 + 16}" text-anchor="middle" font-size="17" '
                     f'font-family="DejaVu Sans, Segoe UI Symbol, Apple Symbols, sans-serif" fill="{col}" stroke="{stroke}" stroke-width="0.6">{g}\ufe0e</text>')  # FE0E: draw as text, never as an emoji
    board.append('<rect x="80" y="80" width="20" height="20" fill="none" stroke="#7fe0ff" stroke-width="2.5"/>')
    board.append('<path d="M92 92 l0 22 l6 -6 l5 10 l4 -2 l-5 -10 l8 0 z" fill="#ffffff" stroke="#1b1c1e" stroke-width="1.2"/>')
    body.append(f'<g transform="matrix(0.95 -0.07 0 0.95 748 292)">{"".join(board)}</g>')

    # The wheelchair: big wheel, seat and back, a small front caster
    body.append('<circle cx="330" cy="600" r="118" fill="none" stroke="#3a3f46" stroke-width="12"/>'
                '<circle cx="330" cy="600" r="100" fill="none" stroke="#8d949c" stroke-width="3"/>')
    for k in range(8):
        import math
        a_ = k * math.pi / 8
        body.append(f'<line x1="{330 + 100 * math.cos(a_):.0f}" y1="{600 + 100 * math.sin(a_):.0f}" x2="{330 - 100 * math.cos(a_):.0f}" y2="{600 - 100 * math.sin(a_):.0f}" stroke="#8d949c" stroke-width="2"/>')
    body.append('<circle cx="330" cy="600" r="12" fill="#3a3f46"/><circle cx="520" cy="690" r="26" fill="none" stroke="#3a3f46" stroke-width="9"/>')
    body.append(f'<polyline points="{pts([(250, 330), (270, 560), (470, 560), (520, 664)])}" fill="none" stroke="#3a3f46" stroke-width="12" stroke-linejoin="round"/>')
    body.append('<rect x="268" y="520" width="200" height="34" rx="10" fill="#2c3e57"/>')  # seat cushion
    body.append('<rect x="244" y="330" width="40" height="210" rx="14" fill="#2c3e57"/>')  # backrest

    # Him, seated, faceless, turned toward the screen; hands resting in his lap
    skin, top, trousers, hair = "#d9a77f", "#6c8eb5", "#3b4656", "#3a2a20"
    body.append(f'<polyline points="{pts([(300, 540), (470, 540), (480, 700)])}" fill="none" stroke="{trousers}" stroke-width="52" stroke-linejoin="round"/>')
    body.append('<ellipse cx="500" cy="716" rx="34" ry="14" fill="#2a2a2a"/>')
    body.append(f'<path d="M268 548 L282 380 Q290 350 330 346 Q372 350 380 380 L394 548 Z" fill="{top}"/>')
    body.append(f'<polyline points="{pts([(352, 400), (398, 486), (452, 516)])}" fill="none" stroke="{top}" stroke-width="40" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<circle cx="462" cy="520" r="18" fill="{skin}"/>')
    body.append(f'<rect x="318" y="308" width="30" height="46" rx="12" fill="{skin}"/>')
    body.append(f'<ellipse cx="340" cy="270" rx="50" ry="56" fill="{skin}"/>')
    body.append(f'<path d="M292 268 Q288 208 344 206 Q394 208 390 250 Q366 236 340 238 Q312 242 300 290 Z" fill="{hair}"/>')
    # The signal: soft arcs travelling from his head to the cursor
    for k in range(4):
        r = 70 + k * 46
        body.append(f'<path d="M{340 + r * 0.82:.0f} {270 - r * 0.45:.0f} A{r} {r} 0 0 1 {340 + r * 0.9:.0f} {270 + r * 0.42:.0f}" fill="none" '
                    f'stroke="#4fb6e0" stroke-width="5" stroke-linecap="round" opacity="{0.75 - k * 0.15:.2f}"/>')
    body.append('<line x1="560" y1="300" x2="830" y2="364" stroke="#4fb6e0" stroke-width="2.5" stroke-dasharray="6 9" opacity="0.6"/>')
    return wrap(defs, body)

def jobs():
    """Steve Jobs at home in 1982, cross-legged on the floor of a nearly empty room with a cup of tea,
    the Tiffany lamp beside him and a record player on the floor. Drawn as a scene, not a copy of the
    photograph, and kept as bare as the room: no more than the photograph has in it."""
    defs = ('<linearGradient id="room" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#3a3029"/><stop offset="1" stop-color="#55463a"/></linearGradient>'
            '<radialGradient id="lamplight" cx="0.5" cy="0.5" r="0.5">'
            '<stop offset="0" stop-color="#ffd58a" stop-opacity="0.5"/><stop offset="0.5" stop-color="#f4b860" stop-opacity="0.15"/>'
            '<stop offset="1" stop-color="#f4b860" stop-opacity="0"/></radialGradient>')
    body = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>']
    # A bare wall and a plain wooden floor
    body.append(f'<rect y="560" width="{W}" height="240" fill="#7a5a3c"/>')
    body.append('<circle cx="760" cy="340" r="430" fill="url(#lamplight)"/>')
    # The record player on the floor, with one speaker beside it
    body.append('<rect x="880" y="628" width="190" height="40" rx="4" fill="#cfc8bb"/>')
    body.append('<ellipse cx="955" cy="626" rx="52" ry="8" fill="#1b1815"/><ellipse cx="955" cy="626" rx="12" ry="3" fill="#c2463a"/>')
    body.append('<rect x="1095" y="500" width="90" height="168" rx="6" fill="#2a2420"/><circle cx="1140" cy="598" r="28" fill="#3a332d"/>')
    # The Tiffany lamp: a bronze stem and a leaded-glass dome in a few calm bands
    cx, top = 720, 250
    body.append(f'<rect x="{cx - 7}" y="{top + 110}" width="14" height="300" fill="#6b4a26"/>')
    body.append(f'<ellipse cx="{cx}" cy="{top + 410}" rx="50" ry="11" fill="#5a3d1f"/>')
    body.append(f'<path d="M{cx - 150} {top + 120} Q{cx} {top - 80} {cx + 150} {top + 120} Z" fill="#e7a33b"/>')
    body.append(f'<path d="M{cx - 150} {top + 120} Q{cx} {top + 50} {cx + 150} {top + 120} Z" fill="#4f8a4e"/>')
    for x in (-90, -30, 30, 90):  # the leading between the panes
        body.append(f'<path d="M{cx + x * 1.5} {top + 120} Q{cx + x * 0.9} {top + 40} {cx + x * 0.25} {top + 22}" fill="none" stroke="#3a2a18" stroke-width="3"/>')
    body.append(f'<path d="M{cx - 150} {top + 120} Q{cx} {top - 80} {cx + 150} {top + 120}" fill="none" stroke="#3a2a18" stroke-width="5"/>')
    body.append(f'<rect x="{cx - 156}" y="{top + 116}" width="312" height="12" rx="4" fill="#4a3218"/>')
    body.append(f'<ellipse cx="{cx}" cy="{top + 132}" rx="120" ry="14" fill="#ffe2a0" opacity="0.75"/>')

    # Him, cross-legged on the floor: dark hair, round glasses, a sweater, jeans, a cup in his hands
    skin, hair, sweater, jeans = "#e0b48e", "#2e231c", "#d9d2c3", "#3e5a7a"
    body.append(f'<path d="M300 690 Q330 610 430 620 L480 650 L530 620 Q630 610 660 690 Q600 712 480 700 Q360 712 300 690 Z" fill="{jeans}"/>')
    body.append(f'<ellipse cx="330" cy="690" rx="34" ry="14" fill="#cfc7b8"/><ellipse cx="630" cy="690" rx="34" ry="14" fill="#cfc7b8"/>')
    body.append(f'<path d="M392 640 Q384 520 420 470 Q480 440 540 470 Q576 520 568 640 Z" fill="{sweater}"/>')
    body.append(f'<path d="M420 490 Q395 560 450 600 L490 598" fill="none" stroke="#c4bcac" stroke-width="40" stroke-linecap="round"/>')
    body.append(f'<path d="M540 490 Q565 560 510 600 L470 598" fill="none" stroke="#c4bcac" stroke-width="40" stroke-linecap="round"/>')
    body.append(f'<circle cx="452" cy="598" r="14" fill="{skin}"/><circle cx="508" cy="598" r="14" fill="{skin}"/>')
    body.append(f'<rect x="462" y="572" width="38" height="40" rx="6" fill="#f3efe6"/>')
    body.append(f'<rect x="465" y="430" width="30" height="34" rx="10" fill="{skin}"/>')
    body.append(f'<ellipse cx="480" cy="396" rx="44" ry="54" fill="{skin}"/>')
    body.append(f'<path d="M434 392 Q430 336 480 334 Q534 334 528 392 Q522 362 500 356 Q470 352 446 366 Q438 376 434 392 Z" fill="{hair}"/>')
    body.append(f'<path d="M442 410 Q446 452 480 452 Q514 452 518 410 Q512 440 480 442 Q448 440 442 410 Z" fill="{hair}" opacity="0.85"/>')
    for gx in (462, 498):
        body.append(f'<circle cx="{gx}" cy="398" r="13" fill="none" stroke="#2a2420" stroke-width="3"/>')
    body.append('<line x1="475" y1="398" x2="485" y2="398" stroke="#2a2420" stroke-width="3"/>')
    return wrap(defs, body)

DRAWINGS = {"messi-world-cup": messi, "alphago-lee-sedol": alphago, "feynman-blackboard": feynman,
            "kipchoge-vienna": kipchoge, "honnold-el-capitan": honnold, "alcaraz-wimbledon": alcaraz,
            "neuralink-chess": neuralink, "jobs-empty-room": jobs}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, draw in DRAWINGS.items():
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(draw())
        print(os.path.join(OUT, name + ".svg"))
