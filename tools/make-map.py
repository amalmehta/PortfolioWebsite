#!/usr/bin/env python3
"""Builds the Travel page's map (photos.html): every place I'm going, would like to go, or have been,
as a pin on a world map, with the countries I've been to tinted.

Run from the repo root after changing PINS or BEEN_COUNTRIES: python3 tools/make-map.py
The tests fail if the page no longer matches, or if a trip or wishlist card has no pin.

The coastlines are Natural Earth's public-domain 1:110m countries, as packaged by world-atlas
(tools/data/, see its README), in the Equal Earth projection. Colours come from styles.css, so the
map follows the light and dark themes. A "going" or "want" pin links to its card (id="place-…").
"""
import html, json, math, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "photos.html"
DATA = ROOT / "tools/data/world-atlas-countries-110m.json"
START, END = "<!-- map:start (built by tools/make-map.py; don't edit by hand) -->", "<!-- map:end -->"
I = "    "

# kind, label, latitude, longitude, card id (going and want only). Soonest trips and favourites first.
PINS = [
    ("going", "Chamonix, France", 45.92, 6.87, "place-chamonix"),
    ("want", "Hokkaido, Japan", 42.83, 140.81, "place-hokkaido"),
    ("want", "Lofoten, Norway", 67.93, 13.09, "place-lofoten"),
    ("want", "Patagonia, Chile", -50.94, -73.41, "place-patagonia"),
    ("want", "Bhutan", 27.49, 89.36, "place-bhutan"),
    ("want", "Samarkand, Uzbekistan", 39.65, 66.96, "place-samarkand"),
    ("want", "Faroe Islands", 62.11, -7.43, "place-faroe-islands"),
    ("want", "Garibaldi, British Columbia", 49.93, -123.03, "place-garibaldi"),
    ("want", "Glacier National Park, Montana", 48.68, -113.60, "place-glacier-national-park"),
    ("want", "Moorea, French Polynesia", -17.53, -149.83, "place-moorea"),
    ("been", "London", 51.51, -0.13, None),
    ("been", "Rome", 41.90, 12.50, None),
    ("been", "Florence", 43.77, 11.26, None),
    ("been", "New York City", 40.71, -74.01, None),
    ("been", "Washington, DC", 38.91, -77.04, None),
    ("been", "Boston", 42.36, -71.06, None),
    ("been", "India", 22.5, 79.0, None),
    ("been", "Japan", 36.2, 138.3, None),
    ("been", "Thailand", 15.5, 101.0, None),
    ("been", "Singapore", 1.35, 103.82, None),
]
# Countries tinted as visited (names as in the data)
BEEN_COUNTRIES = {"United Kingdom", "Italy", "United States of America", "India", "Japan", "Thailand"}
KINDS = {"going": "Going", "want": "Want to go", "been": "Been"}

W = 1200
NORTH, SOUTH = 84.0, -58.0  # Antarctica and the far Arctic are left off

# Equal Earth projection (Šavrič, Patterson and Jenny, 2018)
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2


def equal_earth(lon, lat):
    lam, phi = math.radians(lon), math.radians(lat)
    t = math.asin(M * math.sin(phi))
    t2, t6 = t * t, t ** 6
    x = lam * math.cos(t) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = t * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y


SCALE = (W / 2) / equal_earth(180, 0)[0]
TOP = equal_earth(0, NORTH)[1]
H = round((TOP - equal_earth(0, SOUTH)[1]) * SCALE)


def project(lon, lat):
    x, y = equal_earth(lon, max(SOUTH, min(NORTH, lat)))
    return W / 2 + x * SCALE, (TOP - y) * SCALE


