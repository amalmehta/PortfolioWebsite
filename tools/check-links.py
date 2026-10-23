#!/usr/bin/env python3
"""Check every external link on the site's pages still works. Standard library only.

Run from the repo root: python3 tools/check-links.py
Exits 1 if any link is broken. LinkedIn always refuses automated requests (status
999), so that one status counts as fine for linkedin.com.
"""
import pathlib, re, sys, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SITE = "https://amalmehta.github.io/PortfolioWebsite/"

def links():
    found = {}
    for page in sorted(ROOT.glob("*.html")):
        html = re.sub(r"<!--.*?-->", "", page.read_text(encoding="utf-8"), flags=re.S)
        for url in re.findall(r'href="(https?://[^"#]+)', html):
            # The site's own pages are covered by the tests; REPLACE-ME is a checkout link not set up
            # yet, which the tests keep inside a hidden section.
            if not url.startswith(SITE) and "REPLACE-ME" not in url:
                found.setdefault(url, page.name)
    return found

def status(url):
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "GET" or e.code not in (403, 405, 501):
                return e.code
        except Exception as e:
            if method == "GET":
                return str(e)
    return "no response"

def main():
    broken = []
    for url, page in links().items():
        s = status(url)
        ok = isinstance(s, int) and (200 <= s < 400 or (s == 999 and "linkedin.com" in url))
        print(("ok  " if ok else "FAIL"), s, url, f"({page})")
        if not ok:
            broken.append(url)
    print(f"\n{len(broken)} broken" if broken else "\nall links work")
    return 1 if broken else 0

if __name__ == "__main__":
    sys.exit(main())
