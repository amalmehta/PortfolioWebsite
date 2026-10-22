#!/usr/bin/env python3
"""Builds sitemap.xml: every public page (noindex pages stay out) by its canonical
address, with the date it last changed, so search engines know what to recrawl.

Run from the repo root after editing a page, before committing: python3 tools/make-sitemap.py
A page with uncommitted changes gets today's date; any other, its last commit's.
The tests check the list of pages and that every date is real and not in the future.
"""
import datetime, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent


def changed(page):
    name = page.relative_to(ROOT).as_posix()
    git = lambda *args: subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if git("status", "--porcelain", "--", name):
        return datetime.date.today().isoformat()
    return git("log", "-1", "--format=%cs", "--", name) or datetime.date.today().isoformat()


def build():
    urls = []
    for page in sorted(ROOT.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        if '<meta name="robots" content="noindex">' in html:
            continue
        loc = re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1)
        urls.append((loc, changed(page)))
    urls.sort(key=lambda u: (u[0].count("/"), not u[0].endswith("/"), u[0]))  # the profile first
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!-- Every public page; pages marked noindex (Writings until its first piece, 404) stay out. "
            "Built by tools/make-sitemap.py; the tests check this list. -->\n"
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{loc}</loc><lastmod>{day}</lastmod></url>\n" for loc, day in urls)
            + "</urlset>\n")


if __name__ == "__main__":
    (ROOT / "sitemap.xml").write_text(build(), encoding="utf-8")
    print("wrote sitemap.xml")