def decode(topo):
    """The data's arcs as lists of (lon, lat): delta-encoded and quantized in TopoJSON."""
    (sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    return arcs


def ring(arcs, indexes):
    out = []
    for i in indexes:
        pts = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(pts[1:] if out else pts)
    return out


def path(rings):
    """An SVG path for some rings, dropping points closer than half a pixel, split where a ring
    jumps across the map's edge."""
    d = []
    for r in rings:
        last = None
        for lon, lat in r:
            x, y = project(lon, lat)
            if last is None or abs(x - last[0]) > W / 2:
                d.append(f"M{x:.1f} {y:.1f}")
            elif abs(x - last[0]) + abs(y - last[1]) < 0.5:
                continue
            else:
                d.append(f"L{x:.1f} {y:.1f}")
            last = (x, y)
        d.append("Z")
    return "".join(d).replace("ZM", "Z M")


def country_paths():
    topo = json.loads(DATA.read_text(encoding="utf-8"))
    arcs = decode(topo)
    out = []
    for g in topo["objects"]["countries"]["geometries"]:
        name = g.get("properties", {}).get("name", "")
        if name in ("Antarctica", "Fr. S. Antarctic Lands") or not g.get("arcs"):
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        rings = [ring(arcs, r) for poly in polys for r in poly]
        out.append((name, path(rings)))
    missing = BEEN_COUNTRIES - {n for n, _ in out}
    if missing:
        raise SystemExit(f"make-map.py: no country named {sorted(missing)} in the data")
    return out


def graticule():
    d = []
    for lon in range(-180, 181, 30):
        pts = [project(lon, lat) for lat in range(int(SOUTH), int(NORTH) + 1, 2)]
        d.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts))
    for lat in range(-30, 61, 30):
        pts = [project(lon, lat) for lon in range(-180, 181, 3)]
        d.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts))
    return "".join(d)


def outline():
    left = [project(-180, lat) for lat in range(int(NORTH), int(SOUTH) - 1, -2)]
    right = [project(180, lat) for lat in range(int(SOUTH), int(NORTH) + 1, 2)]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in left + right) + "Z"


def build():
    counts = {k: sum(1 for p in PINS if p[0] == k) for k in KINDS}
    summary = (f"World map of my travels: {counts['going']} place I’m going, {counts['want']} places I’d like to go "
               f"and {counts['been']} places I’ve been")
    lines = [START,
             '<figure class="travel-map">',
             f'  <svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-title">',
             f'    <title id="map-title">{html.escape(summary)}</title>',
             f'    <path class="map-ocean" d="{outline()}"/>',
             f'    <path class="map-grid" d="{graticule()}"/>']
    for name, d in country_paths():
        cls = "map-land map-been" if name in BEEN_COUNTRIES else "map-land"
        lines.append(f'    <path class="{cls}" d="{d}"/>')
    # Been first, then want, then going on top
    for kind in ("been", "want", "going"):
        for k, label, lat, lon, card in PINS:
            if k != kind:
                continue
            x, y = project(lon, lat)
            tip = html.escape(f"{label}: {KINDS[k].lower()}")
            r = {"going": 11, "want": 9, "been": 7}[k]  # big enough to see and tap at phone width
            pin = (f'<g class="pin pin-{k}"><title>{tip}</title><circle class="pin-halo" cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.2:.0f}"/>'
                   f'<circle class="pin-dot" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/></g>')
            lines.append(f'    <a href="#{card}">{pin}</a>' if card else f"    {pin}")
    lines += ["  </svg>",
              '  <figcaption class="map-legend">' + " ".join(
                  f'<span class="key key-{k}">{KINDS[k]} <span class="key-count">{counts[k]}</span></span>' for k in KINDS) + "</figcaption>",
              # Pin names show on hover, which phones don't have, so the places I've been are listed too
              # (the trip and wishlist places have their cards just below)
              '  <p class="map-been-list"><span class="key key-been">Been</span> '
              + html.escape(" · ".join(label for k, label, *_ in PINS if k == "been")) + "</p>",
              "</figure>", END]
    return "\n".join(I + line for line in lines)


def update(page_text, section):
    start = page_text.index(START)
    end = page_text.index(END) + len(END)
    line_start = page_text.rindex("\n", 0, start) + 1
    return page_text[:line_start] + section + page_text[end:]


if __name__ == "__main__":
    PAGE.write_text(update(PAGE.read_text(encoding="utf-8"), build()), encoding="utf-8")
    print("updated the map in photos.html")
