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
        self.roles = []  # (title, has_video) per <article class="role">
        self._role = None
        self.metas = {}  # property/name -> content
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
            self._role = {"title": "", "video": False}
        if self._role is not None:
            if tag == "h3":
                self._in_h3 = True
            if tag == "video":
                self._role["video"] = True

    def handle_endtag(self, tag):
        if tag == "h3":
            self._in_h3 = False
        if self._role is not None and tag == "article":
            self.roles.append(self._role)
            self._role = None
        if self._project is not None and tag == "article":
            self._depth -= 1
            if self._depth == 0:
                self.projects.append(self._project)
                self._project = None

    def handle_data(self, data):
        if self._in_h3 and self._project is not None:
            self._project["title"] += data
        if self._in_h3 and self._role is not None:
            self._role["title"] += data


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def image_size(path):
    """(width, height) of a PNG or baseline/progressive JPEG."""
    data = path.read_bytes()
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


class LinksTest(unittest.TestCase):
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
        og = PAGE.metas.get("og:image", "")
        self.assertTrue(og.startswith(SITE_URL), og)
        path = ROOT / og[len(SITE_URL):]
        self.assertTrue(path.is_file(), path)
        self.assertEqual(image_size(path), (1200, 630))
        self.assertEqual(PAGE.metas.get("og:image:width"), "1200")
        self.assertEqual(PAGE.metas.get("og:image:height"), "630")


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


class MediaTest(unittest.TestCase):
    REQUIRED = ("autoplay", "muted", "loop", "playsinline")
    # Research entries that must carry a clip (matched on their heading).
    RESEARCH = ("PhysicsAI", "Hybrid Robotics Lab", "Video & Image Processing Lab")

    def test_videos_are_silent_inline_loops(self):
        self.assertTrue(PAGE.videos)
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
        with_video = {r["title"] for r in PAGE.roles if r["video"]}
        for name in self.RESEARCH:
            with self.subTest(entry=name):
                self.assertTrue(any(name in title for title in with_video))


class ProjectsTest(unittest.TestCase):
    def test_seven_projects(self):
        self.assertEqual(len(PAGE.projects), 7, [p["title"] for p in PAGE.projects])

    def test_each_card_is_complete(self):
        for p in PAGE.projects:
            with self.subTest(project=p["title"].strip() or "(untitled)"):
                self.assertTrue(p["title"].strip(), "heading")
                self.assertIsNotNone(p["media"], "media slot")
                self.assertTrue(p["text"], "description")
                self.assertGreater(p["chips"], 0, "tags")
                self.assertEqual(p["media"].get("preload"), "none", "lazy media")

    def test_titles_are_unique(self):
        titles = [p["title"].strip() for p in PAGE.projects]
        self.assertEqual(len(titles), len(set(titles)), titles)


class ColoursTest(unittest.TestCase):
    PAIRS = [
        ("accent", "accent-soft"),  # research chips
        ("warm", "warm-soft"),      # project chips
        ("text", "bg"),
        ("muted", "bg"),
        ("accent", "bg"),           # links and dates
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


class ResumeTest(unittest.TestCase):
    def test_source_has_no_phone_number(self):
        self.assertIsNone(PHONE.search(RESUME_TEX.read_text(encoding="utf-8")))

    def test_pdf_is_one_page_without_phone_number(self):
        try:
            from pypdf import PdfReader
        except ImportError:
            self.skipTest("pypdf not installed (pip install pypdf)")
        reader = PdfReader(str(RESUME_PDF))
        self.assertEqual(len(reader.pages), 1)
        self.assertIsNone(PHONE.search(reader.pages[0].extract_text()))


if __name__ == "__main__":
    unittest.main()
