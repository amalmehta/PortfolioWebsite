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


DRAWINGS = {"messi-world-cup": messi}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, draw in DRAWINGS.items():
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(draw())
        print(os.path.join(OUT, name + ".svg"))
