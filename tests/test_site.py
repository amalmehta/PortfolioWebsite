"""Checks for the static site. Standard library only; run from the repo root:

    python3 -m unittest discover tests
"""

import re
import struct
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
STYLES = ROOT / "styles.css"
RESUME_TEX = ROOT / "resume" / "Amal Mehta Resume.tex"
RESUME_PDF = ROOT / "resume" / "Amal Mehta Resume.pdf"
MEDIA_DIR = ROOT / "assets" / "media"
MAX_MEDIA_BYTES = 2 * 1024 * 1024
SITE_URL = "https://amalmehta.github.io/PortfolioWebsite/"


class Page(HTMLParser):
    """Collects the tags, ids and links the tests need from one HTML file."""

    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []  # (tag, attr, value)
        self.imgs = []  # attrs dict per <img>
        self.videos = []  # attrs dict per <video>, plus "sources": [data-src/src]
        self.roles = []  # (title, has_media) per <article class="role">
        self._role = None
        self.metas = {}  # property/name -> content
        self.pictures = []  # (img attrs, [srcset candidate URLs]) per <picture>
        self._picture = None
        self.resume_links = []  # visible text of each link to the resume PDF
        self._resume_link = None
        self.projects = []  # one dict per <article class="project">
        self._project = None
        self._depth = 0
        self._in_h3 = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for attr in ("href", "src", "poster", "data-src"):
            if a.get(attr):
                self.links.append((tag, attr, a[attr]))
        if tag == "img":
            self.imgs.append(a)
            if self._picture is not None:
                self.pictures.append((a, self._picture))
        if tag == "picture":
            self._picture = []
        if tag == "source" and self._picture is not None and a.get("srcset"):
            self._picture += [c.split()[0] for c in a["srcset"].split(",")]
        if tag == "a" and local_target(a.get("href", "")) == RESUME_PDF:
            self._resume_link = ""
        if tag == "video":
            self.videos.append(dict(a, sources=[]))
        if tag == "source" and self.videos:
            self.videos[-1]["sources"].append(a.get("data-src") or a.get("src"))
        if tag == "meta" and "content" in a:
            self.metas[a.get("property") or a.get("name")] = a["content"]

        classes = (a.get("class") or "").split()
        if tag == "article" and "project" in classes:
            self._project = {"title": "", "media": None, "chips": 0, "text": False}
            self._depth = 0
        if self._project is not None:
            if tag == "article":
                self._depth += 1
            if tag == "h3":
                self._in_h3 = True
            if tag in ("img", "video"):
                self._project["media"] = a
            if "chip" in classes:
                self._project["chips"] += 1
            if tag == "p" and not classes:
                self._project["text"] = True
        if tag == "article" and "role" in classes:
            self._role = {"title": "", "media": False}
        if self._role is not None:
            if tag == "h3":
                self._in_h3 = True
            if tag in ("img", "video"):
                self._role["media"] = True

    def handle_endtag(self, tag):
        if tag == "h3":
            self._in_h3 = False
        if tag == "picture":
            self._picture = None
        if tag == "a" and self._resume_link is not None:
            self.resume_links.append(" ".join(self._resume_link.split()))
            self._resume_link = None
        if self._role is not None and tag == "article":
            self.roles.append(self._role)
            self._role = None
        if self._project is not None and tag == "article":
            self._depth -= 1
            if self._depth == 0:
                self.projects.append(self._project)
                self._project = None

    def handle_data(self, data):
        if self._resume_link is not None:
            self._resume_link += data
        if self._in_h3 and self._project is not None:
            self._project["title"] += data
        if self._in_h3 and self._role is not None:
            self._role["title"] += data


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def image_size(path):
    """(width, height) of a PNG, baseline/progressive JPEG, WebP, AVIF, or SVG with width/height."""
    data = path.read_bytes()
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if chunk == b"VP8L":
            b = int.from_bytes(data[21:25], "little")
            return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
        if chunk == b"VP8X":
            return (int.from_bytes(data[24:27], "little") + 1,
                    int.from_bytes(data[27:30], "little") + 1)
    if data[4:12] in (b"ftypavif", b"ftypavis"):
        at = data.find(b"ispe")
        if at > 0:
            return struct.unpack(">II", data[at + 8:at + 16])
    if path.suffix == ".svg":
        m = re.search(rb'<svg[^>]*\swidth="(\d+)"[^>]*\sheight="(\d+)"', data)
        if m:
            return int(m.group(1)), int(m.group(2))
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            while data[i] == 0xFF:
                i += 1
            marker = data[i]
            i += 1
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                continue
            (length,) = struct.unpack(">H", data[i:i + 2])
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 3:i + 7])
                return w, h
            i += length
    raise ValueError("unrecognised image: %s" % path)


