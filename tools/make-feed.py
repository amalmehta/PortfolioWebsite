#!/usr/bin/env python3
"""Builds feed.xml, an RSS feed of Things I'm thinking about, from thinking.html.

Run from the repo root after adding or editing a thought: python3 tools/make-feed.py
The tests fail if feed.xml no longer matches the page.
"""
import datetime, email.utils, html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://amalmehta.github.io/PortfolioWebsite/"


def text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def build():
    page = re.sub(r"<!--.*?-->", "", (ROOT / "thinking.html").read_text(encoding="utf-8"), flags=re.S)
    items = []
    for id_, body in re.findall(r'<li class="thought" id="([^"]+)">(.*?)</li>', page, flags=re.S):
        title = text(re.search(r"<h2>(.*?)</h2>", body, flags=re.S).group(1))
        summary = text(re.search(r"<p>(.*?)</p>", body, flags=re.S).group(1))
        day = datetime.date.fromisoformat(re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})">', body).group(1))
        when = email.utils.format_datetime(datetime.datetime(day.year, day.month, day.day, 12, tzinfo=datetime.timezone.utc))
        link = f"{SITE}thinking.html#{id_}"
        items.append(f"    <item>\n      <title>{html.escape(title)}</title>\n      <link>{link}</link>\n"
                     f"      <guid>{link}</guid>\n      <pubDate>{when}</pubDate>\n"
                     f"      <description>{html.escape(summary)}</description>\n    </item>\n")
    return ('<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0">\n  <channel>\n'
            "    <title>Things I’m thinking about · Amal Mehta</title>\n"
            f"    <link>{SITE}thinking.html</link>\n"
            "    <description>Open questions and ideas Amal Mehta keeps coming back to.</description>\n"
            "    <language>en</language>\n" + "".join(items) + "  </channel>\n</rss>\n")


if __name__ == "__main__":
    (ROOT / "feed.xml").write_text(build(), encoding="utf-8")
    print("wrote feed.xml")
