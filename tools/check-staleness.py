#!/usr/bin/env python3
"""Fail if a "kept current" date on the site is more than six months old:
the profile's Skills list and the Live interests page.

Run from the repo root: python3 tools/check-staleness.py
The weekly Links workflow runs it too, so GitHub emails a reminder when the
"Kept current · updated <month>" line on the profile stops being true.
"""
import datetime, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_MONTHS = 6

DATES = [  # (page, what it is, pattern before the <time datetime="YYYY-MM">)
    ("index.html", "Skills list", r'class="skills-updated">[^<]*'),
    ("interests.html", "Live interests", r'class="page-updated">[^<]*'),
]

def main():
    today, stale = datetime.date.today(), 0
    for page, what, before in DATES:
        html = (ROOT / page).read_text(encoding="utf-8")
        m = re.search(before + r'<time datetime="(\d{4})-(\d{2})">', html)
        if not m:
            print(f"{what}: no 'updated' date found in {page}"); stale += 1; continue
        year, month = int(m.group(1)), int(m.group(2))
        age = (today.year - year) * 12 + (today.month - month)
        print(f"{what} last updated {year}-{month:02d}: {age} month(s) ago")
        if age > MAX_MONTHS:
            print(f"  over {MAX_MONTHS} months: review it and update its date in {page}"); stale += 1
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