def local_target(url):
    """Repo path a relative URL points to, or None for external/anchor-only URLs."""
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    return ROOT / unquote(parts.path)


def colour_tokens():
    """{'light': {...}, 'dark': {...}} of the hex colour tokens in styles.css."""
    css = STYLES.read_text(encoding="utf-8")
    dark_at = css.index("prefers-color-scheme: dark")
    token = re.compile(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;")
    light = dict(token.findall(css[:dark_at]))
    dark_block = css[dark_at:css.index("}\n}", dark_at)]
    return {"light": light, "dark": dict(light, **dict(token.findall(dark_block)))}


def contrast(fg, bg):
    def luminance(hex_colour):
        channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


PAGE = parse(INDEX)
THINKING = ROOT / "thinking.html"


class LinksTest(unittest.TestCase):
    def test_fonts_are_self_hosted(self):
        # No third-party font servers; every @font-face file and preload exists.
        for page in sorted(ROOT.glob("*.html")):
            with self.subTest(page=page.name):
                self.assertNotIn("fonts.googleapis.com", page.read_text(encoding="utf-8"))
        css = STYLES.read_text(encoding="utf-8")
        faces = re.findall(r'@font-face[^}]*url\("([^"]+)"\)', css)
        self.assertTrue(faces)
        preloads = [v for tag, attr, v in PAGE.links if v.endswith(".woff2")]
        self.assertTrue(preloads, "the Latin fonts should be preloaded")
        for url in faces + preloads:
            with self.subTest(font=url):
                self.assertTrue((ROOT / url).is_file(), url)
        self.assertTrue(set(preloads) <= set(faces), "preloading a file no @font-face uses")

    def test_local_files_exist(self):
        missing = [v for _, _, v in PAGE.links
                   if local_target(v) is not None and not local_target(v).is_file()]
        self.assertEqual(missing, [], "links to files that aren't in the repo")

    def test_in_page_anchors_have_targets(self):
        anchors = {urlsplit(v).fragment for _, _, v in PAGE.links if v.startswith("#")}
        self.assertTrue(anchors, "expected the header's in-page links")
        self.assertEqual(sorted(anchors - PAGE.ids), [], "anchors with no matching id")

    def test_archive_is_not_linked(self):
        # Pages doesn't publish _archive/, so any link into it would 404.
        archived = [v for _, _, v in PAGE.links if "_archive" in v]
        self.assertEqual(archived, [])

    def test_resume_is_linked(self):
        resume = [v for _, attr, v in PAGE.links
                  if attr == "href" and local_target(v) == RESUME_PDF]
        self.assertTrue(resume, "no link to the resume PDF")

    def test_link_preview_image_matches_repo(self):
        # Every page's link-preview image exists at 1200x630; each public page has its own.
        seen = {}
        for name in ("index.html", "interests.html", "photos.html", "thinking.html", "values.html"):
            with self.subTest(page=name):
                page = parse(ROOT / name)
                og = page.metas.get("og:image", "")
                self.assertTrue(og.startswith(SITE_URL), og)
                path = ROOT / og[len(SITE_URL):]
                self.assertTrue(path.is_file(), path)
                self.assertEqual(image_size(path), (1200, 630))
                self.assertEqual(page.metas.get("og:image:width"), "1200")
                self.assertEqual(page.metas.get("og:image:height"), "630")
                seen[name] = og
        self.assertEqual(len(set(seen.values())), len(seen), seen)


class SearchTest(unittest.TestCase):
    def test_each_page_names_its_canonical_address(self):
        for name in ("index.html", "interests.html", "photos.html", "thinking.html", "values.html"):
            with self.subTest(page=name):
                html = (ROOT / name).read_text(encoding="utf-8")
                canon = re.search(r'<link rel="canonical" href="([^"]+)">', html)
                og = re.search(r'<meta property="og:url" content="([^"]+)">', html)
                self.assertTrue(canon and og, "canonical and og:url")
                self.assertEqual(canon.group(1), og.group(1))

    def test_profile_describes_the_person(self):
        import json
        html = INDEX.read_text(encoding="utf-8")
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual((data["@type"], data["name"]), ("Person", "Amal Mehta"))
        self.assertIn("https://www.linkedin.com/in/amal-mehta-264413a9/", data["sameAs"])
        self.assertTrue((ROOT / data["image"][len(SITE_URL):]).is_file())


class EmailTest(unittest.TestCase):
    def test_address_is_not_in_the_raw_pages(self):
        # Bots reading the HTML shouldn't find the address; email.js builds it for visitors.
        for page in sorted(ROOT.glob("*.html")):
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                self.assertNotIn("amal.mehta@gmail.com", html)
                if 'class="email"' in html:
                    self.assertRegex(html, r'<script src="(https://amalmehta\.github\.io/PortfolioWebsite/)?email\.js" defer></script>')
        self.assertTrue((ROOT / "email.js").is_file())


class ImagesTest(unittest.TestCase):
    def test_every_image_has_alt_text(self):
        no_alt = [i["src"] for i in PAGE.imgs if not (i.get("alt") or "").strip()]
        self.assertEqual(no_alt, [])

    def test_declared_size_matches_file(self):
        # width/height reserve space before the image loads; a wrong ratio
        # makes the layout jump.
        for img in PAGE.imgs:
            with self.subTest(src=img["src"]):
                self.assertIn("width", img)
                self.assertIn("height", img)
                actual = image_size(local_target(img["src"]))
                self.assertEqual((int(img["width"]), int(img["height"])), actual)


    def test_picture_variants_exist_with_same_shape(self):
        # Each AVIF/WebP in a <picture> must exist and keep the fallback's
        # aspect ratio, or the browser would show a squashed image.
        self.assertTrue(PAGE.pictures)
        for img, candidates in PAGE.pictures:
            ratio = int(img["width"]) / int(img["height"])
            for url in candidates:
                with self.subTest(src=url):
                    path = local_target(url)
                    self.assertTrue(path.is_file(), url)
                    w, h = image_size(path)
                    self.assertAlmostEqual(w / h, ratio, delta=0.01)


class MediaTest(unittest.TestCase):
    REQUIRED = ("autoplay", "muted", "loop", "playsinline")
    # Research entries that must carry an image or clip (matched on their heading).
    RESEARCH = ("PhysicsAI", "Hybrid Robotics Lab", "Video & Image Processing Lab", "Abbasi-Asl Lab")

    def test_videos_are_silent_inline_loops(self):
        # Cards show stills until real clips exist; any clip added must follow these rules.
        for v in PAGE.videos:
            with self.subTest(poster=v.get("poster")):
                for attr in self.REQUIRED:
                    self.assertIn(attr, v)
                self.assertEqual(v.get("preload"), "none")
                self.assertTrue((v.get("aria-label") or "").strip(), "aria-label")
                self.assertTrue(v.get("poster"), "poster fallback")

    def test_clips_wait_for_media_js(self):
        # data-src keeps the browser from fetching clips until media.js sees
        # them near the screen; a plain src would download on page load.
        for v in PAGE.videos:
            with self.subTest(poster=v.get("poster")):
                self.assertTrue(v["sources"], "no <source>")
                for src in v["sources"]:
                    self.assertTrue(src.endswith(".mp4"), src)
                    self.assertTrue(src.startswith("assets/media/"), src)
        self.assertTrue((ROOT / "media.js").is_file())
        # media.js loads only when there's a clip to play.
        loaded = '<script src="media.js" defer></script>' in INDEX.read_text(encoding="utf-8")
        self.assertEqual(loaded, bool(PAGE.videos))

    def test_poster_size_matches_declared(self):
        for v in PAGE.videos:
            with self.subTest(poster=v["poster"]):
                actual = image_size(local_target(v["poster"]))
                self.assertEqual((int(v["width"]), int(v["height"])), actual)

    def test_media_files_are_small(self):
        files = [local_target(v["poster"]) for v in PAGE.videos]
        files += [local_target(s) for v in PAGE.videos for s in v["sources"]]
        big = ["%s (%.1f MB)" % (f.relative_to(ROOT), f.stat().st_size / 1e6)
               for f in files if f.stat().st_size > MAX_MEDIA_BYTES]
        self.assertEqual(big, [], "re-encode these to under 2 MB (see docs/INSTRUCTIONS.md)")

    def test_research_entries_have_media(self):
        with_media = {r["title"] for r in PAGE.roles if r["media"]}
        for name in self.RESEARCH:
            with self.subTest(entry=name):
                self.assertTrue(any(name in title for title in with_media))


class ProjectsTest(unittest.TestCase):
    def test_eight_projects_and_three_products(self):
        # Cards are split across two sections: Selected projects and Products.
        html = INDEX.read_text(encoding="utf-8")
        def cards(section_id):
            sec = html[html.index(f'<section id="{section_id}"'):]
            return len(re.findall(r'<article class="project"[ >]', sec[:sec.index("</section>")]))
        self.assertEqual((cards("projects"), cards("products")), (8, 3))
        self.assertEqual(len(PAGE.projects), 11, [p["title"] for p in PAGE.projects])

    def test_each_card_is_complete(self):
        for p in PAGE.projects:
            with self.subTest(project=p["title"].strip() or "(untitled)"):
                self.assertTrue(p["title"].strip(), "heading")
                self.assertIsNotNone(p["media"], "media slot")
                self.assertTrue(p["text"], "description")
                self.assertGreater(p["chips"], 0, "tags")
                media = p["media"]
                if "loading" in media:  # a still image
                    self.assertEqual(media["loading"], "lazy", "lazy media")
                else:  # a clip
                    self.assertEqual(media.get("preload"), "none", "lazy media")

    def test_titles_are_unique(self):
        titles = [p["title"].strip() for p in PAGE.projects]
        self.assertEqual(len(titles), len(set(titles)), titles)


class MusingsTest(unittest.TestCase):
    def test_three_groups(self):
        for group in ("adventure", "life", "discovery"):
            with self.subTest(group=group):
                self.assertIn("musings-" + group, PAGE.ids)

    def test_hidden_until_first_note(self):
        # Shown and linked from the nav once it has a note; hidden and unlinked before.
        html = re.sub(r"<!--.*?-->", "", INDEX.read_text(encoding="utf-8"), flags=re.S)
        has_notes = re.search(r'class="musing"', html) is not None
        hidden = re.search(r'<section id="musings"[^>]*\bhidden\b', html) is not None
        linked = ("a", "href", "#musings") in PAGE.links
        self.assertEqual((hidden, linked), (not has_notes, has_notes))


class SkillsTest(unittest.TestCase):
    def test_lists_every_resume_skill(self):
        # The site's skills list is the most current one; the resume's Technical
        # Skills must be a subset of it.
        import html as htmllib
        page = INDEX.read_text(encoding="utf-8")
        section = page[page.index('<section id="skills"'):]
        section = section[:section.index("</section>")]
        chips = {htmllib.unescape(c) for c in re.findall(r'<span class="chip">([^<]+)</span>', section)}
        tex = RESUME_TEX.read_text(encoding="utf-8")
        table = tex[tex.index(r"\section*{Technical Skills}"):tex.index(r"\end{tabular}")]
        resume = {s.strip().replace("\\&", "&") for row in re.findall(r"& (.+?) \\\\", table) for s in re.split(r",(?![^()]*\))", row)}  # commas inside (…) belong to one skill
        self.assertTrue(resume)
        self.assertEqual(sorted(resume - chips), [])

    def test_live_interests_says_when_updated(self):
        html = (ROOT / "interests.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'class="page-updated">[^<]*<time datetime="\d{4}-\d{2}">')

    def test_says_when_updated(self):
        self.assertRegex(INDEX.read_text(encoding="utf-8"), r'class="skills-updated">[^<]*<time datetime="\d{4}-\d{2}">')


class SubpagesTest(unittest.TestCase):
    """thinking.html and photos.html: pages of their own, linked from the profile."""
    PAGES = (THINKING, ROOT / "photos.html")

    def test_linked_from_profile(self):
        profile_links = [v for _, _, v in PAGE.links]
        for path in self.PAGES:
            with self.subTest(page=path.name):
                self.assertIn(path.name, profile_links)

    def test_local_links_resolve(self):
        for path in self.PAGES:
            with self.subTest(page=path.name):
                page = parse(path)
                missing = [v for _, _, v in page.links
                           if local_target(v) is not None and not local_target(v).is_file()]
                self.assertEqual(missing, [])
                self.assertIn("index.html", [v for _, _, v in page.links])

    def test_skier_opens_pong(self):
        # The hidden game: a skier button on the Hokkaido drawing, hidden until
        # pong.js (loaded by the page) shows it and wires it up.
        html = (ROOT / "photos.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'<button type="button" class="skier" aria-label="[^"]+" hidden>')
        self.assertIn('<script src="pong.js" defer></script>', html)
        self.assertTrue((ROOT / "pong.js").is_file())

    def test_messi_replay_is_wired(self):
        # The profile's other hidden extra: "soccer tournaments" opens messi.js's replay.
        html = INDEX.read_text(encoding="utf-8")
        self.assertRegex(html, r'<button type="button" class="messi-egg" aria-label="soccer tournaments \(opens a replay[^"]*\)" hidden>soccer tournaments</button>')
        self.assertIn('<span class="messi-plain">soccer tournaments</span>', html)
        self.assertIn('<script src="messi.js" defer></script>', html)
        self.assertTrue((ROOT / "messi.js").is_file())

    def test_photos_have_alt_and_size(self):
        # Each photo needs alt text and its real width/height, so the grid
        # doesn't jump as photos load. The first two are on screen when the
        # page opens, so they load right away; the rest wait (lazy).
        for i, img in enumerate(parse(ROOT / "photos.html").imgs):
            with self.subTest(src=img["src"]):
                self.assertTrue((img.get("alt") or "").strip(), "alt text")
                self.assertEqual(img.get("loading"), None if i < 2 else "lazy")
                self.assertEqual((int(img["width"]), int(img["height"])), image_size(local_target(img["src"])))


class BooksTest(unittest.TestCase):
    """Live interests' Books I'm reading: cards with an optional star rating."""

    def section(self):
        html = re.sub(r"<!--.*?-->", "", (ROOT / "interests.html").read_text(encoding="utf-8"), flags=re.S)
        s = html[html.index('<section class="books"'):]
        return s[:s.index("</section>")]

    def test_hidden_until_first_book(self):
        s = self.section()
        hidden = re.match(r'<section class="books"[^>]*\bhidden\b', s) is not None
        self.assertEqual(hidden, 'class="book"' not in s)

    def test_star_ratings_are_consistent(self):
        # data-stars, the --stars fill and the spoken label all say the same 0-5 rating.
        for tag in re.findall(r'<p class="stars"[^>]*>', self.section()):
            with self.subTest(stars=tag):
                value = re.search(r'data-stars="([\d.]+)"', tag).group(1)
                n = float(value)
                self.assertTrue(0 <= n <= 5 and (n * 2).is_integer(), "0-5 in halves")
                self.assertIn("--stars: " + value, tag)
                self.assertIn('aria-label="' + value + ' out of 5 stars"', tag)


class ArtSectionTest(unittest.TestCase):
    def test_hidden_until_first_piece(self):
        # Live interests' "My art" shows only once it has a piece.
        html = re.sub(r"<!--.*?-->", "", (ROOT / "interests.html").read_text(encoding="utf-8"), flags=re.S)
        section = html[html.index('<section class="art"'):]
        section = section[:section.index("</section>")]
        has_pieces = 'class="photo"' in section
        hidden = re.match(r'<section class="art"[^>]*\bhidden\b', section) is not None
        self.assertEqual(hidden, not has_pieces)


class ValuesPageTest(unittest.TestCase):
    """values.html: linked quietly from the profile footer once it has entries."""

    def test_linked_only_once_filled(self):
        # While every list still says "Coming soon", nothing links to it.
        html = re.sub(r"<!--.*?-->", "", (ROOT / "values.html").read_text(encoding="utf-8"), flags=re.S)
        has_entries = 'class="value"' in html or 'class="inspo-item"' in html
        self.assertEqual("values.html" in [v for _, _, v in PAGE.links], has_entries)
        if not has_entries:  # no other page links to it either
            for other in ("thinking.html", "photos.html", "interests.html"):
                with self.subTest(page=other):
                    self.assertNotIn("values.html", [v for _, _, v in parse(ROOT / other).links])
        # ...and search engines are asked to skip it until then.
        self.assertEqual('<meta name="robots" content="noindex">' in html, not has_entries)

    def test_local_links_resolve(self):
        page = parse(ROOT / "values.html")
        missing = [v for _, _, v in page.links
                   if local_target(v) is not None and not local_target(v).is_file()]
        self.assertEqual(missing, [])


class ColoursTest(unittest.TestCase):
    PAIRS = [
        ("accent", "accent-soft"),  # research chips
        ("warm", "warm-soft"),      # project chips
        ("text", "bg"),
        ("muted", "bg"),
        ("accent", "bg"),           # links and dates
        ("faint", "bg"),            # tags, credits, publication line
        ("faint", "surface"),
    ]

    def test_text_contrast_in_both_themes(self):
        themes = colour_tokens()
        for theme, tokens in themes.items():
            for fg, bg in self.PAIRS:
                with self.subTest(theme=theme, pair="%s on %s" % (fg, bg)):
                    ratio = contrast(tokens[fg], tokens[bg])
                    self.assertGreaterEqual(ratio, 4.5, "%.2f:1" % ratio)

    def test_dark_mode_overrides_every_colour(self):
        css = STYLES.read_text(encoding="utf-8")
        dark_at = css.index("prefers-color-scheme: dark")
        light = set(re.findall(r"--([\w-]+):\s*#", css[:dark_at]))
        dark = set(re.findall(r"--([\w-]+):\s*#", css[dark_at:css.index("}\n}", dark_at)]))
        self.assertEqual(sorted(light - dark), [])


PHONE = re.compile(r"(\+?\d[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}")


class PapersTest(unittest.TestCase):
    def test_link_sizes_match_files(self):
        # "(PDF, 374 KB)" / "(PDF, 1.2 MB)" on each papers/ link matches the file.
        html = INDEX.read_text(encoding="utf-8")
        links = re.findall(r'<a href="(papers/[^"]+\.pdf)"[^>]*>[^<]*\(PDF, ([\d.]+) (KB|MB)\)', html)
        self.assertTrue(links)
        for href, num, unit in links:
            with self.subTest(pdf=href):
                size = (ROOT / href).stat().st_size
                shown = f"{round(size / 1000)}" if unit == "KB" else f"{size / 1e6:.1f}"
                self.assertEqual(num, shown)
                self.assertEqual(unit, "KB" if size < 1e6 else "MB")


class ResumeTest(unittest.TestCase):
    def test_source_has_no_phone_number(self):
        self.assertIsNone(PHONE.search(RESUME_TEX.read_text(encoding="utf-8")))

    def test_links_say_pdf_and_size(self):
        # Every resume link says it opens a PDF; the ones in the page body also
        # give its size, which must match the file (rebuild the PDF -> update).
        size_kb = round(RESUME_PDF.stat().st_size / 1000)
        self.assertTrue(PAGE.resume_links)
        for text in PAGE.resume_links:
            with self.subTest(link=text):
                self.assertIn("PDF", text)
        sized = [t for t in PAGE.resume_links if re.search(r"\d+ KB", t)]
        self.assertGreaterEqual(len(sized), 2, PAGE.resume_links)
        for text in sized:
            with self.subTest(link=text):
                self.assertIn("%d KB" % size_kb, text)

    def test_pdf_is_one_page(self):
        # Counted with the standard library: the page tree may sit in compressed
        # object streams, so inflate every Flate stream and look for /Type /Pages.
        # (The phone-number rule is checked on the LaTeX source above.)
        import zlib
        data = RESUME_PDF.read_bytes()
        chunks = [data]
        for m in re.finditer(rb"/FlateDecode.*?stream\r?\n", data, re.S):
            start = m.end(); end = data.find(b"endstream", start)
            try:
                chunks.append(zlib.decompress(data[start:end]))
            except zlib.error:
                pass
        counts = [int(c) for chunk in chunks
                  for c in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)|/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", chunk)
                  for c in c if c]
        self.assertTrue(counts, "no page tree found")
        self.assertEqual(max(counts), 1, "the resume should fit on one page")


if __name__ == "__main__":
    unittest.main()
